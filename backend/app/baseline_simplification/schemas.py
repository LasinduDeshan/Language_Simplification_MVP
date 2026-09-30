"""
Pydantic v2 schemas for Stage 24 Baseline Simplification methods, registry, and evaluation.
"""
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict, model_validator
from datetime import datetime
import hashlib
import json

class BaselineMethodId(str, Enum):
    B0 = "B0"  # Identity Baseline
    B1 = "B1"  # Lexical Substitution Baseline
    B2 = "B2"  # Sentence Splitting Baseline
    B3 = "B3"  # Syntactic Rule Baseline
    B4 = "B4"  # Combined Deterministic Pipeline
    B5 = "B5"  # Existing Deterministic Offline Fallback

class FinalDisposition(str, Enum):
    AUTOMATIC_CHECK_PASSED = "automatic_check_passed"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"
    AUTOMATIC_CHECK_FAILED = "automatic_check_failed"
    QUARANTINED = "quarantined"

class MeaningValidationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"
    SKIPPED = "skipped"

class ProtectedElementSource(str, Enum):
    GOVERNED_ANNOTATIONS_PLUS_EXTRACTOR = "governed_annotations_plus_extractor"
    AUTOMATED_EXTRACTOR_ONLY = "automated_extractor_only"

class RuleApplicationRecord(BaseModel):
    model_config = ConfigDict(extra="allow")
    rule_id: str = Field(..., description="Unique rule identifier (e.g. SYN-01-PASSIVE-ACTIVE)")
    step: int = Field(..., description="1-indexed execution step in pipeline")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Optional rule-specific context or tokens")

class OperationOutcomeRecord(BaseModel):
    model_config = ConfigDict(extra="allow")
    rule_id: str = Field(..., description="Rule ID that triggered or reverted")
    outcome: str = Field(..., description="'applied', 'reverted', 'skipped'")
    reason: Optional[str] = Field(default=None, description="Reason if reverted or skipped")

class AgeConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid")
    internal_policy: str = Field(default="source_item_target_age", description="Age extraction policy for internal corpus")
    asset_policy: str = Field(default="fixed_generic_age_band", description="Age extraction policy for ASSET")
    asset_target_age_band: str = Field(default="4-8", description="Fixed generic age band for ASSET evaluation")
    uses_learner_profile: bool = Field(default=False, description="Whether personalized learner profiles are used")

class BaselineConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid")
    method_id: BaselineMethodId
    method_name: str
    method_version: str = Field(default="1.0.0")
    configuration_version: str = Field(default="1.0.0")
    generator_method: str
    description: str
    ordered_rules: List[str] = Field(default_factory=list)
    age_configuration: AgeConfiguration = Field(default_factory=AgeConfiguration)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    required_resources: Dict[str, str] = Field(default_factory=dict)
    governance_status: str = Field(default="provisional_baseline_only")
    
    def compute_configuration_hash(self) -> str:
        payload = {
            "method_id": self.method_id.value,
            "method_version": self.method_version,
            "configuration_version": self.configuration_version,
            "generator_method": self.generator_method,
            "ordered_rules": self.ordered_rules,
            "parameters": self.parameters,
            "required_resources": self.required_resources,
        }
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

class BaselineOutputRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_id: str = Field(..., description="Evaluation run ID (e.g. BASE-EN-20260930-0001)")
    dataset_id: str = Field(..., description="Dataset identifier ('internal_english', 'asset')")
    dataset_version: str = Field(..., description="Dataset release version ('0.2.0', '0.1.0')")
    schema_version: str = Field(default="1.0.0", description="Schema version")
    preprocessing_version: str = Field(default="1.0.0", description="Stage 21 preprocessing version")
    complexity_analyzer_version: str = Field(default="1.0.0", description="Stage 22 complexity version")
    
    evaluation_unit: str = Field(default="source_group", description="Unit of evaluation ('source_group')")
    reference_count: int = Field(default=3, description="Number of references evaluated against")
    target_support_level: Optional[str] = Field(default=None, description="Always null for generic Stage 24 baselines")
    uses_learner_profile: bool = Field(default=False, description="Always false for generic Stage 24 baselines")
    protected_element_source: ProtectedElementSource = Field(..., description="Protection extraction mode")
    
    target_content_age: Optional[int] = Field(default=None, description="Governed target content age if available")
    source_record_id: str = Field(..., description="Original source record identifier")
    source_group_id: str = Field(..., description="Source group identifier")
    split: str = Field(..., description="Data split ('development_candidate_validation', 'development_candidate_test', 'test')")
    
    method_id: BaselineMethodId
    method_version: str = Field(default="1.0.0")
    configuration_version: str = Field(default="1.0.0")
    configuration_hash: str = Field(..., description="SHA-256 hash of frozen configuration")
    
    input_text: str = Field(..., description="Canonical source text evaluated")
    output_text: str = Field(..., description="Generated baseline simplification text")
    input_hash: str = Field(..., description="SHA-256 hash of input text")
    output_hash: str = Field(..., description="SHA-256 hash of output text")
    
    rules_applied: List[Dict[str, Any]] = Field(default_factory=list, description="Rules applied in pipeline")
    operation_outcomes: List[Dict[str, Any]] = Field(default_factory=list, description="Operation tracking including rollbacks")
    
    generator_method: str = Field(..., description="Generator method name")
    fallback_used: bool = Field(default=False, description="Whether fallback was invoked")
    meaning_validation_status: MeaningValidationStatus = Field(..., description="Protected meaning validation status")
    quality_disposition: FinalDisposition = Field(..., description="Final output quality disposition")
    
    metric_eligibility: bool = Field(default=True, description="Whether record is eligible for metric evaluation")
    metric_exclusion_reason: Optional[str] = Field(default=None, description="Reason if excluded from metrics")
    latency_ms: float = Field(default=0.0, description="Execution latency in milliseconds")
    
    validation_status: str = Field(default="draft", description="Provisional validation status")
    research_eligible: bool = Field(default=False, description="Whether approved for child research delivery")
    approved_for_child_delivery: bool = Field(default=False, description="Strictly false for Stage 24 baselines")
    requires_expert_review: bool = Field(default=True, description="Strictly true for Stage 24 baselines")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    @model_validator(mode="after")
    def validate_hashes_and_safety(self):
        exp_in_hash = hashlib.sha256(self.input_text.encode("utf-8")).hexdigest()
        if self.input_hash != exp_in_hash:
            raise ValueError(f"input_hash mismatch: expected {exp_in_hash}, got {self.input_hash}")
        exp_out_hash = hashlib.sha256(self.output_text.encode("utf-8")).hexdigest()
        if self.output_hash != exp_out_hash:
            raise ValueError(f"output_hash mismatch: expected {exp_out_hash}, got {self.output_hash}")
        if self.approved_for_child_delivery:
            raise ValueError("approved_for_child_delivery must be false for all Stage 24 baselines")
        return self
