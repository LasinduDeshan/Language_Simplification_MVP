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

    assert len(records) == 150, f"Expected 150 canonical records, got {len(records)}"

    train_records = [r for r in records if r.get("split") == "train"]
    val_records = [r for r in records if r.get("split") == "validation"]
    test_records = [r for r in records if r.get("split") == "locked_test"]

    assert len(train_records) == 124
    assert len(val_records) == 13
    assert len(test_records) == 13

    # Development records must be strictly isolated to train partition
    val_dev = [r for r in val_records if r.get("is_method_development_record")]
    test_dev = [r for r in test_records if r.get("is_method_development_record")]

    assert len(val_dev) == 0, "Validation partition must contain 0 development records"
    assert len(test_dev) == 0, "Locked-test partition must contain 0 development records"
