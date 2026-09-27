"""
Unit tests for Stage 20 Support Monotonicity.
"""
import pytest
from app.datasets.expansion.meaning_validator import MeaningValidator

def test_monotonic_support_trio():
    validator = MeaningValidator()
    source = "Before you place the blue circle inside the box, pick up the red star."
    mild = "Pick up the red star before you put the blue circle inside the box."
    mod = "First, pick up the red star. Then put the blue circle in the box."
    strong = "1. Pick up the red star.\n2. Put the blue circle in the box."
    
    res = validator.validate_support_trio(source, mild, mod, strong)
    assert res["lexical_monotonic"] is True
    assert res["strong_step_clarity"] is True
    assert res["status"] == "passed"
