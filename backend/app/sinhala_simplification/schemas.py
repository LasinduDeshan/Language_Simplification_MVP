"""
Stage 33 — Pydantic v2 Schemas for Sinhala Linguistic Simplification Rules & Rewrite Engine.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.sinhala_simplification.enums import (
    AuthoringMethod,
    CandidateTerminalStatus,
    CorpusView,
    FinalDisposition,
    GuardType,
    MappingStatus,
    OperationType,
    Partition,
    ProtectedSpanCategory,
    RuleAttemptTerminalStatus,
    RuleStatus,
    RuleType,
)


class CodePointSpan(BaseModel):
    """Half-open code point interval [start_code_point, end_code_point) over normalized text."""
    model_config = ConfigDict(frozen=True)

    start_code_point: int = Field(..., ge=0, description="Inclusive start code-point index")
    end_code_point: int = Field(..., ge=0, description="Exclusive end code-point index")
    text: Optional[str] = Field(None, description="Protected internal snippet; omitted in public artifacts")


class ProtectedSpan(BaseModel):
    """Meaning-critical span detected and protected from unallowlisted alteration."""
    model_config = ConfigDict(frozen=True)

    span_id: str = Field(..., description="Unique span identifier e.g. PROT-SPAN-000001")
    category: ProtectedSpanCategory = Field(..., description="Protected span classification")
    span: CodePointSpan = Field(..., description="Code point boundaries")
    text: str = Field(..., description="Extracted protected text")
    detector_rule_id: str = Field(..., description="Identifier of detection rule")
    detector_version: int = Field(1, ge=1, description="Version of detector")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Detection confidence")
    allowlist_override: bool = Field(False, description="Whether an explicit rule is permitted to modify this span")


class RuleApplicabilityCondition(BaseModel):
    """Contextual or grammatical condition required for rule applicability."""
    model_config = ConfigDict(frozen=True)

    condition_type: str = Field(..., description="Type of condition e.g. POS_TAG, INFLECTION_MATCH, SENSE_COMPATIBLE")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Condition parameter constraints")


class RuleBlockingCondition(BaseModel):
    """Condition that strictly blocks rule application."""
    model_config = ConfigDict(frozen=True)

    blocking_type: str = Field(..., description="Type of blocker e.g. OVERLAPS_PROTECTED_SPAN, NEGATION_SCOPE, MODALITY_SCOPE")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Blocking parameter constraints")


class KeyedHmacRef(BaseModel):
    """Structured versioned domain-separated keyed HMAC metadata."""
    model_config = ConfigDict(frozen=True)

    hmac_key_id: str = Field(default="ST33-KEY-01")
    hmac_scheme_version: int = Field(default=1)
    domain_separator: str
    canonical_message_schema: str = Field(default="utf8_nfc_string")
    hmac_value: str


class RightsProfileBinding(BaseModel):
    """Binding of rights profile ID and its frozen version."""
    model_config = ConfigDict(frozen=True)

    rights_profile_id: str
    rights_profile_version: int = 1


class SimplificationRule(BaseModel):
    """Deterministic, versioned linguistic simplification rule definition."""
    model_config = ConfigDict(frozen=True)

    rule_id: str = Field(..., description="Deterministic unique rule identifier e.g. SI-LEX-SUB-0001")
    rule_version: int = Field(1, ge=1, description="Sequential integer version")
    rule_type: RuleType = Field(..., description="Taxonomy classification")
    status: RuleStatus = Field(RuleStatus.TECHNICAL_DRAFT, description="Lifecycle status")
    authoring_method: AuthoringMethod = Field(AuthoringMethod.TECHNICAL_RULE_AUTHORING)
    author_id_or_team: str = Field(..., description="Human technical author or engineering team identity")
    evidence_type: str = Field(..., description="Category of empirical evidence supporting the rule")
    evidence_refs: List[str] = Field(default_factory=list, description="Traceable Stage 31/32 evidence keys")
    rights_profile_refs: List[RightsProfileBinding] = Field(default_factory=list, description="Associated structured rights profile references")
    source_pattern_ref: str = Field(..., description="Keyed HMAC or opaque identifier of source pattern")
    target_template_ref: str = Field(..., description="Keyed HMAC or opaque identifier of target template")
    source_pattern_hmac: Optional[KeyedHmacRef] = Field(default=None, description="Structured keyed HMAC metadata")
    target_template_hmac: Optional[KeyedHmacRef] = Field(default=None, description="Structured keyed HMAC metadata")
    priority: int = Field(100, ge=1, description="Precedence priority (higher number = higher priority)")
    applicability_conditions: List[RuleApplicabilityCondition] = Field(default_factory=list)
    blocking_conditions: List[RuleBlockingCondition] = Field(default_factory=list)
    required_guards: List[GuardType] = Field(default_factory=list)
    expert_validated: bool = Field(False, description="Must remain False in Stage 33")
    approved_for_child_delivery: bool = Field(False, description="Must remain False in Stage 33")


class RewriteRequest(BaseModel):
    """Simplification pipeline input request with expanded cryptographic provenance."""
    model_config = ConfigDict(frozen=True)

    request_id: str = Field(..., description="Unique request ID e.g. SI-SIMP-REQ-000001")
    record_id: str = Field(..., description="Upstream corpus record ID e.g. SI-PILOT-000001")
    source_storage_ref: str = Field(..., description="External protected storage URI")
    source_sha256_internal: str = Field(..., min_length=64, max_length=64)
    language: str = Field("si", description="BCP 47 language code")
    stage30_configuration_hash: str = Field(..., description="Hash of sealed Stage 30 preprocessor config")
    stage31_split_manifest_hash: str = Field(..., description="Hash of sealed Stage 31 split manifest")
    stage31_corpus_view: CorpusView = Field(CorpusView.CANONICAL_ANALYTICAL_150)
    stage32_configuration_hash: str = Field(..., description="Hash of sealed Stage 32 lexicon config")
    stage32_lexicon_manifest_hash: str = Field(..., description="Hash of sealed Stage 32 lexicon manifest")
    stage33_configuration_hash: str = Field(..., description="Hash of sealed Stage 33 rule engine config")
    rights_profile_ids_and_versions: List[RightsProfileBinding] = Field(default_factory=list)
    partition: Partition = Field(..., description="train, val, or test partition")


class RuleAttempt(BaseModel):
    """Audit record of a rule evaluation attempt with mutually exclusive terminal status."""
    model_config = ConfigDict(frozen=True)

    attempt_id: str = Field(..., description="Unique attempt ID e.g. SI-RULE-ATTEMPT-000001")
    request_id: str = Field(..., description="Associated request ID")
    rule_id: str = Field(..., description="Evaluated rule ID")
    rule_version: int = Field(1, ge=1)
    terminal_status: RuleAttemptTerminalStatus = Field(..., description="Mutually exclusive terminal status")
    reason_codes: List[str] = Field(default_factory=list, description="Diagnostic codes")
    source_spans: List[CodePointSpan] = Field(default_factory=list, description="Matched source span(s)")
    candidate_id: Optional[str] = Field(None, description="Generated candidate ID if CANDIDATE_GENERATED")


class TransformationOperation(BaseModel):
    """Atomic transformation operation trace mapping source spans to output spans."""
    model_config = ConfigDict(frozen=True)

    operation_id: str = Field(..., description="Unique operation ID e.g. SI-OP-000001")
    operation_type: OperationType = Field(..., description="Atomic operation type")
    rule_id: str = Field(..., description="Rule responsible for transformation")
    raw_source_spans: List[CodePointSpan] = Field(default_factory=list)
    normalized_source_spans: List[CodePointSpan] = Field(default_factory=list)
    output_spans: List[CodePointSpan] = Field(default_factory=list)
    mapping_status: MappingStatus = Field(MappingStatus.ONE_TO_ONE, description="Qualified mapping state")
    mapping_exact: bool = Field(True, description="True only for exact local substitutions")
    before_hash_internal: str = Field(..., min_length=64, max_length=64)
    after_hash_internal: str = Field(..., min_length=64, max_length=64)
    before_text_internal: Optional[str] = Field(None, description="Protected internal span text")
    after_text_internal: Optional[str] = Field(None, description="Protected internal span text")


class GuardResult(BaseModel):
    """Evaluation result for an individual semantic or structural guard."""
    model_config = ConfigDict(frozen=True)

    guard_type: GuardType = Field(..., description="Guard evaluated")
    passed: bool = Field(..., description="True if guard checks passed without violation")
    reason_codes: List[str] = Field(default_factory=list)
    violation_details: Optional[str] = Field(None, description="Diagnostic message when failed")


class RewriteCandidate(BaseModel):
    """Proposed simplification rewrite candidate prior to selection."""
    model_config = ConfigDict(frozen=True)

    candidate_id: str = Field(..., description="Candidate ID e.g. SI-CAND-000001")
    request_id: str = Field(..., description="Associated request ID")
    rule_id: str = Field(..., description="Primary rule ID")
    candidate_text_internal: Optional[str] = Field(None, description="Protected candidate text")
    candidate_sha256_internal: str = Field(..., min_length=64, max_length=64)
    operations: List[TransformationOperation] = Field(default_factory=list)
    applied_rule_ids: List[str] = Field(default_factory=list, description="Applied rule IDs; must have length 1 in Stage 33")
    guard_results: Dict[str, GuardResult] = Field(default_factory=dict)
    all_guards_passed: bool = Field(False)
    terminal_status: CandidateTerminalStatus = Field(
        CandidateTerminalStatus.NOT_SELECTED_LOWER_RANK,
        description="Mutually exclusive candidate terminal status"
    )


class FinalRewriteRecord(BaseModel):
    """Governed output record of rewrite engine execution."""
    model_config = ConfigDict(frozen=True)

    output_id: str = Field(..., description="Unique output ID e.g. SI-SIMP-OUT-000001")
    request_id: str = Field(..., description="Associated request ID")
    selected_candidate_id: Optional[str] = Field(None, description="Candidate ID if rewrite selected")
    final_disposition: FinalDisposition = Field(..., description="Authoritative terminal disposition")
    output_storage_ref: Optional[str] = Field(None, description="Protected storage URI of output text")
    output_sha256_internal: str = Field(..., min_length=64, max_length=64)
    applied_rule_ids: List[str] = Field(default_factory=list)
    guard_results: Dict[str, GuardResult] = Field(default_factory=dict)
    language: str = Field("si")
    locale: str = Field("si-LK")
    script: str = Field("Sinh")
    validation_status: str = Field("draft", description="Strictly 'draft' in Stage 33")
    expert_validated: bool = Field(False, description="Strictly False in Stage 33")
    research_eligible: bool = Field(False, description="Strictly False in Stage 33")
    approved_for_child_delivery: bool = Field(False, description="Strictly False in Stage 33")
    approved_for_unsupervised_child_delivery: bool = Field(False, description="Strictly False in Stage 33")
    requires_expert_review: bool = Field(True, description="Strictly True in Stage 33")
    corpus_view: CorpusView = Field(CorpusView.CANONICAL_ANALYTICAL_150)
    rights_profile_refs: List[RightsProfileBinding] = Field(default_factory=list)

