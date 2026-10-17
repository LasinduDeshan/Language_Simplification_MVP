"""
Stage 35 Schemas and Data Contracts — Comparative Evaluation of Gemini, mT5, and mBART.

Enforces:
1. Model registry contracts and identity dispositions.
2. Two-tier denominator classification (Primary Common vs Local Only).
3. Attempt records with latency, usage, and cryptographic output hashing.
4. Level 4 and Level 5A/5B mutually exclusive terminal dispositions.
5. Level 6 metric cell records and applicability dispositions.
6. Governed Stage 35 final recommendation.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ModelFamily(str, Enum):
    GEMINI = "gemini"
    MT5 = "mt5"
    MBART = "mbart"
    RULE_BASELINE = "rule_baseline"


class ModelIdentityDisposition(str, Enum):
    IMMUTABLY_PINNED = "IMMUTABLY_PINNED"
    VERSION_METADATA_CAPTURED = "VERSION_METADATA_CAPTURED"
    TIMESTAMP_PINNED_MUTABLE_SERVICE = "TIMESTAMP_PINNED_MUTABLE_SERVICE"
    IDENTITY_INSUFFICIENT_FOR_AUTHORITATIVE_COMPARISON = "IDENTITY_INSUFFICIENT_FOR_AUTHORITATIVE_COMPARISON"


class HumanEvaluationMode(str, Enum):
    AUTOMATED_TECHNICAL_ONLY = "AUTOMATED_TECHNICAL_ONLY"
    NEW_BLINDED_REVIEW = "NEW_BLINDED_REVIEW"


class HumanEvidenceStatus(str, Enum):
    NOT_COLLECTED = "NOT_COLLECTED"
    AVAILABLE_FOR_STAGE35_OUTPUTS = "AVAILABLE_FOR_STAGE35_OUTPUTS"
    INSUFFICIENT_OR_NONCOMPARABLE = "INSUFFICIENT_OR_NONCOMPARABLE"


class ConditionId(str, Enum):
    C0_RULE_BASELINE = "C0_RULE_BASELINE"
    C1_GEMINI_ZERO_SHOT = "C1_GEMINI_ZERO_SHOT"
    C2_MT5_ZERO_SHOT = "C2_MT5_ZERO_SHOT"
    C3_MBART_ZERO_SHOT = "C3_MBART_ZERO_SHOT"
    C4_MT5_ADAPTED = "C4_MT5_ADAPTED"
    C5_MBART_ADAPTED = "C5_MBART_ADAPTED"


class DenominatorClassification(str, Enum):
    PRIMARY_COMMON_DENOMINATOR = "PRIMARY_COMMON_DENOMINATOR"
    LOCAL_ONLY_SUPPLEMENTARY_DENOMINATOR = "LOCAL_ONLY_SUPPLEMENTARY_DENOMINATOR"
    RIGHTS_BLOCKED = "RIGHTS_BLOCKED"
    INVALID_STATE = "INVALID_STATE"


class SplitClassification(str, Enum):
    DRY_RUN_DEVELOPMENT_CALIBRATION_SET = "DRY_RUN_DEVELOPMENT_CALIBRATION_SET"
    RESERVED_UNTOUCHED_EMPIRICAL_TEST_SET = "RESERVED_UNTOUCHED_EMPIRICAL_TEST_SET"


class FreezeClassification(str, Enum):
    PROSPECTIVE_CONFIGURATION_FREEZE = "PROSPECTIVE_CONFIGURATION_FREEZE"
    RETROSPECTIVE_RECONCILIATION_BUNDLE = "RETROSPECTIVE_RECONCILIATION_BUNDLE"


class AttemptStatus(str, Enum):
    SUCCEEDED = "SUCCEEDED"
    TIMEOUT = "TIMEOUT"
    RATE_LIMITED = "RATE_LIMITED"
    REFUSED = "REFUSED"
    INVALID_REQUEST = "INVALID_REQUEST"
    CANCELLED_OR_INTERRUPTED = "CANCELLED_OR_INTERRUPTED"
    PROVIDER_FAILED = "PROVIDER_FAILED"
    LOCAL_RUNTIME_FAILED = "LOCAL_RUNTIME_FAILED"


class SelectedResponseDisposition(str, Enum):
    VALID_CHANGED_OUTPUT = "VALID_CHANGED_OUTPUT"
    VALID_UNCHANGED_OUTPUT = "VALID_UNCHANGED_OUTPUT"
    REVIEW_REQUIRED_SEMANTIC_RISK = "REVIEW_REQUIRED_SEMANTIC_RISK"
    REVIEW_REQUIRED_POTENTIAL_HALLUCINATION = "REVIEW_REQUIRED_POTENTIAL_HALLUCINATION"
    REVIEW_REQUIRED_POTENTIAL_UNSAFE_OUTPUT = "REVIEW_REQUIRED_POTENTIAL_UNSAFE_OUTPUT"
    REJECTED_PROTECTED_SPAN_CHANGE = "REJECTED_PROTECTED_SPAN_CHANGE"
    REJECTED_INVALID_UNICODE_OR_SCRIPT = "REJECTED_INVALID_UNICODE_OR_SCRIPT"
    REJECTED_TRUNCATION = "REJECTED_TRUNCATION"
    REJECTED_EMPTY_OUTPUT = "REJECTED_EMPTY_OUTPUT"


class TerminalExecutionFailureDisposition(str, Enum):
    FAILED_REFUSAL = "FAILED_REFUSAL"
    FAILED_TIMEOUT_EXHAUSTED = "FAILED_TIMEOUT_EXHAUSTED"
    FAILED_RATE_LIMIT_EXHAUSTED = "FAILED_RATE_LIMIT_EXHAUSTED"
    FAILED_PROVIDER_RUNTIME = "FAILED_PROVIDER_RUNTIME"
    FAILED_LOCAL_RUNTIME = "FAILED_LOCAL_RUNTIME"
    FAILED_CANCELLED_OR_INTERRUPTED = "FAILED_CANCELLED_OR_INTERRUPTED"


class EvaluatorApplicability(str, Enum):
    EVALUATOR_APPLICABLE = "EVALUATOR_APPLICABLE"
    EVALUATOR_FALLBACK = "EVALUATOR_FALLBACK"
    EVALUATOR_INSUFFICIENT_RESOURCE = "EVALUATOR_INSUFFICIENT_RESOURCE"
    EVALUATOR_EXCLUDED_BY_FROZEN_RULE = "EVALUATOR_EXCLUDED_BY_FROZEN_RULE"


class ExecutionMode(str, Enum):
    REAL_LOCAL_INFERENCE = "REAL_LOCAL_INFERENCE"
    REAL_PROVIDER_INFERENCE = "REAL_PROVIDER_INFERENCE"
    SIMULATED_RESPONSE = "SIMULATED_RESPONSE"
    CACHED_EMPIRICAL_RESPONSE = "CACHED_EMPIRICAL_RESPONSE"


class ConditionDecision(str, Enum):
    SELECTED = "SELECTED"
    ELIGIBLE_NOT_SELECTED = "ELIGIBLE_NOT_SELECTED"
    INELIGIBLE_CRITICAL_GATE = "INELIGIBLE_CRITICAL_GATE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NOT_EXECUTED = "NOT_EXECUTED"


class Stage35FinalDecision(str, Enum):
    SELECTED_FOR_STAGE36_VALIDATION = "SELECTED_FOR_STAGE36_VALIDATION"
    CONDITIONALLY_SELECTED_WITH_FALLBACK = "CONDITIONALLY_SELECTED_WITH_FALLBACK"
    NO_MODEL_MEETS_MINIMUM_GATE = "NO_MODEL_MEETS_MINIMUM_GATE"
    NO_MODEL_SELECTED_FROM_DRY_RUN = "NO_MODEL_SELECTED_FROM_DRY_RUN"
    INSUFFICIENT_COMPARABLE_EVIDENCE = "INSUFFICIENT_COMPARABLE_EVIDENCE"


class ModelRegistryRecord(BaseModel):
    condition_id: ConditionId
    family: ModelFamily
    requested_model_id: str
    resolved_model_version: Optional[str] = None
    checkpoint_revision: Optional[str] = None
    artifact_sha256: Optional[str] = None
    tokenizer_sha256: Optional[str] = None
    licence_label: str
    licence_verified: bool = False
    terms_snapshot_sha256: Optional[str] = None
    sdk_version: str
    identity_disposition: ModelIdentityDisposition
    safety_settings_dictionary: Optional[Dict[str, str]] = None
    decoding_config: Dict[str, Any]
    prompt_template_sha256: Optional[str] = None
    frozen_at: str
    approved_for_execution: bool = False


class AttemptRecord(BaseModel):
    attempt_id: str
    run_id: str
    condition_id: ConditionId
    record_id: str
    split: str
    repetition_index: int = 1
    attempt_number: int = 1
    started_at: str
    ended_at: str
    latency_ms: float
    input_units: int
    output_units: int
    provider_request_id_hmac: Optional[str] = None
    status: AttemptStatus
    failure_code: Optional[str] = None
    raw_output_storage_ref: Optional[str] = None
    output_sha256: Optional[str] = None
    output_hmac: Optional[str] = None


class EvaluationRecord(BaseModel):
    evaluation_id: str
    record_id: str
    condition_id: ConditionId
    selected_attempt_id: Optional[str] = None
    response_disposition: Optional[SelectedResponseDisposition] = None
    execution_failure_disposition: Optional[TerminalExecutionFailureDisposition] = None
    evaluator_dispositions: Dict[str, EvaluatorApplicability] = Field(default_factory=dict)
    automatic_metrics: Dict[str, Optional[float]] = Field(default_factory=dict)
    critical_gate_passed: bool = False
    gate_failure_reasons: List[str] = Field(default_factory=list)
    human_evidence_status: HumanEvidenceStatus = HumanEvidenceStatus.NOT_COLLECTED
    approved_for_child_delivery: bool = False
    approved_for_unsupervised_child_delivery: bool = False
    requires_expert_review: bool = True
