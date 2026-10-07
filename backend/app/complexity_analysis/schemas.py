"""Pydantic v2 schemas for Stage 22 Complexity Analysis and Difficulty Classification."""

from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


DifficultyLabel = Literal["easy", "medium", "hard"]
DatasetSplit = Literal[
    "development_candidate_train",
    "development_candidate_validation",
    "development_candidate_test",
    "adaptation_test",
    "legacy_excluded",
    "unassigned",
]
LabelStatus = Literal[
    "expert_verified",
    "reviewer_consensus",
    "provisional",
    "rule_seeded",
    "conflicting",
    "missing",
]
PrimaryDisposition = Literal[
    "locked_test",
    "adaptation_test_excluded",
    "preprocessing_failed",
    "stage21_manual_review",
    "missing_or_conflicting_label",
    "provisional_secondary_only",
    "rule_seeded_audit_only",
    "primary_train_eligible",
    "primary_validation_eligible",
]


class ComplexityTrainingEligibility(BaseModel):
    """Data contract for Stage 22 training and validation eligibility."""

    model_config = ConfigDict(extra="forbid")

    text_instance_id: str
    parent_record_id: str
    parent_record_type: str
    text_role: str
    source_group_id: str
    dataset_split: DatasetSplit
    preprocessing_status: str
    label_status: LabelStatus
    primary_disposition: PrimaryDisposition
    eligible_for_primary_training: bool
    eligible_for_secondary_experiment: bool
    exclusion_reasons: List[str] = Field(default_factory=list)


class LabelAuditRecord(BaseModel):
    """Audit record for label governance, provenance and circular leakage tracking."""

    model_config = ConfigDict(extra="forbid")

    text_instance_id: str
    parent_record_id: str
    parent_record_type: str
    source_group_id: str
    assigned_difficulty: Optional[DifficultyLabel] = None
    label_status: LabelStatus
    annotator_tier: Literal["expert", "reviewer_consensus", "provisional_author", "heuristic_rule", "none"]
    provenance_source: str
    reviewer_reference: str = "None (Draft authoring item awaiting expert panel review)"
    reviewer_role: str = "provisional_author"
    annotation_guideline_version: str = "v1.0.0-draft"
    reviewed_at: Optional[str] = None
    agreement_status: str = "single_author_provisional"
    adjudication_status: str = "pending_expert_adjudication"
    rule_seeded_detected: bool = False
    circular_leakage_risk: bool = False
    audit_notes: Optional[str] = None


class ComplexityFactor(BaseModel):
    """Explaining feature contributing to the predicted complexity."""

    model_config = ConfigDict(extra="forbid")

    feature_name: str
    observed_value: Union[float, int, bool]
    contribution_direction: Literal["reduces", "increases", "neutral"]
    importance: Optional[float] = None
    explanation_code: str


class OODDetectionResult(BaseModel):
    """Detailed out-of-distribution evaluation result."""

    model_config = ConfigDict(extra="forbid")

    is_out_of_distribution: bool
    anomaly_score: float
    violating_features: List[str] = Field(default_factory=list)
    violation_details: Dict[str, Dict[str, float]] = Field(default_factory=dict)


class ComplexityClassificationResult(BaseModel):
    """Output data contract for Stage 22 difficulty classification."""

    model_config = ConfigDict(extra="forbid")

    classification_id: str
    text_instance_id: str
    source_group_id: Optional[str] = None
    predicted_difficulty: DifficultyLabel
    class_probabilities: Dict[DifficultyLabel, float]
    confidence: float
    confidence_threshold: float
    margin: float
    margin_threshold: float
    review_required: bool
    review_reasons: List[str] = Field(default_factory=list)
    is_out_of_distribution: bool
    complexity_factors: List[ComplexityFactor] = Field(default_factory=list)
    model_name: str
    model_version: str
    feature_schema_version: str
    preprocessing_pipeline_version: str
    source_dataset_version: str
    record_hash: str


class ModelEvaluationSummary(BaseModel):
    """Multi-class classification evaluation summary metrics."""

    model_config = ConfigDict(extra="forbid")

    model_id: str
    model_name: str
    split_evaluated: str
    sample_count: int
    macro_f1: float
    weighted_f1: float
    balanced_accuracy: float
    accuracy: float
    per_class_recall: Dict[str, float]
    per_class_precision: Dict[str, float]
    per_class_f1: Dict[str, float]
    expected_calibration_error: float
    hard_to_easy_error_rate: float
    hard_to_easy_error_count: int
    hard_to_easy_wilson_ci_lower: float
    hard_to_easy_wilson_ci_upper: float
    fit_time_seconds: float
    inference_latency_ms_per_item: float
