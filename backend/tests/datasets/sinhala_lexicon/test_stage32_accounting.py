"""
Tests for Stage 32 Accounting Equations and Zero-Loss Guarantees (WP9).
"""

from pathlib import Path
import pytest
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.stage32.verify_stage32_accounting import verify_all_accounting

def test_stage32_all_accounting_levels():
    """Verify all 5 levels of accounting reconcile with zero unaccounted units."""
    assert verify_all_accounting() is True
