from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# ----------------- Learner Profile Schemas -----------------
class LearnerProfileBase(BaseModel):
    learner_code: str = Field(..., max_length=50, description="Pseudonymous learner identifier")
    age: int = Field(..., ge=4, le=8, description="Age in years (4 to 8)")
    grade: Optional[str] = Field(None, max_length=50)
    risk_support_level: str = Field("moderate", pattern="^(low|moderate|high)$")
    vocabulary_score: float = Field(50.0, ge=0.0, le=100.0)
    grammar_score: float = Field(50.0, ge=0.0, le=100.0)
    comprehension_score: float = Field(50.0, ge=0.0, le=100.0)
    instruction_following_score: float = Field(50.0, ge=0.0, le=100.0)
    english_level: str = Field("emerging", pattern="^(emerging|developing|proficient)$")
    preferred_language: str = Field("en")

class LearnerProfileCreate(LearnerProfileBase):
    pass

class LearnerProfileResponse(LearnerProfileBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ----------------- Task Schemas -----------------
class ProtectedAnswerRelation(BaseModel):
    subject: str
    relation: str
    answer: str

class ProtectedAnswersSchema(BaseModel):
    relations: List[ProtectedAnswerRelation] = []
    allowed_instruction_terms: List[str] = []
    restricted_solution_phrases: List[str] = []
    answer_reveal_policy: str = "do_not_reveal_before_response"

class AnswerPresentationPolicySchema(BaseModel):
    mode: str = "multiple_choice"
    candidate_answers_may_be_shown: bool = True
    correct_candidate_may_be_identified: bool = False
    explanation_before_attempt: bool = False

class TaskBase(BaseModel):
    task_code: str = Field(..., max_length=50)
    title: str = Field(..., max_length=200)
    task_type: str = Field(..., pattern="^(vocabulary|grammar|categorization|comprehension|ar|classroom|sequence)$")
    language: str = "en"
    learning_objective: str
    original_instruction: str
    minimum_age: int = Field(4, ge=4)
    maximum_age: int = Field(8, le=8)
    base_difficulty: str = Field("medium", pattern="^(easy|medium|hard)$")
    expected_concepts: List[str] = []
    acceptable_answers: List[str] = []
    protected_answers: ProtectedAnswersSchema = Field(default_factory=ProtectedAnswersSchema)
    answer_presentation_policy: Optional[AnswerPresentationPolicySchema] = Field(default_factory=AnswerPresentationPolicySchema)
    vocabulary_targets: List[str] = []
    grammar_targets: List[str] = []
    ar_metadata: Optional[Dict[str, Any]] = None
    is_active: bool = True

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ----------------- Performance Pattern Schemas -----------------
class PerformancePatternBase(BaseModel):
    pattern_type: str = Field(..., pattern="^(vocabulary|grammar|comprehension|instruction)$")
    pattern_code: str
    frequency: int = 1
    confidence: float = Field(0.8, ge=0.0, le=1.0)
    successful_support: Optional[str] = None
    recommended_support: str = Field("moderate", pattern="^(mild|moderate|strong)$")
    source: str = "simulator_component_4"

class PerformancePatternCreate(PerformancePatternBase):
    learner_id: str

class PerformancePatternResponse(PerformancePatternBase):
    id: str
    learner_id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ----------------- Experiment Run Schemas -----------------
class ExperimentRunCreate(BaseModel):
    learner_id: str
    task_id: str
    generation_mode: str = Field("rule", pattern="^(rule|llm|hybrid)$")

class ExperimentRunResponse(BaseModel):
    id: str
    learner_id: str
    task_id: str
    generation_mode: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    final_outcome: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# ----------------- Adaptation Schemas -----------------
class AdaptationResponse(BaseModel):
    id: str
    experiment_run_id: str
    source_attempt_id: Optional[str] = None
    target_attempt_number: int
    support_level: str
    generation_method: str
    child_instruction: str
    supportive_message: Optional[str] = None
    vocabulary_support: Optional[List[Dict[str, Any]]] = None
    answer_format: Optional[str] = None
    visual_cues: Optional[List[str]] = None
    reason_codes: Optional[List[str]] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None
    prompt_version: Optional[str] = None
    processing_time_ms: int = 0
    estimated_cost: Optional[float] = 0.0
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ----------------- Attempt Schemas -----------------
class AttemptCreate(BaseModel):
    adaptation_id: str
    speech_transcript: Optional[str] = None
    speech_confidence: Optional[float] = Field(0.9, ge=0.0, le=1.0)
    selected_answer: Optional[Dict[str, Any]] = None
    response_time_ms: int = Field(5000, ge=0)
    completion_status: str = Field("completed", pattern="^(completed|skipped|incomplete)$")

# ----------------- Language Observation Schemas -----------------
class LanguageObservationResponse(BaseModel):
    id: str
    attempt_id: str
    category: str
    observation_code: str
    evidence: Optional[str] = None
    confidence: float
    confirmed: bool
    child_visible: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AttemptResponse(BaseModel):
    id: str
    experiment_run_id: str
    adaptation_id: str
    attempt_number: int
    instruction_shown: str
    speech_transcript: Optional[str] = None
    speech_confidence: Optional[float] = None
    selected_answer: Optional[Dict[str, Any]] = None
    concept_result: str
    response_time_ms: int
    completion_status: str
    created_at: datetime
    observations: List[LanguageObservationResponse] = []
    model_config = ConfigDict(from_attributes=True)

# ----------------- Validation Result Schemas -----------------
class ValidationResultResponse(BaseModel):
    id: str
    adaptation_id: str
    validation_sequence: int
    generator_output_version: int
    candidate_output: Dict[str, Any]
    language_valid: bool
    age_appropriate: bool
    meaning_preserved: bool
    answer_leakage: bool
    sentence_length_valid: bool
    support_level_valid: bool
    safety_valid: bool
    average_words_per_sentence: Optional[float] = None
    maximum_words_in_sentence: Optional[int] = None
    semantic_score: Optional[float] = None
    status: str
    failure_reasons: List[str]
    is_final: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ----------------- Integration Payloads (Comp 1, 3, 4) -----------------
class Component1OutputPayload(BaseModel):
    task_id: str
    attempt_number: int
    support_level: str
    child_instruction: str
    supportive_message: Optional[str] = None
    answer_format: str
    cues: List[str] = []
    do_not_reveal_answer: bool = True
    validation_status: str = "approved_for_simulation"

class Component4AnalyticsPayload(BaseModel):
    learner_id: str
    task_id: str
    attempt_number: int
    result: str
    observed_patterns: List[str] = []
    support_applied: List[str] = []
    next_recommendation: str = "continue_support"

class Component3ARPayload(BaseModel):
    task_id: str
    language: str = "en"
    child_instruction: str
    object_labels: List[str] = []
    vocabulary_support: List[Dict[str, str]] = []
    audio_text: str
    interaction_type: str
    support_level: str

# ----------------- Expert Evaluation Schemas -----------------
class ExpertEvaluationCreate(BaseModel):
    adaptation_id: str
    evaluator_code: str = Field(..., max_length=50)
    age_appropriateness: int = Field(..., ge=1, le=5)
    clarity: int = Field(..., ge=1, le=5)
    grammar_correctness: int = Field(..., ge=1, le=5)
    meaning_preservation: int = Field(..., ge=1, le=5)
    personalization_suitability: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None

class ExpertEvaluationResponse(ExpertEvaluationCreate):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ----------------- Standalone Endpoint Schemas -----------------
class AnalyzeResponseRequest(BaseModel):
    task_id: str
    speech_transcript: str
    speech_confidence: float = Field(0.9, ge=0.0, le=1.0)
    learner_age: int = Field(6, ge=4, le=8)

class AnalyzeResponseResult(BaseModel):
    concept_result: str
    concept_matches: List[str]
    observations: List[Dict[str, Any]]
    speech_confidence_acceptable: bool

class AdaptInstructionRequest(BaseModel):
    learner_id: str
    task_id: str
    attempt_number: int = 1
    generation_mode: str = "rule"

class ValidateOutputRequest(BaseModel):
    task_id: str
    child_instruction: str
    supportive_message: Optional[str] = None
    target_attempt_number: int = 1
    support_level: str = "moderate"
