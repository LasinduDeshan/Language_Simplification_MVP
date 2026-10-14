"""
Test input loading and integrity hashes for Stage 28A benchmarks.
"""
import pytest
from app.model_comparison.input_repository import InputRepository


def test_internal_locked_full_count():
    repo = InputRepository()
    items = repo.load_internal_locked_full()
    assert len(items) == 135
    # Verify support tiers
    tiers = {it.support_level for it in items}
    assert tiers == {"mild", "moderate", "strong"}
    # Verify 45 distinct source groups
    groups = {it.source_group_id for it in items}
    assert len(groups) == 45


def test_internal_locked_clean_count():
    repo = InputRepository()
    items = repo.load_internal_locked_clean()
    assert len(items) == 39
    groups = {it.source_group_id for it in items}
    assert len(groups) == 13


def test_asset_test_split_count_and_references():
    repo = InputRepository()
    items = repo.load_asset_test_split(operating_mode="generic")
    assert len(items) == 359
    for it in items:
        assert it.support_level == "generic"
        assert len(it.reference_texts) == 10
        assert len(it.source_text.strip()) > 0


def test_input_hashes_64_characters():
    repo = InputRepository()
    h1 = repo.compute_file_sha256(repo.internal_locked_file)
    assert len(h1) == 64
    assert int(h1, 16) > 0

    asset_orig = repo.asset_dir / "asset.test.orig"
    h2 = repo.compute_file_sha256(asset_orig)
    assert len(h2) == 64
    assert int(h2, 16) > 0
