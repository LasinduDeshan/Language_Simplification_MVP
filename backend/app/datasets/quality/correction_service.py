"""Immutable record revision and revalidation service."""
import uuid
import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.datasets.quality.models import RecordRevision, RecordQualitySummary
from app.datasets.quality.schemas import RecordCorrectionRequestV1, RecordRevisionV1


class CorrectionService:
    """Manages immutable record revisions and tracks revalidation status."""

    @classmethod
    def create_revision(
        cls,
        db: Session,
        record_id: str,
        dataset_layer: str,
        request: RecordCorrectionRequestV1,
        previous_content: Dict[str, Any],
        parent_revision_id: Optional[str] = None
    ) -> RecordRevision:
        """Creates an immutable revision entry for a corrected record."""
        revision_id = f"REV-HIST-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
        revision = RecordRevision(
            revision_id=revision_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            parent_revision_id=parent_revision_id,
            previous_content=previous_content,
            corrected_content=request.corrected_content,
            change_reason=request.change_reason,
            created_by=request.reviewer_id,
            created_at=datetime.datetime.utcnow(),
            revalidated=False
        )
        db.add(revision)
        db.commit()
        db.refresh(revision)
        return revision

    @classmethod
    def get_revision_history(cls, db: Session, record_id: str) -> list:
        """Retrieves chronological revision history for a record."""
        return db.query(RecordRevision).filter(RecordRevision.record_id == record_id).order_by(RecordRevision.created_at.asc()).all()

    @classmethod
    def mark_revalidated(cls, db: Session, revision_id: str, run_id: str):
        """Marks a revision as revalidated in a specific validation run."""
        rev = db.query(RecordRevision).filter(RecordRevision.revision_id == revision_id).first()
        if rev:
            rev.revalidated = True
            rev.revalidation_run_id = run_id
            db.commit()
