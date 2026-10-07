"""
Unit tests for metric computation parity (< 0.05 points).
"""
from app.datasets.external_english.benchmark.metrics import compute_sari

def test_sari_parity_definition():
    orig = "The severe environmental conditions made survival difficult for the native plants."
    pred = "The tough weather made it hard for plants to live."
    refs = [
        "The harsh weather made it hard for native plants to survive.",
        "It was hard for local plants to live in the severe conditions.",
        "The native plants struggled because the weather was bad.",
    ]
    sari, add_s, keep_s, del_s = compute_sari(orig, pred, refs)
    recomputed = (add_s + keep_s + del_s) / 3.0
    diff = abs(sari - recomputed)
    assert diff < 0.05
