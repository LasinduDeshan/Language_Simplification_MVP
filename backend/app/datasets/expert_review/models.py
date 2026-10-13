"""SQLAlchemy ORM models for Stage 27 Expert Review persistence.

Defines persistent entities with database-level uniqueness constraints and
append-only audit tracking:
- Reviewers and qualifications
- Consent and confidentiality records
- Batches and assignments
- Sealed review submissions
- Adjudication cases
- Revisions
- Audit events
- Release approvals
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, UniqueConstraint, CheckConstraint, Index, event, DDL
)
from sqlalchemy.orm import relationship
from app.database.db import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class ExpertReviewer(Base):
    __tablename__ = "expert_reviewers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    reviewer_id = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False, default="reviewer")  # reviewer, adjudicator, admin
    qualification_category = Column(String(100), nullable=False)
    qualification_tracks = Column(JSON, nullable=False, default=list)
    relevant_experience_years = Column(Integer, nullable=False, default=5)
    calibration_completed = Column(Boolean, nullable=False, default=False)
    calibration_agreement_score = Column(Float, nullable=False, default=0.0)
    account_status = Column(String(20), nullable=False, default="active")  # active, revoked, suspended
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    consents = relationship("ReviewerConsent", back_populates="reviewer", cascade="all, delete-orphan")
    submissions = relationship("ExpertReviewSubmission", back_populates="reviewer")


class ReviewerConsent(Base):
    __tablename__ = "expert_reviewer_consents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    reviewer_id = Column(String(50), ForeignKey("expert_reviewers.reviewer_id"), nullable=False, index=True)
    participation_agreement_signed = Column(Boolean, nullable=False, default=False)
    confidentiality_undertaking_signed = Column(Boolean, nullable=False, default=False)
    conflict_of_interest_declared = Column(Boolean, nullable=False, default=False)
    coi_details = Column(Text, nullable=True)
    signed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_or_signature_hash = Column(String(64), nullable=True)

    reviewer = relationship("ExpertReviewer", back_populates="consents")


class ExpertReviewBatch(Base):
    __tablename__ = "expert_review_batches"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    batch_id = Column(String(50), unique=True, nullable=False, index=True)
    reviewer_panel_id = Column(String(50), nullable=False)
    reviewer_a_id = Column(String(50), nullable=False)
    reviewer_b_id = Column(String(50), nullable=False)
    item_count = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="assigned")  # assigned, in_progress, completed, revoked
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint("reviewer_a_id != reviewer_b_id", name="ck_batch_distinct_reviewers"),
    )


class ExpertReviewAssignment(Base):
    __tablename__ = "expert_review_assignments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    assignment_id = Column(String(64), nullable=False, index=True)
    batch_id = Column(String(50), nullable=False, index=True)
    record_id = Column(String(64), nullable=False, index=True)
    reviewer_id = Column(String(50), ForeignKey("expert_reviewers.reviewer_id"), nullable=False, index=True)
    reviewer_role = Column(String(20), nullable=False)  # reviewer_a, reviewer_b
    review_round = Column(Integer, nullable=False, default=1)
    status = Column(String(20), nullable=False, default="assigned")  # assigned, completed, revoked
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("assignment_id", "reviewer_role", name="uq_assignment_role"),
        UniqueConstraint("reviewer_id", "record_id", "review_round", name="uq_reviewer_record_round"),
    )


class ExpertReviewSubmission(Base):
    __tablename__ = "expert_review_submissions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    submission_id = Column(String(64), unique=True, nullable=False, index=True)
    record_id = Column(String(64), nullable=False, index=True)
    reviewer_id = Column(String(50), ForeignKey("expert_reviewers.reviewer_id"), nullable=False, index=True)
    batch_id = Column(String(50), nullable=False, index=True)
    review_round = Column(Integer, nullable=False, default=1)
    taxonomy_class = Column(String(50), nullable=False)
    ratings = Column(JSON, nullable=False)
    critical_checks = Column(JSON, nullable=False)
    workflow_flags = Column(JSON, nullable=False)
    support_tier_review = Column(JSON, nullable=True)
    lexicon_disposition = Column(String(50), nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    provisional_disposition = Column(String(50), nullable=False)
    submission_hash = Column(String(64), unique=True, nullable=False)
    is_sealed = Column(Boolean, nullable=False, default=True)  # Append-only sealed record
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("reviewer_id", "record_id", "review_round", name="uq_sub_reviewer_record_round"),
    )

    reviewer = relationship("ExpertReviewer", back_populates="submissions")


class ExpertAdjudicationCase(Base):
    __tablename__ = "expert_adjudications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    adjudication_case_id = Column(String(64), nullable=False, index=True)
    record_id = Column(String(64), nullable=False, index=True)
    adjudicator_id = Column(String(50), ForeignKey("expert_reviewers.reviewer_id"), nullable=False)
    resolution_version = Column(Integer, nullable=False, default=1)
    reviewer_a_submission_id = Column(String(64), nullable=False)
    reviewer_b_submission_id = Column(String(64), nullable=False)
    conflict_reasons = Column(JSON, nullable=False)
    final_taxonomy_class = Column(String(50), nullable=False)
    final_disposition = Column(String(50), nullable=False)
    adjudicated_critical_checks = Column(JSON, nullable=False)
    adjudicated_ratings = Column(JSON, nullable=True)
    decision_rationale = Column(Text, nullable=False)
    revision_required = Column(Boolean, nullable=False, default=False)
    adjudicated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("adjudication_case_id", "resolution_version", name="uq_adj_case_version"),
    )


class ExpertRevision(Base):
    __tablename__ = "expert_revisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    revision_id = Column(String(64), unique=True, nullable=False, index=True)
    record_id = Column(String(64), nullable=False, index=True)
    source_group_id = Column(String(64), nullable=False)
    original_text = Column(Text, nullable=False)
    revised_text = Column(Text, nullable=False)
    original_hash = Column(String(64), nullable=False)
    revised_hash = Column(String(64), nullable=False)
    revision_reason = Column(Text, nullable=False)
    revised_by = Column(String(50), nullable=False)
    stage14_schema_validation = Column(String(20), nullable=False, default="PASSED")
    stage15_quality_validation = Column(String(20), nullable=False, default="PASSED")
    final_disposition = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ExpertReviewAuditLog(Base):
    """Append-only audit trail for all governance events."""
    __tablename__ = "expert_review_audit_log"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_id = Column(String(64), unique=True, nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # submission_sealed, adjudication_resolved, etc.
    actor_id = Column(String(50), nullable=False)
    record_id = Column(String(64), nullable=True)
    details = Column(JSON, nullable=False, default=dict)
    event_hash = Column(String(64), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


class ExpertReleaseApproval(Base):
    __tablename__ = "expert_release_approvals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    release_version = Column(String(20), nullable=False, unique=True)
    approved_by = Column(String(50), nullable=False)
    signoff_role = Column(String(50), nullable=False)
    unresolved_count = Column(Integer, nullable=False, default=0)
    unaccounted_count = Column(Integer, nullable=False, default=0)
    immutability_verified = Column(Boolean, nullable=False, default=False)
    approved_for_stage28_evaluation = Column(Boolean, nullable=False, default=False)
    approved_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# =============================================================================
# Append-Only and Immutability ORM Event Listeners
# =============================================================================

@event.listens_for(ExpertReviewSubmission, "before_update")
def receive_before_update_submission(mapper, connection, target):
    if getattr(target, "is_sealed", False):
        raise ValueError("Cannot update sealed review submission")


@event.listens_for(ExpertReviewSubmission, "before_delete")
def receive_before_delete_submission(mapper, connection, target):
    if getattr(target, "is_sealed", False):
        raise ValueError("Cannot delete sealed review submission")


@event.listens_for(ExpertReviewAuditLog, "before_update")
def receive_before_update_audit(mapper, connection, target):
    raise ValueError("Audit log is append-only: updates not allowed")


@event.listens_for(ExpertReviewAuditLog, "before_delete")
def receive_before_delete_audit(mapper, connection, target):
    raise ValueError("Audit log is append-only: deletions not allowed")


@event.listens_for(ExpertAdjudicationCase, "before_update")
def receive_before_update_adjudication(mapper, connection, target):
    raise ValueError("Adjudication records are immutable: updates not allowed")


@event.listens_for(ExpertAdjudicationCase, "before_delete")
def receive_before_delete_adjudication(mapper, connection, target):
    raise ValueError("Adjudication records are immutable: deletions not allowed")


@event.listens_for(ExpertReleaseApproval, "before_update")
def receive_before_update_release_approval(mapper, connection, target):
    raise ValueError("Release approvals are immutable: updates not allowed")


@event.listens_for(ExpertReleaseApproval, "before_delete")
def receive_before_delete_release_approval(mapper, connection, target):
    raise ValueError("Release approvals are immutable: deletions not allowed")


# =============================================================================
# Database-Level Triggers (Installed on create_all for SQLite engines)
# =============================================================================

TRIGGER_DDLS = [
    """
    CREATE TRIGGER IF NOT EXISTS trg_prevent_sealed_submission_update
    BEFORE UPDATE ON expert_review_submissions
    FOR EACH ROW
    WHEN OLD.is_sealed = 1
    BEGIN
        SELECT RAISE(ABORT, 'Cannot update sealed review submission');
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trg_prevent_sealed_submission_delete
    BEFORE DELETE ON expert_review_submissions
    FOR EACH ROW
    WHEN OLD.is_sealed = 1
    BEGIN
        SELECT RAISE(ABORT, 'Cannot delete sealed review submission');
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trg_prevent_audit_log_update
    BEFORE UPDATE ON expert_review_audit_log
    FOR EACH ROW
    BEGIN
        SELECT RAISE(ABORT, 'Audit log is append-only: updates not allowed');
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trg_prevent_audit_log_delete
    BEFORE DELETE ON expert_review_audit_log
    FOR EACH ROW
    BEGIN
        SELECT RAISE(ABORT, 'Audit log is append-only: deletions not allowed');
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trg_prevent_adjudication_update
    BEFORE UPDATE ON expert_adjudications
    FOR EACH ROW
    BEGIN
        SELECT RAISE(ABORT, 'Adjudication records are immutable: updates not allowed');
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trg_prevent_adjudication_delete
    BEFORE DELETE ON expert_adjudications
    FOR EACH ROW
    BEGIN
        SELECT RAISE(ABORT, 'Adjudication records are immutable: deletions not allowed');
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trg_prevent_release_approval_update
    BEFORE UPDATE ON expert_release_approvals
    FOR EACH ROW
    BEGIN
        SELECT RAISE(ABORT, 'Release approvals are immutable: updates not allowed');
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trg_prevent_release_approval_delete
    BEFORE DELETE ON expert_release_approvals
    FOR EACH ROW
    BEGIN
        SELECT RAISE(ABORT, 'Release approvals are immutable: deletions not allowed');
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trg_prevent_same_reviewer_batch
    BEFORE INSERT ON expert_review_batches
    FOR EACH ROW
    WHEN NEW.reviewer_a_id = NEW.reviewer_b_id
    BEGIN
        SELECT RAISE(ABORT, 'Reviewer A and Reviewer B must be different people');
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trg_prevent_same_reviewer_batch_upd
    BEFORE UPDATE ON expert_review_batches
    FOR EACH ROW
    WHEN NEW.reviewer_a_id = NEW.reviewer_b_id
    BEGIN
        SELECT RAISE(ABORT, 'Reviewer A and Reviewer B must be different people');
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trg_prevent_same_reviewer_dual_assignment
    BEFORE INSERT ON expert_review_assignments
    FOR EACH ROW
    WHEN EXISTS (
        SELECT 1 FROM expert_review_assignments
        WHERE record_id = NEW.record_id
          AND review_round = NEW.review_round
          AND reviewer_id = NEW.reviewer_id
    )
    BEGIN
        SELECT RAISE(ABORT, 'Reviewer A and Reviewer B must be different people');
    END;
    """,
]

for _stmt in TRIGGER_DDLS:
    event.listen(Base.metadata, "after_create", DDL(_stmt))
