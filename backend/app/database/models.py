import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from app.database.db import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    learner_code = Column(String(50), unique=True, nullable=False, index=True)
    age = Column(Integer, nullable=False)
    grade = Column(String(50), nullable=True)
    risk_support_level = Column(String(20), nullable=False)  # low, moderate, high
    vocabulary_score = Column(Float, nullable=False, default=50.0)
    grammar_score = Column(Float, nullable=False, default=50.0)
    comprehension_score = Column(Float, nullable=False, default=50.0)
    instruction_following_score = Column(Float, nullable=False, default=50.0)
    english_level = Column(String(20), nullable=False, default="emerging")  # emerging, developing, proficient
    preferred_language = Column(String(10), nullable=False, default="en")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("age >= 4 AND age <= 8", name="ck_learner_age_range"),
        CheckConstraint("vocabulary_score >= 0 AND vocabulary_score <= 100", name="ck_learner_vocab_score"),
        CheckConstraint("grammar_score >= 0 AND grammar_score <= 100", name="ck_learner_grammar_score"),
        CheckConstraint("comprehension_score >= 0 AND comprehension_score <= 100", name="ck_learner_comprehension_score"),
        CheckConstraint("instruction_following_score >= 0 AND instruction_following_score <= 100", name="ck_learner_instruction_score"),
    )

    experiment_runs = relationship("ExperimentRun", back_populates="learner", cascade="all, delete-orphan")
    activity_sessions = relationship("ActivitySession", back_populates="learner", cascade="all, delete-orphan")
    patterns = relationship("PerformancePattern", back_populates="learner", cascade="all, delete-orphan")
    task_results = relationship("TaskResult", back_populates="learner", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    # 4 Core Categories: vocabulary, grammar, sentence_and_instruction, comprehension
    category = Column(String(50), nullable=False, default="vocabulary")
    task_type = Column(String(50), nullable=False, default="vocabulary")  # legacy compatibility
    subskill = Column(String(100), nullable=True)
    target_skill = Column(String(100), nullable=True)
    language = Column(String(10), nullable=False, default="en")
    learning_objective = Column(Text, nullable=False)
    child_friendly_instruction = Column(Text, nullable=True)
    original_instruction = Column(Text, nullable=False)
    minimum_age = Column(Integer, nullable=False, default=4)
    maximum_age = Column(Integer, nullable=False, default=8)
    base_difficulty = Column(String(20), nullable=False, default="medium")  # easy, medium, hard
    
    # Delivery and interaction modes
    delivery_modes = Column(JSON, nullable=False, default=lambda: ["standard"])
    response_modes = Column(JSON, nullable=False, default=lambda: ["manual_transcript", "multiple_choice"])
    
    # Structured stimuli & prompts
    stimulus = Column(JSON, nullable=True, default=dict)
    prompt = Column(Text, nullable=True)
    options = Column(JSON, nullable=True, default=list)
    passage = Column(Text, nullable=True)
    
    # Expected & acceptable answers
    expected_concepts = Column(JSON, nullable=False, default=list)
    acceptable_answers = Column(JSON, nullable=False, default=list)
    expected_sequence = Column(JSON, nullable=True, default=list)
    protected_answers = Column(JSON, nullable=False, default=dict)
    answer_presentation_policy = Column(JSON, nullable=True, default=dict)
    
    # Support versions
    support_versions = Column(JSON, nullable=True, default=dict)
    follow_up_for_strong = Column(Text, nullable=True)
    
    # Target linguistic tags
    vocabulary_targets = Column(JSON, nullable=False, default=list)
    grammar_targets = Column(JSON, nullable=False, default=list)
    ar_metadata = Column(JSON, nullable=True, default=dict)
    
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("minimum_age >= 4", name="ck_task_min_age"),
        CheckConstraint("maximum_age <= 8", name="ck_task_max_age"),
    )

    experiment_runs = relationship("ExperimentRun", back_populates="task")
    activity_sessions = relationship("ActivitySession", back_populates="task")
    questions = relationship("ActivityQuestion", back_populates="task", cascade="all, delete-orphan", order_by="ActivityQuestion.question_order")
    assets = relationship("ActivityAsset", back_populates="task", cascade="all, delete-orphan", order_by="ActivityAsset.display_order")


