"""Pydantic v2 schemas for Stage 15 Quality Validation."""
import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.datasets.quality.enums import (
    QualityStatus,
    RuleSeverity,
    QualityDimension,
    ReviewPriority,
    ReviewStatus,
    TriageAction,
    ValidationRunStatus,
)


class QualityRuleResultV1(BaseModel):
    """Result of an individual rule evaluation on a dataset record."""
    model_config = ConfigDict(extra="forbid")

    result_id: str = Field(description="Unique ID for this rule execution result")
    run_id: str = Field(description="Associated validation run identifier")
    record_id: str = Field(description="Identifier of the validated record")
    dataset_layer: str = Field(description="Dataset layer (adaptation_test_set, simplification_corpus, lexicons, interaction_exports)")
    
    rule_id: str = Field(description="Identifier of the rule (e.g. SIMP-MEAN-001)")
    rule_version: str = Field(default="1.0.0", description="SemVer version of the rule definition")
    validator_name: str = Field(description="Name of the validator class or function")
    validator_version: str = Field(default="1.0.0", description="Version of the validator implementation")
    
    dimension: QualityDimension = Field(default=QualityDimension.METADATA_INTEGRITY, description="Target quality dimension")
    severity: RuleSeverity = Field(description="Severity level (info, warning, error, critical)")
    passed: bool = Field(description="Whether the rule passed")
    score: Optional[float] = Field(default=None, description="Continuous score if applicable [0.0 - 1.0 or 0 - 100]")
    threshold: Optional[str] = Field(default=None, description="Configured threshold value description")
    
    message: str = Field(description="Human-readable result summary")
    recommended_action: Optional[str] = Field(default=None, description="Recommended remediation step")
    details: Dict[str, Any] = Field(default_factory=dict, description="Diagnostic evidence metadata")
    validated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class QualityScoreBreakdownV1(BaseModel):
    """Breakdown of quality scores across dimensions."""
    model_config = ConfigDict(extra="forbid")

    meaning_preservation: float = Field(default=100.0, ge=0.0, le=100.0)
    grammar_fluency: float = Field(default=100.0, ge=0.0, le=100.0)
    simplicity_improvement: float = Field(default=100.0, ge=0.0, le=100.0)
    age_appropriateness: float = Field(default=100.0, ge=0.0, le=100.0)
    safety_answer_boundary: float = Field(default=100.0, ge=0.0, le=100.0)
    overall_score: float = Field(default=100.0, ge=0.0, le=100.0)


class RecordQualitySummaryV1(BaseModel):
    """Aggregated quality summary and disposition for a single record."""
    model_config = ConfigDict(extra="forbid")

    summary_id: str = Field(description="Unique ID for this summary record")
    run_id: str = Field(description="Associated validation run identifier")
    record_id: str = Field(description="Identifier of the record")
    dataset_layer: str = Field(description="Dataset layer")
    schema_version: str = Field(default="1.0.0", description="Record schema version")
    quality_rule_set_version: str = Field(default="1.0.0", description="Quality rule-set version")
    
    quality_status: QualityStatus = Field(description="Resolved quality status")
    overall_quality_score: float = Field(default=100.0, ge=0.0, le=100.0)
    dimension_scores: Optional[QualityScoreBreakdownV1] = Field(default=None)
    
    rules_executed: int = Field(default=0, ge=0)
    rules_passed: int = Field(default=0, ge=0)
    warnings_count: int = Field(default=0, ge=0)
    errors_count: int = Field(default=0, ge=0)
    critical_count: int = Field(default=0, ge=0)
    
    requires_expert_review: bool = Field(default=True)
    research_eligible: bool = Field(default=False)
    approved_for_child_delivery: bool = Field(default=False)
    validated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    @model_validator(mode="after")
    def enforce_stage15_invariants(self) -> "RecordQualitySummaryV1":
        """Stage 15 strictly prevents automatic research eligibility or child-delivery approval."""
        if self.research_eligible:
            raise ValueError("Stage 15 automatic validation cannot set research_eligible=True")
        if self.approved_for_child_delivery:
            raise ValueError("Stage 15 automatic validation cannot set approved_for_child_delivery=True")
        return self


class ManualReviewQueueEntryV1(BaseModel):
    """Entry in the manual review queue for human triage."""
    model_config = ConfigDict(extra="forbid")

    entry_id: str = Field(description="Unique queue entry identifier")
    run_id: str = Field(description="Validation run ID")
    record_id: str = Field(description="Record ID requiring review")
    dataset_layer: str = Field(description="Dataset layer")
    
    priority: ReviewPriority = Field(default=ReviewPriority.MEDIUM)
    triggering_rule_ids: List[str] = Field(description="List of rule IDs that triggered review")
    summary: str = Field(description="Summary of issues and findings")
    recommended_review_type: str = Field(default="linguistic_triage")
    
    review_status: ReviewStatus = Field(default=ReviewStatus.PENDING)
    assigned_reviewer_id: Optional[str] = Field(default=None)
    resolution_notes: Optional[str] = Field(default=None)
    
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    resolved_at: Optional[datetime.datetime] = Field(default=None)


