"""
Tests for Stage 32 Pipeline Determinism and Replicability (WP9).
Verifies that re-running candidate extraction produces identical entry IDs, counts, and frequencies.
"""

from pathlib import Path
import json
import pytest

from app.datasets.sinhala_lexicon.candidate_extractor import CandidateExtractor
from app.datasets.sinhala_lexicon.schemas import TokenOccurrenceRecord
from app.datasets.sinhala_lexicon.storage import lexicon_storage

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
OCCURRENCE_LEDGER = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "token_occurrence_ledger.jsonl"
CANDIDATE_LEDGER = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "candidate_entry_ledger.jsonl"

def test_pipeline_determinism_across_runs():
    """Verify candidate extraction produces identical count and IDs from occurrence ledger."""
    occurrences = []
    surface_texts = {}
    surface_to_id = {}

    with open(OCCURRENCE_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = TokenOccurrenceRecord.model_validate_json(line)
                occurrences.append(rec)
                txt = lexicon_storage.read_file_text(rec.token_text_storage_ref)
                surface_texts[rec.occurrence_id] = txt
                if rec.entry_id != "SI-LEX-000000":
                    surface_to_id[txt] = rec.entry_id

    extractor = CandidateExtractor()
    run1 = extractor.extract_candidate_entries(occurrences, surface_to_id, surface_texts)
    run2 = extractor.extract_candidate_entries(occurrences, surface_to_id, surface_texts)

    assert len(run1) == len(run2) == 1010
    for c1, c2 in zip(run1, run2):
        assert c1.entry_id == c2.entry_id
        assert c1.canonical_form == c2.canonical_form
        assert c1.canonical_frequency == c2.canonical_frequency