class ActivityAsset(Base):
    __tablename__ = "activity_assets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False, default="image")  # image, audio, 3d_metadata
    asset_key = Column(String(100), nullable=False)
    file_path_or_url = Column(String(500), nullable=False)
    alt_text = Column(Text, nullable=False)
    display_order = Column(Integer, nullable=False, default=1)
    
    # Licensing & attribution
    asset_source = Column(String(200), nullable=False, default="Project team")
    asset_creator = Column(String(200), nullable=False, default="Project team")
    license_type = Column(String(100), nullable=False, default="Original project asset")
    license_url = Column(String(500), nullable=True)
    permission_status = Column(String(100), nullable=False, default="Approved for project use")
    attribution_text = Column(Text, nullable=True, default="Created for Language Simplification MVP")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    task = relationship("Task", back_populates="assets")


class ActivityQuestion(Base):
    __tablename__ = "activity_questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    question_order = Column(Integer, nullable=False, default=1)
    question_text = Column(Text, nullable=False)
    response_mode = Column(String(50), nullable=False, default="manual_transcript")
    options = Column(JSON, nullable=True, default=list)
    acceptable_answers = Column(JSON, nullable=False, default=list)
    expected_concepts = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    task = relationship("Task", back_populates="questions")
    responses = relationship("QuestionResponse", back_populates="question", cascade="all, delete-orphan")


class ActivitySession(Base):
    __tablename__ = "activity_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    learner_id = Column(String(36), ForeignKey("learner_profiles.id"), nullable=False, index=True)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="active")  # active, completed, completed_with_adult_support, adult_support_required
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    current_attempt_number = Column(Integer, nullable=False, default=1)
    initial_support_level = Column(String(20), nullable=False, default="moderate")  # mild, moderate, strong
    current_support_level = Column(String(20), nullable=False, default="moderate")
    support_decision_reasons = Column(JSON, nullable=False, default=list)
    final_outcome = Column(String(50), nullable=True)  # success, unresolved, adult_support_required
    escalation_required = Column(Boolean, nullable=False, default=False)
    created_by = Column(String(100), nullable=False, default="authorized_adult")
    generation_mode = Column(String(20), nullable=False, default="rule")  # rule, llm, hybrid
    
    # Immutable snapshots for research reproducibility
    learner_profile_snapshot = Column(JSON, nullable=False, default=dict)
    task_version = Column(String(20), nullable=False, default="1.0")
    adaptation_configuration_version = Column(String(20), nullable=False, default="1.0")

    learner = relationship("LearnerProfile", back_populates="activity_sessions")
    task = relationship("Task", back_populates="activity_sessions")
    attempts = relationship("Attempt", back_populates="activity_session", cascade="all, delete-orphan", order_by="Attempt.attempt_number")
    integration_events = relationship("IntegrationEvent", back_populates="activity_session", cascade="all, delete-orphan")


class ExperimentRun(Base):
    """Legacy runner model kept for backward compatibility."""
    __tablename__ = "experiment_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    learner_id = Column(String(36), ForeignKey("learner_profiles.id"), nullable=False, index=True)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    generation_mode = Column(String(20), nullable=False, default="rule")  # rule, llm, hybrid
    status = Column(String(20), nullable=False, default="active")  # active, completed, escalated
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    final_outcome = Column(String(20), nullable=True)  # success, unresolved, adult_support

    learner = relationship("LearnerProfile", back_populates="experiment_runs")
    task = relationship("Task", back_populates="experiment_runs")
    adaptations = relationship("Adaptation", back_populates="experiment_run", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="experiment_run", cascade="all, delete-orphan")
    integration_events = relationship("IntegrationEvent", back_populates="experiment_run", cascade="all, delete-orphan")


