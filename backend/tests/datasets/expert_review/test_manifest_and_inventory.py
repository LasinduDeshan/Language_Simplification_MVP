"""Tests for Stage 27 review manifest inventory and cryptographic integrity."""
import os
import json
import hashlib
import pytest

from app.datasets.expert_review.manifest_repository import ManifestRepository
from app.datasets.expert_review.schemas import (
    ReviewRecordType,
    SubmissionAccounting,
    InventoryAccounting,
)


@pytest.fixture
def repo():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    return ManifestRepository(root_dir=root)


def test_manifest_inventory_counts(repo):
    """Verifies inventory accounting: 1,110 pairs, 378 lexicon entries, 192 activities, 326 reformulation candidates."""
    items = repo.load_or_generate_manifest()
    
    pairs = [i for i in items if i.record_type == ReviewRecordType.SIMPLIFICATION_PAIR]
    lexicon = [i for i in items if i.record_type == ReviewRecordType.LEXICON_ENTRY]
    activities = [i for i in items if i.record_type == ReviewRecordType.ADAPTATION_ACTIVITY]
    reformulations = [i for i in items if i.is_reformulation_candidate]

    assert len(pairs) == 1110, f"Expected 1,110 pairs, got {len(pairs)}"
    assert len(lexicon) == 378, f"Expected 378 lexicon entries, got {len(lexicon)}"
    assert len(activities) == 192, f"Expected 192 adaptation activities, got {len(activities)}"
    assert len(items) == 1680, f"Expected 1,680 total items, got {len(items)}"
    assert len(reformulations) == 326, f"Expected 326 reformulation candidates, got {len(reformulations)}"


def test_manifest_file_sha256_hash_match(repo):
    """Verifies that the frozen manifest JSON strictly matches its .sha256 hash file."""
    json_path = os.path.join(repo.manifest_dir, "review_manifest_v1.json")
    sha_path = os.path.join(repo.manifest_dir, "review_manifest_v1.sha256")

    assert os.path.exists(json_path), "review_manifest_v1.json missing"
    assert os.path.exists(sha_path), "review_manifest_v1.sha256 missing"

    with open(json_path, "rb") as fp:
        actual_hash = hashlib.sha256(fp.read()).hexdigest()

    with open(sha_path, "r", encoding="utf-8") as fp:
        expected_hash = fp.read().strip().split()[0]

    assert actual_hash == expected_hash, f"Hash mismatch: actual {actual_hash} != expected {expected_hash}"


def test_submission_accounting_invariants():
    """Verifies the independent submission accounting target: 3,360 = completed + revoked + pending + unaccounted."""
    accounting = SubmissionAccounting(
        expected_submissions=3360,
        completed_submissions=3360,
        revoked_incomplete_submissions=0,
        pending_reassigned_submissions=0,
        unaccounted_submissions=0,
    )
    assert accounting.verify_conservation() is True

    # Fail if unaccounted > 0
    invalid_accounting = SubmissionAccounting(
        expected_submissions=3360,
        completed_submissions=3300,
        unaccounted_submissions=60,
    )
    assert invalid_accounting.verify_conservation() is False
