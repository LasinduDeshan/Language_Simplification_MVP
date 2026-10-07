"""
Unit tests for Stage 20 Split Builder.
"""
import pytest
from app.datasets.expansion.split_builder import SplitBuilder

def test_group_aware_split_assignment():
    splitter = SplitBuilder(seed=42)
    
    # 10 groups with 3 pairs each = 30 pairs
    records = []
    for g in range(10):
        for p in range(3):
            records.append({
                "source_item_id": f"SRC-GROUP-{g}",
                "pair_id": f"SIMP-{g}-{p}",
                "schema_version": "1.0.0",
                "provenance": {"created_by": "user", "batch_id": "B1"}
            })

    eligible, excluded = splitter.filter_candidate_eligibility(records)
    splits = splitter.build_group_aware_splits(eligible)

    train_cnt = len(splits["development_candidate_train"])
    val_cnt = len(splits["development_candidate_validation"])
    test_cnt = len(splits["development_candidate_test"])

    assert train_cnt + val_cnt + test_cnt == 30
    
    # Verify group integrity: each group in only one split
    group_splits = {}
    for split_name, recs in splits.items():
        for r in recs:
            gid = r["source_item_id"]
            if gid in group_splits:
                assert group_splits[gid] == split_name
            else:
                group_splits[gid] = split_name