class Adaptation(Base):
    __tablename__ = "adaptations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experiment_run_id = Column(String(36), ForeignKey("experiment_runs.id"), nullable=True, index=True)
    activity_session_id = Column(String(36), ForeignKey("activity_sessions.id"), nullable=True, index=True)
    source_attempt_id = Column(String(36), ForeignKey("attempts.id", use_alter=True, name="fk_adaptation_source_attempt"), nullable=True)
    target_attempt_number = Column(Integer, nullable=False)  # 1, 2, or 3
    support_level = Column(String(20), nullable=False)  # mild, moderate, strong
    generation_method = Column(String(50), nullable=False, default="rule")  # curated, rule, llm, fallback
    child_instruction = Column(Text, nullable=False)
    supportive_message = Column(Text, nullable=True)
    vocabulary_support = Column(JSON, nullable=True, default=list)
    answer_format = Column(String(50), nullable=True, default="speech")
    visual_cues = Column(JSON, nullable=True, default=list)
    reason_codes = Column(JSON, nullable=True, default=list)
    provider = Column(String(50), nullable=True)
    model_name = Column(String(100), nullable=True)
    prompt_version = Column(String(50), nullable=True)
    temperature = Column(Float, nullable=True)
    processing_time_ms = Column(Integer, nullable=False, default=0)
    estimated_cost = Column(Float, nullable=True, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    experiment_run = relationship("ExperimentRun", back_populates="adaptations")
    validation_results = relationship("ValidationResult", back_populates="adaptation", cascade="all, delete-orphan")
    expert_evaluations = relationship("ExpertEvaluation", back_populates="adaptation", cascade="all, delete-orphan")


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experiment_run_id = Column(String(36), ForeignKey("experiment_runs.id"), nullable=True, index=True)
    activity_session_id = Column(String(36), ForeignKey("activity_sessions.id"), nullable=True, index=True)
    adaptation_id = Column(String(36), ForeignKey("adaptations.id"), nullable=True, index=True)
    attempt_number = Column(Integer, nullable=False)  # 1, 2, or 3
    attempt_status = Column(String(30), nullable=False, default="awaiting_response")  # awaiting_response, response_recorded, confirmed, analysed, completed
    
    # Stored exact presented instruction before child sees it
    presented_instruction = Column(Text, nullable=True)
    instruction_shown = Column(Text, nullable=True)  # legacy compatibility
    support_level = Column(String(20), nullable=False, default="moderate")  # mild, moderate, strong
    adaptation_strategy = Column(String(100), nullable=True)
    visual_cues = Column(JSON, nullable=True, default=list)
    vocabulary_cues = Column(JSON, nullable=True, default=list)
    generation_method = Column(String(50), nullable=False, default="curated")  # curated, rule_based, llm_generated, llm_generated_rule_validated, adult_revised
    validation_status = Column(String(30), nullable=False, default="approved")  # approved, fallback_used, reviewed
    
    # Response fields
    response_source = Column(String(50), nullable=False, default="adult_transcribed")  # adult_transcribed, manual_selection, child_direct_input, browser_speech
    manual_transcript = Column(Text, nullable=True)
    speech_transcript = Column(Text, nullable=True)  # legacy alias
    speech_confidence = Column(Float, nullable=True)  # null for adult_transcribed
    adult_confirmed = Column(Boolean, nullable=False, default=False)
    
    # Structured response capture
    selected_option = Column(Text, nullable=True)
    selected_answer = Column(JSON, nullable=True)  # legacy alias
    selected_items = Column(JSON, nullable=True, default=list)
    ordered_items = Column(JSON, nullable=True, default=list)
    
    # Performance & Status
    response_time_ms = Column(Integer, nullable=False, default=0)
    completion_status = Column(String(30), nullable=False, default="completed")  # completed, no_response, asked_for_help, skipped
    assistance_level = Column(String(30), nullable=False, default="independent")  # independent, prompted, visually_supported, modelled, fully_assisted
    independent_success = Column(Boolean, nullable=True)
    response_format_adjusted = Column(Boolean, nullable=False, default=False)
    original_response_mode = Column(String(50), nullable=True)
    current_response_mode = Column(String(50), nullable=True)
    
    # Automated Analysis Result
    target_skill = Column(String(100), nullable=True)
    concept_result = Column(String(30), nullable=False, default="unclear")  # correct, partial, incorrect, unclear
    target_skill_result = Column(String(30), nullable=True, default="not_applicable")  # correct, partial, incorrect, not_applicable
    grammar_observations = Column(JSON, nullable=False, default=list)
    vocabulary_observations = Column(JSON, nullable=False, default=list)
    retry_required = Column(Boolean, nullable=False, default=False)
    retry_reason = Column(String(100), nullable=True)
    automatic_analysis_snapshot = Column(JSON, nullable=True, default=dict)
    
    # Human Review & Final Decision
    final_concept_result = Column(String(30), nullable=True)
    final_target_skill_result = Column(String(30), nullable=True)
    final_retry_required = Column(Boolean, nullable=True)
    override_reason = Column(Text, nullable=True)
    reviewed_by_user_id = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    adult_interpretation = Column(String(30), nullable=True)  # legacy alias
    adult_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("attempt_number >= 1 AND attempt_number <= 3", name="ck_attempt_number_range"),
        CheckConstraint("response_time_ms >= 0", name="ck_attempt_response_time"),
    )

    experiment_run = relationship("ExperimentRun", back_populates="attempts")
    activity_session = relationship("ActivitySession", back_populates="attempts")
    adaptation = relationship("Adaptation", foreign_keys=[adaptation_id])
    observations = relationship("LanguageObservation", back_populates="attempt", cascade="all, delete-orphan")
    question_responses = relationship("QuestionResponse", back_populates="attempt", cascade="all, delete-orphan")


