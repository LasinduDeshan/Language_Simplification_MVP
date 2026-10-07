"""
Unit tests for tier-specific simplifications (Mild, Moderate, Strong) and composite monotonicity.
"""

import pytest
from app.controlled_simplification.engine import ControlledSimplificationEngine
from app.controlled_simplification.schemas import SimplificationRequest, SupportLevel
from app.controlled_simplification.monotonicity_validator import MonotonicityValidator


def test_tier_differentiation_mild_moderate_strong():
    engine = ControlledSimplificationEngine()
    source_text = "Before placing the red ball inside the box, carefully select the smaller blue object."

    req_mild = SimplificationRequest(
        request_id="TEST-MILD",
        text=source_text,
        target_support_level=SupportLevel.MILD
    )
    req_mod = SimplificationRequest(
        request_id="TEST-MOD",
        text=source_text,
        target_support_level=SupportLevel.MODERATE
    )
    req_strong = SimplificationRequest(
        request_id="TEST-STRONG",
        text=source_text,
        target_support_level=SupportLevel.STRONG
    )

    res_mild = engine.simplify(req_mild)
    res_mod = engine.simplify(req_mod)
    res_strong = engine.simplify(req_strong)

    assert res_mild.status.value in {"PASSED", "PASSED_WITH_ROLLBACK"}
    assert res_mod.status.value in {"PASSED", "PASSED_WITH_ROLLBACK"}
    assert res_strong.status.value in {"PASSED", "PASSED_WITH_ROLLBACK"}

    # Strong must have numbered steps for multi-action
    assert "1." in res_strong.simplified_text
    assert "2." in res_strong.simplified_text


def test_multidimensional_monotonicity():
    validator = MonotonicityValidator()
    orig = "Before placing the large red ball inside the container, carefully select the smaller blue object."
    mild = "Before placing the large red ball in the box, carefully select the small blue thing."
    mod = "1. Pick the small blue thing. 2. Put the large red ball in the box."
    strong = "1. Pick the blue thing. 2. Put the ball in the box."

    is_mono, report = validator.verify_tier_progression(orig, mild, mod, strong)
    assert is_mono is True
    assert report["mild_le_orig"] is True
    assert report["mod_le_mild"] is True
    assert report["strong_le_mod"] is True
