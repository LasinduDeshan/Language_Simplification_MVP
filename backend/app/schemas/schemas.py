from typing import List, Dict, Any, Optional, Union
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

# ----------------- Activity Asset Schemas -----------------
class ActivityAssetResponse(BaseModel):
    id: str
    task_id: str
    asset_type: str = "image"
    asset_key: str
    file_path_or_url: str
    alt_text: str
    display_order: int = 1
    asset_source: str = "Project team"
    asset_creator: str = "Project team"
    license_type: str = "Original project asset"
    license_url: Optional[str] = None
    permission_status: str = "Approved for project use"
    attribution_text: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ----------------- Activity Question Schemas -----------------
class ActivityQuestionResponse(BaseModel):
    id: str
    task_id: str
    question_order: int
    question_text: str
    response_mode: str
    options: Optional[List[str]] = None
    acceptable_answers: List[str] = []
    expected_concepts: List[str] = []
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class QuestionResponseCreate(BaseModel):
    question_id: str
    manual_response: Optional[str] = None
    selected_option: Optional[Any] = None
    concept_result: str = "unclear"
    target_skill_result: Optional[str] = "not_applicable"
    adult_confirmed: bool = False
    response_time_ms: int = 0

class QuestionResponseSchema(QuestionResponseCreate):
    id: str
    attempt_id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ----------------- Task / Activity Schemas -----------------
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
    category: str = Field("vocabulary", pattern="^(vocabulary|grammar|sentence_and_instruction|comprehension)$")
    task_type: Optional[str] = "vocabulary"
    subskill: Optional[str] = None
    target_skill: Optional[str] = None
    language: str = "en"
    learning_objective: str
    child_friendly_instruction: Optional[str] = None
    original_instruction: str
    minimum_age: int = Field(4, ge=4)
    maximum_age: int = Field(8, le=8)
    base_difficulty: str = Field("medium", pattern="^(easy|medium|hard)$")
    
    delivery_modes: List[str] = ["standard"]
    response_modes: List[str] = ["manual_transcript", "multiple_choice"]
    
    stimulus: Optional[Dict[str, Any]] = None
    prompt: Optional[str] = None
    options: Optional[List[str]] = None
    passage: Optional[str] = None
    
    expected_concepts: List[str] = []
    acceptable_answers: List[str] = []
    expected_sequence: Optional[List[str]] = None
    protected_answers: Optional[Dict[str, Any]] = Field(default_factory=dict)
    answer_presentation_policy: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    support_versions: Optional[Dict[str, str]] = None
    follow_up_for_strong: Optional[str] = None
    
    vocabulary_targets: List[str] = []
    grammar_targets: List[str] = []
    ar_metadata: Optional[Dict[str, Any]] = None
    is_active: bool = True

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: str
    created_at: datetime
    assets: List[ActivityAssetResponse] = []
    questions: List[ActivityQuestionResponse] = []
    model_config = ConfigDict(from_attributes=True)

# ----------------- Activity Session Schemas -----------------
class ActivitySessionCreate(BaseModel):
    learner_id: str
    task_id: str
    generation_mode: str = Field("rule", pattern="^(rule|llm|hybrid)$")
    created_by: str = "authorized_adult"

class ActivitySessionResponse(BaseModel):
    id: str
    learner_id: str
    task_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    current_attempt_number: int
    initial_support_level: str
    current_support_level: str
    support_decision_reasons: List[str] = []
    final_outcome: Optional[str] = None
    escalation_required: bool
    created_by: str
    generation_mode: str
    learner_profile_snapshot: Dict[str, Any]
    task_version: str
    adaptation_configuration_version: str
    model_config = ConfigDict(from_attributes=True)

# ----------------- Attempt & Response Schemas -----------------
class AttemptCreateInstruction(BaseModel):
    """Payload to create an attempt and generate/store exact instruction before child sees it."""
    generation_mode: Optional[str] = None

class AttemptResponseInput(BaseModel):
    """Adult records child response."""
    response_source: str = Field("adult_transcribed", pattern="^(adult_transcribed|manual_selection|child_direct_input|browser_speech)$")
    manual_transcript: Optional[str] = None
    selected_option: Optional[str] = None
    selected_items: Optional[List[str]] = None
    ordered_items: Optional[List[str]] = None
    response_time_ms: int = Field(0, ge=0)
    completion_status: str = Field("completed", pattern="^(completed|no_response|asked_for_help|skipped)$")
    assistance_level: str = Field("independent", pattern="^(independent|prompted|visually_supported|modelled|fully_assisted)$")
    adult_notes: Optional[str] = None

