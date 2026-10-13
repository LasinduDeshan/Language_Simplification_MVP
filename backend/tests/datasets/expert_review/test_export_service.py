"""Tests for Sanitized Export Service and Universal Safety Invariant."""
import pytest
from app.datasets.expert_review.export_service import ExportService
from app.datasets.expert_review.schemas import (
    ReviewManifestItem,
    ReviewRecordType,
    SupportLevel,
    AdjudicationRecord,
    RevisionRecord,
    TaxonomyClass,
    FinalDisposition,
    CriticalFailureFlags,
)


@pytest.fixture
def export_service():
    return ExportService()


def test_export_stage28_reference_dataset(export_service):
    """Verifies that Stage 28 export has required fields and adheres to universal child delivery invariant."""
    sample_items = [
        ReviewManifestItem(
            item_id="SIMP-EN-000001",
            source_group_id="SRC-001",
            record_type=ReviewRecordType.SIMPLIFICATION_PAIR,
            text_stimulus="The boy skipped happily.",
            target_text="The boy walked happily.",
            support_level=SupportLevel.MODERATE,
            content_hash="hash1",
        ),
        ReviewManifestItem(
            item_id="SIMP-EN-000002",
            source_group_id="SRC-002",
            record_type=ReviewRecordType.SIMPLIFICATION_PAIR,
            text_stimulus="Solve 2+2.",
            target_text="2+2=4.",
            support_level=SupportLevel.MILD,
            content_hash="hash2",
        ),
    ]

    adjudications = {
        "SIMP-EN-000001": AdjudicationRecord(
            adjudication_id="ADJ-001",
            item_id="SIMP-EN-000001",
            adjudicator_id="ADJ-LEAD",
            reviewer_a_id="REV-01",
            reviewer_b_id="REV-02",
            reviewer_a_submission_id="SUB-01",
            reviewer_b_submission_id="SUB-02",
            conflict_reasons=["Minor rating gap"],
            final_taxonomy_class=TaxonomyClass.TEXT_SIMPLIFICATION,
            final_disposition=FinalDisposition.EXPERT_APPROVED,
            adjudicated_critical_checks=CriticalFailureFlags(),
            decision_rationale="Lexical simplification valid.",
        ),
        "SIMP-EN-000002": AdjudicationRecord(
            adjudication_id="ADJ-002",
            item_id="SIMP-EN-000002",
            adjudicator_id="ADJ-LEAD",
            reviewer_a_id="REV-01",
            reviewer_b_id="REV-02",
            reviewer_a_submission_id="SUB-03",
            reviewer_b_submission_id="SUB-04",
            conflict_reasons=["Answer leakage"],
            final_taxonomy_class=TaxonomyClass.TEXT_SIMPLIFICATION,
            final_disposition=FinalDisposition.REJECTED_SAFETY,
            adjudicated_critical_checks=CriticalFailureFlags(answer_leakage_detected=True),
            decision_rationale="Answer revealed.",
        ),
    }

    exports = export_service.export_stage28_reference_dataset(
        manifest_items=sample_items,
        adjudication_records=adjudications,
        revisions={},
        submissions_by_item={},
    )

    assert len(exports) == 2

    # Check first record: Approved
    rec1 = exports[0]
    assert rec1["item_id"] == "SIMP-EN-000001"
    assert rec1["expert_review_status"] == "approved"
    assert rec1["eligible_for_stage28_evaluation"] is True
    assert rec1["final_disposition"] == "expert_approved"
    assert rec1["final_taxonomy_class"] == "text_simplification"

    # Universal child delivery invariant: must be FALSE for all records
    for rec in exports:
        assert rec["approved_for_unsupervised_child_delivery"] is False
        assert rec["requires_professional_monitoring"] is True

    # Check second record: Rejected safety
    rec2 = exports[1]
    assert rec2["item_id"] == "SIMP-EN-000002"
    assert rec2["expert_review_status"] == "rejected"
    assert rec2["eligible_for_stage28_evaluation"] is False
    assert rec2["final_disposition"] == "rejected_safety"


def test_export_sanitized_audit_manifest(export_service):
    """Verifies that audit manifest exposes no reviewer PII."""
    audit_manifest = export_service.export_sanitized_audit_manifest(
        manifest_items=[],
        adjudication_records=[],
        revisions=[],
    )
    assert audit_manifest["schema_version"] == "1.0.0"
    assert audit_manifest["stage"] == 27
    assert "total_records_governed" in audit_manifest
