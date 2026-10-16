"""
Stage 33 — Test configuration & fixtures.
Ensures mandatory external protected storage root is set during testing.
"""

import os
from pathlib import Path
import pytest

DEFAULT_PROTECTED_ROOT = Path.home() / ".sinhala_simplification_protected_data"


@pytest.fixture(autouse=True, scope="session")
def setup_protected_storage_env():
    """Configures mandatory protected storage environment variable for tests."""
    if not os.environ.get("SINHALA_SIMPLIFICATION_PROTECTED_ROOT"):
        DEFAULT_PROTECTED_ROOT.mkdir(parents=True, exist_ok=True)
        os.environ["SINHALA_SIMPLIFICATION_PROTECTED_ROOT"] = str(DEFAULT_PROTECTED_ROOT)
