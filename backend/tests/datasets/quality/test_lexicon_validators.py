"""Tests for Lexicon repository quality rules."""
import pytest
from app.datasets.quality.validators.lexicon import LexiconValidator
from app.datasets.quality.enums import RuleSeverity


@pytest.fixture
def validator():
    return LexiconValidator()


def test_valid_lexicon_entry(validator):
    record = {
        "entry_id": "LEX-EN-000001",
        "word": "habitat",
        "child_friendly_definition": "the place where an animal lives",
        "simpler_alternatives": ["home"],
        "part_of_speech": "noun",
        "example_sentence": "The forest is a natural habitat for bears."
    }
    results = validator.validate(record)
    assert all(r.passed for r in results)


def test_circular_replacement_detection(validator):
    record = {
        "entry_id": "LEX-EN-000002",
        "word": "cat",
        "child_friendly_definition": "a small domestic animal",
        "simpler_alternatives": ["cat"]  # Circular self-replacement!
    }
    results = validator.validate(record)
    circ_res = next(r for r in results if r.rule_id == "LEX-CIRC-002")
    assert circ_res.passed is False
    assert circ_res.severity == RuleSeverity.ERROR
    assert "Self-circular replacement" in circ_res.message
