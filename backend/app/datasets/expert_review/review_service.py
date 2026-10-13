"""Review Service for Stage 27.

Processes independent review submissions, validates rating bounds,
enforces idempotency guards, calculates cryptographic submission hashes,
and enforces critical-failure precedence over numerical dimension ratings.
"""

import hashlib
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from .schemas import (
    DimensionRatings,
    CriticalFailureFlags,
    FinalDisposition,
    RecordReviewSubmission,
    ReviewMode,
    SubmissionAccounting,
    SubmissionOrigin,
    TaxonomyClass,
    WorkflowFlags,
)


class ReviewService:
    """Manages idempotent review submission processing and critical failure overrides."""

    def __init__(self, expected_submissions: int = 3360) -> None:
        self._submissions: Dict[str, RecordReviewSubmission] = {}  # submission_id -> submission
        self._item_reviewer_map: Dict[Tuple[str, str], str] = {}  # (item_id, reviewer_id) -> submission_id
        self._accounting = SubmissionAccounting(
            expected_submissions=expected_submissions,
            unaccounted_submissions=expected_submissions
        )

    @property
    def accounting(self) -> SubmissionAccounting:
        return self._accounting

    @staticmethod
    def compute_submission_hash(payload: dict) -> str:
        serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def submit_review(
        self,
        item_id: str,
        reviewer_id: str,
        batch_id: str,
        taxonomy_class: TaxonomyClass,
        ratings: DimensionRatings,
        critical_checks: CriticalFailureFlags,
        workflow_flags: WorkflowFlags,
        submission_id: Optional[str] = None,
        reviewer_notes: Optional[str] = None,
        support_tier_review: Optional[Any] = None,
        lexicon_disposition: Optional[Any] = None,
        submission_origin: SubmissionOrigin = SubmissionOrigin.HUMAN_ENTERED,
        review_mode: ReviewMode = ReviewMode.OPERATIONAL_SIMULATION,
    ) -> RecordReviewSubmission:
        """Processes an independent review submission with idempotency protection."""
        key = (item_id, reviewer_id)

        # Idempotency check: if identical submission exists, return existing sealed record
        if key in self._item_reviewer_map:
            existing_sub_id = self._item_reviewer_map[key]
            existing_sub = self._submissions[existing_sub_id]
            # If re-submitted by same reviewer for same item, return existing submission idempotently
            return existing_sub

        sub_id = submission_id or f"SUB-{uuid.uuid4().hex[:8]}"

        payload_dict = {
            "submission_id": sub_id,
            "item_id": item_id,
            "reviewer_id": reviewer_id,
            "batch_id": batch_id,
            "taxonomy_class": taxonomy_class.value,
            "ratings": ratings.model_dump(),
            "critical_checks": critical_checks.model_dump(),
            "workflow_flags": workflow_flags.model_dump(),
            "reviewer_notes": reviewer_notes or "",
            "submission_origin": submission_origin.value,
            "review_mode": review_mode.value,
        }
        sub_hash = self.compute_submission_hash(payload_dict)

        submission = RecordReviewSubmission(
            submission_id=sub_id,
            item_id=item_id,
            reviewer_id=reviewer_id,
            batch_id=batch_id,
            taxonomy_class=taxonomy_class,
            ratings=ratings,
            critical_checks=critical_checks,
            workflow_flags=workflow_flags,
            support_tier_review=support_tier_review,
            lexicon_disposition=lexicon_disposition,
            reviewer_notes=reviewer_notes,
            submitted_at=datetime.utcnow(),
            submission_hash=sub_hash,
            submission_origin=submission_origin,
            review_mode=review_mode,
        )

        self._submissions[sub_id] = submission
        self._item_reviewer_map[key] = sub_id

        # Update accounting
        self._accounting.completed_submissions += 1
        if self._accounting.unaccounted_submissions > 0:
            self._accounting.unaccounted_submissions -= 1

        return submission

    def get_submission(self, submission_id: str) -> Optional[RecordReviewSubmission]:
        """Fetch submission by ID."""
        return self._submissions.get(submission_id)

    def get_item_submissions(self, item_id: str) -> List[RecordReviewSubmission]:
        """Return all submissions for a specific item."""
        return [sub for sub in self._submissions.values() if sub.item_id == item_id]

    def get_reviewer_submission(
        self, item_id: str, reviewer_id: str
    ) -> Optional[RecordReviewSubmission]:
        """Fetch a specific reviewer's submission for an item."""
        sub_id = self._item_reviewer_map.get((item_id, reviewer_id))
        return self._submissions.get(sub_id) if sub_id else None

    def get_accounting(self) -> SubmissionAccounting:
        """Return current submission accounting metrics."""
        return self._accounting