class QuestionResponse(Base):
    __tablename__ = "question_responses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    attempt_id = Column(String(36), ForeignKey("attempts.id"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("activity_questions.id"), nullable=False, index=True)
    manual_response = Column(Text, nullable=True)
    selected_option = Column(JSON, nullable=True)
    concept_result = Column(String(30), nullable=False, default="unclear")
    target_skill_result = Column(String(30), nullable=True, default="not_applicable")
    adult_confirmed = Column(Boolean, nullable=False, default=False)
    response_time_ms = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    attempt = relationship("Attempt", back_populates="question_responses")
    question = relationship("ActivityQuestion", back_populates="responses")


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    adaptation_id = Column(String(36), ForeignKey("adaptations.id"), nullable=False, index=True)
    validation_sequence = Column(Integer, nullable=False, default=1)
    generator_output_version = Column(Integer, nullable=False, default=1)
    candidate_output = Column(JSON, nullable=False, default=dict)
    language_valid = Column(Boolean, nullable=False, default=True)
    age_appropriate = Column(Boolean, nullable=False, default=True)
    meaning_preserved = Column(Boolean, nullable=False, default=True)
    answer_leakage = Column(Boolean, nullable=False, default=False)
    sentence_length_valid = Column(Boolean, nullable=False, default=True)
    support_level_valid = Column(Boolean, nullable=False, default=True)
    safety_valid = Column(Boolean, nullable=False, default=True)
    average_words_per_sentence = Column(Float, nullable=True)
    maximum_words_in_sentence = Column(Integer, nullable=True)
    semantic_score = Column(Float, nullable=True)
    status = Column(String(20), nullable=False, default="approved")  # approved, rejected, review_required
    failure_reasons = Column(JSON, nullable=False, default=list)
    is_final = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("adaptation_id", "validation_sequence", name="uq_validation_adaptation_sequence"),
    )

    adaptation = relationship("Adaptation", back_populates="validation_results")


class PerformancePattern(Base):
    __tablename__ = "performance_patterns"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    learner_id = Column(String(36), ForeignKey("learner_profiles.id"), nullable=False, index=True)
    pattern_type = Column(String(50), nullable=False)  # vocabulary, grammar, comprehension, instruction
    pattern_code = Column(String(100), nullable=False)
    frequency = Column(Integer, nullable=False, default=1)
    confidence = Column(Float, nullable=False, default=0.8)
    successful_support = Column(String(100), nullable=True)
    recommended_support = Column(String(20), nullable=False, default="moderate")  # mild, moderate, strong
    source = Column(String(50), nullable=False, default="manual_input_session")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_pattern_confidence"),
    )

    learner = relationship("LearnerProfile", back_populates="patterns")


class LanguageObservation(Base):
    __tablename__ = "language_observations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    attempt_id = Column(String(36), ForeignKey("attempts.id"), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # vocabulary, grammar, comprehension, instruction
    observation_code = Column(String(100), nullable=False)
    evidence = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True, default=0.8)
    confirmed = Column(Boolean, nullable=False, default=True)
    child_visible = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    attempt = relationship("Attempt", back_populates="observations")


