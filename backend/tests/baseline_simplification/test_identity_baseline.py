"""
Unit tests for B0: Identity Baseline.
"""
from app.baseline_simplification.identity_baseline import IdentityBaseline

def test_identity_baseline_unchanged():
    b0 = IdentityBaseline()
    text = "The quick brown fox jumps over the lazy dog."
    res = b0.simplify(text)
    assert res["output_text"] == text
    assert len(res["rules_applied"]) == 0
    assert res["fallback_used"] is False
