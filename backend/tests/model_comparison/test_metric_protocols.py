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


def test_fkgl_computation():
    simple_text = "The dog ran."
    complex_text = "The extraordinarily multifaceted domestic canine executed an abrupt terrestrial displacement."
    simple_grade = compute_fkgl(simple_text)
    complex_grade = compute_fkgl(complex_text)
    assert complex_grade > simple_grade
    assert simple_grade <= 3.0