class IntegrationEvent(Base):
    __tablename__ = "integration_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experiment_run_id = Column(String(36), ForeignKey("experiment_runs.id"), nullable=True, index=True)
    activity_session_id = Column(String(36), ForeignKey("activity_sessions.id"), nullable=True, index=True)
    attempt_id = Column(String(36), ForeignKey("attempts.id"), nullable=True)
    adaptation_id = Column(String(36), ForeignKey("adaptations.id"), nullable=True)
    target_component = Column(String(50), nullable=False)  # component_1, component_3_ar, component_4
    event_type = Column(String(100), nullable=False)
    schema_version = Column(String(20), nullable=False, default="1.0")
    payload = Column(JSON, nullable=False)
    delivery_status = Column(String(20), nullable=False, default="generated")  # generated, simulated, sent, failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    experiment_run = relationship("ExperimentRun", back_populates="integration_events")
    activity_session = relationship("ActivitySession", back_populates="integration_events")


class ExpertEvaluation(Base):
    __tablename__ = "expert_evaluations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    adaptation_id = Column(String(36), ForeignKey("adaptations.id"), nullable=False, index=True)
    evaluator_code = Column(String(50), nullable=False)
    age_appropriateness = Column(Integer, nullable=False)
    clarity = Column(Integer, nullable=False)
    grammar_correctness = Column(Integer, nullable=False)
    meaning_preservation = Column(Integer, nullable=False)
    personalization_suitability = Column(Integer, nullable=False)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("age_appropriateness >= 1 AND age_appropriateness <= 5", name="ck_eval_age"),
        CheckConstraint("clarity >= 1 AND clarity <= 5", name="ck_eval_clarity"),
        CheckConstraint("grammar_correctness >= 1 AND grammar_correctness <= 5", name="ck_eval_grammar"),
        CheckConstraint("meaning_preservation >= 1 AND meaning_preservation <= 5", name="ck_eval_meaning"),
        CheckConstraint("personalization_suitability >= 1 AND personalization_suitability <= 5", name="ck_eval_personalization"),
    )

    adaptation = relationship("Adaptation", back_populates="expert_evaluations")


class TaskResult(Base):
    """
    Immutable task outcome record automatically created whenever an ActivitySession
    reaches a terminal state (success, completed_with_adult_support, adult_support_required).
    Stores a full longitudinal snapshot of learner scores BEFORE and AFTER the session
    so educators can track skill progression task-by-task over time.
    """
    __tablename__ = "task_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)

    # Session & Learner Links
    session_id = Column(String(36), ForeignKey("activity_sessions.id"), nullable=True, index=True)
    learner_id = Column(String(36), ForeignKey("learner_profiles.id"), nullable=False, index=True)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)

    # Denormalized lookup fields (never change after creation)
    learner_code = Column(String(50), nullable=False, index=True)
    learner_age = Column(Integer, nullable=False)
    task_code = Column(String(50), nullable=False, index=True)
    task_title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)          # vocabulary | grammar | comprehension | sentence_and_instruction
    target_skill = Column(String(100), nullable=True)
    difficulty = Column(String(20), nullable=False, default="medium")  # easy | medium | hard

    # Session Outcome
    final_outcome = Column(String(50), nullable=False)     # success | completed_with_adult_support | adult_support_required
    attempts_count = Column(Integer, nullable=False, default=1)
    independent_success = Column(Boolean, nullable=False, default=False)

    # Score Snapshots (JSON objects with vocabulary_score, grammar_score, comprehension_score, instruction_following_score, risk_support_level, english_level)
    score_before = Column(JSON, nullable=False, default=dict)   # captured at session START
    score_after = Column(JSON, nullable=False, default=dict)    # captured AFTER profile update
    score_deltas = Column(JSON, nullable=False, default=dict)   # {vocabulary, grammar, comprehension, instruction}

    # Risk Recalibration
    risk_before = Column(String(20), nullable=True)             # e.g. "moderate"
    risk_after = Column(String(20), nullable=True)              # e.g. "high"
    risk_changed = Column(Boolean, nullable=False, default=False)
    composite_language_index = Column(Float, nullable=True)     # CLI after this session

    # Attempt-by-attempt history for educators
    attempt_history = Column(JSON, nullable=False, default=list)
    # Each entry: {attempt_number, instruction, transcript, selected_option, result, target_skill_result,
    #              assistance_level, response_time_ms, grammar_observations, vocabulary_observations}

    # Educational Summary
    diagnostic_notes = Column(Text, nullable=True)

    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    learner = relationship("LearnerProfile", back_populates="task_results")
    session = relationship("ActivitySession")
    task = relationship("Task")

