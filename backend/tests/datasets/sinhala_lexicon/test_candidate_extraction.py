"""
Tests for Candidate Lexicon Extraction and Quality Routing (WP3).
Verifies deterministic extraction, zero collision in entry IDs,
proper noun routing, and mixed script / sensitive word policies.
"""

from pathlib import Path
import json
import pytest

from app.datasets.sinhala_lexicon.enums import TerminalEntryDisposition
from app.datasets.sinhala_lexicon.quality_router import LexiconQualityRouter
from app.datasets.sinhala_lexicon.schemas import CandidateLexiconEntry

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
CANDIDATE_LEDGER = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "candidate_entry_ledger.jsonl"
ACCOUNTING_FILE = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "candidate_entry_accounting.json"

def test_candidate_entry_ids_are_deterministic_and_unique():
    """Verify all 1010 candidate entries have unique, valid SI-LEX-XXXXXX IDs."""
    assert CANDIDATE_LEDGER.exists()
    entries = []
    ids = set()

    with open(CANDIDATE_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            entry = CandidateLexiconEntry.model_validate_json(line)
            entries.append(entry)
            ids.add(entry.entry_id)

    assert len(entries) == 1010
    assert len(ids) == 1010
    # Sequential verification
    for idx, entry in enumerate(entries, start=1):
        assert entry.entry_id == f"SI-LEX-{idx:06d}"

def test_candidate_entry_accounting_reconciles():
    """Verify candidate accounting equation resolves with zero unaccounted entries."""
    assert ACCOUNTING_FILE.exists()
    with open(ACCOUNTING_FILE, "r", encoding="utf-8") as f:
        acc = json.load(f)

    assert acc["unaccounted_entries"] == 0
    assert acc["total_extracted_candidates"] == 1010
    assert acc["accepted_draft_entries"] + acc["manual_review_required_entries"] + acc["excluded_non_lexical_entries"] == 1010

def test_sensitive_vocabulary_routing():
    """Verify sensitive or clinical vocabulary triggers quality flags and review routing."""
    router = LexiconQualityRouter()
    flags, findings, is_proper, is_sensitive = router.screen_surface_form("රෝගියා")
    assert "POTENTIALLY_SENSITIVE_SEMANTIC_REVIEW" in flags
    assert is_sensitive is True
    assert len(findings) == 1
    assert findings[0].reason_code == "POTENTIALLY_SENSITIVE_SEMANTIC_REVIEW"
    assert findings[0].rule_id == "STAGE32-RULE-SEMANTIC-SENSITIVE-HEURISTIC-V1"

def test_mixed_script_detection():
    """Verify mixed script surface forms trigger MIXED_SCRIPT_PRESENT flag."""
    router = LexiconQualityRouter()
    flags, findings, _, _ = router.screen_surface_form("COVID-19රෝගය")
    assert "MIXED_SCRIPT_PRESENT" in flags
    assert any(f.reason_code == "MIXED_SCRIPT_PRESENT" for f in findings)

def test_ocr_artifact_detection():
    """Verify excessive character repetition triggers suspected OCR flag."""
    router = LexiconQualityRouter()
    flags, findings, _, _ = router.screen_surface_form("ගගගගස")
    assert "OCR_OR_REPETITION_FLAG" in flags
    assert any(f.reason_code == "OCR_OR_REPETITION_FLAG" for f in findings)
