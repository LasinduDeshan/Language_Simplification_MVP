from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import ExperimentRun
from app.retry_controller.retry_manager import retry_manager

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
        Delegates attempt recording, concept evaluation, observation extraction,
        and retry state machine progression to RetryManager.
        """
        return retry_manager.process_attempt_response(
            db=db,
            experiment_run_id=experiment_run_id,
            adaptation_id=adaptation_id,
            speech_transcript=speech_transcript,
            speech_confidence=speech_confidence,
            selected_answer=selected_answer,
            response_time_ms=response_time_ms,
            completion_status=completion_status
        )

experiment_service = ExperimentService()
