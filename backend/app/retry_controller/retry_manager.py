from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.database.models import (
    ExperimentRun, Attempt, Adaptation, IntegrationEvent, LanguageObservation, ValidationResult
)
from app.security.input_sanitizer import sanitize_text
from app.personalization.profile_updater import profile_updater
from app.response_analysis.answer_checker import answer_checker
from app.grammar_analysis.grammar_extractor import grammar_extractor
from app.response_analysis.language_extractor import language_extractor

class RetryManager:
    """
    Retry state machine controller for the 3-attempt progression.
    State transitions:
    - Attempt 1 (Initial Adaptation)
    - Attempt 2 (First Retry: single sub-step, +1 support level)
    - Attempt 3 (Final Retry: binary picture choice, strong support, pointing cues)
    - Post-Attempt 3 Escalation: Halts automated retries, displays non-punitive child reassurance,
      and emits comprehensive clinician diagnostic summary.
    """

    def process_attempt_response(
        self,
        db: Session,
        experiment_run_id: str,
        adaptation_id: str,
        speech_transcript: Optional[str] = None,
        speech_confidence: Optional[float] = 0.9,
        selected_answer: Optional[Dict[str, Any]] = None,
        response_time_ms: int = 5000,
        completion_status: str = "completed"
    ) -> Dict[str, Any]:
        """
        Executes an attempt transition:
        1. Evaluates concept correctness via AnswerChecker
        2. Gathers language and grammar observations
        3. Advances state machine (Success -> Completed, Failure -> Next Attempt or Adult Escalation)
        """
        # Late import to prevent circular dependency
        from app.services.adaptation_service import adaptation_service

        experiment = db.query(ExperimentRun).filter(ExperimentRun.id == experiment_run_id).first()
        if not experiment:
            raise ValueError(f"ExperimentRun '{experiment_run_id}' not found")

        adaptation = db.query(Adaptation).filter(Adaptation.id == adaptation_id).first()
        if not adaptation:
            raise ValueError(f"Adaptation '{adaptation_id}' not found")

        # Determine attempt number
        existing_attempts_count = db.query(Attempt).filter(Attempt.experiment_run_id == experiment_run_id).count()
        current_attempt_number = existing_attempts_count + 1

        if current_attempt_number > 3 or experiment.status in ["completed", "escalated"]:
            raise ValueError("Scenario has already ended (completed or escalated to adult support).")

        # Sanitize transcript
        clean_transcript = sanitize_text(speech_transcript, max_length=300) if speech_transcript else None
        conf = speech_confidence if speech_confidence is not None else 0.9

        # Evaluate concept result
        task = experiment.task
        learner = experiment.learner
        eval_res = answer_checker.evaluate_answer(task, clean_transcript, selected_answer)
        concept_result = eval_res["concept_result"]

        # Create Attempt record
        attempt = Attempt(
            experiment_run_id=experiment_run_id,
            adaptation_id=adaptation_id,
            attempt_number=current_attempt_number,
            instruction_shown=adaptation.child_instruction,
            speech_transcript=clean_transcript,
            speech_confidence=conf,
            selected_answer=selected_answer,
            concept_result=concept_result,
            response_time_ms=response_time_ms,
            completion_status=completion_status
        )
        db.add(attempt)
        db.flush()

        # Extract observations
        self._record_observations(db, attempt, clean_transcript, conf, task=task, learner=learner)

        # State transition logic
        next_adaptation = None
        escalation_payload = None

        if concept_result == "correct":
            experiment.status = "completed"
            experiment.completed_at = datetime.utcnow()
            experiment.final_outcome = "success"

            # Emit Component 4 success event
            self._emit_event(
                db, experiment_run_id, attempt.id, adaptation.id,
                target_component="component_4",
                event_type="progress_event",
                payload={
                    "learner_id": learner.learner_code,
                    "task_id": task.task_code,
                    "attempt_number": current_attempt_number,
                    "result": "correct",
                    "status": "completed",
                    "support_applied": [adaptation.support_level, adaptation.answer_format]
                }
            )
        else:
            # Unsuccessful attempt (incorrect, partial, unclear, or skipped)
            if current_attempt_number >= 3:
                # Escalation after 3 unsuccessful attempts
                experiment.status = "escalated"
                experiment.completed_at = datetime.utcnow()
                experiment.final_outcome = "adult_support"

                escalation_payload = self._build_adult_escalation_payload(db, experiment, attempt, adaptation)

                # Emit Component 1 adult escalation event
                self._emit_event(
                    db, experiment_run_id, attempt.id, adaptation.id,
                    target_component="component_1",
                    event_type="adult_escalation",
                    payload=escalation_payload
                )

                # Emit Component 4 diagnostic pattern event
                self._emit_event(
                    db, experiment_run_id, attempt.id, adaptation.id,
                    target_component="component_4",
                    event_type="diagnostic_pattern_event",
                    payload={
                        "learner_id": learner.learner_code,
                        "task_id": task.task_code,
                        "outcome": "adult_support",
                        "attempts_count": 3,
                        "diagnostic_notes": escalation_payload.get("researcher_summary", "")
                    }
                )
            else:
                # Trigger next adaptation (Attempt 2 or 3)
                next_target = current_attempt_number + 1
                next_adaptation = adaptation_service.create_retry_adaptation(
                    db=db,
                    experiment_run=experiment,
                    source_attempt=attempt,
                    target_attempt_number=next_target,
                    generation_mode=experiment.generation_mode
                )

        profile_update = None
        if experiment.status in ["completed", "escalated"]:
            obs = db.query(LanguageObservation).filter(LanguageObservation.attempt_id == attempt.id).all()
            grammar_err_count = len([o for o in obs if getattr(o, "category", None) == "grammar"])
            profile_update = profile_updater.update_profile_after_session(
                db=db,
                learner=learner,
                task=task,
                session_final_outcome=experiment.final_outcome,
                attempt_number=current_attempt_number,
                grammar_errors_count=grammar_err_count,
                assistance_level="independent"
            )

        db.commit()
        db.refresh(attempt)
        if next_adaptation:
            db.refresh(next_adaptation)

        return {
            "attempt": attempt,
            "next_adaptation": next_adaptation,
            "experiment_status": experiment.status,
            "final_outcome": experiment.final_outcome,
            "escalation_payload": escalation_payload,
            "profile_update": profile_update
        }

    def _build_adult_escalation_payload(
        self,
        db: Session,
        experiment: ExperimentRun,
        last_attempt: Attempt,
        last_adaptation: Adaptation
    ) -> Dict[str, Any]:
        """
        Builds dual escalation payload:
        - Child-facing message: Warm, positive, reassuring ('Let's ask your teacher or helper!')
        - Researcher / Clinician summary: Comprehensive diagnostic audit
        """
        all_attempts = db.query(Attempt).filter(Attempt.experiment_run_id == experiment.id).order_by(Attempt.attempt_number).all()

        attempt_history = []
        observed_grammar_errors = set()
        observed_vocab_issues = set()

        for att in all_attempts:
            attempt_history.append({
                "attempt_number": att.attempt_number,
                "instruction_shown": att.instruction_shown,
                "speech_transcript": att.speech_transcript,
                "confidence": att.speech_confidence,
                "concept_result": att.concept_result,
                "response_time_ms": att.response_time_ms
            })
            for obs in att.observations:
                if obs.category == "grammar":
                    observed_grammar_errors.add(obs.observation_code)
                elif obs.category == "vocabulary":
                    observed_vocab_issues.add(obs.observation_code)

        child_message = "Great effort! Let's ask your teacher or helper to look together!"

        researcher_summary = (
            f"Learner {experiment.learner.learner_code} completed {len(all_attempts)} attempts on task '{experiment.task.title}' ({experiment.task.task_code}). "
            f"Unresolved concept after attempt 3. "
            f"Detected grammar patterns: {list(observed_grammar_errors) or ['none']}. "
            f"Vocabulary patterns: {list(observed_vocab_issues) or ['none']}. "
            f"Recommended strategy: In-person 1-on-1 scaffolding with physical concrete manipulatives."
        )


        return {
            "task_id": experiment.task.task_code,
            "task_title": experiment.task.title,
            "learner_id": experiment.learner.learner_code,
            "attempt_count": len(all_attempts),
            "child_message": child_message,
            "child_visual_theme": "helper_hands",
            "researcher_summary": researcher_summary,
            "observed_grammar_patterns": list(observed_grammar_errors),
            "observed_vocabulary_patterns": list(observed_vocab_issues),
            "attempt_history": attempt_history,
            "status": "adult_support_requested"
        }

    def _record_observations(
        self,
        db: Session,
        attempt: Attempt,
        transcript: Optional[str],
        confidence: float,
        task: Any,
        learner: Any
    ):
        """Extracts grammar and vocabulary diagnostic observations."""
        if not transcript:
            return

        speech_conf = confidence if confidence is not None else 0.9

        # 1. Grammar analysis
        grammar_res = grammar_extractor.analyze_grammar(transcript, speech_confidence=speech_conf)
        for g_obs in grammar_res.get("observations", []):
            db.add(LanguageObservation(
                attempt_id=attempt.id,
                category=g_obs.get("category", "grammar"),
                observation_code=g_obs.get("observation_code", "grammar_error"),
                evidence=g_obs.get("evidence", transcript),
                confidence=g_obs.get("confidence", speech_conf),
                confirmed=g_obs.get("confirmed", False),
                child_visible=False
            ))

        # 2. Vocabulary & instruction drop-off analysis
        if task and learner:
            lang_obs_list = language_extractor.analyze_vocabulary_and_comprehension(
                transcript=transcript,
                task=task,
                learner_age=getattr(learner, "age", 6),
                concept_result=attempt.concept_result
            )
            for l_obs in lang_obs_list:
                db.add(LanguageObservation(
                    attempt_id=attempt.id,
                    category=l_obs.get("category", "vocabulary"),
                    observation_code=l_obs.get("observation_code", "vocabulary_difficulty"),
                    evidence=l_obs.get("evidence", transcript),
                    confidence=l_obs.get("confidence", 0.85),
                    confirmed=l_obs.get("confirmed", True),
                    child_visible=False
                ))

        db.flush()


    def _emit_event(
        self,
        db: Session,
        experiment_id: str,
        attempt_id: str,
        adaptation_id: str,
        target_component: str,
        event_type: str,
        payload: Dict[str, Any]
    ):
        event = IntegrationEvent(
            experiment_run_id=experiment_id,
            attempt_id=attempt_id,
            adaptation_id=adaptation_id,
            target_component=target_component,
            event_type=event_type,
            payload=payload,
            delivery_status="generated"
        )
        db.add(event)
        db.flush()


    def get_retry_state(self, db: Session, experiment_run_id: str) -> Dict[str, Any]:
        """Returns full state inspection for the experiment run."""
        experiment = db.query(ExperimentRun).filter(ExperimentRun.id == experiment_run_id).first()
        if not experiment:
            raise ValueError("ExperimentRun not found")

        attempts = db.query(Attempt).filter(Attempt.experiment_run_id == experiment_run_id).order_by(Attempt.attempt_number).all()
        adaptations = db.query(Adaptation).filter(Adaptation.experiment_run_id == experiment_run_id).order_by(Adaptation.target_attempt_number).all()

        validation_map = {}
        for ad in adaptations:
            val_results = db.query(ValidationResult).filter(ValidationResult.adaptation_id == ad.id).order_by(ValidationResult.validation_sequence).all()
            validation_map[ad.id] = [
                {
                    "sequence": v.validation_sequence,
                    "status": v.status,
                    "is_final": v.is_final,
                    "language_valid": v.language_valid,
                    "safety_valid": v.safety_valid,
                    "answer_leakage": v.answer_leakage,
                    "sentence_length_valid": v.sentence_length_valid,
                    "words_max": v.maximum_words_in_sentence,
                    "semantic_score": v.semantic_score,
                    "failure_reasons": v.failure_reasons,
                    "candidate_instruction": v.candidate_output.get("child_instruction") if isinstance(v.candidate_output, dict) else None
                }
                for v in val_results
            ]

        attempts_data = [
            {
                "id": a.id,
                "attempt_number": a.attempt_number,
                "adaptation_id": a.adaptation_id,
                "instruction_shown": a.instruction_shown,
                "transcript": a.speech_transcript,
                "confidence": a.speech_confidence,
                "concept_result": a.concept_result,
                "response_time_ms": a.response_time_ms,
                "observations": [
                    {
                        "category": o.category,
                        "code": o.observation_code,
                        "evidence": o.evidence,
                        "confirmed": o.confirmed
                    }
                    for o in a.observations
                ]
            }
            for a in attempts
        ]

        adaptations_data = [
            {
                "id": ad.id,
                "target_attempt_number": ad.target_attempt_number,
                "source_attempt_id": ad.source_attempt_id,
                "support_level": ad.support_level,
                "child_instruction": ad.child_instruction,
                "supportive_message": ad.supportive_message,
                "answer_format": ad.answer_format,
                "visual_cues": ad.visual_cues,
                "reason_codes": ad.reason_codes,
                "validation_sequences": validation_map.get(ad.id, [])
            }
            for ad in adaptations
        ]

        can_retry = experiment.status == "active" and len(attempts) < 3
        next_attempt_number = (len(attempts) + 1) if can_retry else None

        escalation_info = None
        if experiment.status == "escalated":
            # Retrieve the latest escalation event payload if present
            esc_event = db.query(IntegrationEvent).filter(
                IntegrationEvent.experiment_run_id == experiment_run_id,
                IntegrationEvent.event_type == "adult_escalation"
            ).order_by(IntegrationEvent.created_at.desc()).first()
            if esc_event:
                escalation_info = esc_event.payload
            else:
                last_att = attempts[-1] if attempts else None
                last_ad = adaptations[-1] if adaptations else None
                if last_att and last_ad:
                    escalation_info = self._build_adult_escalation_payload(db, experiment, last_att, last_ad)

        return {
            "experiment_id": experiment.id,
            "status": experiment.status,
            "final_outcome": experiment.final_outcome,
            "task_code": experiment.task.task_code,
            "task_title": experiment.task.title,
            "learner_code": experiment.learner.learner_code,
            "attempts_count": len(attempts),
            "can_retry": can_retry,
            "next_attempt_number": next_attempt_number,
            "attempts": attempts_data,
            "adaptations": adaptations_data,
            "escalation_info": escalation_info
        }

retry_manager = RetryManager()
