"""Tests for Interaction Export dataset wrapper validator."""
import pytest
from app.datasets.quality.validators.interaction_export import InteractionExportValidator
from app.datasets.quality.enums import RuleSeverity


@pytest.fixture
def validator():
    return InteractionExportValidator()


def test_valid_interaction_export(validator):
    record = {
        "interaction_id": "INT-20260924-000001",
        "pseudonymous_learner_id": "LRN-001",
        "activity_id": "C3-EN-VOC-001",
        "screening_risk_level": "moderate",
        "recommended_support_level": "mild"
    }
    results = validator.validate(record)
    assert all(r.passed for r in results)


def test_interaction_export_with_forbidden_notes(validator):
    record = {
        "interaction_id": "INT-20260924-000002",
        "raw_screening_notes": "Child displays speech difficulty."  # FORBIDDEN
    }
    results = validator.validate(record)
    allow_res = next(r for r in results if r.rule_id == "PRIV-ALLOW-001")
    assert allow_res.passed is False
    assert allow_res.severity == RuleSeverity.CRITICAL
