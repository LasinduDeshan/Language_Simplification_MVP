"""
Stage 33 — Unit Tests for Canonical Corpus View Denominator & Isolation.
"""

import json
from pathlib import Path
from app.sinhala_simplification.storage import PROJECT_ROOT


def test_canonical_corpus_view_metrics():
    canonical_file = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "canonical_analytical_corpus.jsonl"
    with open(canonical_file, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]

    meta_file = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "corpus_metadata.json"
    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    expected_total = meta["exact_duplicate_analytical_view"]["unique_exact_text_canonical_records"]
    expected_locked = meta["split_counts"]["locked_test"]
    expected_val = meta["split_counts"]["validation"]
    expected_train = expected_total - expected_locked - expected_val

    assert len(records) == expected_total, f"Expected {expected_total} canonical records, got {len(records)}"

    train_records = [r for r in records if r.get("split") == "train"]
    val_records = [r for r in records if r.get("split") == "validation"]
    test_records = [r for r in records if r.get("split") == "locked_test"]

    assert len(train_records) == expected_train
    assert len(val_records) == expected_val
    assert len(test_records) == expected_locked

    # Development records must be strictly isolated to train partition
    val_dev = [r for r in val_records if r.get("is_method_development_record")]
    test_dev = [r for r in test_records if r.get("is_method_development_record")]

    assert len(val_dev) == 0, "Validation partition must contain 0 development records"
    assert len(test_dev) == 0, "Locked-test partition must contain 0 development records"