class RecordRevisionV1(BaseModel):
    """Immutable correction revision model."""
    model_config = ConfigDict(extra="forbid")

    revision_id: str = Field(description="Unique revision identifier")
    record_id: str = Field(description="Target record ID")
    dataset_layer: str = Field(description="Dataset layer")
    parent_revision_id: Optional[str] = Field(default=None)
    
    previous_content: Dict[str, Any] = Field(description="Previous record state snapshot")
    corrected_content: Dict[str, Any] = Field(description="Corrected record content")
    change_reason: str = Field(description="Explanation of corrections made")
    created_by: str = Field(description="Reviewer identifier")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    
    revalidated: bool = Field(default=False)
    revalidation_run_id: Optional[str] = Field(default=None)


class ValidationRunManifestV1(BaseModel):
    """Manifest of an executed validation run."""
    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(description="Validation run identifier")
    dataset_layer: str = Field(description="Target dataset layer or 'all'")
    dataset_version: str = Field(default="0.1.0")
    quality_rule_set_version: str = Field(default="1.0.0")
    status: ValidationRunStatus = Field(default=ValidationRunStatus.COMPLETED)
    
    total_records: int = Field(default=0, ge=0)
    passed_count: int = Field(default=0, ge=0)
    failed_count: int = Field(default=0, ge=0)
    review_required_count: int = Field(default=0, ge=0)
    quarantined_count: int = Field(default=0, ge=0)
    
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    completed_at: Optional[datetime.datetime] = Field(default=None)
    execution_time_seconds: Optional[float] = Field(default=None)
    error_message: Optional[str] = Field(default=None)

    @model_validator(mode="after")
    def verify_accounting_balance(self) -> "ValidationRunManifestV1":
        """Verify strict accounting invariant."""
        if self.status == ValidationRunStatus.COMPLETED:
            reconciled = self.passed_count + self.failed_count + self.review_required_count + self.quarantined_count
            if self.total_records != reconciled:
                raise ValueError(
                    f"Accounting balance mismatch in run {self.run_id}: "
                    f"total_records={self.total_records} != reconciled={reconciled}"
                )
        return self


# API Request/Response Schemas

class ValidationRunCreateRequestV1(BaseModel):
    """Request payload to initiate an asynchronous validation run."""
    model_config = ConfigDict(extra="forbid")

    dataset_layer: str = Field(default="all", description="Layer to validate (all, adaptation_test_set, simplification_corpus, lexicons, interaction_exports)")
    dataset_version: str = Field(default="0.1.0")
    quality_rule_set_version: str = Field(default="1.0.0")
    enable_nlp: bool = Field(default=True, description="Whether to execute NLP-assisted rules")
    enable_llm_review: bool = Field(default=False, description="Whether to run optional LLM review")


class ValidationRunResponseV1(BaseModel):
    """HTTP 202 Accepted response for an initiated validation run."""
    model_config = ConfigDict(extra="forbid")

    run_id: str
    status: ValidationRunStatus
    message: str
    created_at: datetime.datetime


class TriageDecisionRequestV1(BaseModel):
    """Request payload for reviewer triage decision."""
    model_config = ConfigDict(extra="forbid")

    action: TriageAction = Field(description="Permitted Stage 15 triage action")
    reviewer_id: str = Field(description="Reviewer identifier")
    resolution_notes: str = Field(description="Rationale and review notes")
    corrected_content: Optional[Dict[str, Any]] = Field(default=None, description="Required when action is submit_correction")


class RecordCorrectionRequestV1(BaseModel):
    """Direct record correction request payload."""
    model_config = ConfigDict(extra="forbid")

    reviewer_id: str = Field(description="Author of correction")
    change_reason: str = Field(description="Justification for correction")
    corrected_content: Dict[str, Any] = Field(description="New record content")


class LLMReviewResponseV1(BaseModel):
    """Structured response schema for advisory LLM evaluations."""
    model_config = ConfigDict(extra="forbid")

    meaning_preserved: bool = Field(description="Whether core meaning is preserved")
    meaning_confidence: float = Field(ge=0.0, le=1.0, description="Confidence score [0.0 - 1.0]")
    age_appropriate: bool = Field(description="Whether vocabulary and syntax suit ages 4-8")
    naturalness_score: float = Field(ge=0.0, le=1.0, description="Fluency and naturalness score")
    identified_issues: List[str] = Field(default_factory=list, description="Specific identified issues")
    suggested_review_notes: Optional[str] = Field(default=None, description="Advisory notes for human reviewer")
