"""Tests for Child Safety and Protected Answer Boundary validators."""
import pytest
from app.datasets.quality.validators.child_safety import ChildSafetyValidator
from app.datasets.quality.enums import RuleSeverity


@pytest.fixture
def validator():
    return ChildSafetyValidator()


def test_clean_child_view_passes(validator):
    record = {
        "activity_id": "C3-EN-VOC-001",
        "instruction": "Look at the picture and say what it is.",
        "child_view": {
            "activity_id": "C3-EN-VOC-001",
            "instruction": "Look at the picture and say what it is.",
            "options": ["cat", "dog"]
        }
    }
    results = validator.validate(record)
    assert all(r.passed for r in results)


def test_protected_answer_leakage_triggers_critical(validator):
    """Protected answer key exposed in child_view triggers SAFE-LEAK-001 CRITICAL."""
    record = {
        "activity_id": "C3-EN-VOC-LEAK-001",
        "instruction": "Name the animal.",
        "child_view": {
            "instruction": "Name the animal.",
            "protected_answer": "cat"  # LEAK!
        }
    }
    results = validator.validate(record)
    leak_res = next(r for r in results if r.rule_id == "SAFE-LEAK-001")
    assert leak_res.passed is False
    assert leak_res.severity == RuleSeverity.CRITICAL
    assert "Critical leakage" in leak_res.message


def test_inappropriate_content_detection(validator):
    """Inappropriate violent content triggers SAFE-TEXT-002 ERROR."""
    record = {
        "activity_id": "C3-EN-VOC-INAPP-001",
        "instruction": "Point to the weapon or knife.",
        "child_view": {"instruction": "Point to the weapon or knife."}
    }
    results = validator.validate(record)
    text_res = next(r for r in results if r.rule_id == "SAFE-TEXT-002")
    assert text_res.passed is False
    assert text_res.severity == RuleSeverity.ERROR
