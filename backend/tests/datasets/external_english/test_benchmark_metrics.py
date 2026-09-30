"""Unit tests for sentence simplification benchmark metrics."""

import pytest
from app.datasets.external_english.benchmark.metrics import (
    compute_bleu,
    compute_bertscore_proxy,
    compute_complexity_reduction,
    compute_sari,
    estimate_fkgl,
)


def test_sari_identity_baseline():
    orig = "This is a complex original sentence for testing."
    pred = "This is a complex original sentence for testing."
    refs = [
        "This is a simple sentence for testing.",
        "This is a short test sentence.",
    ]
    sari, add_s, keep_s, del_s = compute_sari(orig, pred, refs)
    assert 0.0 <= sari <= 100.0
    assert add_s == 0.0  # No additions made in identity baseline
    assert keep_s > 0.0


def test_sari_perfect_simplification():
    orig = "The huge canine commenced barking loudly."
    pred = "The big dog started barking."
    refs = [
        "The big dog started barking.",
        "A large dog began to bark.",
    ]
    sari, add_s, keep_s, del_s = compute_sari(orig, pred, refs)
    assert sari > 50.0
    assert add_s > 0.0
    assert del_s > 0.0


def test_bleu_multi_reference():
    pred = "The boy played in the park."
    refs = [
        "The boy played in the park.",
        "A young boy was playing in the park.",
    ]
    bleu = compute_bleu(pred, refs)
    assert bleu == 100.0


def test_bertscore_proxy():
    pred = "The quick brown fox jumps."
    refs = [
        "The quick brown fox jumps over the lazy dog.",
        "A fast brown fox jumps.",
    ]
    bert_proxy = compute_bertscore_proxy(pred, refs)
    assert 50.0 <= bert_proxy <= 100.0


def test_complexity_reduction():
    orig = "The university demonstrated extraordinary institutional capabilities."
    pred = "The school showed great skill."
    res = compute_complexity_reduction(orig, pred)
    assert res["word_compression_ratio"] < 1.0
    assert res["char_compression_ratio"] < 1.0
    assert res["fkgl_reduction"] > 0.0
