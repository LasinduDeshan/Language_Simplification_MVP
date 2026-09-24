"""Tests for Simplification Corpus quality rules and draft governance invariants."""
import pytest
from app.datasets.quality.validators.simplification import SimplificationValidator
from app.datasets.quality.enums import RuleSeverity


@pytest.fixture
def validator():
    return SimplificationValidator()


def test_valid_simplification_pair(validator):
    record = {
        "pair_id": "SIMP-EN-000001",
        "original_text": "The massive elephant proceeded towards the watering hole.",
        "simplified_text": "The big elephant walked to the water.",
        "validation_status": "draft",
        "research_eligible": False,
        "approved_for_child_delivery": False
    }
    results = validator.validate(record)
    assert all(r.passed for r in results)


def test_negation_inversion_detection(validator):
    """Inverted negation triggers SIMP-NEG-002 error."""
    record = {
        "pair_id": "SIMP-EN-000002",
        "original_text": "Do not touch the hot stove.",
        "simplified_text": "Touch the hot stove.",  # Dropped negation!
        "validation_status": "draft",
        "research_eligible": False,
        "approved_for_child_delivery": False
    }
    results = validator.validate(record)
    neg_res = next(r for r in results if r.rule_id == "SIMP-NEG-002")
    assert neg_res.passed is False
    assert neg_res.severity == RuleSeverity.ERROR
    assert "Negation mismatch" in neg_res.message


def test_number_quantity_mismatch_detection(validator):
    """Altered number triggers SIMP-NUM-003 error."""
    record = {
        "pair_id": "SIMP-EN-000003",
        "original_text": "The child found three red apples on the table.",
        "simplified_text": "The child found five apples on the table.",  # Changed 3 -> 5
        "validation_status": "draft",
        "research_eligible": False,
        "approved_for_child_delivery": False
    }
    results = validator.validate(record)
    num_res = next(r for r in results if r.rule_id == "SIMP-NUM-003")
    assert num_res.passed is False
    assert num_res.severity == RuleSeverity.ERROR
    assert "Number divergence" in num_res.message


def test_draft_governance_invariant_violation(validator):
    """Attempting to set research_eligible=True on draft pair triggers SIMP-GOV-006 critical failure."""
    record = {
        "pair_id": "SIMP-EN-000004",
        "original_text": "The dog barked.",
        "simplified_text": "The dog barked.",
        "validation_status": "draft",
        "research_eligible": True,  # Violation!
        "approved_for_child_delivery": False
    }
    results = validator.validate(record)
    gov_res = next(r for r in results if r.rule_id == "SIMP-GOV-006")
    assert gov_res.passed is False
    assert gov_res.severity == RuleSeverity.CRITICAL
