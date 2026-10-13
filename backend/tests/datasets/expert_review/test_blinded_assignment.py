"""Tests for blinded assignment service and cross-reviewer isolation."""
import os
import pytest
from app.datasets.expert_review.assignment_service import AssignmentService
from app.datasets.expert_review.manifest_repository import ManifestRepository


@pytest.fixture
def assignment_setup():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    repo = ManifestRepository(root_dir=root)
    items = repo.load_or_generate_manifest()
    service = AssignmentService()
    return service, items


def test_batch_creation_and_zero_duplicate_assignments(assignment_setup):
    """Test batches assign each item to exactly two reviewers (A and B) with zero duplicate assignments."""
    service, items = assignment_setup
    sample_items = items[:100]  # Test on slice

    batches = service.create_assignment_batches(
        items=sample_items,
        reviewer_pairs=[("REV-01", "REV-02"), ("REV-03", "REV-04")],
        batch_size=25,
    )

    assert len(batches) > 0

    # Collect assignments
    item_assignments = {}
    for batch in batches:
        for item_id in batch.item_ids:
            if item_id not in item_assignments:
                item_assignments[item_id] = []
            item_assignments[item_id].append((batch.reviewer_a_id, batch.reviewer_b_id))

    # Verify zero duplicate assignments and exactly 1 pair per item
    for item_id, pairs in item_assignments.items():
        assert len(pairs) == 1, f"Item {item_id} assigned in multiple batches: {pairs}"
        r_a, r_b = pairs[0]
        assert r_a != r_b, f"Reviewer A cannot be Reviewer B on item {item_id}"


def test_blinded_view_isolation(assignment_setup):
    """Verify blinded view completely hides model origin, dataset split, automated scores, and cross-reviewer info."""
    service, items = assignment_setup
    sample_item = items[0]

    blinded_a = service.generate_blinded_item_view(sample_item, reviewer_id="REV-01")
    blinded_b = service.generate_blinded_item_view(sample_item, reviewer_id="REV-02")

    # Both views must be blinded identically
    for blinded in (blinded_a, blinded_b):
        assert "model_family" not in blinded
        assert "generation_pipeline" not in blinded
        assert "sari_score" not in blinded
        assert "bleu_score" not in blinded
        assert "fkgl_grade" not in blinded
        assert "dataset_split" not in blinded
        assert "other_reviewer_ratings" not in blinded
        assert "other_reviewer_id" not in blinded

    # Cross-reviewer isolation: Reviewer A sees only reviewer_id: REV-01
    assert blinded_a["reviewer_id"] == "REV-01"
    assert blinded_b["reviewer_id"] == "REV-02"
    assert "REV-02" not in str(blinded_a)
    assert "REV-01" not in str(blinded_b)
