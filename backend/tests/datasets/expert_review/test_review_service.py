"""Tests for Review Service, idempotency, and critical-failure precedence."""
import pytest
from app.datasets.expert_review.review_service import ReviewService
from app.datasets.expert_review.schemas import (
    TaxonomyClass,
    FinalDisposition,
    DimensionRatings,
    CriticalFailureFlags,
    WorkflowFlags,
    AuthorizationDecisions,
)


@pytest.fixture
def review_service():
    return ReviewService(expected_submissions=3360)


def test_submission_idempotency(review_service):
    """Proves duplicate review submissions return identical submission_id without duplicate counting."""
    sub1 = review_service.submit_review(
        item_id="SIMP-EN-000001",
        reviewer_id="REV-01",
        batch_id="BATCH-01",
        taxonomy_class=TaxonomyClass.TEXT_SIMPLIFICATION,
        ratings=DimensionRatings(),
        critical_checks=CriticalFailureFlags(),
        workflow_flags=WorkflowFlags(),
    )
    assert review_service.accounting.completed_submissions == 1

    # Resubmit identical review
    sub2 = review_service.submit_review(
        item_id="SIMP-EN-000001",
        reviewer_id="REV-01",
        batch_id="BATCH-01",
        taxonomy_class=TaxonomyClass.TEXT_SIMPLIFICATION,
        ratings=DimensionRatings(),
        critical_checks=CriticalFailureFlags(),
        workflow_flags=WorkflowFlags(),
    )
    assert sub1.submission_id == sub2.submission_id
    assert sub1.submission_hash == sub2.submission_hash
    # completed_submissions must still be 1 (zero duplication in ledger)
    assert review_service.accounting.completed_submissions == 1


def test_critical_failure_override(review_service):
    """Proves that a critical failure flag overrides high numerical ratings (5/5)."""
    # High ratings (perfect 5/5) but critical failure: meaning_changed = True
    perfect_ratings = DimensionRatings(
        meaning_preservation=5,
        grammatical_correctness=5,
        syntactic_simplicity=5,
        vocabulary_accessibility=5,
        age_appropriateness=5,
        support_level_appropriateness=5,
        instructional_actionability=5,
        cognitive_load_reduction=5,
        protected_element_preservation=5,
        overall_suitability=5,
    )
    critical_flags = CriticalFailureFlags(meaning_changed=True)

    submission = review_service.submit_review(
        item_id="SIMP-EN-000002",
        reviewer_id="REV-01",
        batch_id="BATCH-01",
        taxonomy_class=TaxonomyClass.TEXT_SIMPLIFICATION,
        ratings=perfect_ratings,
        critical_checks=critical_flags,
        workflow_flags=WorkflowFlags(),
    )

    disposition = submission.determine_provisional_disposition()
    assert disposition == FinalDisposition.REJECTED_MEANING_CHANGE
    assert disposition != FinalDisposition.EXPERT_APPROVED


def test_safety_critical_failure_override(review_service):
    """Proves that safety violations or answer leakage immediately trigger REJECTED_SAFETY."""
    critical_flags = CriticalFailureFlags(answer_leakage_detected=True)
    submission = review_service.submit_review(
        item_id="SIMP-EN-000003",
        reviewer_id="REV-02",
        batch_id="BATCH-01",
        taxonomy_class=TaxonomyClass.TEXT_SIMPLIFICATION,
        ratings=DimensionRatings(),
        critical_checks=critical_flags,
        workflow_flags=WorkflowFlags(),
    )
    assert submission.determine_provisional_disposition() == FinalDisposition.REJECTED_SAFETY


def test_unsupervised_child_delivery_invariant():
    """Proves that approved_for_unsupervised_child_delivery cannot be set to True."""
    with pytest.raises(ValueError, match="must NEVER be True in Stage 27"):
        AuthorizationDecisions(approved_for_unsupervised_child_delivery=True)
