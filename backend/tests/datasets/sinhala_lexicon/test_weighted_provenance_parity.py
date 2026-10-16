"""
Tests for Weighted Provenance Parity and Zero Inflation Verification in Stage 32 (WP5).
Verifies that no frequency inflation was detected under the frozen exact-duplicate
clusters, weights, canonical mappings, and declared numerical tolerance (1e-6).
"""

from pathlib import Path
import json
import pytest

from app.datasets.sinhala_lexicon.parity_analyzer import ParityAnalyzer
from app.datasets.sinhala_lexicon.schemas import CandidateLexiconEntry

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
CANDIDATE_LEDGER = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "candidate_entry_ledger.jsonl"
CANONICAL_PATH = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "canonical_analytical_corpus.jsonl"
PROVENANCE_PATH = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "pilot_corpus.jsonl"

def test_weighted_provenance_parity_diagnostic():
    """Verify weighted provenance parity across all candidates and 180 records."""
    assert CANDIDATE_LEDGER.exists()
    candidates = []
    with open(CANDIDATE_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                candidates.append(CandidateLexiconEntry.model_validate_json(line))

    analyzer = ParityAnalyzer(tolerance=1e-6)
    report = analyzer.run_parity_diagnostic(
        candidates=candidates,
        provenance_records_path=PROVENANCE_PATH,
        canonical_records_path=CANONICAL_PATH
    )

    assert report["parity_status"] == "VERIFIED_NO_INFLATION_DETECTED"
    assert report["provenance_records"] == 180
    assert report["canonical_records"] == 150
    assert report["invalid_weights"] == 0
    assert report["canonical_mapping_failures"] == 0
    assert report["per_term_parity_failures"] == 0
    assert report["maximum_absolute_delta"] <= 1e-6
