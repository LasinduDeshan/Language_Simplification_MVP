"""
Unit tests for B3: Syntactic Rule Baseline.
"""
from app.baseline_simplification.syntactic_rule_baseline import SyntacticRuleBaseline

def test_passive_to_active_conversion():
    b3 = SyntacticRuleBaseline()
    text = "The ball was caught by Sam."
    res = b3.simplify(text)
    assert res["output_text"] == "Sam caught the ball."
    assert len(res["rules_applied"]) > 0
    assert res["rules_applied"][0]["rule_id"] == "SYN-01-PASSIVE-ACTIVE"

def test_nominalization_unpacking():
    b3 = SyntacticRuleBaseline()
    text = "The teacher made a decision today."
    res = b3.simplify(text)
    assert "decided" in res["output_text"]
    assert any(r["rule_id"] == "SYN-03-NOMINALIZATION-UNPACK" for r in res["rules_applied"])
