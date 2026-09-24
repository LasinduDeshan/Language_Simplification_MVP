"""Tests for Stage 15 Review Queue and triage boundary enforcement."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.db import Base
from app.datasets.quality.models import ValidationRun, ManualReviewQueueEntry
from app.datasets.quality.enums import ReviewPriority, ReviewStatus, TriageAction
from app.datasets.quality.schemas import TriageDecisionRequestV1
from app.datasets.quality.review_queue import ReviewQueueManager


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Create parent run
        run = ValidationRun(run_id="VAL-QUEUE-TEST", dataset_layer="simplification_corpus")
        session.add(run)
        session.commit()
        yield session
    finally:
        session.close()


def test_create_and_query_review_entry(db):
    entry = ReviewQueueManager.create_entry(
        db=db,
        run_id="VAL-QUEUE-TEST",
        record_id="SIMP-EN-000001",
        dataset_layer="simplification_corpus",
        triggering_rule_ids=["SIMP-MEAN-001"],
        summary="Meaning divergence",
        priority=ReviewPriority.HIGH
    )
    assert entry.entry_id.startswith("REV-")
    assert entry.priority == "high"

    entries = ReviewQueueManager.get_entries(db=db, dataset_layer="simplification_corpus")
    assert len(entries) == 1
    assert entries[0].record_id == "SIMP-EN-000001"


def test_apply_permitted_triage_actions(db):
    entry = ReviewQueueManager.create_entry(
        db=db,
        run_id="VAL-QUEUE-TEST",
        record_id="SIMP-EN-000002",
        dataset_layer="simplification_corpus",
        triggering_rule_ids=["SIMP-NEG-002"],
        summary="Negation issue"
    )

    req = TriageDecisionRequestV1(
        action=TriageAction.SUBMIT_CORRECTION,
        reviewer_id="linguist_alice",
        resolution_notes="Corrected negation in simplified text."
    )
    updated = ReviewQueueManager.apply_triage_decision(db=db, entry_id=entry.entry_id, request=req)
    assert updated.review_status == ReviewStatus.CORRECTION_SUBMITTED.value
    assert updated.assigned_reviewer_id == "linguist_alice"
