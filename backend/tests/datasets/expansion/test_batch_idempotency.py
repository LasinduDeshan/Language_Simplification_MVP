"""
Unit tests for Stage 20 Batch Idempotency & Immutability.
"""
import pytest
import hashlib
import json
from app.datasets.expansion.split_builder import SplitBuilder

def test_split_generation_deterministic_with_same_seed():
    splitter_1 = SplitBuilder(seed=42)
    splitter_2 = SplitBuilder(seed=42)

    records = [
        {"source_item_id": f"SRC-{i}", "pair_id": f"SIMP-{i}", "schema_version": "1.0.0", "provenance": {"created_by": "u", "batch_id": "B"}}
        for i in range(50)
    ]

    splits_1 = splitter_1.build_group_aware_splits(records)
    splits_2 = splitter_2.build_group_aware_splits(records)

    hash_1 = hashlib.sha256(json.dumps(splits_1, sort_keys=True).encode()).hexdigest()
    hash_2 = hashlib.sha256(json.dumps(splits_2, sort_keys=True).encode()).hexdigest()

    assert hash_1 == hash_2
