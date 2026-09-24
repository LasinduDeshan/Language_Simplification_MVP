"""Tests for Privacy Scanner and Interaction Export Allowlist validators."""
import pytest
from app.datasets.quality.validators.privacy import PrivacyValidator
from app.datasets.quality.enums import RuleSeverity


@pytest.fixture
def validator():
    return PrivacyValidator()


def test_deidentified_export_passes(validator):
    record = {
        "interaction_id": "INT-20260924-000001",
        "pseudonymous_learner_id": "LRN-001",
        "activity_id": "C3-EN-VOC-001",
        "screening_risk_level": "low",
        "recommended_support_level": "mild",
        "preliminary_trend": "stable"
    }
    results = validator.validate(record)
    assert all(r.passed for r in results)


def test_pii_email_phone_leakage_triggers_critical(validator):
    """Email or phone number in export triggers PRIV-PII-002 CRITICAL."""
    record = {
        "interaction_id": "INT-20260924-000002",
        "pseudonymous_learner_id": "LRN-002",
        "notes": "Parent email: teacher@school.edu, phone: 555-019-2834"
    }
    results = validator.validate(record)
    pii_res = next(r for r in results if r.rule_id == "PRIV-PII-002")
    assert pii_res.passed is False
    assert pii_res.severity == RuleSeverity.CRITICAL


def test_forbidden_field_triggers_critical(validator):
    """Direct learner name field triggers PRIV-ALLOW-001 CRITICAL."""
    record = {
        "interaction_id": "INT-20260924-000003",
        "learner_name": "Alice Smith"  # FORBIDDEN
    }
    results = validator.validate(record)
    allow_res = next(r for r in results if r.rule_id == "PRIV-ALLOW-001")
    assert allow_res.passed is False
    assert allow_res.severity == RuleSeverity.CRITICAL
