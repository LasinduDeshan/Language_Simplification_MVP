"""
Test separation of Sentence BLEU-4 and Corpus SacreBLEU metrics.
"""
import pytest
from app.model_comparison.metric_adapter import (
    compute_sentence_bleu_4,
    compute_corpus_sacrebleu,
)


def test_sentence_bleu_smoothed():
    pred = "The cat sat on the mat."
    refs = ["The cat was sitting on the mat.", "A cat sat on a mat."]
    score = compute_sentence_bleu_4(pred, refs)
    assert 0.0 <= score <= 100.0
    assert score > 20.0


def test_corpus_sacrebleu_has_signature():
    preds = ["The cat sat.", "The dog barked."]
    refs = [["The cat sat on the mat."], ["The dog barked loudly."]]
    score, signature = compute_corpus_sacrebleu(preds, refs)
    assert 0.0 <= score <= 100.0
    assert "nrefs" in signature
    assert "case" in signature
    assert "tok" in signature


def test_sentence_vs_corpus_separation():
    # Sentence BLEU evaluates individual items; corpus BLEU evaluates the corpus as a scalar
    pred = "The quick brown fox."
    refs = ["The fast brown fox."]
    sent_bleu = compute_sentence_bleu_4(pred, [refs[0]])

    corpus_bleu, sig = compute_corpus_sacrebleu([pred], [[refs[0]]])
    # Mathematical formulations differ (sentence smoothing vs corpus n-gram aggregation)
    assert isinstance(sent_bleu, float)
    assert isinstance(corpus_bleu, float)
    assert isinstance(sig, str) and len(sig) > 0
