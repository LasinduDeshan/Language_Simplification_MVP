"""Tests for Adaptation Test Set quality rules and boundary validators."""
import pytest
from app.datasets.quality.validators.adaptation import AdaptationValidator
from app.datasets.quality.enums import RuleSeverity


@pytest.fixture
def validator():
    return AdaptationValidator()


def test_valid_adaptation_activity(validator):
    record = {
        "activity_id": "C3-EN-VOC-NAMING-001",
        "activity_owner": "component_3_language",
        "primary_domain": "vocabulary",
        "child_friendly_instruction": "What animal is this?",
        "protected": {
            "answer": "cat",
            "acceptable_answers": ["cat", "kitty"]
        },
        "distractors": ["dog", "rabbit"],
        "mild_scaffold": "Look at the cute pet and say its name.",
        "strong_scaffold": "It says meow! Is it a cat or a dog?"
    }
    results = validator.validate(record)
    assert all(r.passed for r in results)


def test_distractor_collision_detection(validator):
    """Distractor matching correct answer triggers ADAPT-DIST-004 error."""
    record = {
        "activity_id": "C3-EN-VOC-COLLISION-001",
        "activity_owner": "component_3_local",
        "primary_domain": "vocabulary",
        "child_friendly_instruction": "Choose the animal.",
        "protected": {
            "answer": "cat",
            "acceptable_answers": ["cat"]
        },
        "distractors": ["dog", "cat"],  # Collision!
    }
    results = validator.validate(record)
    dist_res = next(r for r in results if r.rule_id == "ADAPT-DIST-004")
    assert dist_res.passed is False
    assert dist_res.severity == RuleSeverity.ERROR
    assert "Distractor collision detected" in dist_res.message


def test_invalid_domain_classification(validator):
    """Invalid primary domain triggers ADAPT-DOM-002 error."""
    record = {
        "activity_id": "C3-EN-INVALID-DOM-001",
        "activity_owner": "component_3_local",
        "primary_domain": "math_reasoning",  # Invalid domain
        "child_friendly_instruction": "Count the apples.",
        "protected": {"answer": "5"}
    }
    results = validator.validate(record)
    dom_res = next(r for r in results if r.rule_id == "ADAPT-DOM-002")
    assert dom_res.passed is False
    assert dom_res.severity == RuleSeverity.ERROR
