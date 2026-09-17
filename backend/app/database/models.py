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
    patterns = relationship("PerformancePattern", back_populates="learner", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    task_type = Column(String(50), nullable=False)  # vocabulary, grammar, categorization, comprehension, ar, classroom, sequence
    language = Column(String(10), nullable=False, default="en")
    learning_objective = Column(Text, nullable=False)
    original_instruction = Column(Text, nullable=False)
    minimum_age = Column(Integer, nullable=False, default=4)
    maximum_age = Column(Integer, nullable=False, default=8)
    base_difficulty = Column(String(20), nullable=False, default="medium")  # easy, medium, hard
    expected_concepts = Column(JSON, nullable=False, default=list)
    acceptable_answers = Column(JSON, nullable=False, default=list)
    protected_answers = Column(JSON, nullable=False, default=dict)
    answer_presentation_policy = Column(JSON, nullable=True, default=dict)
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


class ExperimentRun(Base):
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
    experiment_run_id = Column(String(36), ForeignKey("experiment_runs.id"), nullable=False, index=True)
    source_attempt_id = Column(String(36), ForeignKey("attempts.id", use_alter=True, name="fk_adaptation_source_attempt"), nullable=True)
    target_attempt_number = Column(Integer, nullable=False)  # 1, 2, or 3
    support_level = Column(String(20), nullable=False)  # mild, moderate, strong
    generation_method = Column(String(20), nullable=False)  # rule, llm, fallback
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

    __table_args__ = (
        CheckConstraint("target_attempt_number >= 1 AND target_attempt_number <= 3", name="ck_adaptation_target_attempt"),
        CheckConstraint("processing_time_ms >= 0", name="ck_adaptation_proc_time"),
        CheckConstraint("estimated_cost >= 0", name="ck_adaptation_cost"),
        UniqueConstraint("experiment_run_id", "target_attempt_number", name="uq_adaptation_run_target_attempt"),
    )

    experiment_run = relationship("ExperimentRun", back_populates="adaptations")
    validation_results = relationship("ValidationResult", back_populates="adaptation", cascade="all, delete-orphan")
    expert_evaluations = relationship("ExpertEvaluation", back_populates="adaptation", cascade="all, delete-orphan")


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experiment_run_id = Column(String(36), ForeignKey("experiment_runs.id"), nullable=False, index=True)
    adaptation_id = Column(String(36), ForeignKey("adaptations.id"), nullable=False, index=True)
    attempt_number = Column(Integer, nullable=False)  # 1, 2, or 3
    instruction_shown = Column(Text, nullable=False)
    speech_transcript = Column(Text, nullable=True)
    speech_confidence = Column(Float, nullable=True)
    selected_answer = Column(JSON, nullable=True)
    concept_result = Column(String(20), nullable=False, default="unclear")  # correct, partial, incorrect, unclear
    response_time_ms = Column(Integer, nullable=False, default=0)
    completion_status = Column(String(20), nullable=False, default="completed")  # completed, skipped, incomplete
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("attempt_number >= 1 AND attempt_number <= 3", name="ck_attempt_number_range"),
        CheckConstraint("speech_confidence >= 0 AND speech_confidence <= 1", name="ck_attempt_speech_conf"),
        CheckConstraint("response_time_ms >= 0", name="ck_attempt_response_time"),
        UniqueConstraint("experiment_run_id", "attempt_number", name="uq_attempt_run_number"),
    )

    experiment_run = relationship("ExperimentRun", back_populates="attempts")
    adaptation = relationship("Adaptation", foreign_keys=[adaptation_id])
    observations = relationship("LanguageObservation", back_populates="attempt", cascade="all, delete-orphan")


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
    source = Column(String(50), nullable=False, default="simulator_component_4")
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
    confidence = Column(Float, nullable=False, default=0.8)
    confirmed = Column(Boolean, nullable=False, default=True)
    child_visible = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_obs_confidence"),
    )

    attempt = relationship("Attempt", back_populates="observations")


class IntegrationEvent(Base):
    __tablename__ = "integration_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experiment_run_id = Column(String(36), ForeignKey("experiment_runs.id"), nullable=False, index=True)
    attempt_id = Column(String(36), ForeignKey("attempts.id"), nullable=True)
    adaptation_id = Column(String(36), ForeignKey("adaptations.id"), nullable=True)
    target_component = Column(String(50), nullable=False)  # component_1, component_3_ar, component_4
    event_type = Column(String(100), nullable=False)
    schema_version = Column(String(20), nullable=False, default="1.0")
    payload = Column(JSON, nullable=False)
    delivery_status = Column(String(20), nullable=False, default="simulated")  # generated, simulated, sent, failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    experiment_run = relationship("ExperimentRun", back_populates="integration_events")


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
