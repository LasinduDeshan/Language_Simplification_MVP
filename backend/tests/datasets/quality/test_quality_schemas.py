"""Tests for Stage 15 quality validation Pydantic v2 schemas and governance invariants."""
import pytest
from app.datasets.quality.enums import QualityStatus, RuleSeverity, QualityDimension, ReviewPriority, ReviewStatus, TriageAction
from app.datasets.quality.schemas import (
    QualityRuleResultV1,
    RecordQualitySummaryV1,
    ManualReviewQueueEntryV1,
    ValidationRunManifestV1,
    QualityScoreBreakdownV1
)


def test_quality_rule_result_v1():
    res = QualityRuleResultV1(
        result_id="RES-001",
        run_id="VAL-001",
        record_id="SIMP-EN-000001",
        dataset_layer="simplification_corpus",
        rule_id="SIMP-MEAN-001",
        validator_name="meaning_validator",
        dimension=QualityDimension.MEANING_PRESERVATION,
        severity=RuleSeverity.ERROR,
        passed=False,
        message="Meaning unit missing",
        recommended_action="Review text"
    )
    assert res.result_id == "RES-001"
    assert res.severity == RuleSeverity.ERROR
    assert res.passed is False


def test_stage15_invariant_rejection():
    """Stage 15 schemas strictly forbid setting research_eligible=True or approved_for_child_delivery=True."""
    with pytest.raises(ValueError, match="Stage 15 automatic validation cannot set research_eligible=True"):
        RecordQualitySummaryV1(
            summary_id="SUM-001",
            run_id="VAL-001",
            record_id="SIMP-EN-000001",
            dataset_layer="simplification_corpus",
            quality_status=QualityStatus.AUTOMATIC_CHECK_PASSED,
            research_eligible=True,
            approved_for_child_delivery=False
        )

    with pytest.raises(ValueError, match="Stage 15 automatic validation cannot set approved_for_child_delivery=True"):
        RecordQualitySummaryV1(
            summary_id="SUM-002",
            run_id="VAL-001",
            record_id="SIMP-EN-000001",
            dataset_layer="simplification_corpus",
            quality_status=QualityStatus.AUTOMATIC_CHECK_PASSED,
            research_eligible=False,
            approved_for_child_delivery=True
        )


def test_validation_run_manifest_accounting_validation():
    """ValidationRunManifestV1 verifies accounting balance."""
    manifest = ValidationRunManifestV1(
        run_id="VAL-001",
        dataset_layer="all",
        total_records=100,
        passed_count=80,
        failed_count=10,
        review_required_count=10,
        quarantined_count=0
    )
    assert manifest.total_records == 100

    # Discrepancy raises ValueError
    with pytest.raises(ValueError, match="Accounting balance mismatch"):
        ValidationRunManifestV1(
            run_id="VAL-002",
            dataset_layer="all",
            total_records=100,
            passed_count=80,
            failed_count=10,
            review_required_count=5,  # 80+10+5+0 = 95 != 100
            quarantined_count=0
        )
