import os
import json
from datetime import datetime
from typing import Optional
from app.integrations.component4.interface import Component4Interface
from app.integrations.component4.schemas import Component4PerformanceExportSchema, DomainPerformancePayload
from app.database.models import LearnerProfile, TaskResult

class Component4MockAdapter(Component4Interface):
    """
    Mock adapter that generates Component 4 performance export payloads
    and saves them locally under data/integration_previews/component4_outputs/
    """
    def __init__(self, previews_dir: Optional[str] = None):
        if previews_dir is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
            previews_dir = os.path.join(base_dir, "data", "integration_previews", "component4_outputs")
        self.previews_dir = previews_dir
        os.makedirs(self.previews_dir, exist_ok=True)

    def export_learner_performance(self, learner_id: str, db_session) -> Component4PerformanceExportSchema:
        learner = db_session.query(LearnerProfile).filter(
            (LearnerProfile.id == learner_id) | (LearnerProfile.learner_code == learner_id)
        ).first()

        if not learner:
            raise ValueError(f"Learner '{learner_id}' not found.")

        # Find latest task results
        results = db_session.query(TaskResult).filter(
            TaskResult.learner_id == learner.id
        ).order_by(TaskResult.completed_at.desc()).all()

        latest = results[0] if results else None

        # Build domain payloads
        domains = {
            "vocabulary": DomainPerformancePayload(
                score=round(learner.vocabulary_score, 1),
                evidence_count=learner.vocabulary_evidence_count or 0,
                local_preliminary_trend="stable",
                recent_activity_scores=[r.score_after.get("vocabulary_score", 50.0) for r in results[:5] if r.score_after] if results else [learner.vocabulary_score],
                latest_updated_at=learner.updated_at
            ),
            "grammar": DomainPerformancePayload(
                score=round(learner.grammar_score, 1),
                evidence_count=learner.grammar_evidence_count or 0,
                local_preliminary_trend="stable",
                recent_activity_scores=[r.score_after.get("grammar_score", 50.0) for r in results[:5] if r.score_after] if results else [learner.grammar_score],
                latest_updated_at=learner.updated_at
            ),
            "comprehension": DomainPerformancePayload(
                score=round(learner.comprehension_score, 1),
                evidence_count=learner.comprehension_evidence_count or 0,
                local_preliminary_trend="stable",
                recent_activity_scores=[r.score_after.get("comprehension_score", 50.0) for r in results[:5] if r.score_after] if results else [learner.comprehension_score],
                latest_updated_at=learner.updated_at
            ),
            "instruction_following": DomainPerformancePayload(
                score=round(learner.instruction_following_score, 1),
                evidence_count=learner.instruction_evidence_count or 0,
                local_preliminary_trend="stable",
                recent_activity_scores=[r.score_after.get("instruction_following_score", 50.0) for r in results[:5] if r.score_after] if results else [learner.instruction_following_score],
                latest_updated_at=learner.updated_at
            ),
        }

        # Compute preliminary local trend
        for dom_key, dom_payload in domains.items():
            if len(dom_payload.recent_activity_scores) >= 2:
                first = dom_payload.recent_activity_scores[-1]
                last = dom_payload.recent_activity_scores[0]
                diff = last - first
                if diff > 2.0:
                    dom_payload.local_preliminary_trend = "improving"
                elif diff < -2.0:
                    dom_payload.local_preliminary_trend = "needs_support"

        screening_risk = getattr(learner, "screening_risk_level", None) or getattr(learner, "risk_support_level", "moderate")
        recommended_support = getattr(learner, "recommended_support_level", "moderate")

        payload = Component4PerformanceExportSchema(
            schema_version="1.0",
            learner_id=learner.learner_code,
            screening_risk_level=screening_risk,
            screening_source=getattr(learner, "screening_source", "component_1") or "component_1",
            risk_modified_by_component_3=False,
            recommended_support_level=recommended_support,
            performance_profile=domains,
            latest_session_id=latest.session_id if latest else None,
            latest_task_code=latest.task_code if latest else None,
            latest_outcome=latest.final_outcome if latest else None,
            latest_independent_success=latest.independent_success if latest else None,
            latest_attempt_count=latest.attempts_count if latest else None,
            is_simulated=True,
            environment="development",
            research_eligible=False,
            export_timestamp=datetime.utcnow(),
            export_status="generated_locally_not_delivered"
        )

        # Save to previews folder
        output_file = os.path.join(self.previews_dir, f"{learner.learner_code}_component4_export.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(payload.model_dump(mode="json"), f, indent=2)

        return payload
