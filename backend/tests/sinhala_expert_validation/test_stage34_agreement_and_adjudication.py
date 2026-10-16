"""
Unit tests for Stage 34 agreement metrics and adjudication logic.
Validates:
1. Krippendorff's alpha (nominal and ordinal) math and missingness handling;
2. Bootstrap 95% confidence interval properties;
3. Adjudication queue inspection triggers and Level 6 accounting reconciliation.
"""

import pytest

from app.datasets.sinhala_expert_validation.adjudication import AdjudicationService
from app.datasets.sinhala_expert_validation.agreement import (
    bootstrap_ci,
    compute_exact_agreement,
    compute_krippendorff_alpha_nominal,
    compute_krippendorff_alpha_ordinal,
)
from app.datasets.sinhala_expert_validation.enums import (
    AdjudicationDisposition,
    DimensionStatus,
    OverallDisposition,
    ReasonCode,
    SafetyFlag,
    SimplicityRating,
)
from app.datasets.sinhala_expert_validation.schemas import (
    AdjudicationRecord,
    AnnotationRecord,
    DimensionRating,
)


def test_krippendorff_alpha_perfect_agreement():
    # If all raters agree on all items, alpha must be 1.0
    data: dict[str, dict[str, Any]] = {
        "ITEM-1": {"R1": 3, "R2": 3, "R3": 3},
        "ITEM-2": {"R1": 2, "R2": 2, "R3": 2},
        "ITEM-3": {"R1": 1, "R2": 1, "R3": 1},
    }
    alpha_ord = compute_krippendorff_alpha_ordinal(data)
    assert alpha_ord == 1.0

    alpha_nom = compute_krippendorff_alpha_nominal(data)
    assert alpha_nom == 1.0


def test_krippendorff_alpha_missingness_support():
    # Raters with None (CANNOT_ASSESS) should not break computation
    data: dict[str, dict[str, Any]] = {
        "ITEM-1": {"R1": 3, "R2": 3, "R3": None},
        "ITEM-2": {"R1": 2, "R2": 2, "R3": None},
        "ITEM-3": {"R1": None, "R2": 1, "R3": 1},
    }
    alpha_ord = compute_krippendorff_alpha_ordinal(data)
    assert alpha_ord == 1.0


def test_bootstrap_ci():
    data: dict[str, dict[str, Any]] = {
        "ITEM-1": {"R1": 3, "R2": 3},
        "ITEM-2": {"R1": 2, "R2": 2},
        "ITEM-3": {"R1": 1, "R2": 1},
    }
    low, high = bootstrap_ci(data, compute_krippendorff_alpha_ordinal, n_resamples=50, seed=42)
    assert low <= high
    assert high <= 1.0


def _build_dummy_annotation(ann_id: str, item_id: str, rev_id: str, m_score: int, disp: OverallDisposition) -> AnnotationRecord:
    return AnnotationRecord(
        annotation_id=ann_id,
        item_id=item_id,
        reviewer_id=rev_id,
        assignment_id=f"ASN-{ann_id}",
        rubric_version="S34-RUBRIC-V1",
        rubric_hash="80b60486002208f63df1b67caa82b7a90611907e11b617233595cb69b933de23",
        submitted_at="2026-10-16T12:00:00Z",
        meaning_preservation=DimensionRating(status=DimensionStatus.RATED, score=m_score),
        grammatical_acceptability=DimensionRating(status=DimensionStatus.RATED, score=3),
        morphology_preservation=DimensionRating(status=DimensionStatus.NOT_APPLICABLE, score=None),
        fluency_naturalness=DimensionRating(status=DimensionStatus.RATED, score=3),
        simplicity_improvement=DimensionRating(status=DimensionStatus.RATED, score=SimplicityRating.SAME.value),
        vocabulary_suitability=DimensionRating(status=DimensionStatus.RATED, score=3),
        sentence_structure_suitability=DimensionRating(status=DimensionStatus.RATED, score=3),
        developmental_suitability=DimensionRating(status=DimensionStatus.RATED, score=3),
        safety=DimensionRating(status=DimensionStatus.RATED, score=SafetyFlag.NO_FLAG.value),
        overall_disposition=DimensionRating(status=DimensionStatus.RATED, score=disp.value),
        is_draft=False,
    )


def test_adjudication_triggers_and_reconciliation(tmp_path):
    adj_service = AdjudicationService()

    # Create 2 annotations with meaning spread >= 2 (m_score 1 vs 3)
    ann1 = _build_dummy_annotation("ANN-T1", "ITEM-T1", "REV-001", m_score=1, disp=OverallDisposition.REVISE)
    ann2 = _build_dummy_annotation("ANN-T2", "ITEM-T1", "REV-002", m_score=3, disp=OverallDisposition.ACCEPT_DRAFT)

    queue_entry = adj_service.inspect_item_for_adjudication("ITEM-T1", [ann1, ann2])
    assert queue_entry is not None
    assert "MAJOR_SEMANTIC_DRIFT" in queue_entry["triggers"]
    assert "MEANING_SPREAD_GE_2" in queue_entry["triggers"]

    # Before resolution: Level 6 accounting shows 1 pending
    acc_before = adj_service.reconcile_adjudication_accounting()
    assert acc_before["total_queue"] == 1
    assert acc_before["pending"] == 1
    assert acc_before["resolved"] == 0

    # Resolve adjudication
    adj_rec = AdjudicationRecord(
        adjudication_id="ADJ-TEST-001",
        item_id="ITEM-T1",
        independent_annotation_ids=["ANN-T1", "ANN-T2"],
        adjudicator_id="REV-S34-006",
        final_disposition=AdjudicationDisposition.REVISE_RULE_OUTPUT,
        reason_codes=[ReasonCode.SEMANTIC_OMISSION],
        rationale_ref="protected://stage34/adjudications/ADJ-TEST-001.json",
        resolved=True,
    )
    adj_service.record_adjudication(adj_rec)

    # After resolution: Level 6 accounting shows 1 resolved, 0 pending, 0 unaccounted
    acc_after = adj_service.reconcile_adjudication_accounting()
    assert acc_after["total_queue"] == 1
    assert acc_after["resolved"] == 1
    assert acc_after["pending"] == 0
    assert acc_after["unaccounted"] == 0
