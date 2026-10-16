"""
Stage 33 — Unit Tests for Partition Isolation.
Verifies that rule development and evaluation denominator strictly respect train partition.
"""

import json
from pathlib import Path
from app.sinhala_simplification.enums import Partition
from app.sinhala_simplification.storage import PROJECT_ROOT


def test_partition_boundaries_in_canonical_corpus():
    canonical_file = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "canonical_analytical_corpus.jsonl"
    meta_file = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "corpus_metadata.json"

    with open(canonical_file, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]

    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    expected_locked_count = meta["split_counts"]["locked_test"]
    expected_val_count = meta["split_counts"]["validation"]
    expected_canonical_total = meta["exact_duplicate_analytical_view"]["unique_exact_text_canonical_records"]

    partitions = {r.get("split") for r in records}
    assert partitions == {"train", "validation", "locked_test"}

    locked = [r for r in records if r.get("split") == "locked_test"]
    val = [r for r in records if r.get("split") == "validation"]
    train = [r for r in records if r.get("split") == "train"]

    # Verify dynamic parity
    assert len(records) == expected_canonical_total
    assert len(locked) == expected_locked_count
    assert len(val) == expected_val_count
    assert len(train) == expected_canonical_total - expected_locked_count - expected_val_count

    # Locked test must be completely isolated and contain zero development predeclared records
    for r in locked:
        assert r.get("is_method_development_record") is False
