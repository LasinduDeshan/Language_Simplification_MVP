import time
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.database.models import (
    Adaptation, ValidationResult, Task, LearnerProfile, ExperimentRun, Attempt, IntegrationEvent
)
from app.tasks.repository import task_repository
from app.personalization.controller import personalization_controller
from app.generation.rule_generator import rule_generator
from app.validation.validator import adaptation_validator

class AdaptationService:
    """
    Orchestration service for generating personalized, child-friendly task adaptations.
    Coordinates between PersonalizationController (support level & reasons),
    Generator engines (RuleGenerator, LLM/Hybrid generators), and
    AdaptationValidator (relation-aware leakage, safety, suitability, length).
    """

    def determine_support_level(
        self,
        learner: LearnerProfile,
        target_attempt_number: int,
        previous_observations: Optional[List[Dict[str, Any]]] = None,
        component_4_recommendation: Optional[str] = None
    ) -> str:
        """Determines support intensity: mild, moderate, or strong."""
        res = personalization_controller.determine_support_level(
            learner=learner,
            target_attempt_number=target_attempt_number,
            previous_observations=previous_observations,
            component_4_recommendation=component_4_recommendation
        )
        return res["support_level"]

    def determine_support_details(
        self,
        learner: LearnerProfile,
        target_attempt_number: int,
        previous_observations: Optional[List[Dict[str, Any]]] = None,
        component_4_recommendation: Optional[str] = None
    ) -> Dict[str, Any]:
        """Returns full support evaluation including base support and explainable reason codes."""
        return personalization_controller.determine_support_level(
            learner=learner,
            target_attempt_number=target_attempt_number,
            previous_observations=previous_observations,
            component_4_recommendation=component_4_recommendation
        )

    def generate_child_friendly_instruction(
        self,
        task: Task,
        learner: LearnerProfile,
        target_attempt_number: int,
        support_level: str,
        generation_mode: str = "rule",
        previous_attempt: Optional[Attempt] = None,
        previous_observations: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generates child-friendly instruction payload with length enforcement (<= 8-10 words target),
        vocabulary replacement, visual cues, and supportive phrasing.
        """
        return rule_generator.generate(
            task=task,
            learner=learner,
            target_attempt_number=target_attempt_number,
            support_level=support_level,
            previous_attempt=previous_attempt,
            previous_observations=previous_observations
        )

    def create_initial_adaptation(
        self,
        db: Session,
        experiment_run: ExperimentRun,
        generation_mode: str = "rule",
        candidate_override: Optional[Dict[str, Any]] = None
    ) -> Adaptation:
        """
        Creates the initial adaptation BEFORE Attempt 1.
        source_attempt_id is NULL.
        Validates candidate output: if candidate is rejected, logs sequence 1 as rejected
        and falls back to safe rule template (sequence 2, approved).
        """
        start_time = time.time()
        learner = experiment_run.learner
        task = experiment_run.task

        # 1. Resolve support level and reason codes
        support_details = personalization_controller.determine_support_level(
            learner, target_attempt_number=1
        )
        support_level = support_details["support_level"]

        # 2. Candidate generation (uses candidate_override if supplied, otherwise generator)
        if candidate_override:
            gen_data = candidate_override
        else:
            gen_data = self.generate_child_friendly_instruction(
                task=task,
                learner=learner,
                target_attempt_number=1,
                support_level=support_level,
                generation_mode=generation_mode
            )

        combined_reason_codes = list(dict.fromkeys(support_details["reason_codes"] + gen_data.get("reason_codes", [])))
        gen_data["reason_codes"] = combined_reason_codes

        # 3. Validate Candidate (Sequence 1)
        val_eval = adaptation_validator.validate_candidate(task, gen_data, learner)
        elapsed_ms = int((time.time() - start_time) * 1000)

        # Check if candidate passed or requires fallback
        if val_eval["status"] == "approved":
            # Approved on Sequence 1
            adaptation = Adaptation(
                experiment_run_id=experiment_run.id,
                source_attempt_id=None,
                target_attempt_number=1,
                support_level=support_level,
                generation_method=generation_mode,
                child_instruction=gen_data["child_instruction"],
                supportive_message=gen_data.get("supportive_message"),
                vocabulary_support=gen_data.get("vocabulary_support", []),
                answer_format=gen_data.get("answer_format", "speech"),
                visual_cues=gen_data.get("visual_cues", []),
                reason_codes=combined_reason_codes,
                provider="local_template",
                model_name="rule_engine_v1" if generation_mode == "rule" else f"{generation_mode}_engine",
                processing_time_ms=elapsed_ms,
                estimated_cost=0.0
            )
            db.add(adaptation)
            db.flush()

            val_result = ValidationResult(
                adaptation_id=adaptation.id,
                validation_sequence=1,
                generator_output_version=1,
                candidate_output=gen_data,
                language_valid=val_eval["language_valid"],
                age_appropriate=val_eval["age_appropriate"],
                meaning_preserved=val_eval["meaning_preserved"],
                answer_leakage=val_eval["answer_leakage"],
                sentence_length_valid=val_eval["sentence_length_valid"],
                support_level_valid=val_eval["support_level_valid"],
                safety_valid=val_eval["safety_valid"],
                average_words_per_sentence=val_eval["average_words_per_sentence"],
                maximum_words_in_sentence=val_eval["maximum_words_in_sentence"],
                semantic_score=val_eval["semantic_score"],
                status="approved",
                failure_reasons=val_eval["failure_reasons"],
                is_final=True
            )
            db.add(val_result)
        else:
            # Candidate REJECTED -> Sequence 1 rejected, Fallback to safe rule template on Sequence 2
            safe_fallback = rule_generator.generate(
                task=task,
                learner=learner,
                target_attempt_number=1,
                support_level=support_level
            )
            fallback_reasons = list(dict.fromkeys(support_details["reason_codes"] + safe_fallback.get("reason_codes", []) + ["fallback_safe_rule_applied"]))
            safe_fallback["reason_codes"] = fallback_reasons

            fallback_val = adaptation_validator.validate_candidate(task, safe_fallback, learner)

            adaptation = Adaptation(
                experiment_run_id=experiment_run.id,
                source_attempt_id=None,
                target_attempt_number=1,
                support_level=support_level,
                generation_method="fallback",
                child_instruction=safe_fallback["child_instruction"],
                supportive_message=safe_fallback.get("supportive_message"),
                vocabulary_support=safe_fallback.get("vocabulary_support", []),
                answer_format=safe_fallback.get("answer_format", "speech"),
                visual_cues=safe_fallback.get("visual_cues", []),
                reason_codes=fallback_reasons,
                provider="local_fallback_template",
                model_name="rule_fallback_v1",
                processing_time_ms=elapsed_ms,
                estimated_cost=0.0
            )
            db.add(adaptation)
            db.flush()

            # Sequence 1: Rejected candidate
            val_result_seq1 = ValidationResult(
                adaptation_id=adaptation.id,
                validation_sequence=1,
                generator_output_version=1,
                candidate_output=gen_data,
                language_valid=val_eval["language_valid"],
                age_appropriate=val_eval["age_appropriate"],
                meaning_preserved=val_eval["meaning_preserved"],
                answer_leakage=val_eval["answer_leakage"],
                sentence_length_valid=val_eval["sentence_length_valid"],
                support_level_valid=val_eval["support_level_valid"],
                safety_valid=val_eval["safety_valid"],
                average_words_per_sentence=val_eval["average_words_per_sentence"],
                maximum_words_in_sentence=val_eval["maximum_words_in_sentence"],
                semantic_score=val_eval["semantic_score"],
                status="rejected",
                failure_reasons=val_eval["failure_reasons"],
                is_final=False
            )
            db.add(val_result_seq1)

            # Sequence 2: Approved fallback
            val_result_seq2 = ValidationResult(
                adaptation_id=adaptation.id,
                validation_sequence=2,
                generator_output_version=2,
                candidate_output=safe_fallback,
                language_valid=fallback_val["language_valid"],
                age_appropriate=fallback_val["age_appropriate"],
                meaning_preserved=fallback_val["meaning_preserved"],
                answer_leakage=fallback_val["answer_leakage"],
                sentence_length_valid=fallback_val["sentence_length_valid"],
                support_level_valid=fallback_val["support_level_valid"],
                safety_valid=fallback_val["safety_valid"],
                average_words_per_sentence=fallback_val["average_words_per_sentence"],
                maximum_words_in_sentence=fallback_val["maximum_words_in_sentence"],
                semantic_score=fallback_val["semantic_score"],
                status="approved",
                failure_reasons=fallback_val["failure_reasons"],
                is_final=True
            )
            db.add(val_result_seq2)

        db.commit()
        db.refresh(adaptation)
        return adaptation

    def create_retry_adaptation(
        self,
        db: Session,
        experiment_run: ExperimentRun,
        source_attempt: Attempt,
        target_attempt_number: int,
        generation_mode: str = "rule",
        candidate_override: Optional[Dict[str, Any]] = None
    ) -> Adaptation:
        """
        Creates a retry adaptation (Attempts 2 or 3) linked to the previous attempt.
        Validates candidate output: if candidate is rejected, logs sequence 1 as rejected
        and falls back to safe rule template (sequence 2, approved).
        """
        start_time = time.time()
        learner = experiment_run.learner
        task = experiment_run.task

        # Gather previous observations
        prev_obs = [
            {"observation_code": o.observation_code, "category": o.category}
            for o in source_attempt.observations
        ] if hasattr(source_attempt, "observations") and source_attempt.observations else []

        # 1. Resolve escalated support level and reason codes
        support_details = personalization_controller.determine_support_level(
            learner=learner,
            target_attempt_number=target_attempt_number,
            previous_observations=prev_obs
        )
        support_level = support_details["support_level"]

        # 2. Candidate generation
        if candidate_override:
            gen_data = candidate_override
        else:
            gen_data = self.generate_child_friendly_instruction(
                task=task,
                learner=learner,
                target_attempt_number=target_attempt_number,
                support_level=support_level,
                generation_mode=generation_mode,
                previous_attempt=source_attempt,
                previous_observations=prev_obs
            )

        combined_reason_codes = list(dict.fromkeys(support_details["reason_codes"] + gen_data.get("reason_codes", [])))
        gen_data["reason_codes"] = combined_reason_codes

        # 3. Validate Candidate (Sequence 1)
        val_eval = adaptation_validator.validate_candidate(task, gen_data, learner)
        elapsed_ms = int((time.time() - start_time) * 1000)

        if val_eval["status"] == "approved":
            adaptation = Adaptation(
                experiment_run_id=experiment_run.id,
                source_attempt_id=source_attempt.id,
                target_attempt_number=target_attempt_number,
                support_level=support_level,
                generation_method=generation_mode,
                child_instruction=gen_data["child_instruction"],
                supportive_message=gen_data.get("supportive_message"),
                vocabulary_support=gen_data.get("vocabulary_support", []),
                answer_format=gen_data.get("answer_format", "speech"),
                visual_cues=gen_data.get("visual_cues", []),
                reason_codes=combined_reason_codes,
                provider="local_template",
                model_name="rule_engine_v1" if generation_mode == "rule" else f"{generation_mode}_engine",
                processing_time_ms=elapsed_ms,
                estimated_cost=0.0
            )
            db.add(adaptation)
            db.flush()

            val_result = ValidationResult(
                adaptation_id=adaptation.id,
                validation_sequence=1,
                generator_output_version=1,
                candidate_output=gen_data,
                language_valid=val_eval["language_valid"],
                age_appropriate=val_eval["age_appropriate"],
                meaning_preserved=val_eval["meaning_preserved"],
                answer_leakage=val_eval["answer_leakage"],
                sentence_length_valid=val_eval["sentence_length_valid"],
                support_level_valid=val_eval["support_level_valid"],
                safety_valid=val_eval["safety_valid"],
                average_words_per_sentence=val_eval["average_words_per_sentence"],
                maximum_words_in_sentence=val_eval["maximum_words_in_sentence"],
                semantic_score=val_eval["semantic_score"],
                status="approved",
                failure_reasons=val_eval["failure_reasons"],
                is_final=True
            )
            db.add(val_result)
        else:
            # Candidate REJECTED -> Fallback to safe rule template
            safe_fallback = rule_generator.generate(
                task=task,
                learner=learner,
                target_attempt_number=target_attempt_number,
                support_level=support_level,
                previous_attempt=source_attempt,
                previous_observations=prev_obs
            )
            fallback_reasons = list(dict.fromkeys(support_details["reason_codes"] + safe_fallback.get("reason_codes", []) + ["fallback_safe_rule_applied"]))
            safe_fallback["reason_codes"] = fallback_reasons

            fallback_val = adaptation_validator.validate_candidate(task, safe_fallback, learner)

            adaptation = Adaptation(
                experiment_run_id=experiment_run.id,
                source_attempt_id=source_attempt.id,
                target_attempt_number=target_attempt_number,
                support_level=support_level,
                generation_method="fallback",
                child_instruction=safe_fallback["child_instruction"],
                supportive_message=safe_fallback.get("supportive_message"),
                vocabulary_support=safe_fallback.get("vocabulary_support", []),
                answer_format=safe_fallback.get("answer_format", "speech"),
                visual_cues=safe_fallback.get("visual_cues", []),
                reason_codes=fallback_reasons,
                provider="local_fallback_template",
                model_name="rule_fallback_v1",
                processing_time_ms=elapsed_ms,
                estimated_cost=0.0
            )
            db.add(adaptation)
            db.flush()

            val_result_seq1 = ValidationResult(
                adaptation_id=adaptation.id,
                validation_sequence=1,
                generator_output_version=1,
                candidate_output=gen_data,
                language_valid=val_eval["language_valid"],
                age_appropriate=val_eval["age_appropriate"],
                meaning_preserved=val_eval["meaning_preserved"],
                answer_leakage=val_eval["answer_leakage"],
                sentence_length_valid=val_eval["sentence_length_valid"],
                support_level_valid=val_eval["support_level_valid"],
                safety_valid=val_eval["safety_valid"],
                average_words_per_sentence=val_eval["average_words_per_sentence"],
                maximum_words_in_sentence=val_eval["maximum_words_in_sentence"],
                semantic_score=val_eval["semantic_score"],
                status="rejected",
                failure_reasons=val_eval["failure_reasons"],
                is_final=False
            )
            db.add(val_result_seq1)

            val_result_seq2 = ValidationResult(
                adaptation_id=adaptation.id,
                validation_sequence=2,
                generator_output_version=2,
                candidate_output=safe_fallback,
                language_valid=fallback_val["language_valid"],
                age_appropriate=fallback_val["age_appropriate"],
                meaning_preserved=fallback_val["meaning_preserved"],
                answer_leakage=fallback_val["answer_leakage"],
                sentence_length_valid=fallback_val["sentence_length_valid"],
                support_level_valid=fallback_val["support_level_valid"],
                safety_valid=fallback_val["safety_valid"],
                average_words_per_sentence=fallback_val["average_words_per_sentence"],
                maximum_words_in_sentence=fallback_val["maximum_words_in_sentence"],
                semantic_score=fallback_val["semantic_score"],
                status="approved",
                failure_reasons=fallback_val["failure_reasons"],
                is_final=True
            )
            db.add(val_result_seq2)

        db.commit()
        db.refresh(adaptation)
        return adaptation

adaptation_service = AdaptationService()
