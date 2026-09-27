"""
Unit tests for Stage 20 Meaning Preservation.
"""
import pytest
from app.datasets.expansion.meaning_validator import MeaningValidator

def test_meaning_units_preserved():
    validator = MeaningValidator()
    orig = "Put the red ball beside the small box."
    simp = "Place the red ball next to the small box."
    units = ["red ball", "small box"]
    
    res = validator.validate_meaning_units(orig, simp, units)
    assert res["is_preserved"] is True
    assert res["status"] == "passed"

def test_meaning_units_missing():
    validator = MeaningValidator()
    orig = "Put the red ball beside the small box."
    simp = "Put the blue star in the box."
    units = ["red ball", "small box"]
    
    res = validator.validate_meaning_units(orig, simp, units)
    assert res["is_preserved"] is False
    assert len(res["missing_meaning_units"]) > 0
    assert res["status"] == "manual_review_required"

def test_negation_inversion_detected():
    validator = MeaningValidator()
    orig = "Do not touch the red circle."
    simp = "Touch the red circle."
    units = ["red circle"]
    
    res = validator.validate_meaning_units(orig, simp, units)
    assert res["negation_mismatch"] is True
    assert res["status"] == "manual_review_required"
