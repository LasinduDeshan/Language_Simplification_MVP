"""Tests for synthetic deferred candidate dataset adapters."""

import pytest
from app.datasets.external_english.adapters.deferred_adapter import SyntheticDeferredAdapter


def test_turkcorpus_synthetic_adapter():
    adapter = SyntheticDeferredAdapter(
        dataset_id="EXTDATA-TURKCORPUS",
        status_reason="pending_content_rights_verification",
    )
    rec = adapter.parse_synthetic_fixture(
        raw_source="This is a complex synthetic source sentence.",
        raw_refs=[f"Synthetic reference simplification {i}." for i in range(8)],
        source_idx=1,
        split="validation",
    )
    assert rec.dataset_id == "EXTDATA-TURKCORPUS"
    assert rec.reference_count == 8
    assert rec.final_disposition == "excluded_rights"
    assert rec.benchmark_eligible is False
    assert rec.training_eligible is False
    assert rec.provenance["is_synthetic_fixture"] is True


def test_oasissimp_synthetic_adapter():
    adapter = SyntheticDeferredAdapter(
        dataset_id="EXTDATA-OASISSIMP-EN",
        status_reason="pending_content_rights_verification",
    )
    rec = adapter.parse_synthetic_fixture(
        raw_source="A specialized scientific sentence for child adaptation testing.",
        raw_refs=["A simple sentence for children."],
        source_idx=1,
        split="test",
    )
    assert rec.dataset_id == "EXTDATA-OASISSIMP-EN"
    assert rec.reference_count == 1
    assert rec.final_disposition == "excluded_rights"
    assert rec.benchmark_eligible is False
