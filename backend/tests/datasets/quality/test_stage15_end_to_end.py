"""End-to-end dataset validation run and accounting test."""
import asyncio
from app.database.db import SessionLocal, Base, engine
from app.datasets.quality.orchestrator import QualityOrchestrator
from app.datasets.quality.schemas import ValidationRunCreateRequestV1


def test_stage15_full_validation_run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        orchestrator = QualityOrchestrator(db=db)
        req = ValidationRunCreateRequestV1(
            dataset_layer="all",
            dataset_version="0.1.0",
            quality_rule_set_version="1.0.0",
            enable_nlp=True,
            enable_llm_review=False
        )
        run = orchestrator.create_run(req, created_by="e2e_test")
        completed = asyncio.run(orchestrator.execute_validation_run(run_id=run.run_id, enable_nlp=True, enable_llm_review=False))

        assert completed.status == "completed"
        assert completed.total_records >= 268  # 40 activities + 210 pairs + 18 lexicons
        
        # Accounting invariant
        reconciled = completed.passed_count + completed.failed_count + completed.review_required_count + completed.quarantined_count
        assert completed.total_records == reconciled
        assert completed.quarantined_count >= 0

    finally:
        db.close()
