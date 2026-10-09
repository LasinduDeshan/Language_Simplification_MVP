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
    ForeignKey, UniqueConstraint, Index
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
