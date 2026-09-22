import csv
import io
import json
import zipfile
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.database.models import (
    ExpertEvaluation, ExperimentRun, Adaptation, Attempt, ValidationResult,
    Task, LearnerProfile, IntegrationEvent, LanguageObservation
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
        """
        Records a 5-dimension Likert evaluation (1-5 scale) from an expert evaluator.
        Enforces 1 <= score <= 5 check bounds.
        """
        scores = [age_appropriateness, clarity, grammar_correctness, meaning_preservation, personalization_suitability]
        for s in scores:
            if not isinstance(s, int) or s < 1 or s > 5:
                raise ValueError("Evaluation scores must be integers between 1 and 5 inclusive.")

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

    def get_evaluations_for_adaptation(self, db: Session, adaptation_id: str) -> List[Dict[str, Any]]:
        """Retrieves all expert evaluations recorded for a specific adaptation."""
        evals = db.query(ExpertEvaluation).filter(
            ExpertEvaluation.adaptation_id == adaptation_id
        ).order_by(ExpertEvaluation.created_at.desc()).all()

        results = []
        for ev in evals:
            mean_score = round(
                (ev.age_appropriateness + ev.clarity + ev.grammar_correctness +
                 ev.meaning_preservation + ev.personalization_suitability) / 5.0, 2
            )
            results.append({
                "id": ev.id,
                "adaptation_id": ev.adaptation_id,
                "evaluator_code": ev.evaluator_code,
                "age_appropriateness": ev.age_appropriateness,
                "clarity": ev.clarity,
                "grammar_correctness": ev.grammar_correctness,
                "meaning_preservation": ev.meaning_preservation,
                "personalization_suitability": ev.personalization_suitability,
                "mean_score": mean_score,
                "comments": ev.comments,
                "created_at": ev.created_at.isoformat() if ev.created_at else None
            })
        return results

    def get_evaluation_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Calculates aggregate statistical metrics across all recorded expert evaluations,
        including overall means, dimension averages, and comparative breakdown by generation method.
        """
        evals = db.query(ExpertEvaluation).all()
        if not evals:
            return {
                "total_evaluations": 0,
                "total_evaluators": 0,
                "overall_mean": 0.0,
                "dimensions": {
                    "age_appropriateness": 0.0,
                    "clarity": 0.0,
                    "grammar_correctness": 0.0,
                    "meaning_preservation": 0.0,
                    "personalization_suitability": 0.0
                },
                "by_generation_method": {
                    "rule": {"count": 0, "overall_mean": 0.0, "dimensions": {}},
                    "llm": {"count": 0, "overall_mean": 0.0, "dimensions": {}},
                    "hybrid": {"count": 0, "overall_mean": 0.0, "dimensions": {}}
                },
                "score_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }

        total = len(evals)
        evaluators = set(e.evaluator_code for e in evals)

        dim_sums = {
            "age_appropriateness": sum(e.age_appropriateness for e in evals),
            "clarity": sum(e.clarity for e in evals),
            "grammar_correctness": sum(e.grammar_correctness for e in evals),
            "meaning_preservation": sum(e.meaning_preservation for e in evals),
            "personalization_suitability": sum(e.personalization_suitability for e in evals)
        }

        dim_means = {k: round(v / total, 2) for k, v in dim_sums.items()}
        overall_mean = round(sum(dim_means.values()) / 5.0, 2)

        # Score distribution
        score_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for e in evals:
            for val in [e.age_appropriateness, e.clarity, e.grammar_correctness, e.meaning_preservation, e.personalization_suitability]:
                if val in score_dist:
                    score_dist[val] += 1

        # By generation method
        method_groups: Dict[str, List[ExpertEvaluation]] = {"rule": [], "llm": [], "hybrid": []}
        for e in evals:
            ad = e.adaptation
            method = (ad.generation_method if ad else "rule").lower()
            if method not in method_groups:
                method_groups[method] = []
            method_groups[method].append(e)

        by_method = {}
        for method, group in method_groups.items():
            if not group:
                by_method[method] = {
                    "count": 0,
                    "overall_mean": 0.0,
                    "dimensions": {k: 0.0 for k in dim_sums.keys()}
                }
            else:
                m_total = len(group)
                m_dims = {
                    "age_appropriateness": round(sum(item.age_appropriateness for item in group) / m_total, 2),
                    "clarity": round(sum(item.clarity for item in group) / m_total, 2),
                    "grammar_correctness": round(sum(item.grammar_correctness for item in group) / m_total, 2),
                    "meaning_preservation": round(sum(item.meaning_preservation for item in group) / m_total, 2),
                    "personalization_suitability": round(sum(item.personalization_suitability for item in group) / m_total, 2)
                }
                m_overall = round(sum(m_dims.values()) / 5.0, 2)
                by_method[method] = {
                    "count": m_total,
                    "overall_mean": m_overall,
                    "dimensions": m_dims
                }

        return {
            "total_evaluations": total,
            "total_evaluators": len(evaluators),
            "overall_mean": overall_mean,
            "dimensions": dim_means,
            "by_generation_method": by_method,
            "score_distribution": score_dist
        }

    def get_component_1_payload(self, db: Session, experiment_id: str) -> Dict[str, Any]:
        """
        Component 1: Task Delivery Subsystem Payload.
        Delivers validated child instruction, visual cues, and format.
        Strict anti-leakage: do_not_reveal_answer = True.
        """
        experiment = db.query(ExperimentRun).filter(ExperimentRun.id == experiment_id).first()
        if not experiment:
            return {}

        latest_adaptation = db.query(Adaptation).filter(
            Adaptation.experiment_run_id == experiment_id
        ).order_by(Adaptation.target_attempt_number.desc()).first()

        if not latest_adaptation:
            return {}

        latest_val = db.query(ValidationResult).filter(
            ValidationResult.adaptation_id == latest_adaptation.id,
            ValidationResult.is_final == True
        ).first()

        payload = {
            "task_id": experiment.task.task_code,
            "attempt_number": latest_adaptation.target_attempt_number,
            "support_level": latest_adaptation.support_level,
            "child_instruction": latest_adaptation.child_instruction,
            "supportive_message": latest_adaptation.supportive_message,
            "answer_format": latest_adaptation.answer_format or "speech",
            "cues": latest_adaptation.visual_cues or [],
            "vocabulary_support": latest_adaptation.vocabulary_support or [],
            "do_not_reveal_answer": True,
            "validation_status": latest_val.status if latest_val else "approved",
            "generation_method": latest_adaptation.generation_method,
            "provider": latest_adaptation.provider,
            "model_name": latest_adaptation.model_name
        }

        existing = db.query(IntegrationEvent).filter(
            IntegrationEvent.experiment_run_id == experiment_id,
            IntegrationEvent.adaptation_id == latest_adaptation.id,
            IntegrationEvent.target_component == "component_1"
        ).first()
        if not existing:
            self.log_integration_event(
                db=db,
                experiment_run_id=experiment_id,
                target_component="component_1",
                event_type="component_1_payload_fetch",
                payload=payload,
                adaptation_id=latest_adaptation.id
            )

        return payload

    def get_component_4_payload(self, db: Session, experiment_id: str) -> Dict[str, Any]:
        """
        Component 4: Analytics / Learner Modeling Subsystem Payload.
        Reports performance metrics, observed language patterns, and next-step recommendations.
        Child-safe: diagnostic codes are strictly clinician-facing.
        """
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
        clinician_observations = []
        if latest_attempt and latest_attempt.observations:
            for obs in latest_attempt.observations:
                observed_patterns.append(obs.observation_code)
                clinician_observations.append({
                    "category": obs.category,
                    "code": obs.observation_code,
                    "evidence": obs.evidence,
                    "confidence": obs.confidence,
                    "child_visible": obs.child_visible
                })

        next_rec = f"continue_{latest_adaptation.support_level}_support" if latest_adaptation else "continue_support"
        if latest_attempt and latest_attempt.attempt_number >= 3 and result_str != "correct":
            next_rec = "escalate_to_human_educator"

        payload = {
            "learner_id": experiment.learner.learner_code,
            "task_id": experiment.task.task_code,
            "attempt_number": attempt_num,
            "result": result_str,
            "observed_patterns": observed_patterns,
            "support_applied": [latest_adaptation.support_level] if latest_adaptation else ["mild"],
            "next_recommendation": next_rec,
            "processing_time_ms": latest_adaptation.processing_time_ms if latest_adaptation else 0,
            "diagnostic_summary": {
                "total_observations": len(observed_patterns),
                "observations_detail": clinician_observations,
                "speech_confidence": latest_attempt.speech_confidence if latest_attempt else None,
                "response_time_ms": latest_attempt.response_time_ms if latest_attempt else None
            }
        }

        if latest_attempt:
            existing = db.query(IntegrationEvent).filter(
                IntegrationEvent.experiment_run_id == experiment_id,
                IntegrationEvent.attempt_id == latest_attempt.id,
                IntegrationEvent.target_component == "component_4"
            ).first()
            if not existing:
                self.log_integration_event(
                    db=db,
                    experiment_run_id=experiment_id,
                    target_component="component_4",
                    event_type="component_4_payload_fetch",
                    payload=payload,
                    attempt_id=latest_attempt.id,
                    adaptation_id=latest_adaptation.id if latest_adaptation else None
                )

        return payload

    def get_ar_payload(self, db: Session, experiment_id: str) -> Dict[str, Any]:
        """
        Component 3: Augmented Reality Subsystem Payload.
        Provides 3D spatial anchors, interactive target objects, and audio prompt cues.
        """
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
        cues = latest_adaptation.visual_cues if latest_adaptation else []

        labels = ar_meta.get("object_labels", ["object_1", "object_2"])

        payload = {
            "task_id": task.task_code,
            "language": "en",
            "child_instruction": child_instruction,
            "object_labels": labels,
            "spatial_anchors": ar_meta.get("spatial_anchors", {
                "workspace_plane": "tabletop",
                "center_point": [0.0, 0.0, -0.5]
            }),
            "highlight_targets": [c for c in cues if any(k in c for k in ["highlight", "point", "pulse", "show"])],
            "vocabulary_support": latest_adaptation.vocabulary_support if latest_adaptation else [],
            "audio_text": child_instruction,
            "interaction_type": ar_meta.get("interaction_type", "drag_and_drop"),
            "support_level": support_level
        }

        if latest_adaptation:
            existing = db.query(IntegrationEvent).filter(
                IntegrationEvent.experiment_run_id == experiment_id,
                IntegrationEvent.adaptation_id == latest_adaptation.id,
                IntegrationEvent.target_component == "component_3_ar"
            ).first()
            if not existing:
                self.log_integration_event(
                    db=db,
                    experiment_run_id=experiment_id,
                    target_component="component_3_ar",
                    event_type="ar_payload_fetch",
                    payload=payload,
                    adaptation_id=latest_adaptation.id
                )

        return payload

    def log_integration_event(
        self,
        db: Session,
        experiment_run_id: str,
        target_component: str,
        event_type: str,
        payload: Dict[str, Any],
        attempt_id: Optional[str] = None,
        adaptation_id: Optional[str] = None,
        schema_version: str = "1.0",
        delivery_status: str = "simulated"
    ) -> IntegrationEvent:
        """Persists an integration event between MVP subsystem and external component simulators."""
        event = IntegrationEvent(
            experiment_run_id=experiment_run_id,
            attempt_id=attempt_id,
            adaptation_id=adaptation_id,
            target_component=target_component,
            event_type=event_type,
            schema_version=schema_version,
            payload=payload,
            delivery_status=delivery_status
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    def get_integration_events(self, db: Session, experiment_id: str) -> List[Dict[str, Any]]:
        """Retrieves chronological integration events for an experiment run."""
        events = db.query(IntegrationEvent).filter(
            IntegrationEvent.experiment_run_id == experiment_id
        ).order_by(IntegrationEvent.created_at.asc()).all()

        return [
            {
                "id": ev.id,
                "experiment_run_id": ev.experiment_run_id,
                "attempt_id": ev.attempt_id,
                "adaptation_id": ev.adaptation_id,
                "target_component": ev.target_component,
                "event_type": ev.event_type,
                "schema_version": ev.schema_version,
                "payload": ev.payload,
                "delivery_status": ev.delivery_status,
                "created_at": ev.created_at.isoformat() if ev.created_at else None
            }
            for ev in events
        ]

    def export_experiments_json(self, db: Session) -> List[Dict[str, Any]]:
        """Exports full hierarchical dataset tree in JSON format."""
        experiments = db.query(ExperimentRun).all()
        results = []
        for exp in experiments:
            attempts_data = []
            for a in exp.attempts:
                observations_data = [
                    {
                        "category": o.category,
                        "observation_code": o.observation_code,
                        "confidence": o.confidence,
                        "evidence": o.evidence,
                        "child_visible": o.child_visible
                    }
                    for o in a.observations
                ]
                attempts_data.append({
                    "id": a.id,
                    "attempt_number": a.attempt_number,
                    "adaptation_id": a.adaptation_id,
                    "transcript": a.speech_transcript,
                    "confidence": a.speech_confidence,
                    "concept_result": a.concept_result,
                    "response_time_ms": a.response_time_ms,
                    "completion_status": a.completion_status,
                    "observations": observations_data
                })

            adaptations_data = []
            for ad in exp.adaptations:
                val_data = [
                    {
                        "sequence": v.validation_sequence,
                        "status": v.status,
                        "language_valid": v.language_valid,
                        "answer_leakage": v.answer_leakage,
                        "sentence_length_valid": v.sentence_length_valid,
                        "semantic_score": v.semantic_score,
                        "failure_reasons": v.failure_reasons,
                        "is_final": v.is_final
                    }
                    for v in ad.validation_results
                ]
                evals_data = [
                    {
                        "evaluator_code": ev.evaluator_code,
                        "age_appropriateness": ev.age_appropriateness,
                        "clarity": ev.clarity,
                        "grammar_correctness": ev.grammar_correctness,
                        "meaning_preservation": ev.meaning_preservation,
                        "personalization_suitability": ev.personalization_suitability,
                        "comments": ev.comments
                    }
                    for ev in ad.expert_evaluations
                ]
                adaptations_data.append({
                    "id": ad.id,
                    "target_attempt": ad.target_attempt_number,
                    "support_level": ad.support_level,
                    "generation_method": ad.generation_method,
                    "instruction": ad.child_instruction,
                    "supportive_message": ad.supportive_message,
                    "word_count": len(ad.child_instruction.split()) if ad.child_instruction else 0,
                    "answer_format": ad.answer_format,
                    "visual_cues": ad.visual_cues,
                    "vocabulary_support": ad.vocabulary_support,
                    "reason_codes": ad.reason_codes,
                    "provider": ad.provider,
                    "model_name": ad.model_name,
                    "processing_time_ms": ad.processing_time_ms,
                    "estimated_cost": float(ad.estimated_cost) if ad.estimated_cost is not None else 0.0,
                    "validations": val_data,
                    "expert_evaluations": evals_data
                })

            results.append({
                "experiment_id": exp.id,
                "learner": {
                    "code": exp.learner.learner_code if exp.learner else None,
                    "age": exp.learner.age if exp.learner else None,
                    "risk_level": exp.learner.risk_support_level if exp.learner else None,
                    "english_level": exp.learner.english_level if exp.learner else None
                },
                "task": {
                    "code": exp.task.task_code if exp.task else None,
                    "title": exp.task.title if exp.task else None,
                    "original_instruction": exp.task.original_instruction if exp.task else None
                },
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
        """Exports core experiments summary CSV."""
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

    def export_adaptations_csv(self, db: Session) -> str:
        """Exports detailed task adaptations CSV."""
        adaptations = db.query(Adaptation).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "adaptation_id", "experiment_run_id", "task_code", "learner_code",
            "target_attempt_number", "support_level", "generation_method",
            "child_instruction", "word_count", "answer_format", "provider",
            "model_name", "processing_time_ms", "estimated_cost", "created_at"
        ])
        for ad in adaptations:
            exp = ad.experiment_run
            writer.writerow([
                ad.id,
                ad.experiment_run_id,
                exp.task.task_code if exp and exp.task else "",
                exp.learner.learner_code if exp and exp.learner else "",
                ad.target_attempt_number,
                ad.support_level,
                ad.generation_method,
                ad.child_instruction,
                len(ad.child_instruction.split()) if ad.child_instruction else 0,
                ad.answer_format,
                ad.provider,
                ad.model_name,
                ad.processing_time_ms,
                ad.estimated_cost or 0.0,
                ad.created_at.isoformat() if ad.created_at else ""
            ])
        return output.getvalue()

    def export_attempts_csv(self, db: Session) -> str:
        """Exports learner attempt responses and speech acoustic metrics CSV."""
        attempts = db.query(Attempt).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "attempt_id", "experiment_run_id", "adaptation_id", "attempt_number",
            "instruction_shown", "speech_transcript", "speech_confidence",
            "concept_result", "response_time_ms", "completion_status", "created_at"
        ])
        for att in attempts:
            writer.writerow([
                att.id,
                att.experiment_run_id,
                att.adaptation_id,
                att.attempt_number,
                att.instruction_shown,
                att.speech_transcript,
                att.speech_confidence,
                att.concept_result,
                att.response_time_ms,
                att.completion_status,
                att.created_at.isoformat() if att.created_at else ""
            ])
        return output.getvalue()

    def export_evaluations_csv(self, db: Session) -> str:
        """Exports expert evaluations across 5 Likert dimensions CSV."""
        evals = db.query(ExpertEvaluation).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "evaluation_id", "adaptation_id", "evaluator_code", "generation_method",
            "age_appropriateness", "clarity", "grammar_correctness",
            "meaning_preservation", "personalization_suitability", "mean_score",
            "comments", "created_at"
        ])
        for ev in evals:
            mean_score = round(
                (ev.age_appropriateness + ev.clarity + ev.grammar_correctness +
                 ev.meaning_preservation + ev.personalization_suitability) / 5.0, 2
            )
            gen_method = ev.adaptation.generation_method if ev.adaptation else "unknown"
            writer.writerow([
                ev.id,
                ev.adaptation_id,
                ev.evaluator_code,
                gen_method,
                ev.age_appropriateness,
                ev.clarity,
                ev.grammar_correctness,
                ev.meaning_preservation,
                ev.personalization_suitability,
                mean_score,
                ev.comments or "",
                ev.created_at.isoformat() if ev.created_at else ""
            ])
        return output.getvalue()

    def export_research_bundle_zip(self, db: Session) -> bytes:
        """
        Assembles all research CSVs, complete JSON dataset, and a metadata manifest
        into an in-memory downloadable ZIP archive.
        """
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # 1. JSON full tree
            json_data = json.dumps(self.export_experiments_json(db), indent=2)
            zf.writestr("experiments_full_tree.json", json_data)

            # 2. Individual CSVs
            zf.writestr("experiments.csv", self.export_experiments_csv(db))
            zf.writestr("adaptations.csv", self.export_adaptations_csv(db))
            zf.writestr("attempts.csv", self.export_attempts_csv(db))
            zf.writestr("expert_evaluations.csv", self.export_evaluations_csv(db))

            # 3. Statistical summary
            stats = self.get_evaluation_statistics(db)
            stats_json = json.dumps(stats, indent=2)
            zf.writestr("evaluation_statistics.json", stats_json)

            # 4. Manifest / README
            manifest = (
                "ENGLISH-FIRST ADAPTIVE CHILD-FRIENDLY LANGUAGE SUPPORT MVP (v2.2)\n"
                "RESEARCH DATASET ARCHIVE\n"
                "=================================================================\n\n"
                f"Generated: {datetime.utcnow().isoformat()}Z\n"
                f"Total Evaluations: {stats['total_evaluations']}\n"
                f"Overall Likert Mean: {stats['overall_mean']}/5.00\n\n"
                "INCLUDED ARTIFACTS:\n"
                "- experiments_full_tree.json: Complete nested hierarchical dataset.\n"
                "- experiments.csv: High-level experiment run progression logs.\n"
                "- adaptations.csv: Child-friendly instructions, word counts, and latency.\n"
                "- attempts.csv: Acoustic transcripts, confidence gating, and concept outcomes.\n"
                "- expert_evaluations.csv: 5-dimension Likert rubric ratings and qualitative notes.\n"
                "- evaluation_statistics.json: Pre-computed statistical aggregates.\n"
            )
            zf.writestr("DATASET_METADATA.txt", manifest)

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

evaluation_service = EvaluationService()
