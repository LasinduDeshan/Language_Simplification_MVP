"""Tests for Stage 15 database models, SQLite persistence, and transaction integrity."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.db import Base
from app.datasets.quality.models import (
    ValidationRun,
    QualityRuleResult,
    RecordQualitySummary,
    ManualReviewQueueEntry,
    RecordRevision
)


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_validation_run_persistence(test_db):
    run = ValidationRun(
        run_id="VAL-TEST-001",
        dataset_layer="adaptation_test_set",
        dataset_version="0.1.0",
        quality_rule_set_version="1.0.0",
        status="completed",
        total_records=40,
        passed_count=35,
        failed_count=3,
        review_required_count=2,
        quarantined_count=0
    )
    test_db.add(run)
    test_db.commit()

    queried = test_db.query(ValidationRun).filter(ValidationRun.run_id == "VAL-TEST-001").first()
    assert queried is not None
    assert queried.total_records == 40
    assert queried.passed_count == 35


def test_cascade_deletion(test_db):
    run = ValidationRun(
        run_id="VAL-TEST-CASCADE",
        dataset_layer="all",
        status="completed"
    )
    test_db.add(run)
    test_db.commit()

    res = QualityRuleResult(
        result_id="RES-001",
        run_id="VAL-TEST-CASCADE",
        record_id="REC-001",
        dataset_layer="simplification_corpus",
        rule_id="RULE-1",
        validator_name="test_val",
        severity="error",
        passed=False,
        message="Failure"
    )
    test_db.add(res)
    test_db.commit()

    assert test_db.query(QualityRuleResult).filter(QualityRuleResult.run_id == "VAL-TEST-CASCADE").count() == 1

    # Delete run should cascade delete results
    test_db.delete(run)
    test_db.commit()

    assert test_db.query(QualityRuleResult).filter(QualityRuleResult.run_id == "VAL-TEST-CASCADE").count() == 0


def test_transaction_rollback(test_db):
    run = ValidationRun(run_id="VAL-ROLLBACK", dataset_layer="all")
    test_db.add(run)
    test_db.commit()

    try:
        # Intentionally invalid duplicate PK insertion
        dup = ValidationRun(run_id="VAL-ROLLBACK", dataset_layer="all")
        test_db.add(dup)
        test_db.commit()
    except Exception:
        test_db.rollback()

    # Session is clean and intact
    count = test_db.query(ValidationRun).filter(ValidationRun.run_id == "VAL-ROLLBACK").count()
    assert count == 1