class AttemptConfirmInput(BaseModel):
    """Adult confirms transcript accuracy."""
    confirmed: bool = True
    manual_transcript: Optional[str] = None  # If adult corrected typo during confirmation

class AttemptReviewInput(BaseModel):
    """Adult reviews/overrides automated analysis."""
    final_concept_result: str = Field(..., pattern="^(correct|partial|incorrect|unclear)$")
    final_target_skill_result: str = Field(..., pattern="^(correct|partial|incorrect|not_applicable)$")
    final_retry_required: bool
    override_reason: Optional[str] = None
    reviewed_by_user_id: str = "authorized_adult"
    adult_notes: Optional[str] = None

class LanguageObservationResponse(BaseModel):
    id: str
    attempt_id: str
    category: str
    observation_code: str
    evidence: Optional[str] = None
    confidence: Optional[float] = None
    confirmed: bool
    child_visible: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AttemptResponse(BaseModel):
    id: str
    activity_session_id: Optional[str] = None
    experiment_run_id: Optional[str] = None
    adaptation_id: Optional[str] = None
    attempt_number: int
    attempt_status: str
    presented_instruction: Optional[str] = None
    instruction_shown: Optional[str] = None
    support_level: str
    adaptation_strategy: Optional[str] = None
    visual_cues: Optional[List[str]] = []
    vocabulary_cues: Optional[List[str]] = []
    generation_method: str
    validation_status: str
    
    response_source: str
    manual_transcript: Optional[str] = None
    speech_transcript: Optional[str] = None
    speech_confidence: Optional[float] = None
    adult_confirmed: bool
    
    selected_option: Optional[str] = None
    selected_items: Optional[List[str]] = []
    ordered_items: Optional[List[str]] = []
    response_time_ms: int
    completion_status: str
    assistance_level: str
    independent_success: Optional[bool] = None
    response_format_adjusted: bool
    original_response_mode: Optional[str] = None
    current_response_mode: Optional[str] = None
    
    target_skill: Optional[str] = None
    concept_result: str
    target_skill_result: Optional[str] = None
    grammar_observations: List[str] = []
    vocabulary_observations: List[str] = []
    retry_required: bool
    retry_reason: Optional[str] = None
    automatic_analysis_snapshot: Optional[Dict[str, Any]] = None
    
    final_concept_result: Optional[str] = None
    final_target_skill_result: Optional[str] = None
    final_retry_required: Optional[bool] = None
    override_reason: Optional[str] = None
    reviewed_by_user_id: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    adult_notes: Optional[str] = None
    
    created_at: datetime
    observations: List[LanguageObservationResponse] = []
    model_config = ConfigDict(from_attributes=True)

# ----------------- Child-Safe View Schema -----------------
class ChildSafeViewResponse(BaseModel):
    session_id: str
    attempt_id: str
    attempt_number: int
    presented_instruction: str
    supportive_message: Optional[str] = None
    stimulus: Optional[Dict[str, Any]] = None
    prompt: Optional[str] = None
    options: Optional[List[str]] = None
    response_modes: List[str] = []
    visual_cues: List[str] = []
    audio_available: bool = True
    session_status: str = "active"
    retry_cue: Optional[str] = None
    adult_support_message: Optional[str] = None

# ----------------- Legacy Schemas (Backward Compatibility) -----------------
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

class AdaptationResponse(BaseModel):
    id: str
    experiment_run_id: Optional[str] = None
    activity_session_id: Optional[str] = None
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

class AttemptCreate(BaseModel):
    adaptation_id: Optional[str] = None
    speech_transcript: Optional[str] = None
    speech_confidence: Optional[float] = None
    selected_answer: Optional[Dict[str, Any]] = None
    response_time_ms: int = Field(5000, ge=0)
    completion_status: str = Field("completed", pattern="^(completed|no_response|asked_for_help|skipped)$")

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
    assistance_level: str = "independent"
    independent_success: bool = True
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

class AnalyzeResponseRequest(BaseModel):
    task_id: str
    speech_transcript: str
    speech_confidence: Optional[float] = None
    learner_age: int = Field(6, ge=4, le=8)

class AnalyzeResponseResult(BaseModel):
    concept_result: str
    target_skill_result: Optional[str] = None
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
    learner_id: Optional[str] = None
