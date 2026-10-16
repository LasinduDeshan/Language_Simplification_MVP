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
    with open(canonical_file, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]

    partitions = {r.get("split") for r in records}
    assert partitions == {"train", "validation", "locked_test"}

    # Locked test must be completely isolated
    locked = [r for r in records if r.get("split") == "locked_test"]
    assert len(locked) == 13
    for r in locked:
        assert r.get("is_method_development_record") is False
