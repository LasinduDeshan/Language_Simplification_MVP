import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import ActivitySession, Attempt, TaskResult, IntegrationEvent
from app.datasets.common.draft_models import DraftInteractionRecord
from app.datasets.common.paths import INTERACTION_PRIVATE_DIR, INTERACTION_DEIDENTIFIED_DIR

class InteractionRepository:
    """
    Repository interface for runtime learner interaction records.
    The SQLAlchemy relational database is the operational source of truth.
    Local JSON exports are strictly private, audited, and excluded from Git.
    """
    def __init__(self, private_dir: Optional[str] = None, deidentified_dir: Optional[str] = None):
        self.private_dir = private_dir or INTERACTION_PRIVATE_DIR
        self.deidentified_dir = deidentified_dir or INTERACTION_DEIDENTIFIED_DIR
        os.makedirs(self.private_dir, exist_ok=True)
        os.makedirs(self.deidentified_dir, exist_ok=True)

    def get_session_interactions(self, db: Session, session_id: str) -> List[DraftInteractionRecord]:
        session = db.query(ActivitySession).filter(ActivitySession.id == session_id).first()
        if not session:
            return []

        attempts = db.query(Attempt).filter(Attempt.activity_session_id == session.id).order_by(Attempt.attempt_number).all()
        records = []
        for att in attempts:
            rec = DraftInteractionRecord(
                interaction_id=f"INT-{att.id[:8]}",
                session_id=session.id,
                learner_id=session.learner.learner_code if session.learner else "CHILD-ANON",
                activity_id=session.task.task_code if session.task else "TASK-UNKNOWN",
                activity_owner="component_3",
                attempt_number=att.attempt_number,
                support_level_used=att.support_level or "moderate",
                response_mode="manual_transcript" if att.manual_transcript else "multiple_choice",
                response_text_private=att.manual_transcript or att.speech_transcript,
                normalized_response=att.manual_transcript.lower().strip() if att.manual_transcript else None,
                outcome=session.final_outcome or "in_progress",
                error_categories=[obs.get("error_type", "observation") if isinstance(obs, dict) else str(obs) for obs in (att.grammar_observations or [])] if hasattr(att, "grammar_observations") else [],
                response_time_ms=att.response_time_ms or 0,
                updated_domain=session.task.category if session.task else "vocabulary",
                adult_confirmed=True if session.status in ["completed", "adult_support_required"] else False,
                screening_risk_modified=False,
                consent_status="not_verified",
                is_simulated=True,
                research_eligible=False,
                timestamp=att.created_at or datetime.utcnow()
            )
            records.append(rec)
        return records

    def get_interactions(self, db: Session, limit: int = 100) -> List[DraftInteractionRecord]:
        sessions = db.query(ActivitySession).limit(limit).all()
        all_records = []
        for s in sessions:
            all_records.extend(self.get_session_interactions(db, s.id))
        return all_records

    def export_private_snapshot(self, db: Session, output_filename: str = "private_interactions.json") -> str:
        """
        Exports an audited, private interaction snapshot to private storage.
        """
        sessions = db.query(ActivitySession).all()
        all_records = []
        for s in sessions:
            all_records.extend(self.get_session_interactions(db, s.id))

        output_path = os.path.join(self.private_dir, output_filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([r.model_dump(mode="json") for r in all_records], f, indent=2)

        # Audit the export in IntegrationEvent
        db.add(IntegrationEvent(
            target_component="component_3",
            event_type="private_interaction_snapshot_exported",
            schema_version="1.0",
            delivery_status="saved_locally_private",
            payload={"exported_count": len(all_records), "output_path": output_path}
        ))
        db.commit()

        return output_path

InteractionDatasetRepository = InteractionRepository

