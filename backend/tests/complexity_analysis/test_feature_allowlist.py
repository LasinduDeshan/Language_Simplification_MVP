"""Unit tests for feature allowlist validation and leakage prevention."""

from app.complexity_analysis.feature_registry import (
    FEATURE_ALLOWLIST,
    FEATURE_NAMES,
    validate_feature_allowlist,
)


def test_feature_allowlist_valid():
    valid, violations = validate_feature_allowlist(FEATURE_NAMES)
    assert valid
    assert len(violations) == 0


def test_prohibited_clinical_and_screening_signals_rejected():
    prohibited_cols = [
        "word_count",
        "child_screening_risk_level",
        "dld_clinical_score",
        "learner_profile_id",
        "gold_difficulty_label",
    ]
    valid, violations = validate_feature_allowlist(prohibited_cols)
    assert not valid
    assert len(violations) >= 4
