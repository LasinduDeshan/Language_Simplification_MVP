"""Tests for conflict detection and adjudication service."""
import pytest
from app.datasets.expert_review.adjudication import AdjudicationService
from app.datasets.expert_review.schemas import (
    RecordReviewSubmission,
    TaxonomyClass,
    FinalDisposition,
    DimensionRatings,
    CriticalFailureFlags,
    WorkflowFlags,
    SupportTierReview,
)


@pytest.fixture
def adj_service():
    return AdjudicationService()


def _make_sub(sub_id, reviewer_id, item_id, tax, ratings=None, crit=None, tier=None):
    return RecordReviewSubmission(
        submission_id=sub_id,
        item_id=item_id,
        reviewer_id=reviewer_id,
        batch_id="BATCH-01",
        taxonomy_class=tax,
        ratings=ratings or DimensionRatings(),
        critical_checks=crit or CriticalFailureFlags(),
        workflow_flags=WorkflowFlags(),
        support_tier_review=tier,
        submission_hash=f"hash-{sub_id}",
    )


def test_conflict_detection_taxonomy_mismatch(adj_service):
    """Detects conflict when Reviewer A and B disagree on taxonomy classification."""
    sub_a = _make_sub("S1", "REV-01", "ITEM-01", TaxonomyClass.TEXT_SIMPLIFICATION)
    sub_b = _make_sub("S2", "REV-02", "ITEM-01", TaxonomyClass.INSTRUCTION_REPHRASING)

    conflicts = adj_service.detect_conflicts(sub_a, sub_b)
    assert len(conflicts) > 0
    assert any("Taxonomy mismatch" in c for c in conflicts)


def test_conflict_detection_rating_gap(adj_service):
    """Detects conflict when key ratings differ by >= 2 points."""
    ratings_a = DimensionRatings(meaning_preservation=5)
    ratings_b = DimensionRatings(meaning_preservation=2)

    sub_a = _make_sub("S1", "REV-01", "ITEM-02", TaxonomyClass.TEXT_SIMPLIFICATION, ratings=ratings_a)
    sub_b = _make_sub("S2", "REV-02", "ITEM-02", TaxonomyClass.TEXT_SIMPLIFICATION, ratings=ratings_b)

    conflicts = adj_service.detect_conflicts(sub_a, sub_b)
    assert any("meaning_preservation gap >= 2" in c for c in conflicts)


def test_conflict_detection_critical_check_mismatch(adj_service):
    """Detects conflict when raters disagree on critical failure flags."""
    crit_a = CriticalFailureFlags(negation_changed=True)
    crit_b = CriticalFailureFlags(negation_changed=False)

    sub_a = _make_sub("S1", "REV-01", "ITEM-03", TaxonomyClass.TEXT_SIMPLIFICATION, crit=crit_a)
    sub_b = _make_sub("S2", "REV-02", "ITEM-03", TaxonomyClass.TEXT_SIMPLIFICATION, crit=crit_b)

    conflicts = adj_service.detect_conflicts(sub_a, sub_b)
    assert any("Critical flag mismatch" in c for c in conflicts)


def test_adjudication_resolution(adj_service):
    """Adjudicator binds final resolution with decision rationale."""
    sub_a = _make_sub("S1", "REV-01", "ITEM-04", TaxonomyClass.TEXT_SIMPLIFICATION)
    sub_b = _make_sub("S2", "REV-02", "ITEM-04", TaxonomyClass.INSTRUCTION_REPHRASING)

    conflicts = adj_service.detect_conflicts(sub_a, sub_b)
    adj_service.add_to_queue("ITEM-04", sub_a, sub_b, conflicts)

    record = adj_service.resolve_adjudication(
        item_id="ITEM-04",
        adjudicator_id="ADJ-01",
        final_taxonomy_class=TaxonomyClass.TEXT_SIMPLIFICATION,
        final_disposition=FinalDisposition.EXPERT_APPROVED,
        adjudicated_critical_checks=CriticalFailureFlags(),
        decision_rationale="Linguistic analysis confirms proposition is preserved with lexical simplification.",
    )

    assert record.item_id == "ITEM-04"
    assert record.adjudicator_id == "ADJ-01"
    assert record.final_taxonomy_class == TaxonomyClass.TEXT_SIMPLIFICATION
    assert record.final_disposition == FinalDisposition.EXPERT_APPROVED
    assert len(adj_service.get_unresolved_items()) == 0
