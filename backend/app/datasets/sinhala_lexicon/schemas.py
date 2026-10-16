"""
Pydantic v2 Schemas for Stage 32 Sinhala Child-Vocabulary Lexicon Construction.
Enforces multi-tier separation between canonical entries, exact surface forms,
token occurrences, morphology hypotheses, rights provenance, and expert review records.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.datasets.sinhala_lexicon.enums import (
    OccurrenceDisposition,
    TerminalEntryDisposition,
    ProvisionalVocabularyBand,
    LemmaMethod,
    ReviewDecision,
    AgeBandReviewDecision,
    FieldExportPolicy
)

class RightsProfileReference(BaseModel):
    """Version-pinned source rights reference."""
    model_config = ConfigDict(extra="forbid")
    source_id: str = Field(..., description="Unique source identifier, e.g. SRC-SI-001")
    rights_profile_id: str = Field(..., description="Unique rights profile identifier")
    rights_profile_version: int = Field(default=1, ge=1)

class SurfaceFormRecord(BaseModel):
    """Observed surface form statistics aggregated under a candidate lexicon entry."""
    model_config = ConfigDict(extra="forbid")
    surface_form: str
    canonical_frequency: int = Field(..., ge=0)
    canonical_document_frequency: int = Field(..., ge=0)
    weighted_provenance_frequency: float = Field(..., ge=0.0)

class MorphologyHypothesis(BaseModel):
    """Rule-based candidate lemma or morphological relationship hypothesis."""
    model_config = ConfigDict(extra="forbid")
    rule_id: str
    rule_version: str = "1.0.0"
    base_form: str
    inflected_form: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    linguistic_note: Optional[str] = "Illustrative rule-based morphology hypothesis; not expert-validated linguistic evidence."

class TokenOccurrenceRecord(BaseModel):
    """Lossless occurrence ledger record tracking an individual token within a corpus record."""
    model_config = ConfigDict(extra="forbid")
    occurrence_id: str = Field(..., pattern=r"^SI-OCC-\d{8}$")
    entry_id: Optional[str] = Field(default=None, pattern=r"^SI-LEX-\d{6}$")
    candidate_extraction_status: str = Field(default="EXTRACTED", description="EXTRACTED or NOT_EXTRACTED")
    canonical_record_id: str = Field(..., description="Primary canonical analytical record ID, e.g. SI-PILOT-000001")
    provenance_record_id: str = Field(..., description="Provenance corpus record ID")
    source_id: str = Field(..., description="Contributing source ID")
    split_group_id: str = Field(..., description="Unified transitive split group ID")
    token_index: int = Field(..., ge=0)
    normalized_start_code_point: int = Field(..., ge=0)
    normalized_end_code_point: int = Field(..., ge=0)
    offset_interval: str = Field(default="zero_based_half_open")
    surface_form_hmac: Optional[str] = Field(default=None, description="Populated at runtime; null in templates")
    hmac_key_id: str = Field(default="HMAC-2026-V1")
    hmac_scheme_version: str = Field(default="v1")
    hmac_domain: str = Field(default="sinhala-lexicon-surface-form")
    context_storage_ref: str = Field(..., description="Abstract protected URI for concordance sentence")
    token_text_storage_ref: str = Field(..., description="Abstract protected URI for isolated token text")
    protected_context_ref: Optional[str] = Field(default=None, description="Abstract protected URI alias for concordance context")
    duplicate_weight_numerator: int = Field(default=1, ge=1)
    duplicate_weight_denominator: int = Field(default=1, ge=1)
    duplicate_weight_float: float = Field(default=1.0, gt=0.0)
    duplicate_weight_display: str = Field(default="1.0")
    authoritative_weight_representation: str = Field(default="rational")
    rights_profile_id: str
    rights_profile_version: int = Field(default=1, ge=1)
    stage30_configuration_hash: str
    stage31_configuration_hash: str
    corpus_artifact_sha256: str
    occurrence_disposition: OccurrenceDisposition
    exclusion_reason_code: Optional[str] = None
    reason_codes: List[str] = Field(default_factory=list)

    @field_validator("context_storage_ref", "token_text_storage_ref")
    @classmethod
    def validate_storage_ref(cls, v: str) -> str:
        if not v.startswith("protected://"):
            raise ValueError(f"Storage reference must use abstract protected:// URI, got: {v}")
        return v

    @field_validator("normalized_end_code_point")
    @classmethod
    def validate_offset_order(cls, v: int, info) -> int:
        start = info.data.get("normalized_start_code_point")
        if start is not None and v < start:
            raise ValueError(f"normalized_end_code_point ({v}) cannot be less than normalized_start_code_point ({start})")
        return v

    @property
    def exact_duplicate_weight(self) -> float:
        return self.duplicate_weight_float

class SurfaceFormMappingRecord(BaseModel):
    """Deterministic lookup mapping between observed surface variant and canonical candidate entry."""
    model_config = ConfigDict(extra="forbid")
    surface_form: str
    canonical_form: str
    entry_id: str = Field(..., pattern=r"^SI-LEX-\d{6}$")
    morphology_rule_id: str
    rule_version: str = "1.0.0"
    mapping_confidence: float = Field(..., ge=0.0, le=1.0)
    is_base_form: bool
    canonical_frequency: int = Field(..., ge=0)
    canonical_document_frequency: int = Field(..., ge=0)
    weighted_provenance_frequency: float = Field(..., ge=0.0)

class ReviewFindingRecord(BaseModel):
    """Evidence-based trigger record explaining an automated review referral."""
    model_config = ConfigDict(extra="forbid")
    reason_code: str
    rule_id: str
    trigger_evidence: Dict[str, Any]
    automated_finding_only: bool = True
    human_validated: bool = False

class CandidateLexiconEntry(BaseModel):
    """Authoritative candidate entry in the governed Sinhala child-vocabulary candidate lexicon."""
    model_config = ConfigDict(extra="forbid")
    entry_id: str = Field(..., pattern=r"^SI-LEX-\d{6}$")
    language: str = "si"
    locale: str = "si-LK"
    script: str = "Sinh"
    canonical_form: str
    candidate_lemma: Optional[str] = None
    lemma_method: LemmaMethod = LemmaMethod.IDENTITY_CANONICAL
    lemma_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    surface_forms: List[SurfaceFormRecord] = Field(default_factory=list)
    token_class: str = "SINHALA_WORD"
    grapheme_count: int = Field(..., ge=0)
    code_point_count: int = Field(..., ge=0)
    syllable_proxy_count: Optional[int] = Field(default=None, ge=0)
    morphology_hypotheses: List[MorphologyHypothesis] = Field(default_factory=list)
    canonical_frequency: int = Field(..., ge=0)
    canonical_document_frequency: int = Field(..., ge=0)
    weighted_provenance_frequency: float = Field(..., ge=0.0)
    source_count: int = Field(..., ge=0)
    source_frequency_distribution: Dict[str, int] = Field(default_factory=dict)
    eligible_source_count: int = Field(..., ge=1)
    observed_source_count: int = Field(..., ge=0)
    source_dispersion: float = Field(..., ge=0.0, le=1.0)
    dispersion_formula_version: str = "fixed_k_entropy_v1"
    provisional_band: ProvisionalVocabularyBand = ProvisionalVocabularyBand.REVIEW_REQUIRED
    band_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    band_evidence: List[str] = Field(default_factory=list)
    quality_flags: List[str] = Field(default_factory=list)
    review_findings: List[ReviewFindingRecord] = Field(default_factory=list)
    rights_profile_refs: List[RightsProfileReference] = Field(default_factory=list)
    field_export_policies: Dict[str, FieldExportPolicy] = Field(default_factory=dict)
    terminal_entry_disposition: TerminalEntryDisposition = TerminalEntryDisposition.ACCEPTED_DRAFT_LEXICON_ENTRY
    validation_status: str = "draft"
    expert_validated: bool = False
    research_eligible: bool = False
    approved_for_child_delivery: bool = False
    approved_for_unsupervised_child_delivery: bool = False
    requires_expert_review: bool = True

class LexiconExpertReviewRecord(BaseModel):
    """Controlled schema for future human expert review rounds. Real identities remain null until Stage 34."""
    model_config = ConfigDict(extra="forbid")
    entry_id: str = Field(..., pattern=r"^SI-LEX-\d{6}$")
    reviewer_id: Optional[str] = Field(default=None, description="Pseudonymous reviewer ID, e.g. REV-EXP-01")
    reviewer_role: str = "sinhala_linguist_or_early_childhood_language_expert"
    independent_review_round: int = Field(default=1, ge=1)
    lemma_decision: ReviewDecision = ReviewDecision.NOT_REVIEWED
    age_band_decision: AgeBandReviewDecision = AgeBandReviewDecision.NOT_REVIEWED
    meaning_review_status: ReviewDecision = ReviewDecision.NOT_REVIEWED
    safety_status: ReviewDecision = ReviewDecision.NOT_REVIEWED
    comments_storage_ref: Optional[str] = None
    reviewed_at: Optional[str] = None

    @model_validator(mode="after")
    def validate_reviewer_fields(self) -> "LexiconExpertReviewRecord":
        # Invariant: reviewed_at cannot be set without an authorized reviewer_id
        if self.reviewed_at is not None and self.reviewer_id is None:
            raise ValueError("reviewed_at cannot be populated when reviewer_id is null")
        # Invariant: reviewed_at cannot be set if all decisions remain NOT_REVIEWED
        all_unreviewed = (
            self.lemma_decision == ReviewDecision.NOT_REVIEWED and
            self.age_band_decision == AgeBandReviewDecision.NOT_REVIEWED and
            self.meaning_review_status == ReviewDecision.NOT_REVIEWED and
            self.safety_status == ReviewDecision.NOT_REVIEWED
        )
        if self.reviewed_at is not None and all_unreviewed:
            raise ValueError("reviewed_at cannot be populated when all review decisions are NOT_REVIEWED")
        return self
