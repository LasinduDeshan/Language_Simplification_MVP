"""
Stage 33 — Candidate Selector and Governed Fallback Coordinator.
Coordinates two-stage candidate resolution and produces the final rewrite record
with fail-closed fallback.
"""

from typing import Dict, List, Optional, Tuple

from app.sinhala_simplification.candidate_filter import CandidateEligibilityFilter
from app.sinhala_simplification.candidate_ranker import CandidateRanker
from app.sinhala_simplification.enums import (
    CandidateTerminalStatus,
    FinalDisposition,
)
from app.sinhala_simplification.rule_registry import GovernedRuleDefinition
from app.sinhala_simplification.schemas import (
    FinalRewriteRecord,
    ProtectedSpan,
    RewriteCandidate,
    RewriteRequest,
)
from app.sinhala_simplification.storage import compute_sha256, write_protected_text


class CandidateSelector:
    """
    Coordinates candidate filtering, ranking, unchanged fallback, and final record creation.
    """

    def __init__(self):
        self.filter = CandidateEligibilityFilter()
        self.ranker = CandidateRanker()

    def select_candidate(
        self,
        request: RewriteRequest,
        source_text: str,
        generated_candidates: List[RewriteCandidate],
        protected_spans: List[ProtectedSpan],
        rules_map: Dict[str, GovernedRuleDefinition],
        output_counter: int,
    ) -> Tuple[FinalRewriteRecord, List[RewriteCandidate]]:
        """
        Executes two-stage resolution and returns (final_rewrite_record, all_candidates_with_terminal_statuses).
        """
        output_id = f"SI-SIMP-OUT-{output_counter:06d}"

        # Stage 1: Eligibility filtering
        eligible, eliminated = self.filter.filter_candidates(
            generated_candidates, source_text, protected_spans
        )

        all_final_candidates: List[RewriteCandidate] = []

        if eligible:
            # Stage 2: Ranking among eligible candidates
            selected, ranked_eligible = self.ranker.rank_candidates(
                eligible, rules_map, source_text
            )
            all_final_candidates.extend(ranked_eligible)
            all_final_candidates.extend(eliminated)

            output_text = selected.candidate_text_internal or ""
            storage_ref, sha256_val = write_protected_text(
                "outputs", f"{output_id}.txt", output_text
            )

            record = FinalRewriteRecord(
                output_id=output_id,
                request_id=request.request_id,
                selected_candidate_id=selected.candidate_id,
                final_disposition=FinalDisposition.DRAFT_REWRITE_SELECTED,
                output_storage_ref=storage_ref,
                output_sha256_internal=sha256_val,
                applied_rule_ids=[selected.rule_id],
                guard_results=selected.guard_results,
                language="si",
                locale="si-LK",
                script="Sinh",
                validation_status="draft",
                expert_validated=False,
                research_eligible=False,
                approved_for_child_delivery=False,
                approved_for_unsupervised_child_delivery=False,
                requires_expert_review=True,
                corpus_view=request.stage31_corpus_view,
                rights_profile_refs=[b.rights_profile_id for b in request.rights_profile_ids_and_versions]
            )
            return record, all_final_candidates

        # If eligible is empty: determine appropriate fail-closed fallback
        all_final_candidates.extend(eliminated)

        # Check if any candidate was deferred to manual review
        has_review = any(c.terminal_status == CandidateTerminalStatus.DEFERRED_MANUAL_REVIEW for c in eliminated)
        has_blocked = len(eliminated) > 0

        if has_review:
            disposition = FinalDisposition.MANUAL_REVIEW_REQUIRED
        elif has_blocked:
            disposition = FinalDisposition.UNCHANGED_ALL_CANDIDATES_BLOCKED
        else:
            disposition = FinalDisposition.UNCHANGED_NO_APPLICABLE_RULE

        output_text = source_text
        storage_ref, sha256_val = write_protected_text(
            "outputs", f"{output_id}.txt", output_text
        )

        record = FinalRewriteRecord(
            output_id=output_id,
            request_id=request.request_id,
            selected_candidate_id=None,
            final_disposition=disposition,
            output_storage_ref=storage_ref,
            output_sha256_internal=sha256_val,
            applied_rule_ids=[],
            guard_results={},
            language="si",
            locale="si-LK",
            script="Sinh",
            validation_status="draft",
            expert_validated=False,
            research_eligible=False,
            approved_for_child_delivery=False,
            approved_for_unsupervised_child_delivery=False,
            requires_expert_review=True,
            corpus_view=request.stage31_corpus_view,
            rights_profile_refs=[b.rights_profile_id for b in request.rights_profile_ids_and_versions]
        )
        return record, all_final_candidates
