import csv
import io
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.database.models import (
    ExpertEvaluation, ExperimentRun, Adaptation, Attempt, ValidationResult, Task, LearnerProfile
)

class EvaluationService:
    def submit_expert_evaluation(
        self,
        db: Session,
        adaptation_id: str,
        evaluator_code: str,
        age_appropriateness: int,
        clarity: int,
        grammar_correctness: int,
        meaning_preservation: int,
        personalization_suitability: int,
        comments: Optional[str] = None
    ) -> ExpertEvaluation:
        eval_record = ExpertEvaluation(
            adaptation_id=adaptation_id,
            evaluator_code=evaluator_code,
            age_appropriateness=age_appropriateness,
            clarity=clarity,
            grammar_correctness=grammar_correctness,
            meaning_preservation=meaning_preservation,
            personalization_suitability=personalization_suitability,
            comments=comments
        )
        db.add(eval_record)
        db.commit()
        db.refresh(eval_record)
        return eval_record

    def get_component_1_payload(self, db: Session, experiment_id: str) -> Dict[str, Any]:
        experiment = db.query(ExperimentRun).filter(ExperimentRun.id == experiment_id).first()
        if not experiment:
            return {}

        latest_adaptation = db.query(Adaptation).filter(
            Adaptation.experiment_run_id == experiment_id
        ).order_by(Adaptation.target_attempt_number.desc()).first()

        if not latest_adaptation:
            return {}

        return {
            "task_id": experiment.task.task_code,
            "attempt_number": latest_adaptation.target_attempt_number,
            "support_level": latest_adaptation.support_level,
            "child_instruction": latest_adaptation.child_instruction,
            "supportive_message": latest_adaptation.supportive_message,
            "answer_format": latest_adaptation.answer_format or "speech",
            "cues": latest_adaptation.visual_cues or [],
            "do_not_reveal_answer": True,
            "validation_status": "approved_for_simulation"
        }

    def get_component_4_payload(self, db: Session, experiment_id: str) -> Dict[str, Any]:
        experiment = db.query(ExperimentRun).filter(ExperimentRun.id == experiment_id).first()
        if not experiment:
            return {}

        latest_attempt = db.query(Attempt).filter(
            Attempt.experiment_run_id == experiment_id
        ).order_by(Attempt.attempt_number.desc()).first()

        latest_adaptation = db.query(Adaptation).filter(
            Adaptation.experiment_run_id == experiment_id
        ).order_by(Adaptation.target_attempt_number.desc()).first()

        attempt_num = latest_attempt.attempt_number if latest_attempt else 1
        result_str = latest_attempt.concept_result if latest_attempt else "in_progress"

        observed_patterns = []
        if latest_attempt and latest_attempt.observations:
            observed_patterns = [obs.observation_code for obs in latest_attempt.observations]

        return {
            "learner_id": experiment.learner.learner_code,
            "task_id": experiment.task.task_code,
            "attempt_number": attempt_num,
            "result": result_str,
            "observed_patterns": observed_patterns,
            "support_applied": [latest_adaptation.support_level] if latest_adaptation else ["mild"],
            "next_recommendation": f"continue_{latest_adaptation.support_level}_support" if latest_adaptation else "continue_support"
        }

    def get_ar_payload(self, db: Session, experiment_id: str) -> Dict[str, Any]:
        experiment = db.query(ExperimentRun).filter(ExperimentRun.id == experiment_id).first()
        if not experiment:
            return {}

        task = experiment.task
        latest_adaptation = db.query(Adaptation).filter(
            Adaptation.experiment_run_id == experiment_id
        ).order_by(Adaptation.target_attempt_number.desc()).first()

        child_instruction = latest_adaptation.child_instruction if latest_adaptation else task.original_instruction
        support_level = latest_adaptation.support_level if latest_adaptation else "mild"
        ar_meta = task.ar_metadata or {}

        return {
            "task_id": task.task_code,
            "language": "en",
            "child_instruction": child_instruction,
            "object_labels": ar_meta.get("object_labels", ["object_1", "object_2"]),
            "vocabulary_support": latest_adaptation.vocabulary_support if latest_adaptation else [],
            "audio_text": child_instruction,
            "interaction_type": ar_meta.get("interaction_type", "drag_and_drop"),
            "support_level": support_level
        }

    def export_experiments_json(self, db: Session) -> List[Dict[str, Any]]:
        experiments = db.query(ExperimentRun).all()
        results = []
        for exp in experiments:
            attempts_data = [
                {
                    "attempt_number": a.attempt_number,
                    "transcript": a.speech_transcript,
                    "confidence": a.speech_confidence,
                    "concept_result": a.concept_result,
                    "response_time_ms": a.response_time_ms
                }
                for a in exp.attempts
            ]
            adaptations_data = [
                {
                    "target_attempt": ad.target_attempt_number,
                    "support_level": ad.support_level,
                    "generation_method": ad.generation_method,
                    "instruction": ad.child_instruction
                }
                for ad in exp.adaptations
            ]
            results.append({
                "experiment_id": exp.id,
                "learner_code": exp.learner.learner_code,
                "task_code": exp.task.task_code,
                "generation_mode": exp.generation_mode,
                "status": exp.status,
                "final_outcome": exp.final_outcome,
                "started_at": exp.started_at.isoformat() if exp.started_at else None,
                "completed_at": exp.completed_at.isoformat() if exp.completed_at else None,
                "attempts": attempts_data,
                "adaptations": adaptations_data
            })
        return results

    def export_experiments_csv(self, db: Session) -> str:
        experiments = db.query(ExperimentRun).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "experiment_id", "learner_code", "task_code", "generation_mode",
            "status", "final_outcome", "attempts_count", "started_at", "completed_at"
        ])
        for exp in experiments:
            writer.writerow([
                exp.id,
                exp.learner.learner_code if exp.learner else "",
                exp.task.task_code if exp.task else "",
                exp.generation_mode,
                exp.status,
                exp.final_outcome or "",
                len(exp.attempts),
                exp.started_at.isoformat() if exp.started_at else "",
                exp.completed_at.isoformat() if exp.completed_at else ""
            ])
        return output.getvalue()

evaluation_service = EvaluationService()
