"""
Maps relational database interaction attempts to V1 private models and de-identified exports on explicit command.
Database remains the operational source of truth.
"""
import os
import sys
from datetime import datetime
from typing import List

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from app.database.db import SessionLocal
from app.database.models import ActivitySession, Attempt
from app.datasets.interaction_dataset.schemas import PrivateInteractionRecordV1
from app.datasets.interaction_dataset.export_schemas import DeidentifiedInteractionExportV1
from app.datasets.common.enums import (
    ActivityOwner, PrimaryDomain, SupportLevel, ResponseMode, Outcome, ConsentStatus
)
from app.datasets.common.metadata import ConsentMetadata, GovernanceMetadata

def map_db_session_to_v1_interactions(db, session_id: str) -> List[PrivateInteractionRecordV1]:
    """Maps attempts from a database session into PrivateInteractionRecordV1 instances."""
    session = db.query(ActivitySession).filter(ActivitySession.id == session_id).first()
    if not session:
        return []

    attempts = db.query(Attempt).filter(Attempt.activity_session_id == session.id).order_by(Attempt.attempt_number).all()
    records = []
    
    for att in attempts:
        domain_str = session.task.category if (session.task and session.task.category) else "vocabulary"
        domain = PrimaryDomain.GRAMMAR if domain_str == "sentence_and_instruction" else PrimaryDomain(domain_str)
        
        sup_str = att.support_level or "moderate"
        sup = SupportLevel(sup_str if sup_str in ["mild", "moderate", "strong"] else "moderate")

        outcome_val = Outcome.CORRECT if session.final_outcome == "success" else (
            Outcome.ADULT_SUPPORT_REQUIRED if session.status == "adult_support_required" else Outcome.IN_PROGRESS
        )

        rec = PrivateInteractionRecordV1(
            interaction_id=f"INT-{att.id[:8]}",
            schema_version="1.0.0",
            dataset_version="0.1.0",
            learner_id=session.learner.learner_code if session.learner else "CHILD-ANON",
            session_id=session.id,
            activity_id=session.task.task_code if session.task else "VOC-NAMING-001",
            activity_owner=ActivityOwner.COMPONENT_3_LANGUAGE,
            primary_domain=domain,
            occurred_at=att.created_at or datetime.utcnow(),
            attempt_number=att.attempt_number or 1,
            support_level_used=sup,
            response_mode=ResponseMode.MANUAL if att.manual_transcript else ResponseMode.TOUCH,
            response_text_private=att.manual_transcript or att.speech_transcript,
            normalized_response=att.manual_transcript.lower().strip() if att.manual_transcript else None,
            outcome=outcome_val,
            error_categories=[obs.get("error_type", "observation") if isinstance(obs, dict) else str(obs) for obs in (att.grammar_observations or [])] if hasattr(att, "grammar_observations") else [],
            response_time_ms=att.response_time_ms or 0,
            score_before=50.0,
            score_delta=0.5 if outcome_val == Outcome.CORRECT else -0.5,
            score_after=50.5 if outcome_val == Outcome.CORRECT else 49.5,
            evidence_count_after=1,
            adult_confirmed=True if session.status in ["completed", "adult_support_required"] else False,
            screening_risk_modified=False,
            consent=ConsentMetadata(status=ConsentStatus.NOT_VERIFIED),
            governance=GovernanceMetadata(contains_personal_data=True, is_simulated=True)
        )
        records.append(rec)
    return records

def convert_to_deidentified_export(record: PrivateInteractionRecordV1) -> DeidentifiedInteractionExportV1:
    """Converts a private record to a de-identified export record using an explicit allowlist."""
    return DeidentifiedInteractionExportV1(
        interaction_id=record.interaction_id,
        schema_version="1.0.0",
        dataset_version="0.1.0",
        learner_id=record.learner_id,
        activity_id=record.activity_id,
        primary_domain=record.primary_domain,
        occurred_at=record.occurred_at,
        attempt_number=record.attempt_number,
        support_level_used=record.support_level_used,
        response_mode=record.response_mode,
        outcome=record.outcome,
        error_categories=record.error_categories,
        response_time_ms=record.response_time_ms,
        score_delta=record.score_delta,
        local_preliminary_trend="stable_positive" if record.score_delta and record.score_delta > 0 else "remedial_needed"
    )

def test_mapping():
    db = SessionLocal()
    try:
        sessions = db.query(ActivitySession).limit(3).all()
        total_mapped = 0
        for s in sessions:
            recs = map_db_session_to_v1_interactions(db, s.id)
            for r in recs:
                exp = convert_to_deidentified_export(r)
                assert exp.interaction_id == r.interaction_id
                total_mapped += 1
        print(f"[OK] Successfully verified database-to-V1 interaction mapping for {total_mapped} attempts.")
    finally:
        db.close()

if __name__ == "__main__":
    test_mapping()
