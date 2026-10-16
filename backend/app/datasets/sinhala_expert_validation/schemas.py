"""
Stage 34 — Pydantic Schemas and Contracts
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, model_validator

from .enums import (
    AdjudicationDisposition,
    AmendmentStatus,
    DimensionStatus,
    ExperienceBand,
    OverallDisposition,
    ReasonCode,
    ReviewerRole,
    RuleDisposition,
    SafetyFlag,
    SimplicityRating,
    TrainingStatus,
)


class DimensionRating(BaseModel):
    status: DimensionStatus
    score: Optional[Union[int, str]] = None

    @model_validator(mode="after")
    def validate_status_and_score(self):
        if self.status == DimensionStatus.RATED:
            if self.score is None:
                raise ValueError("When status is RATED, score must be provided and non-null.")
        else:
            if self.score is not None:
                raise ValueError(f"When status is {self.status.value}, score must be null.")
        return self


class CompetencyDeclarations(BaseModel):
    meaning_preservation: bool = True
    grammatical_acceptability: bool = True
    morphology_preservation: bool = True
    fluency_naturalness: bool = True
    simplicity_improvement: bool = True
    vocabulary_suitability: bool = True
    sentence_structure_suitability: bool = True
    developmental_suitability: bool = False


class ReviewerEligibility(BaseModel):
    reviewer_id: str
    roles: List[ReviewerRole]
    qualification_evidence_ref: str
    years_relevant_experience_band: ExperienceBand
    native_or_professional_sinhala_proficiency: bool = True
    ages_4_to_8_experience: bool = False
    competency_declarations: CompetencyDeclarations
    conflict_declaration_completed: bool = True
    consent_version: str
    consent_version_hash: str
    training_status: TrainingStatus = TrainingStatus.TRAINING_PENDING
    identity_publicly_disclosed: bool = False
    is_project_team_member: bool = False


class ErrorSpan(BaseModel):
    target: str = Field(..., pattern="^(source|candidate)$")
    start_char: int = Field(..., ge=0)
    end_char: int = Field(..., ge=0)
    reason_code: ReasonCode
    rule_id: Optional[str] = None

    @model_validator(mode="after")
    def validate_bounds(self):
        if self.end_char <= self.start_char:
            raise ValueError(f"end_char ({self.end_char}) must be strictly greater than start_char ({self.start_char}).")
        return self


class AnnotationRecord(BaseModel):
    annotation_id: str
    item_id: str
    reviewer_id: str
    assignment_id: str
    rubric_version: str
    rubric_hash: str
    submitted_at: Optional[str] = None
    meaning_preservation: DimensionRating
    grammatical_acceptability: DimensionRating
    morphology_preservation: DimensionRating
    fluency_naturalness: DimensionRating
    simplicity_improvement: DimensionRating
    vocabulary_suitability: DimensionRating
    sentence_structure_suitability: DimensionRating
    developmental_suitability: DimensionRating
    safety: DimensionRating
    overall_disposition: DimensionRating
    reason_codes: List[ReasonCode] = Field(default_factory=list)
    error_spans: List[ErrorSpan] = Field(default_factory=list)
    confidence: str = Field(default="HIGH", pattern="^(HIGH|MEDIUM|LOW)$")
    independent_submission: bool = True
    human_authored: bool = True
    has_protected_comments: bool = False
    protected_comment_ref: Optional[str] = None
    is_draft: bool = False

    @model_validator(mode="after")
    def validate_submission_completeness(self):
        # Invariant 23: Submitted annotations must not contain MISSING in any mandatory dimension
        if not self.is_draft:
            if not self.submitted_at:
                raise ValueError(f"Submitted annotation {self.annotation_id} must have submitted_at timestamp.")
            mandatory_dims = [
                ("meaning_preservation", self.meaning_preservation),
                ("grammatical_acceptability", self.grammatical_acceptability),
                ("morphology_preservation", self.morphology_preservation),
                ("fluency_naturalness", self.fluency_naturalness),
                ("simplicity_improvement", self.simplicity_improvement),
                ("vocabulary_suitability", self.vocabulary_suitability),
                ("sentence_structure_suitability", self.sentence_structure_suitability),
                ("developmental_suitability", self.developmental_suitability),
                ("safety", self.safety),
                ("overall_disposition", self.overall_disposition),
            ]
            for name, dim in mandatory_dims:
                if dim.status == DimensionStatus.MISSING:
                    raise ValueError(
                        f"Validation error: Submitted annotation {self.annotation_id} contains MISSING for mandatory dimension '{name}'. Use CANNOT_ASSESS with null score if unable to evaluate."
                    )
        return self


class AmendmentRecord(BaseModel):
    amendment_id: str
    original_annotation_id: str
    reviewer_id: str
    item_id: str
    reason_codes: List[ReasonCode]
    amended_fields: Dict[str, Any]
    status: AmendmentStatus = AmendmentStatus.ACCEPTED
    submitted_at: str
    rationale_ref: Optional[str] = None


class AdjudicationRecord(BaseModel):
    adjudication_id: str
    item_id: str
    independent_annotation_ids: List[str]
    adjudicator_id: str
    final_disposition: AdjudicationDisposition
    reason_codes: List[ReasonCode]
    rationale_ref: str
    resolved: bool = True
    changes_upstream_artifact: bool = False


class RuleDispositionRecord(BaseModel):
    rule_id: str
    version: str
    evaluated_items_count: int
    disposition: RuleDisposition
    agreement_alpha: Optional[float] = None
    findings: Dict[str, Any] = Field(default_factory=dict)
    recommended_action: str
    governance_flags: List[str] = Field(default_factory=list)
    sealed: bool = True
