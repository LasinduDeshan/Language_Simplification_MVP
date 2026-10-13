"""Tests for revision provenance, Stage 14/15 hooks, Release 0.2.0 immutability, and Release 0.3.0 building."""
import os
import json
import pytest

from app.datasets.expert_review.revision_service import RevisionService
from app.datasets.expert_review.release_builder import ReleaseBuilder
from app.datasets.expert_review.schemas import (
    ReviewRecordType,
    FinalDisposition,
    TaxonomyClass,
    InventoryAccounting,
    ReviewManifestItem,
    SupportLevel,
)


@pytest.fixture
def root_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


@pytest.fixture
def rev_service():
    return RevisionService()


def test_revision_provenance_and_validation_hooks(rev_service):
    """Tests that text revisions preserve hashes and pass Stage 14/15 validation hooks."""
    original = "The dog sprinted across the meadow."
    revised = "The dog ran across the grass."

    rev = rev_service.create_revision(
        item_id="SIMP-EN-000001",
        original_text=original,
        revised_text=revised,
        source_group_id="SRC-001",
        revision_reason="Simplify vocabulary ('sprinted' -> 'ran', 'meadow' -> 'grass')",
        revised_by="ADJ-01",
        record_type=ReviewRecordType.SIMPLIFICATION_PAIR,
        support_level="moderate",
    )

    assert rev.item_id == "SIMP-EN-000001"
    assert rev.original_hash != rev.revised_hash
    assert rev.stage14_schema_validation == "PASSED"
    assert rev.stage15_quality_validation == "PASSED"
    assert rev.final_disposition == FinalDisposition.APPROVED_WITH_REVISION

    # Audit trail verifies privacy protection
    audit = rev_service.get_sanitized_audit_trail()
    assert len(audit) == 1
    assert "ADJ-01" not in str(audit[0])  # sanitized
    assert audit[0]["original_hash"] == rev.original_hash


def test_revision_empty_text_rejected(rev_service):
    """Empty revision text must be rejected."""
    with pytest.raises(ValueError, match="revised_text cannot be empty"):
        rev_service.create_revision(
            item_id="SIMP-EN-000002",
            original_text="Valid text",
            revised_text="   ",
            source_group_id="SRC-002",
            revision_reason="Invalid empty",
            revised_by="ADJ-01",
        )


def test_release_0_2_0_hard_immutability(root_dir):
    """Verifies that all files in Release 0.2.0 remain strictly byte-for-byte unmodified."""
    builder = ReleaseBuilder(root_dir=root_dir)
    verified_hashes = builder.verify_release_0_2_0_immutability()
    assert len(verified_hashes) == 6
    assert "simplification_corpus.json" in verified_hashes
    assert "dataset_issue_register.json" in verified_hashes


def test_release_0_3_0_builder_and_auxiliary_partitioning(root_dir, rev_service, tmp_path):
    """Tests building Release 0.3.0, ensuring auxiliary partitioning and checksum manifest generation."""
    builder = ReleaseBuilder(root_dir=root_dir)
    builder.rel_0_3_0_dir = str(tmp_path / "0.3.0")

    # Mock manifest item
    sample_items = [
        ReviewManifestItem(
            item_id="SIMP-EN-000001",
            source_group_id="SRC-001",
            record_type=ReviewRecordType.SIMPLIFICATION_PAIR,
            text_stimulus="The big cat sat.",
            target_text="The cat sat.",
            support_level=SupportLevel.MODERATE,
            content_hash="abc123hash",
        ),
        ReviewManifestItem(
            item_id="SIMP-EN-000002",
            source_group_id="SRC-002",
            record_type=ReviewRecordType.SIMPLIFICATION_PAIR,
            text_stimulus="Circle the animal.",
            target_text="Find the dog.",
            support_level=SupportLevel.MILD,
            content_hash="def456hash",
        ),
    ]

    accounting = InventoryAccounting()

    build_res = builder.build_release_0_3_0(
        manifest_items=sample_items,
        adjudication_records={},
        revisions={},
        inventory_accounting=accounting,
    )

    assert build_res["release_version"] == "0.3.0"
    assert os.path.exists(os.path.join(builder.rel_0_3_0_dir, "simplification_corpus.json"))
    assert os.path.exists(os.path.join(builder.rel_0_3_0_dir, "release_manifest.json"))
    assert os.path.exists(os.path.join(builder.rel_0_3_0_dir, "release_manifest.sha256"))
