"""
Pydantic v2 schemas and enums for Stage 36 Sinhala Output Validation and Fallback Pipeline.
Enforces strict fail-closed typing, rights inheritance, and non-negotiable child safety defaults.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ==============================================================================
# 1. Enums
# ==============================================================================

class ProviderCondition(str, Enum):
    C0_RULE_BASELINE = "C0_RULE_BASELINE"
    C1_GEMINI_EXPERIMENTAL = "C1_GEMINI_EXPERIMENTAL"
    C2_MT5_EXPERIMENTAL = "C2_MT5_EXPERIMENTAL"
    C3_MBART_EXPERIMENTAL = "C3_MBART_EXPERIMENTAL"
    OTHER_GOVERNED_EXPERIMENTAL_PROVIDER = "OTHER_GOVERNED_EXPERIMENTAL_PROVIDER"


class ExecutionMode(str, Enum):
    REAL_PROVIDER = "REAL_PROVIDER"
    REAL_LOCAL_MODEL = "REAL_LOCAL_MODEL"
    CACHED_EMPIRICAL = "CACHED_EMPIRICAL"
    SIMULATED = "SIMULATED"
    RULE_ENGINE = "RULE_ENGINE"


class SpanCategory(str, Enum):
    """Three-tier protected span hierarchy."""
    DECLARED_PROTECTED_SPAN = "DECLARED_PROTECTED_SPAN"      # Exact source annotation or frozen rule (hard gate)
    DETERMINISTIC_PROTECTED_SPAN = "DETERMINISTIC_PROTECTED_SPAN"  # Numbers, dates, units, currencies, URLs (hard gate)
    INFERRED_PROTECTED_SPAN = "INFERRED_PROTECTED_SPAN"        # Heuristic entity detector outputs (review gate)


class EvidenceClass(str, Enum):
    AUTHORITATIVE_DETERMINISTIC = "AUTHORITATIVE_DETERMINISTIC"
    GOVERNED_HEURISTIC = "GOVERNED_HEURISTIC"
    AUTOMATED_PROXY = "AUTOMATED_PROXY"
    HUMAN_EXPERT_DECISION = "HUMAN_EXPERT_DECISION"


class SeverityLevel(str, Enum):
    CRITICAL = "CRITICAL"    # Causes immediate hard rejection
    REVIEW = "REVIEW"        # Routes to manual review queue
    WARNING = "WARNING"      # Advisory warning, does not alone block delivery
    DIAGNOSTIC = "DIAGNOSTIC"  # Telemetry / statistical proxy evaluation


class AutomatedValidationStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"  # Halted early by design due to a hard rejection gate
    COMPLETED = "COMPLETED"                      # Evaluated through all applicable stages
    FAILED_INTERNAL = "FAILED_INTERNAL"          # Exception or infrastructure error occurred


class ExecutionOutcome(str, Enum):
    COMPLETED = "COMPLETED"
    FAILED_INTERNAL = "FAILED_INTERNAL"


class CandidateDisposition(str, Enum):
    """
    Mutually exclusive terminal dispositions evaluated in fixed left-to-right precedence.
    """
    REJECTED_CONFIGURATION_OR_PROVENANCE = "REJECTED_CONFIGURATION_OR_PROVENANCE"
    REJECTED_INVALID_UNICODE = "REJECTED_INVALID_UNICODE"
    REJECTED_PROTECTED_SPAN_VIOLATION = "REJECTED_PROTECTED_SPAN_VIOLATION"
    REJECTED_NUMERICAL_OR_POLARITY_DRIFT = "REJECTED_NUMERICAL_OR_POLARITY_DRIFT"
    REJECTED_UNSUPPORTED_INSERTION = "REJECTED_UNSUPPORTED_INSERTION"
    REJECTED_CRITICAL_SEMANTIC_RISK = "REJECTED_CRITICAL_SEMANTIC_RISK"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    VALID_UNCHANGED_NO_SIMPLIFICATION = "VALID_UNCHANGED_NO_SIMPLIFICATION"
    ACCEPTED_TECHNICAL_RESEARCH_CANDIDATE = "ACCEPTED_TECHNICAL_RESEARCH_CANDIDATE"


class RequestFinalOutcome(str, Enum):
    """Level 1 / Level 7 terminal request selection states."""
    PRIMARY_CANDIDATE_SELECTED = "PRIMARY_CANDIDATE_SELECTED"
    RULE_FALLBACK_SELECTED = "RULE_FALLBACK_SELECTED"
    UNCHANGED_SOURCE_SELECTED_FOR_RESEARCH_ONLY = "UNCHANGED_SOURCE_SELECTED_FOR_RESEARCH_ONLY"
    MANUAL_REVIEW_NO_OUTPUT = "MANUAL_REVIEW_NO_OUTPUT"
    REJECTED_NO_OUTPUT = "REJECTED_NO_OUTPUT"
    FAILED_INTERNAL_NO_OUTPUT = "FAILED_INTERNAL_NO_OUTPUT"


class FallbackTransitionType(str, Enum):
    """Level 6 mutually exclusive transition categories."""
    TO_RULE_BASELINE = "TO_RULE_BASELINE"
    TO_UNCHANGED_SOURCE = "TO_UNCHANGED_SOURCE"
    TO_MANUAL_REVIEW_NO_OUTPUT = "TO_MANUAL_REVIEW_NO_OUTPUT"
    TO_REJECTED_NO_OUTPUT = "TO_REJECTED_NO_OUTPUT"
    TO_FAILED_INTERNAL_NO_OUTPUT = "TO_FAILED_INTERNAL_NO_OUTPUT"


# ==============================================================================
# 2. Base Model Configuration
# ==============================================================================

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=True
    )


# ==============================================================================
# 3. Core Data Contracts
# ==============================================================================

class TextSpan(StrictBaseModel):
    """Unicode code-point half-open interval [start, end)."""
    start: int = Field(..., ge=0, description="0-indexed starting code-point offset")
    end: int = Field(..., gt=0, description="Ending code-point offset (exclusive)")
    text: Optional[str] = Field(None, description="Extracted slice for audit verification")

    @field_validator("end")
    @classmethod
    def validate_range(cls, end_val: int, info) -> int:
        start_val = info.data.get("start")
        if start_val is not None and end_val <= start_val:
            raise ValueError(f"Span end ({end_val}) must be strictly greater than start ({start_val})")
        return end_val


class CandidateEnvelope(StrictBaseModel):
    """
    Provider-neutral envelope carrying source and candidate simplification text,
    lineage rights, processing authorizations, and execution mode receipts.
    """
    candidate_id: str = Field(..., min_length=5, description="Unique candidate identifier")
    request_id: str = Field(..., min_length=5, description="Correlation request identifier")
    parent_candidate_id: Optional[str] = Field(None, description="Parent candidate ID if produced via fallback")
    fallback_depth: int = Field(default=0, ge=0, le=3, description="Depth in fallback ladder (max 3)")
    fallback_reason_code: Optional[str] = Field(None, description="Reason code triggering this fallback attempt")
    source_record_id: str = Field(..., min_length=1, description="Opaque source record ID")
    source_text_ref: str = Field(..., min_length=1, description="Protected URI reference for source text")
    source_text_sha256_internal: str = Field(..., pattern=r"^[0-9a-f]{64}$", description="64-char hex SHA-256")
    candidate_text_ref: str = Field(..., min_length=1, description="Protected URI reference for candidate text")
    candidate_text_sha256_internal: str = Field(..., pattern=r"^[0-9a-f]{64}$", description="64-char hex SHA-256")
    provider_condition: ProviderCondition
    execution_mode: ExecutionMode
    provider_model_id: Optional[str] = Field(None, description="Exact model ID if external/local ML")
    provider_version: Optional[str] = Field(None, description="Model or engine version")
    provider_terms_profile_id: Optional[str] = Field(None, description="Terms profile identifier")
    model_license_profile_id: Optional[str] = Field(None, description="Model/codebase license profile ID")
    rights_evidence_ref: Optional[str] = Field(None, description="Protected URI reference for rights evidence")
    external_processing_authorized: bool = Field(
        default=False,
        description="True strictly when external API data transmission is explicitly approved"
    )
    execution_region: str = Field(default="LOCAL_WORKSPACE", description="Execution host/region")
    generation_configuration_hash: str = Field(..., min_length=16, description="Cryptographic hash of generation config")
    rights_profile_refs: List[str] = Field(default_factory=list, description="Inherited rights profile IDs")
    received_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 UTC timestamp"
    )
    simulation_only: bool = Field(default=False, description="True if generated via offline/test mock simulation")

    @field_validator("external_processing_authorized")
    @classmethod
    def validate_external_processing(cls, v: bool, info) -> bool:
        mode = info.data.get("execution_mode")
        cond = info.data.get("provider_condition")
        if mode == ExecutionMode.REAL_PROVIDER.value and cond == ProviderCondition.C1_GEMINI_EXPERIMENTAL.value and not v:
            raise ValueError("external_processing_authorized must be True for REAL_PROVIDER Gemini execution")
        return v


class ValidatorFinding(StrictBaseModel):
    """
    Granular diagnostic or gate violation emitted by a specific validator.
    """
    finding_id: str = Field(..., min_length=5, description="Unique finding ID")
    validator_id: str = Field(..., min_length=3, description="Identifier of the executing validator")
    validator_version: str = Field(..., min_length=1, description="Validator version")
    severity: SeverityLevel
    reason_code: str = Field(..., min_length=3, description="Standardized finding reason code")
    evidence_class: EvidenceClass
    span_category: Optional[SpanCategory] = Field(None, description="Category if related to a protected span")
    source_representation: str = Field(default="NFC_CODEPOINTS", description="Text representation encoding for spans")
    source_spans: List[TextSpan] = Field(default_factory=list)
    candidate_representation: str = Field(default="NFC_CODEPOINTS", description="Candidate text representation")
    candidate_spans: List[TextSpan] = Field(default_factory=list)
    mapping_exact: bool = Field(default=True, description="Whether span mapping between source and candidate is exact")
    protected_evidence_ref: Optional[str] = Field(None, description="Protected URI reference for detailed evidence")
    public_summary: str = Field(..., min_length=5, description="Privacy-safe public diagnostic summary")


class ValidationResult(StrictBaseModel):
    """
    Comprehensive result of validating a candidate simplification envelope.
    Separates the execution outcome from the linguistic candidate disposition.
    """
    validation_result_id: str = Field(..., min_length=5)
    candidate_id: str = Field(..., min_length=5)
    configuration_hash: str = Field(..., min_length=16)
    execution_outcome: ExecutionOutcome
    candidate_disposition: Optional[CandidateDisposition] = Field(
        None,
        description="Assigned terminal disposition if execution_outcome == COMPLETED; null if FAILED_INTERNAL"
    )
    automated_validation_status: AutomatedValidationStatus
    completed_validator_count: int = Field(default=0, ge=0, le=9)
    expected_validator_count: int = Field(default=9, ge=1)
    critical_gate_passed: bool = Field(default=False)
    fallback_required: bool = Field(default=False)
    findings: List[ValidatorFinding] = Field(default_factory=list)
    diagnostic_metrics: Dict[str, Optional[float]] = Field(default_factory=dict)
    selected_output_ref: Optional[str] = Field(None, description="Protected URI to selected output if accepted")
    selected_output_origin: Optional[str] = Field(None, description="Origin condition of selected output")
    approved_for_child_delivery: bool = Field(
        default=False,
        description="Immutable safety invariant: automated validation never approves child delivery"
    )
    approved_for_unsupervised_child_delivery: bool = Field(
        default=False,
        description="Immutable safety invariant: direct unsupervised delivery is strictly prohibited"
    )
    requires_expert_review: bool = Field(
        default=True,
        description="All outputs remain subject to human expert review"
    )

    @field_validator("candidate_disposition")
    @classmethod
    def validate_disposition_coupling(cls, v: Optional[CandidateDisposition], info) -> Optional[CandidateDisposition]:
        outcome = info.data.get("execution_outcome")
        if outcome == ExecutionOutcome.COMPLETED.value and v is None:
            raise ValueError("candidate_disposition is required when execution_outcome is COMPLETED")
        if outcome == ExecutionOutcome.FAILED_INTERNAL.value and v is not None:
            raise ValueError("candidate_disposition must be None when execution_outcome is FAILED_INTERNAL")
        return v

    @field_validator("approved_for_child_delivery", "approved_for_unsupervised_child_delivery")
    @classmethod
    def enforce_child_safety_invariants(cls, v: bool) -> bool:
        if v is not False:
            raise ValueError("Stage 36 automated validation can never set child delivery flags to True")
        return False


class GovernanceStatusContract(StrictBaseModel):
    """
    Stage 36 governance contract metadata emitted with every output record.
    """
    language: str = Field(default="si")
    locale: str = Field(default="si-LK")
    script: str = Field(default="Sinh")
    validation_status: str = Field(default="draft")
    automated_validation_status: AutomatedValidationStatus = Field(default=AutomatedValidationStatus.NOT_STARTED)
    completed_validator_count: int = Field(default=0, ge=0, le=9)
    expected_validator_count: int = Field(default=9)
    expert_validated_for_this_output: bool = Field(default=False)
    research_eligible: bool = Field(default=False)
    approved_for_child_delivery: bool = Field(default=False)
    approved_for_unsupervised_child_delivery: bool = Field(default=False)
    requires_expert_review: bool = Field(default=True)


class FallbackStep(StrictBaseModel):
    """
    Audit record of an individual fallback transition step.
    """
    step_number: int = Field(..., ge=1, le=3)
    transition_type: FallbackTransitionType
    from_candidate_id: str
    to_candidate_id: Optional[str] = None
    triggering_reason_code: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RequestTrace(StrictBaseModel):
    """
    End-to-end request-level audit trace from registration to final selection or safe abstention.
    """
    request_id: str
    source_record_id: str
    final_outcome: RequestFinalOutcome
    primary_candidate_id: str
    selected_candidate_id: Optional[str] = None
    fallback_steps: List[FallbackStep] = Field(default_factory=list)
    total_fallback_transitions: int = Field(default=0, ge=0, le=3)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
