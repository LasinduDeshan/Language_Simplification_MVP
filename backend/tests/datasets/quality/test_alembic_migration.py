"""Tests for Alembic migration upgrade, downgrade, and table preservation on a database copy."""
import os
import shutil
import tempfile
import pytest
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, inspect


@pytest.fixture
def temp_alembic_db():
    temp_dir = tempfile.mkdtemp()
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    prod_db_path = os.path.join(backend_dir, "adaptive_learning.db")
    test_db_path = os.path.join(temp_dir, "test_copy.db")

    # Copy current production database to test environment
    if os.path.exists(prod_db_path):
        shutil.copy2(prod_db_path, test_db_path)

    db_url = f"sqlite:///{test_db_path.replace(os.sep, '/')}"
    alembic_ini_path = os.path.join(backend_dir, "alembic.ini")

    cfg = Config(alembic_ini_path)
    cfg.set_main_option("sqlalchemy.url", db_url)
    cfg.set_main_option("script_location", os.path.join(backend_dir, "alembic"))

    yield db_url, cfg

    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass


def test_alembic_stage15_migration_lifecycle(temp_alembic_db):
    db_url, cfg = temp_alembic_db
    engine = create_engine(db_url)

    expected_quality_tables = {
        "dataset_validation_runs",
        "dataset_quality_rule_results",
        "dataset_record_quality_summaries",
        "dataset_manual_review_queue",
        "dataset_record_revisions"
    }

    # 1. Downgrade to Stage 12 (91ee0a12abcd)
    command.downgrade(cfg, "91ee0a12abcd")
    inspector = inspect(engine)
    tables_downgraded = set(inspector.get_table_names())
    for t in expected_quality_tables:
        assert t not in tables_downgraded, f"Table {t} should have been dropped on downgrade"

    # Verify baseline tables remain preserved during downgrade
    assert "learner_profiles" in tables_downgraded
    assert "tasks" in tables_downgraded
    assert "activity_sessions" in tables_downgraded

    # 2. Upgrade to Stage 15 head (a15b8c9d0e1f)
    command.upgrade(cfg, "a15b8c9d0e1f")
    inspector = inspect(engine)
    tables_upgraded = set(inspector.get_table_names())
    assert expected_quality_tables.issubset(tables_upgraded), f"Missing tables after upgrade: {expected_quality_tables - tables_upgraded}"
    assert "learner_profiles" in tables_upgraded
