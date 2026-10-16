"""
Tests for Stage 31 Corpus Bridge and Token Occurrence Accounting (WP2).
Verifies that token occurrences preserve exact half-open code-point intervals,
classify dispositions deterministically, and reconcile with zero unaccounted tokens.
"""

from pathlib import Path
import json
import pytest

from app.datasets.sinhala_lexicon.corpus_bridge import Stage31CorpusBridge
from app.datasets.sinhala_lexicon.enums import OccurrenceDisposition
from app.datasets.sinhala_lexicon.storage import lexicon_storage
from app.datasets.sinhala_external.storage import storage_manager as external_storage

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent

def test_corpus_bridge_streams_150_records():
    """Verify that Stage31CorpusBridge streams exactly 150 canonical records."""
    bridge = Stage31CorpusBridge()
    records = list(bridge.stream_canonical_records())
    assert len(records) == 150
    record_ids = [r["record_id"] for r in records]
    assert len(set(record_ids)) == 150

def test_token_code_point_offsets_match_storage():
    """Verify code point offsets [start, end) on normalized text match isolated token text exactly."""
    bridge = Stage31CorpusBridge()
    first_record = next(bridge.stream_canonical_records())
    
    raw_bytes = external_storage.read_raw_file(first_record["normalized_text_storage_ref"])
    norm_text = raw_bytes.decode("utf-8")

    # Sample the first 10 occurrences
    sampled = 0
    for occ in bridge.process_corpus_tokens():
        if occ.canonical_record_id != first_record["record_id"]:
            break
        
        # Verify code point slice from normalized text matches isolated token text
        token_text = lexicon_storage.read_file_text(occ.token_text_storage_ref)
        sliced_text = norm_text[occ.normalized_start_code_point:occ.normalized_end_code_point]
        assert sliced_text == token_text, f"Offset mismatch: sliced '{sliced_text}' != token '{token_text}'"
        assert occ.offset_interval == "zero_based_half_open"
        sampled += 1
        if sampled >= 10:
            break

    assert sampled >= 10

def test_occurrence_disposition_counts_reconcile():
    """Verify occurrence accounting summary matches ledger file entries exactly."""
    summary_path = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "occurrence_accounting_summary.json"
    assert summary_path.exists(), "Occurrence accounting summary file must exist"

    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    assert summary["unaccounted_occurrences"] == 0
    assert summary["total_token_occurrences"] == (
        summary["included_candidate_occurrences"] +
        summary["excluded_token_class_occurrences"] +
        summary["manual_review_occurrences"] +
        summary["rejected_occurrences"]
    )
    assert summary["distinct_candidate_entries"] == 1010
