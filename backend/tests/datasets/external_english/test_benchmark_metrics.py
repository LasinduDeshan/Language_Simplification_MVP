"""Unit tests for sentence simplification benchmark metrics (SARI, BLEU, Semantic Similarity Proxy)."""

import pytest
from app.datasets.external_english.benchmark.metrics import (
    compute_bleu,
    compute_complexity_reduction,
    compute_sari,
    compute_semantic_similarity_proxy,
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


def test_semantic_similarity_proxy():
    pred = "The quick brown fox jumps."
    refs = [
        "The quick brown fox jumps over the lazy dog.",
        "A fast brown fox jumps.",
    ]
    sem_proxy = compute_semantic_similarity_proxy(pred, refs)
    assert 50.0 <= sem_proxy <= 100.0


def test_complexity_reduction():
    orig = "The university demonstrated extraordinary institutional capabilities."
    pred = "The school showed great skill."
    res = compute_complexity_reduction(orig, pred)
    assert res["word_compression_ratio"] < 1.0
    assert res["char_compression_ratio"] < 1.0
    assert res["fkgl_reduction"] > 0.0


def test_multi_reference_benchmark_fixture():
    """Validates metrics on fixed 10-reference benchmark fixture."""
    orig = "About 95 species are currently accepted."
    pred = "About 95 kinds are now known."
    refs = [
        "About 95 species are accepted now.",
        "There are about 95 species accepted.",
        "About 95 types are currently accepted.",
        "About 95 species are now recognized.",
        "Around 95 species are accepted today.",
        "Currently, about 95 species are accepted.",
        "About 95 kinds are known.",
        "About 95 species are recognized.",
        "95 species are currently accepted.",
        "About 95 species are accepted.",
    ]
    sari, add_s, keep_s, del_s = compute_sari(orig, pred, refs)
    bleu = compute_bleu(pred, refs)
    sem_proxy = compute_semantic_similarity_proxy(pred, refs)

    assert sari > 15.0
    assert bleu > 20.0
    assert sem_proxy > 50.0
