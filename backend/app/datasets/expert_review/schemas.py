"""Pydantic schemas and enums for Stage 27 Expert Review and Validation.

Enforces strict domain boundaries, separation of critical failure flags from authorizations,
taxonomies, and batch/submission accounting models.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class ReviewRecordType(str, Enum):
    SIMPLIFICATION_PAIR = "simplification_pair"
    LEXICON_ENTRY = "lexicon_entry"
    ADAPTATION_ACTIVITY = "adaptation_activity"


class SubmissionOrigin(str, Enum):
    HUMAN_ENTERED = "human_entered"
    SCRIPT_GENERATED = "script_generated"
    FIXTURE_GENERATED = "fixture_generated"
    LLM_GENERATED = "llm_generated"
    UNKNOWN_ORIGIN = "unknown_origin"


class ReviewMode(str, Enum):
    OPERATIONAL_SIMULATION = "operational_simulation"
    REAL_HUMAN_EXPERT_REVIEW = "real_human_expert_review"


# Backward compatibility alias
PilotReviewMode = ReviewMode


class SupportLevel(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    STRONG = "strong"


class TaxonomyClass(str, Enum):
    TEXT_SIMPLIFICATION = "text_simplification"
    INSTRUCTION_REPHRASING = "instruction_rephrasing"
    ACTIVITY_FORMAT_TRANSFORMATION = "activity_format_transformation"
    QUESTION_GENERATION = "question_generation"
    RESPONSE_MODE_ADAPTATION = "response_mode_adaptation"
    INVALID_OR_UNUSABLE = "invalid_or_unusable"


class FinalDisposition(str, Enum):
    EXPERT_APPROVED = "expert_approved"
    APPROVED_WITH_REVISION = "approved_with_revision"
    MANUAL_REVISION_REQUIRED = "manual_revision_required"
    REJECTED_SAFETY = "rejected_safety"
    REJECTED_MEANING_CHANGE = "rejected_meaning_change"
    INVALID_OR_UNUSABLE = "invalid_or_unusable"


class LexiconDisposition(str, Enum):
    APPROVED = "approved"
    APPROVED_WITH_REVISION = "approved_with_revision"
    WRONG_WORD_SENSE = "wrong_word_sense"
    REPLACEMENT_NOT_SIMPLER = "replacement_not_simpler"
    AGE_TIER_INCORRECT = "age_tier_incorrect"
    DEFINITION_NOT_CHILD_FRIENDLY = "definition_not_child_friendly"
    CIRCULAR_DEFINITION = "circular_definition"
    REJECTED = "rejected"


class ICCForm(str, Enum):
    ICC_A_1 = "ICC(A,1)"  # Two-way mixed effects, single rater, absolute agreement (fixed panel)
    ICC_3_1 = "ICC(3,1)"  # Two-way mixed effects, single rater, consistency (fixed panel)
    ICC_2_1 = "ICC(2,1)"  # Two-way random effects, single rater, absolute agreement (random panel)



class ReviewerProfile(BaseModel):
    reviewer_id: str
    professional_role: str = "Expert Reviewer"
    qualification_category: str = "Linguistics/Education"
    relevant_experience_years: int = 5
    language_expertise: List[str] = Field(default_factory=lambda: ["en-US", "en-GB"])
    child_age_expertise: List[str] = Field(default_factory=lambda: ["4-6", "6-8"])
    qualification_tracks: List[str] = Field(default_factory=list)
    conflict_of_interest_declared: bool = False
    participation_agreement_signed: bool = False
    confidentiality_undertaking_signed: bool = False
    calibration_completed: bool = False
    calibration_agreement_score: float = 0.0
    authorized_dimensions: List[str] = Field(default_factory=list)
    account_status: str = "active"  # "active", "revoked", "suspended", "completed"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def is_active(self) -> bool:
        return self.account_status == "active"

    @property
    def calibration_passed(self) -> bool:
        return self.calibration_completed and self.calibration_agreement_score >= 0.80

    def is_eligible(self) -> bool:
        return (
            self.participation_agreement_signed
            and self.confidentiality_undertaking_signed
            and not self.conflict_of_interest_declared
            and self.calibration_completed
            and self.calibration_agreement_score >= 0.80
            and self.account_status == "active"
        )


class DimensionRatings(BaseModel):
    meaning_preservation: int = Field(default=4, ge=1, le=5)
    grammatical_correctness: int = Field(default=4, ge=1, le=5)
    fluency_and_naturalness: int = Field(default=4, ge=1, le=5)
    vocabulary_simplicity: int = Field(default=4, ge=1, le=5)
    sentence_structure_simplicity: int = Field(default=4, ge=1, le=5)
    age_appropriateness: int = Field(default=4, ge=1, le=5)
    support_level_appropriateness: int = Field(default=4, ge=1, le=5)
    instruction_clarity: int = Field(default=4, ge=1, le=5)
    protected_element_preservation: int = Field(default=4, ge=1, le=5)
    overall_child_language_suitability: int = Field(default=4, ge=1, le=5)

    def average_score(self) -> float:
        ratings = [
            self.meaning_preservation,
            self.grammatical_correctness,
            self.fluency_and_naturalness,
            self.vocabulary_simplicity,
            self.sentence_structure_simplicity,
            self.age_appropriateness,
            self.support_level_appropriateness,
            self.instruction_clarity,
            self.protected_element_preservation,
            self.overall_child_language_suitability,
        ]
        return round(sum(ratings) / len(ratings), 2)


class CriticalFailureFlags(BaseModel):
    meaning_changed: bool = False
    important_information_removed: bool = False
    unsupported_information_added: bool = False
    negation_changed: bool = False
    quantity_or_number_changed: bool = False
    entity_changed: bool = False
    spatial_relation_changed: bool = False
    temporal_or_action_order_changed: bool = False
    answer_leakage_detected: bool = False
    unsafe_or_inappropriate_content: bool = False

    def has_critical_failure(self) -> bool:
        return any([
            self.meaning_changed,
            self.important_information_removed,
            self.unsupported_information_added,
            self.negation_changed,
            self.quantity_or_number_changed,
            self.entity_changed,
            self.spatial_relation_changed,
            self.temporal_or_action_order_changed,
            self.answer_leakage_detected,
            self.unsafe_or_inappropriate_content,
        ])


class WorkflowFlags(BaseModel):
    requires_revision: bool = False
    requires_adjudication: bool = False
    requires_expert_recheck: bool = False


class AuthorizationDecisions(BaseModel):
    eligible_for_stage28_evaluation: bool = False
    recommended_for_supervised_child_delivery_review: bool = False
    approved_for_unsupervised_child_delivery: bool = False

    @field_validator("approved_for_unsupervised_child_delivery")
    @classmethod
    def validate_unsupervised_child_delivery(cls, v: bool) -> bool:
        if v is True:
            raise ValueError(
                "approved_for_unsupervised_child_delivery must NEVER be True in Stage 27."
            )
        return False


class SupportTierReview(BaseModel):
    support_progression_valid: bool = True
    mild_tier_appropriate: bool = True
    moderate_tier_appropriate: bool = True
    strong_tier_appropriate: bool = True
    meaning_preserved_across_tiers: bool = True
    recommended_tier_change: Optional[str] = None
    support_progression_issue: Optional[str] = None


class ReviewManifestItem(BaseModel):
    item_id: str
    source_group_id: str
    record_type: ReviewRecordType
    text_stimulus: str
    target_text: str
    support_level: Optional[SupportLevel] = None
    target_age_min: int = 4
    target_age_max: int = 8
    domain: str = "general"
    difficulty: str = "medium"
    is_reformulation_candidate: bool = False
    is_locked_evaluation: bool = False
    dataset_split: Optional[str] = None
    content_hash: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ReviewBatch(BaseModel):
    batch_id: str
    reviewer_panel_id: str
    reviewer_a_id: str
    reviewer_b_id: str
    item_ids: List[str]
    status: str = "assigned"  # "assigned", "in_progress", "completed", "revoked"
    review_mode: ReviewMode = ReviewMode.OPERATIONAL_SIMULATION
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class RecordReviewSubmission(BaseModel):
    submission_id: str
    item_id: str
    reviewer_id: str
    batch_id: str
    taxonomy_class: TaxonomyClass
    ratings: DimensionRatings
    critical_checks: CriticalFailureFlags
    workflow_flags: WorkflowFlags
    support_tier_review: Optional[SupportTierReview] = None
    lexicon_disposition: Optional[LexiconDisposition] = None
    reviewer_notes: Optional[str] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    submission_hash: str
    submission_origin: SubmissionOrigin = SubmissionOrigin.SCRIPT_GENERATED
    review_mode: ReviewMode = ReviewMode.OPERATIONAL_SIMULATION

    def determine_provisional_disposition(self) -> FinalDisposition:
        if self.critical_checks.unsafe_or_inappropriate_content or self.critical_checks.answer_leakage_detected:
            return FinalDisposition.REJECTED_SAFETY
        if self.critical_checks.meaning_changed or self.critical_checks.negation_changed or self.critical_checks.unsupported_information_added:
            return FinalDisposition.REJECTED_MEANING_CHANGE
        if self.critical_checks.has_critical_failure():
            return FinalDisposition.INVALID_OR_UNUSABLE
        if self.taxonomy_class == TaxonomyClass.INVALID_OR_UNUSABLE:
            return FinalDisposition.INVALID_OR_UNUSABLE
        if self.workflow_flags.requires_revision:
            return FinalDisposition.APPROVED_WITH_REVISION
        if (
            self.ratings.meaning_preservation >= 4
            and self.ratings.grammatical_correctness >= 4
            and self.ratings.age_appropriateness >= 4
            and self.ratings.support_level_appropriateness >= 4
        ):
            return FinalDisposition.EXPERT_APPROVED
        return FinalDisposition.APPROVED_WITH_REVISION


class AdjudicationRecord(BaseModel):
    adjudication_id: str
    item_id: str
    adjudicator_id: str
    reviewer_a_id: str
    reviewer_b_id: str
    reviewer_a_submission_id: str
    reviewer_b_submission_id: str
    conflict_reasons: List[str]
    final_taxonomy_class: TaxonomyClass
    final_disposition: FinalDisposition
    adjudicated_critical_checks: CriticalFailureFlags
    adjudicated_ratings: Optional[DimensionRatings] = None
    decision_rationale: str
    revision_required: bool = False
    review_mode: ReviewMode = ReviewMode.OPERATIONAL_SIMULATION
    adjudicated_at: datetime = Field(default_factory=datetime.utcnow)


class CalibrationReference(BaseModel):
    reference_status: str = "template_pending_human_creation"
    calibration_manifest_hash: Optional[str] = None
    reference_created_by_reviewer_id: Optional[str] = None
    reference_created_by_role_required: str = "authorized_lead_adjudicator"
    reference_creation_date: Optional[str] = None
    historical_locked_overlap_required: int = 0
    eligible_for_human_calibration: bool = False
    reference_rationale: Optional[str] = None
    concordance_rule_definition: str = (
        "Multi-criterion pilot_calibration_eligibility_threshold: "
        "(1) taxonomy_exact_agreement >= 0.80 (at least 8/10 exact taxonomy matches; Cohen's kappa reported descriptively); "
        "(2) 100% agreement on predefined critical safety cases; "
        "(3) weighted ordinal agreement target met (quadratic weighted kappa >= 0.75, mean absolute difference <= 0.50); "
        "(4) all serious disagreements discussed with the lead adjudicator."
    )
    items: List[Dict[str, Any]] = Field(default_factory=list)


class RevisionRecord(BaseModel):
    revision_id: str
    item_id: str
    source_group_id: str
    original_text: str
    revised_text: str
    original_hash: str
    revised_hash: str
    revision_reason: str
    revised_by: str
    stage14_schema_validation: str = "PASSED"
    stage15_quality_validation: str = "PASSED"
    final_disposition: FinalDisposition = FinalDisposition.APPROVED_WITH_REVISION
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SubmissionAccounting(BaseModel):
    expected_submissions: int = 3360
    completed_submissions: int = 0
    revoked_incomplete_submissions: int = 0
    pending_reassigned_submissions: int = 0
    unaccounted_submissions: int = 0

    def verify_conservation(self) -> bool:
        total = (
            self.completed_submissions
            + self.revoked_incomplete_submissions
            + self.pending_reassigned_submissions
            + self.unaccounted_submissions
        )
        return total == self.expected_submissions and self.pending_reassigned_submissions == 0 and self.unaccounted_submissions == 0


class InventoryAccounting(BaseModel):
    total_pairs: int = 1110
    total_lexicon: int = 378
    total_activities: int = 192
    reformulation_queue: int = 326
    consensus_resolved: int = 0
    adjudicated: int = 0
    unresolved_reformulations: int = 0
    retained_text_simplification: int = 0
    reclassified_auxiliary: int = 0
    rejected: int = 0

    def verify_route_conservation(self) -> bool:
        total = self.consensus_resolved + self.adjudicated + self.unresolved_reformulations
        return total == self.reformulation_queue and self.unresolved_reformulations == 0

    def verify_disposition_conservation(self) -> bool:
        total = (
            self.retained_text_simplification
            + self.reclassified_auxiliary
            + self.rejected
            + self.unresolved_reformulations
        )
        return total == self.reformulation_queue and self.unresolved_reformulations == 0
