"""Adjudication Service for Stage 27.

Detects reviewer conflicts across taxonomies, critical failure flags, and rating divergence.
Manages the adjudication queue and records binding arbiter resolutions.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from .schemas import (
    AdjudicationRecord,
    CriticalFailureFlags,
    DimensionRatings,
    FinalDisposition,
    RecordReviewSubmission,
    TaxonomyClass,
)


class AdjudicationService:
    """Manages conflict detection, adjudication routing, and resolution logging."""

    def __init__(self) -> None:
        self._adjudications: Dict[str, AdjudicationRecord] = {}  # adjudication_id -> record
        self._adjudication_queue: Dict[str, List[str]] = {}  # item_id -> list of conflict reasons
        self._queue_submissions: Dict[str, Tuple[RecordReviewSubmission, RecordReviewSubmission]] = {}

    def check_conflict(
        self,
        sub_a: RecordReviewSubmission,
        sub_b: RecordReviewSubmission,
        is_reformulation_candidate: bool = False,
    ) -> Tuple[bool, List[str]]:
        """Evaluates whether dual independent reviews require lead adjudicator resolution."""
        reasons = []

        # 1. Taxonomy classification mismatch
        if sub_a.taxonomy_class != sub_b.taxonomy_class:
            reasons.append(
                f"Taxonomy mismatch: Reviewer A assigned '{sub_a.taxonomy_class.value}', "
                f"Reviewer B assigned '{sub_b.taxonomy_class.value}'."
            )

        # 2. Critical binary check conflict
        crit_a_dict = sub_a.critical_checks.model_dump()
        crit_b_dict = sub_b.critical_checks.model_dump()
        for flag_name, val_a in crit_a_dict.items():
            val_b = crit_b_dict.get(flag_name)
            if val_a != val_b:
                reasons.append(
                    f"Critical flag mismatch on '{flag_name}': A={val_a}, B={val_b}."
                )

        # 3. Discrepancy >= 2 points on core dimensions
        core_dims = [
            ("meaning_preservation", sub_a.ratings.meaning_preservation, sub_b.ratings.meaning_preservation),
            ("age_appropriateness", sub_a.ratings.age_appropriateness, sub_b.ratings.age_appropriateness),
            ("overall_child_language_suitability", sub_a.ratings.overall_child_language_suitability, sub_b.ratings.overall_child_language_suitability),
        ]
        for dim_name, score_a, score_b in core_dims:
            if abs(score_a - score_b) >= 2:
                reasons.append(
                    f"Rating gap >= 2 points ({dim_name} gap >= 2): A={score_a}, B={score_b}."
                )

        # 4. Opposing provisional dispositions
        disp_a = sub_a.determine_provisional_disposition()
        disp_b = sub_b.determine_provisional_disposition()
        if disp_a != disp_b:
            reasons.append(
                f"Opposing dispositions: Reviewer A={disp_a.value}, Reviewer B={disp_b.value}."
            )

        # 5. Support-tier progression dispute
        if sub_a.support_tier_review and sub_b.support_tier_review:
            if sub_a.support_tier_review.support_progression_valid != sub_b.support_tier_review.support_progression_valid:
                reasons.append("Support-tier progression validity dispute between reviewers.")

        # 6. Mandatory reformulation queue without exact consensus
        if is_reformulation_candidate and reasons:
            reasons.append("Mandatory reformulation queue member requires unanimous consensus.")

        is_conflict = len(reasons) > 0
        if is_conflict:
            self._adjudication_queue[sub_a.item_id] = reasons
            self._queue_submissions[sub_a.item_id] = (sub_a, sub_b)

        return is_conflict, reasons

    def detect_conflicts(
        self,
        sub_a: RecordReviewSubmission,
        sub_b: RecordReviewSubmission,
        is_reformulation_candidate: bool = False,
    ) -> List[str]:
        """Convenience method returning list of conflict reasons."""
        _, reasons = self.check_conflict(sub_a, sub_b, is_reformulation_candidate)
        return reasons

    def add_to_queue(
        self,
        item_id: str,
        sub_a: RecordReviewSubmission,
        sub_b: RecordReviewSubmission,
        reasons: List[str],
    ) -> None:
        """Explicitly add item to adjudication queue with reviews."""
        self._adjudication_queue[item_id] = reasons
        self._queue_submissions[item_id] = (sub_a, sub_b)

    def list_queue_items(self) -> Dict[str, List[str]]:
        """List items currently awaiting adjudication with conflict reasons."""
        return dict(self._adjudication_queue)

    def get_unresolved_items(self) -> List[str]:
        """List IDs of items awaiting adjudication."""
        return list(self._adjudication_queue.keys())

    def record_adjudication(
        self,
        adjudication_id: str,
        item_id: str,
        adjudicator_id: str,
        reviewer_a_id: str,
        reviewer_b_id: str,
        reviewer_a_submission_id: str,
        reviewer_b_submission_id: str,
        final_taxonomy_class: TaxonomyClass,
        final_disposition: FinalDisposition,
        adjudicated_critical_checks: CriticalFailureFlags,
        decision_rationale: str,
        adjudicated_ratings: Optional[DimensionRatings] = None,
        revision_required: bool = False,
    ) -> AdjudicationRecord:
        """Records a binding adjudication decision, resolving the item."""
        conflict_reasons = self._adjudication_queue.pop(item_id, ["Direct arbiter review"])
        self._queue_submissions.pop(item_id, None)

        record = AdjudicationRecord(
            adjudication_id=adjudication_id,
            item_id=item_id,
            adjudicator_id=adjudicator_id,
            reviewer_a_id=reviewer_a_id,
            reviewer_b_id=reviewer_b_id,
            reviewer_a_submission_id=reviewer_a_submission_id,
            reviewer_b_submission_id=reviewer_b_submission_id,
            conflict_reasons=conflict_reasons,
            final_taxonomy_class=final_taxonomy_class,
            final_disposition=final_disposition,
            adjudicated_critical_checks=adjudicated_critical_checks,
            adjudicated_ratings=adjudicated_ratings,
            decision_rationale=decision_rationale,
            revision_required=revision_required,
            adjudicated_at=datetime.utcnow(),
        )

        self._adjudications[adjudication_id] = record
        return record

    def resolve_adjudication(
        self,
        item_id: str,
        adjudicator_id: str,
        final_taxonomy_class: TaxonomyClass,
        final_disposition: FinalDisposition,
        adjudicated_critical_checks: CriticalFailureFlags,
        decision_rationale: str,
        adjudication_id: Optional[str] = None,
        adjudicated_ratings: Optional[DimensionRatings] = None,
        revision_required: bool = False,
    ) -> AdjudicationRecord:
        """Resolves queued item by look up or synthetic review references."""
        subs = self._queue_submissions.get(item_id)
        r_a_id = subs[0].reviewer_id if subs else "REV-A"
        r_b_id = subs[1].reviewer_id if subs else "REV-B"
        s_a_id = subs[0].submission_id if subs else "SUB-A"
        s_b_id = subs[1].submission_id if subs else "SUB-B"

        adj_id = adjudication_id or f"ADJ-{uuid.uuid4().hex[:8]}"

        return self.record_adjudication(
            adjudication_id=adj_id,
            item_id=item_id,
            adjudicator_id=adjudicator_id,
            reviewer_a_id=r_a_id,
            reviewer_b_id=r_b_id,
            reviewer_a_submission_id=s_a_id,
            reviewer_b_submission_id=s_b_id,
            final_taxonomy_class=final_taxonomy_class,
            final_disposition=final_disposition,
            adjudicated_critical_checks=adjudicated_critical_checks,
            decision_rationale=decision_rationale,
            adjudicated_ratings=adjudicated_ratings,
            revision_required=revision_required,
        )

    def get_adjudication(self, adjudication_id: str) -> Optional[AdjudicationRecord]:
        """Fetch adjudication record by ID."""
        return self._adjudications.get(adjudication_id)

    def list_adjudications(self) -> List[AdjudicationRecord]:
        """List all recorded adjudications."""
        return list(self._adjudications.values())
