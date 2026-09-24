"""Tests for Stage 15 immutable record revisions and revalidation history."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.db import Base
from app.datasets.quality.models import RecordRevision
from app.datasets.quality.schemas import RecordCorrectionRequestV1
from app.datasets.quality.correction_service import CorrectionService


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_immutable_revision_creation(db):
    prev_content = {
        "pair_id": "SIMP-EN-000001",
        "original_text": "The massive elephant walked.",
        "simplified_text": "The elephant walked."
    }
    req = RecordCorrectionRequestV1(
        reviewer_id="reviewer_1",
        change_reason="Add adjective for clarity",
        corrected_content={
            "pair_id": "SIMP-EN-000001",
            "original_text": "The massive elephant walked.",
            "simplified_text": "The big elephant walked."
        }
    )

    rev = CorrectionService.create_revision(
        db=db,
        record_id="SIMP-EN-000001",
        dataset_layer="simplification_corpus",
        request=req,
        previous_content=prev_content
    )

    assert rev.revision_id.startswith("REV-HIST-")
    assert rev.revalidated is False

    history = CorrectionService.get_revision_history(db=db, record_id="SIMP-EN-000001")
    assert len(history) == 1
    assert history[0].change_reason == "Add adjective for clarity"

    CorrectionService.mark_revalidated(db=db, revision_id=rev.revision_id, run_id="VAL-REVAL-001")
    updated = db.query(RecordRevision).filter(RecordRevision.revision_id == rev.revision_id).first()
    assert updated.revalidated is True
    assert updated.revalidation_run_id == "VAL-REVAL-001"
