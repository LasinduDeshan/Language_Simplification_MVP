"""
Test safety evaluation gates: entity, number, negation preservation, and leakage prevention.
"""
import pytest
from app.model_comparison.safety_evaluator import SafetyEvaluator


def test_entity_preservation():
    src = "Doctor Smith gave Sarah three red apples."
    pred_pass = "Dr. Smith gave Sarah 3 red apples."
    pred_fail = "The person gave someone some apples."

    pass_ok, ratio_ok = SafetyEvaluator.check_entity_preservation(src, pred_pass, ["Smith", "Sarah"])
    assert pass_ok is True
    assert ratio_ok == 1.0

    pass_bad, ratio_bad = SafetyEvaluator.check_entity_preservation(src, pred_fail, ["Smith", "Sarah"])
    assert pass_bad is False
    assert ratio_bad == 0.0


def test_number_preservation():
    src = "There are 5 birds on the fence."
    pred_ok = "There are five birds on the fence."
    pred_bad = "There are birds on the fence."

    pass_ok, ratio_ok = SafetyEvaluator.check_number_preservation(src, pred_ok)
    assert pass_ok is True

    pass_bad, ratio_bad = SafetyEvaluator.check_number_preservation(src, pred_bad)
    assert pass_bad is False


def test_negation_preservation():
    src = "Do not touch the hot stove."
    pred_ok = "Don't touch the stove. It is hot."
    pred_bad = "Touch the hot stove."

    pass_ok, _ = SafetyEvaluator.check_negation_preservation(src, pred_ok)
    assert pass_ok is True

    pass_bad, _ = SafetyEvaluator.check_negation_preservation(src, pred_bad)
    assert pass_bad is False


def test_answer_leakage_detection():
    pred_clean = "Choose the option that describes a feline animal."
    pred_leaked = "The secret correct answer is cat."

    assert SafetyEvaluator.check_answer_leakage(pred_clean, ["cat"]) is True
    assert SafetyEvaluator.check_answer_leakage(pred_leaked, ["cat"]) is False
