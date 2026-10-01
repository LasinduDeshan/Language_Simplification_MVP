"""
Pydantic schemas and contracts for the Stage 25 Controlled Simplification Engine.
"""

from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field


class SupportLevel(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    STRONG = "strong"


class SupportLevelSource(str, Enum):
    AUTHORIZED_REQUEST = "authorized_request"
    LEARNER_PROFILE_RECOMMENDATION = "learner_profile_recommendation"
    ATTEMPT_ESCALATION = "attempt_escalation"
    DEFAULT_FALLBACK = "default_fallback"


class TerminalStatus(str, Enum):
    PASSED = "PASSED"
    PASSED_WITH_ROLLBACK = "PASSED_WITH_ROLLBACK"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    REJECTED = "REJECTED"
    ADULT_SUPPORT_REQUIRED = "ADULT_SUPPORT_REQUIRED"


class ModifierCriticality(str, Enum):
    SAFETY_CRITICAL = "safety_critical"
    TASK_CRITICAL = "task_critical"
    MEANING_RELEVANT = "meaning_relevant"
    OPTIONAL_STYLE = "optional_style"


class ModifierNode(BaseModel):
    text: str
    criticality: ModifierCriticality = ModifierCriticality.OPTIONAL_STYLE


class ActionNode(BaseModel):
    sequence: int
    verb: str
    object: str = ""
    relation: Optional[str] = None
    reference_object: Optional[str] = None
    modifiers: List[ModifierNode] = Field(default_factory=list)
    raw_clause: Optional[str] = None


class ActionGraph(BaseModel):
    actions: List[ActionNode] = Field(default_factory=list)
    has_temporal_inversion: bool = False
    is_multi_step: bool = False


class LearnerProfileContext(BaseModel):
    learner_id_hash: str = Field(default="ANON-LRN-000000", description="Pseudonymous learner identifier hash")
    grade_level: str = "Grade 1"
    vocabulary_score: float = Field(default=0.5, ge=0.0, le=1.0)
    grammar_score: float = Field(default=0.5, ge=0.0, le=1.0)
    comprehension_score: float = Field(default=0.5, ge=0.0, le=1.0)
    instruction_following_score: float = Field(default=0.5, ge=0.0, le=1.0)
    recommended_support_level: SupportLevel = SupportLevel.MODERATE
    attempt_number: int = Field(default=1, ge=1)
    previous_error_pattern: Optional[str] = None


class SemanticEquivalenceRule(BaseModel):
    source: str
    allowed: List[str] = Field(default_factory=list)


class ProtectedElementsConfig(BaseModel):
    exact_preservation: List[str] = Field(default_factory=list)
    semantic_equivalence_allowed: List[SemanticEquivalenceRule] = Field(default_factory=list)
    quantities: List[Union[str, int, float]] = Field(default_factory=list)
    forbidden_disclosure_refs: List[str] = Field(default_factory=list)
    forbidden_disclosure_hashes: List[str] = Field(default_factory=list)


class EffectiveProtectionContext(BaseModel):
    detected_protected_elements: Dict[str, Any] = Field(default_factory=dict)
    effective_protected_elements: ProtectedElementsConfig = Field(default_factory=ProtectedElementsConfig)
    protection_conflicts: List[str] = Field(default_factory=list)


class SimplificationRequest(BaseModel):
    request_id: str
    text: str
    language: str = "en"
    target_content_age: int = Field(default=6, ge=4, le=8)
    target_support_level: Optional[SupportLevel] = None
    content_type: str = "instruction"
    response_mode: str = "direct_action"
    learner_profile: Optional[LearnerProfileContext] = None
    provided_protected_elements: Optional[ProtectedElementsConfig] = None
    provided_action_sequence: Optional[List[ActionNode]] = None


class AdvisorySemanticSimilarity(BaseModel):
    model: str = "sentence-transformers/all-MiniLM-L6-v2"
    model_revision: str = "e4ce9877ab0b32132d0"
    similarity_score: float = 1.0
    threshold: float = 0.85
    passed: bool = True
    is_fallback: bool = False


class ValidationResults(BaseModel):
    language_consistency: bool = True
    grammar_completeness: bool = True
    exact_elements_preserved: bool = True
    semantic_elements_preserved: bool = True
    quantities_preserved: bool = True
    colors_shapes_preserved: bool = True
    negation_preserved: bool = True
    spatial_temporal_preserved: bool = True
    action_order_preserved: bool = True
    answer_boundary_preserved: bool = True
    support_compliance: bool = True
    advisory_semantic_similarity: AdvisorySemanticSimilarity = Field(default_factory=AdvisorySemanticSimilarity)
    child_safe_checks_passed: bool = True
    detected_violations: List[str] = Field(default_factory=list)

    @property
    def all_critical_passed(self) -> bool:
        return (
            self.language_consistency
            and self.grammar_completeness
            and self.exact_elements_preserved
            and self.semantic_elements_preserved
            and self.quantities_preserved
            and self.colors_shapes_preserved
            and self.negation_preserved
            and self.spatial_temporal_preserved
            and self.action_order_preserved
            and self.answer_boundary_preserved
            and self.support_compliance
            and self.child_safe_checks_passed
        )


class VocabularyExplanation(BaseModel):
    word: str
    simplified_term: Optional[str] = None
    simple_definition: str
    example: str
    source: str = "governed_lexicon"


class AppliedOperation(BaseModel):
    rule_id: str
    type: str
    status: str = "applied"  # applied | rolled_back | skipped
    description: Optional[str] = None


class ComplexityDeltas(BaseModel):
    fkgl_delta: float = 0.0
    word_count_delta: int = 0
    mean_clause_length_delta: float = 0.0
    difficult_word_ratio_delta: float = 0.0


class ScaffoldingMetadata(BaseModel):
    attempt_number: int = 1
    visual_hint_flag: bool = False
    audio_hint_flag: bool = False
    requires_adult_escalation: bool = False


class GovernanceMetadata(BaseModel):
    validation_status: str = "draft"
    approved_for_child_delivery: bool = False
    requires_expert_review: bool = True


class SimplificationResponse(BaseModel):
    request_id: str
    engine_version: str = "1.0.0"
    configuration_hash: str
    original_text_hash: str
    original_text: str
    simplified_text: str
    requested_support_level: Optional[SupportLevel] = None
    recommended_support_level: Optional[SupportLevel] = None
    applied_support_level: SupportLevel
    support_level_source: SupportLevelSource
    support_override_reason: Optional[str] = None
    status: TerminalStatus
    governance_metadata: GovernanceMetadata = Field(default_factory=GovernanceMetadata)
    validation_results: ValidationResults = Field(default_factory=ValidationResults)
    vocabulary_explanations: List[VocabularyExplanation] = Field(default_factory=list)
    applied_operations: List[AppliedOperation] = Field(default_factory=list)
    complexity_deltas: ComplexityDeltas = Field(default_factory=ComplexityDeltas)
    scaffolding_metadata: ScaffoldingMetadata = Field(default_factory=ScaffoldingMetadata)
    action_graph: Optional[ActionGraph] = None
