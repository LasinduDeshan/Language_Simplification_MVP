"""Tests for transparent multi-dimensional scoring and mutually exclusive precedence."""
import pytest
from app.datasets.quality.scoring import QualityScorer
from app.datasets.quality.enums import QualityStatus, RuleSeverity, QualityDimension
from app.datasets.quality.schemas import QualityRuleResultV1


def test_scoring_precedence_quarantined():
    """Any critical failure forces QUARANTINED regardless of score."""
    results = [
        QualityRuleResultV1(
            result_id="RES-1",
            run_id="VAL-1",
            record_id="REC-1",
            dataset_layer="simplification_corpus",
            rule_id="RULE-CRIT",
            validator_name="val",
            dimension=QualityDimension.SAFETY_ANSWER_BOUNDARY,
            severity=RuleSeverity.CRITICAL,
            passed=False,
            message="Critical leak"
        )
    ]
    breakdown, score = QualityScorer.calculate_scores(results)
    status, w_c, e_c, c_c = QualityScorer.resolve_status(results, score)
    assert status == QualityStatus.QUARANTINED
    assert c_c == 1


def test_scoring_precedence_failed():
    """An error rule results in AUTOMATIC_CHECK_FAILED."""
    results = [
        QualityRuleResultV1(
            result_id="RES-2",
            run_id="VAL-1",
            record_id="REC-2",
            dataset_layer="simplification_corpus",
            rule_id="RULE-ERR",
            validator_name="val",
            dimension=QualityDimension.MEANING_PRESERVATION,
            severity=RuleSeverity.ERROR,
            passed=False,
            message="Meaning failure"
        )
    ]
    breakdown, score = QualityScorer.calculate_scores(results)
    status, w_c, e_c, c_c = QualityScorer.resolve_status(results, score)
    assert status == QualityStatus.AUTOMATIC_CHECK_FAILED
    assert e_c == 1


def test_scoring_precedence_manual_review():
    """A warning rule results in MANUAL_REVIEW_REQUIRED."""
    results = [
        QualityRuleResultV1(
            result_id="RES-3",
            run_id="VAL-1",
            record_id="REC-3",
            dataset_layer="simplification_corpus",
            rule_id="RULE-WARN",
            validator_name="val",
            dimension=QualityDimension.SIMPLICITY_IMPROVEMENT,
            severity=RuleSeverity.WARNING,
            passed=False,
            message="Compression warning"
        )
    ]
    breakdown, score = QualityScorer.calculate_scores(results)
    status, w_c, e_c, c_c = QualityScorer.resolve_status(results, score)
    assert status == QualityStatus.MANUAL_REVIEW_REQUIRED
    assert w_c == 1


def test_scoring_precedence_passed():
    """All rules passed results in AUTOMATIC_CHECK_PASSED."""
    results = [
        QualityRuleResultV1(
            result_id="RES-4",
            run_id="VAL-1",
            record_id="REC-4",
            dataset_layer="simplification_corpus",
            rule_id="RULE-OK",
            validator_name="val",
            dimension=QualityDimension.MEANING_PRESERVATION,
            severity=RuleSeverity.INFO,
            passed=True,
            message="Passed"
        )
    ]
    breakdown, score = QualityScorer.calculate_scores(results)
    status, w_c, e_c, c_c = QualityScorer.resolve_status(results, score)
    assert status == QualityStatus.AUTOMATIC_CHECK_PASSED
    assert score == 100.0
