"""
Tests for Canonical Frequency Accounting in Stage 32 (WP5).
Verifies that primary statistics are computed strictly over the 150 canonical records,
and bounded source dispersion obeys the fixed K entropy formula.
"""

from pathlib import Path
import json
import pytest

from app.datasets.sinhala_lexicon.parity_analyzer import ParityAnalyzer
from app.datasets.sinhala_lexicon.schemas import CandidateLexiconEntry

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
CANDIDATE_LEDGER = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "candidate_entry_ledger.jsonl"

def test_bounded_source_dispersion_formula():
    """Verify source dispersion calculation handles single source and multi-source distributions."""
    analyzer = ParityAnalyzer()

    # K = 1: returns 0.0 by definition (avoiding log_1)
    d0 = analyzer.compute_bounded_source_dispersion({"SRC-1": 10}, eligible_source_count=1)
    assert d0 == 0.0

    # Single source in K = 5: entropy is 0.0, dispersion = 0.0
    d1 = analyzer.compute_bounded_source_dispersion({"SRC-1": 10}, eligible_source_count=5)
    assert d1 == 0.0

    # Perfectly uniform across all K = 5 sources: dispersion = 1.0
    uniform_dist = {f"SRC-{i}": 10 for i in range(1, 6)}
    d_uniform = analyzer.compute_bounded_source_dispersion(uniform_dist, eligible_source_count=5)
    assert abs(d_uniform - 1.0) < 1e-4

    # Skewed distribution: 0 < dispersion < 1.0
    skewed_dist = {"SRC-1": 8, "SRC-2": 2}
    d_skewed = analyzer.compute_bounded_source_dispersion(skewed_dist, eligible_source_count=5)
    assert 0.0 < d_skewed < 1.0

def test_canonical_frequencies_are_positive_integers():
    """Verify all candidate entries have canonical_frequency >= 1 and document_frequency in [1, 150]."""
    assert CANDIDATE_LEDGER.exists()
    with open(CANDIDATE_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            entry = CandidateLexiconEntry.model_validate_json(line)
            assert entry.canonical_frequency >= 1
            assert 1 <= entry.canonical_document_frequency <= 150
            assert entry.eligible_source_count >= 1
            assert 1 <= entry.observed_source_count <= entry.eligible_source_count
