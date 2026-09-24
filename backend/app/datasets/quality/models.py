"""SQLAlchemy models for Stage 15 Quality Validation persistent storage."""
import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    JSON,
    Index
)
from sqlalchemy.orm import relationship
from app.database.db import Base


class ValidationRun(Base):
    """Represents an executed or running dataset quality validation session."""
    __tablename__ = "dataset_validation_runs"

    run_id = Column(String(64), primary_key=True, index=True)
    dataset_layer = Column(String(64), nullable=False, index=True)  # 'all', 'adaptation_test_set', 'simplification_corpus', etc.
    dataset_version = Column(String(32), nullable=False, default="0.1.0")
    quality_rule_set_version = Column(String(32), nullable=False, default="1.0.0")
    status = Column(String(32), nullable=False, default="queued", index=True)  # queued, running, completed, failed, cancelled
    
    total_records = Column(Integer, nullable=False, default=0)
    passed_count = Column(Integer, nullable=False, default=0)
    failed_count = Column(Integer, nullable=False, default=0)
    review_required_count = Column(Integer, nullable=False, default=0)
    quarantined_count = Column(Integer, nullable=False, default=0)
    
    idempotency_key = Column(String(128), nullable=True, unique=True, index=True)
    created_by = Column(String(64), nullable=False, default="system_validator")
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    rule_results = relationship("QualityRuleResult", back_populates="validation_run", cascade="all, delete-orphan")
    summaries = relationship("RecordQualitySummary", back_populates="validation_run", cascade="all, delete-orphan")
    review_entries = relationship("ManualReviewQueueEntry", back_populates="validation_run", cascade="all, delete-orphan")


class QualityRuleResult(Base):
    """Evaluation result for an individual quality rule applied to a record."""
    __tablename__ = "dataset_quality_rule_results"

    result_id = Column(String(64), primary_key=True, index=True)
    run_id = Column(String(64), ForeignKey("dataset_validation_runs.run_id"), nullable=False, index=True)
    record_id = Column(String(64), nullable=False, index=True)
    dataset_layer = Column(String(64), nullable=False, index=True)
    
    rule_id = Column(String(64), nullable=False, index=True)
    rule_version = Column(String(32), nullable=False, default="1.0.0")
    validator_name = Column(String(128), nullable=False)
    validator_version = Column(String(32), nullable=False, default="1.0.0")
    
    severity = Column(String(32), nullable=False)  # info, warning, error, critical
    passed = Column(Boolean, nullable=False)
    score = Column(Float, nullable=True)
    threshold = Column(String(64), nullable=True)
    
    message = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
    validated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    validation_run = relationship("ValidationRun", back_populates="rule_results")


class RecordQualitySummary(Base):
    """Aggregated quality summary and assigned disposition for a single record."""
    __tablename__ = "dataset_record_quality_summaries"

    summary_id = Column(String(64), primary_key=True, index=True)
    run_id = Column(String(64), ForeignKey("dataset_validation_runs.run_id"), nullable=False, index=True)
    record_id = Column(String(64), nullable=False, index=True)
    dataset_layer = Column(String(64), nullable=False, index=True)
    schema_version = Column(String(32), nullable=False, default="1.0.0")
    quality_rule_set_version = Column(String(32), nullable=False, default="1.0.0")
    
    quality_status = Column(String(64), nullable=False, index=True)  # automatic_check_passed, automatic_check_failed, etc.
    overall_quality_score = Column(Float, nullable=False, default=100.0)
    dimension_scores = Column(JSON, nullable=True)
    
    rules_executed = Column(Integer, nullable=False, default=0)
    rules_passed = Column(Integer, nullable=False, default=0)
    warnings_count = Column(Integer, nullable=False, default=0)
    errors_count = Column(Integer, nullable=False, default=0)
    critical_count = Column(Integer, nullable=False, default=0)
    
    requires_expert_review = Column(Boolean, nullable=False, default=True)
    research_eligible = Column(Boolean, nullable=False, default=False)
    approved_for_child_delivery = Column(Boolean, nullable=False, default=False)
    validated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    validation_run = relationship("ValidationRun", back_populates="summaries")


class ManualReviewQueueEntry(Base):
    """Entry in the human review queue for triage and revalidation."""
    __tablename__ = "dataset_manual_review_queue"

    entry_id = Column(String(64), primary_key=True, index=True)
    run_id = Column(String(64), ForeignKey("dataset_validation_runs.run_id"), nullable=False, index=True)
    record_id = Column(String(64), nullable=False, index=True)
    dataset_layer = Column(String(64), nullable=False, index=True)
    
    priority = Column(String(32), nullable=False, default="medium", index=True)  # low, medium, high, urgent
    triggering_rule_ids = Column(JSON, nullable=False)
    summary = Column(Text, nullable=False)
    recommended_review_type = Column(String(64), nullable=False, default="linguistic_triage")
    
    review_status = Column(String(64), nullable=False, default="pending", index=True)  # pending, acknowledged, etc.
    assigned_reviewer_id = Column(String(64), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    validation_run = relationship("ValidationRun", back_populates="review_entries")


class RecordRevision(Base):
    """Immutable record revision history tracking reviewer corrections."""
    __tablename__ = "dataset_record_revisions"

    revision_id = Column(String(64), primary_key=True, index=True)
    record_id = Column(String(64), nullable=False, index=True)
    dataset_layer = Column(String(64), nullable=False, index=True)
    parent_revision_id = Column(String(64), nullable=True)
    
    previous_content = Column(JSON, nullable=False)
    corrected_content = Column(JSON, nullable=False)
    change_reason = Column(Text, nullable=False)
    created_by = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    revalidated = Column(Boolean, nullable=False, default=False)
    revalidation_run_id = Column(String(64), nullable=True)
