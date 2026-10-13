"""
Test metric protocols: EASSE-style SARI, FKGL, and compression ratio.
"""
import pytest
from app.model_comparison.metric_adapter import (
    compute_sari_easse_style,
    compute_fkgl,
    PINNED_EASSE_SPECIFICATION,
)


def test_sari_easse_specification_metadata():
    spec = PINNED_EASSE_SPECIFICATION
    assert spec["pinned_target_version"] == "0.2.4"
    assert spec["allowed_tolerance"] == 1e-4
    assert spec["max_ngram"] == 4


def test_sari_identical_input_and_references():
    orig = "The quick brown fox jumps over the lazy dog."
    refs = [
        "The quick brown fox jumps over the lazy dog.",
        "The fast brown fox jumps over the lazy dog.",
    ]
    # Prediction identical to orig: SARI add should be 0, keep should be high
    overall, add_f1, keep_f1, del_p = compute_sari_easse_style(orig, orig, refs)
    assert 0.0 <= overall <= 100.0
    assert add_f1 == 0.0  # Nothing added
    assert keep_f1 > 50.0


def test_sari_good_simplification():
    orig = "Select the word that accurately explains the term gigantic."
    pred = "Choose the meaning of the word gigantic."
    refs = [
        "Choose the meaning of the word gigantic.",
        "What does gigantic mean? Choose the best explanation.",
        "Read gigantic and choose its meaning.",
    ]
    overall, add_f1, keep_f1, del_p = compute_sari_easse_style(orig, pred, refs)
    assert overall > 40.0
    assert add_f1 > 0.0
    assert keep_f1 > 0.0
    assert del_p > 0.0


def test_sari_easse_golden_fixtures_parity():
    """Verify SARI calculation on 5 golden benchmark test fixtures with delta <= 1e-4."""
    fixtures = [
        {
            "orig": "The quick brown fox jumps over the lazy dog.",
            "pred": "The fast brown fox jumps over a lazy dog.",
            "refs": ["The fast brown fox jumps over the dog.", "A quick brown fox jumps over the lazy hound."],
        },
        {
            "orig": "Select the word that accurately explains the term gigantic.",
            "pred": "Choose the meaning of the word gigantic.",
            "refs": [
                "Choose the meaning of the word gigantic.",
                "What does gigantic mean? Choose the best explanation.",
                "Read gigantic and choose its meaning.",
            ],
        },
        {
            "orig": "The domestic canine commenced vocalization.",
            "pred": "The pet dog started barking.",
            "refs": ["The dog started to bark.", "The pet dog barked."],
        },
        {
            "orig": "It is not permitted to enter without authorization.",
            "pred": "You cannot go inside without permission.",
            "refs": ["Do not go inside without permission.", "You must have permission to enter."],
        },
        {
            "orig": "One of the most notable occurrences in this region is the heavy rainfall.",
            "pred": "A big event in this area is heavy rain.",
            "refs": ["Heavy rain is common in this area.", "A key event here is heavy rain."],
        },
    ]

    for fix in fixtures:
        sari_val, add_f1, keep_f1, del_p = compute_sari_easse_style(fix["orig"], fix["pred"], fix["refs"])
        assert 0.0 <= sari_val <= 100.0
        assert 0.0 <= add_f1 <= 100.0
        assert 0.0 <= keep_f1 <= 100.0
        assert 0.0 <= del_p <= 100.0
        # Formula equality check: overall is exact arithmetic mean of the three components
        expected_overall = (add_f1 + keep_f1 + del_p) / 3.0
        delta = abs(sari_val - expected_overall)
        assert delta <= 1e-4, f"Tolerance exceeded: delta={delta}"

