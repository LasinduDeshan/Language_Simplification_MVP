"""Tests for official ASSET dataset adapter."""

from pathlib import Path
import pytest

from app.datasets.external_english.adapters.asset_adapter import ASSETAdapter


@pytest.fixture
def asset_adapter():
    return ASSETAdapter()


def test_asset_adapter_validation_records(asset_adapter):
    val_records = asset_adapter.load_validation_records()
    assert len(val_records) == 2000
    
    # Check first record structure
    rec1 = val_records[0]
    assert rec1.external_record_id == "EXTREC-ASSET-VAL-0001"
    assert rec1.source_group_id == "ASSET-VAL-0001"
    assert rec1.original_source_split == "validation"
    assert rec1.reference_count == 10
    assert len(rec1.raw_references) == 10
    assert len(rec1.evaluation_references) == 10
    assert rec1.raw_text_preserved is True
    assert rec1.evaluation_view_derived is True
    assert rec1.evaluation_protected is True
    assert rec1.approved_for_child_delivery is False
    assert rec1.training_eligible is False
    assert rec1.benchmark_eligible is True
    assert rec1.final_disposition == "benchmark_only"
    assert len(rec1.content_hash) == 64


def test_asset_adapter_test_records(asset_adapter):
    test_records = asset_adapter.load_test_records()
    assert len(test_records) == 359
    
    rec_last = test_records[-1]
    assert rec_last.external_record_id == "EXTREC-ASSET-TEST-0359"
    assert rec_last.source_group_id == "ASSET-TEST-0359"
    assert rec_last.original_source_split == "test"
    assert rec_last.reference_count == 10
    assert len(rec_last.raw_references) == 10
    assert len(rec_last.evaluation_references) == 10


def test_asset_adapter_total_accounting(asset_adapter):
    all_records = asset_adapter.load_all_records()
    assert len(all_records) == 2359
    
    total_refs = sum(r.reference_count for r in all_records)
    assert total_refs == 23590

    # Ensure all record IDs and source group IDs are unique
    rec_ids = {r.external_record_id for r in all_records}
    assert len(rec_ids) == 2359

    group_ids = {r.source_group_id for r in all_records}
    assert len(group_ids) == 2359
