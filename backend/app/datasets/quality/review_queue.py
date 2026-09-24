"""Manual review queue management and Stage 15 triage decision engine."""
import uuid
import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.datasets.quality.enums import ReviewPriority, ReviewStatus, TriageAction, QualityStatus, RuleSeverity
from app.datasets.quality.models import ManualReviewQueueEntry, RecordQualitySummary, QualityRuleResult
from app.datasets.quality.schemas import ManualReviewQueueEntryV1, TriageDecisionRequestV1


class ReviewQueueManager:
    """Manages creation, filtering, and triage of manual review queue entries."""

    @classmethod
    def create_entry(
        cls,
        db: Session,
        run_id: str,
        record_id: str,
        dataset_layer: str,
        triggering_rule_ids: List[str],
        summary: str,
        priority: ReviewPriority = ReviewPriority.MEDIUM,
        recommended_review_type: str = "linguistic_triage"
    ) -> ManualReviewQueueEntry:
        """Creates a persistent review queue entry."""
        entry_id = f"REV-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
        entry = ManualReviewQueueEntry(
            entry_id=entry_id,
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            priority=priority.value if hasattr(priority, "value") else str(priority),
            triggering_rule_ids=triggering_rule_ids,
            summary=summary,
            recommended_review_type=recommended_review_type,
            review_status=ReviewStatus.PENDING.value,
            created_at=datetime.datetime.utcnow()
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @classmethod
    def get_entries(
        cls,
        db: Session,
        dataset_layer: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ManualReviewQueueEntry]:
        """Queries and filters review queue entries with pagination."""
        query = db.query(ManualReviewQueueEntry)
        if dataset_layer:
            query = query.filter(ManualReviewQueueEntry.dataset_layer == dataset_layer)
        if priority:
            query = query.filter(ManualReviewQueueEntry.priority == priority)
        if status:
            query = query.filter(ManualReviewQueueEntry.review_status == status)
        return query.order_by(ManualReviewQueueEntry.created_at.desc()).offset(skip).limit(limit).all()

    @classmethod
    def apply_triage_decision(
        cls,
        db: Session,
        entry_id: str,
        request: TriageDecisionRequestV1
    ) -> ManualReviewQueueEntry:
        """
        Applies a Stage 15 permitted triage decision to a review queue entry.
        Strictly rejects 'approved', 'expert_reviewed', or child-delivery flags.
        """
        entry = db.query(ManualReviewQueueEntry).filter(ManualReviewQueueEntry.entry_id == entry_id).first()
        if not entry:
            raise ValueError(f"Review queue entry '{entry_id}' not found.")

        action = request.action
        if action == TriageAction.ACKNOWLEDGE_FINDING:
            entry.review_status = ReviewStatus.ACKNOWLEDGED.value
        elif action == TriageAction.MARK_FALSE_POSITIVE:
            entry.review_status = ReviewStatus.FALSE_POSITIVE.value
        elif action == TriageAction.SUBMIT_CORRECTION:
            entry.review_status = ReviewStatus.CORRECTION_SUBMITTED.value
        elif action == TriageAction.REQUEST_EXPERT_REVIEW:
            entry.review_status = ReviewStatus.EXPERT_REVIEW_REQUESTED.value
        elif action == TriageAction.REVALIDATE:
            entry.review_status = ReviewStatus.PENDING.value

        entry.assigned_reviewer_id = request.reviewer_id
        entry.resolution_notes = request.resolution_notes
        entry.resolved_at = datetime.datetime.utcnow()

        db.commit()
        db.refresh(entry)
        return entry
