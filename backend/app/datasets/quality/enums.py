"""Controlled enums for Stage 15 Quality Validation."""
from enum import Enum


class QualityStatus(str, Enum):
    """Controlled quality status model for dataset records."""
    NOT_CHECKED = "not_checked"
    AUTOMATIC_CHECK_PASSED = "automatic_check_passed"
    AUTOMATIC_CHECK_FAILED = "automatic_check_failed"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"
    QUARANTINED = "quarantined"
    # Reserved for Stage 16+ expert governance
    EXPERT_REVIEWED = "expert_reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


class RuleSeverity(str, Enum):
    """Severity levels for quality validation rules."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class QualityDimension(str, Enum):
    """Quality dimensions for multi-dimensional evaluation."""
    MEANING_PRESERVATION = "meaning_preservation"
    GRAMMAR_FLUENCY = "grammar_fluency"
    SIMPLICITY_IMPROVEMENT = "simplicity_improvement"
    AGE_APPROPRIATENESS = "age_appropriateness"
    SAFETY_ANSWER_BOUNDARY = "safety_answer_boundary"
    METADATA_INTEGRITY = "metadata_integrity"


class ReviewPriority(str, Enum):
    """Priority levels for manual review queue entries."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ReviewStatus(str, Enum):
    """Triage status for manual review queue items."""
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    FALSE_POSITIVE = "false_positive"
    CORRECTION_SUBMITTED = "correction_submitted"
    EXPERT_REVIEW_REQUESTED = "expert_review_requested"


class TriageAction(str, Enum):
    """Permitted Stage 15 triage actions."""
    ACKNOWLEDGE_FINDING = "acknowledge_finding"
    MARK_FALSE_POSITIVE = "mark_false_positive"
    SUBMIT_CORRECTION = "submit_correction"
    REQUEST_EXPERT_REVIEW = "request_expert_review"
    REVALIDATE = "revalidate"


class ValidationRunStatus(str, Enum):
    """Lifecycle status of a validation run."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
