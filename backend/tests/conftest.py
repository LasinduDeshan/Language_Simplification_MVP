"""
Global test configuration and database isolation fixture.
Ensures test execution runs on an isolated temporary database copy,
preventing any modification or contamination of the tracked baseline database.
"""

import os
import shutil
import tempfile
import atexit

# 1. Immediately create an isolated temporary copy of the baseline database
_TEMP_DIR = tempfile.mkdtemp()
_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_BASELINE_DB = os.path.join(_BACKEND_DIR, "adaptive_learning.db")
_TEMP_DB = os.path.join(_TEMP_DIR, "test_adaptive_learning.db")

if os.path.exists(_BASELINE_DB):
    shutil.copy2(_BASELINE_DB, _TEMP_DB)

# 2. Set DATABASE_URL in environment BEFORE any app modules are imported
_TEMP_DB_URL = f"sqlite:///{_TEMP_DB.replace(os.sep, '/')}"
os.environ["DATABASE_URL"] = _TEMP_DB_URL

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(autouse=True, scope="session")
def isolate_database_session():
    """Explicitly ensure settings and app.database.db use the temporary database."""
    try:
        import app.core.config as config
        config.settings.database_url = _TEMP_DB_URL
    except Exception:
        pass
    try:
        import app.database.db as app_db
        connect_args = {"check_same_thread": False}
        app_db.engine = create_engine(_TEMP_DB_URL, connect_args=connect_args, echo=False)
        app_db.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=app_db.engine)
    except Exception:
        pass
    yield

# Register cleanup on process exit
def _cleanup():
    shutil.rmtree(_TEMP_DIR, ignore_errors=True)

atexit.register(_cleanup)
