from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import (
    ExperimentRun, Attempt, Adaptation, IntegrationEvent, LanguageObservation
)
from app.services.adaptation_service import adaptation_service
from app.security.input_sanitizer import sanitize_text
from app.response_analysis.answer_checker import answer_checker
from app.grammar_analysis.grammar_extractor import grammar_extractor
from app.response_analysis.language_extractor import language_extractor


class ExperimentService:
    def create_experiment_run(
        self,
        db: Session,
        learner_id: str,
        task_id: str,
        generation_mode: str = "rule"
    ) -> ExperimentRun:
        experiment = ExperimentRun(
            learner_id=learner_id,
            task_id=task_id,
            generation_mode=generation_mode,
            status="active"
        )
        db.add(experiment)
        db.commit()
        db.refresh(experiment)
        return experiment

    def record_attempt(
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
        Records child response for the attempt, checks concept match, and triggers
        the next adaptation or escalates to adult support if max attempts (3) is reached.
        """
        experiment = db.query(ExperimentRun).filter(ExperimentRun.id == experiment_run_id).first()
        if not experiment:
            raise ValueError("ExperimentRun not found")

        adaptation = db.query(Adaptation).filter(Adaptation.id == adaptation_id).first()
        if not adaptation:
            raise ValueError("Adaptation not found")

        # Determine attempt number
        existing_attempts_count = db.query(Attempt).filter(Attempt.experiment_run_id == experiment_run_id).count()
        current_attempt_number = existing_attempts_count + 1

        if current_attempt_number > 3:
            raise ValueError("Maximum of 3 attempts exceeded. Scenario already escalated.")

        # Sanitize transcript
        clean_transcript = sanitize_text(speech_transcript, max_length=300) if speech_transcript else None

        # Determine concept correctness (Exact / acceptable answer check)
        task = experiment.task
        concept_result = self._evaluate_concept(task, clean_transcript, selected_answer)

        # Create Attempt record with required adaptation_id
        attempt = Attempt(
            experiment_run_id=experiment_run_id,
            adaptation_id=adaptation_id,
            attempt_number=current_attempt_number,
            instruction_shown=adaptation.child_instruction,
            speech_transcript=clean_transcript,
            speech_confidence=speech_confidence,
            selected_answer=selected_answer,
            concept_result=concept_result,
            response_time_ms=response_time_ms,
            completion_status=completion_status
        )
        db.add(attempt)
        db.flush()

        # Extract language observations
        self._record_observations(db, attempt, clean_transcript, speech_confidence, task=task, learner=experiment.learner)

        # State transitions
        next_adaptation = None
        if concept_result == "correct":
            experiment.status = "completed"
            experiment.completed_at = datetime.utcnow()
            experiment.final_outcome = "success"
            
            # Emit Component 4 success progress event
            self._emit_integration_event(
                db, experiment_run_id, attempt.id, adaptation.id,
                target_component="component_4",
                event_type="progress_event",
                payload={
                    "learner_id": experiment.learner.learner_code,
                    "task_id": task.task_code,
                    "attempt_number": current_attempt_number,
                    "result": "correct",
                    "status": "completed",
                    "support_applied": [adaptation.support_level, adaptation.answer_format]
                }
            )
        else:
            if current_attempt_number >= 3:
                # Escalate to adult support after attempt 3
                experiment.status = "escalated"
                experiment.completed_at = datetime.utcnow()
                experiment.final_outcome = "adult_support"
                
                # Emit Component 1 adult assistance payload
                self._emit_integration_event(
                    db, experiment_run_id, attempt.id, adaptation.id,
                    target_component="component_1",
                    event_type="adult_escalation",
                    payload={
                        "task_id": task.task_code,
                        "attempt_number": current_attempt_number,
                        "escalation_message": "Let's ask your teacher or helper to look together!",
                        "status": "adult_support_requested"
                    }
                )
            else:
                # Trigger next adaptation (target attempt 2 or 3)
                next_target = current_attempt_number + 1
                next_adaptation = adaptation_service.create_retry_adaptation(
                    db, experiment, source_attempt=attempt, target_attempt_number=next_target,
                    generation_mode=experiment.generation_mode
                )

        db.commit()
        db.refresh(attempt)
        if next_adaptation:
            db.refresh(next_adaptation)

        return {
            "attempt": attempt,
            "next_adaptation": next_adaptation,
            "experiment_status": experiment.status,
            "final_outcome": experiment.final_outcome
        }

    def _evaluate_concept(self, task, transcript: Optional[str], selected_answer: Optional[Dict[str, Any]]) -> str:
        eval_res = answer_checker.evaluate_answer(task, transcript, selected_answer)
        return eval_res["concept_result"]

    def _record_observations(self, db: Session, attempt: Attempt, transcript: Optional[str], confidence: Optional[float], task=None, learner=None):
        if not transcript:
            return

        speech_conf = confidence if confidence is not None else 0.9

        # 1. Grammar error extraction using spaCy and custom rules
        grammar_res = grammar_extractor.analyze_grammar(transcript, speech_confidence=speech_conf)
        for g_obs in grammar_res.get("observations", []):
            db.add(LanguageObservation(
                attempt_id=attempt.id,
                category=g_obs["category"],
                observation_code=g_obs["observation_code"],
                evidence=g_obs.get("evidence", transcript),
                confidence=g_obs.get("confidence", speech_conf),
                confirmed=g_obs.get("confirmed", False),
                child_visible=False
            ))

        # 2. Vocabulary difficulty & comprehension extraction
        if task and learner:
            lang_obs_list = language_extractor.analyze_vocabulary_and_comprehension(
                transcript=transcript,
                task=task,
                learner_age=learner.age,
                concept_result=attempt.concept_result
            )
            for l_obs in lang_obs_list:
                db.add(LanguageObservation(
                    attempt_id=attempt.id,
                    category=l_obs["category"],
                    observation_code=l_obs["observation_code"],
                    evidence=l_obs.get("evidence", transcript),
                    confidence=l_obs.get("confidence", 0.9),
                    confirmed=l_obs.get("confirmed", True),
                    child_visible=False
                ))


    def _emit_integration_event(
        self, db: Session, experiment_run_id: str, attempt_id: str, adaptation_id: str,
        target_component: str, event_type: str, payload: Dict[str, Any]
    ):
        event = IntegrationEvent(
            experiment_run_id=experiment_run_id,
            attempt_id=attempt_id,
            adaptation_id=adaptation_id,
            target_component=target_component,
            event_type=event_type,
            schema_version="1.0",
            payload=payload,
            delivery_status="generated"
        )
        db.add(event)

experiment_service = ExperimentService()
