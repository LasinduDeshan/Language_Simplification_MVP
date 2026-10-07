"""
Unit tests for Language Verifier
"""
from app.nlp_preprocessing.language_verifier import LanguageVerifier

def test_language_verifier_valid_english():
    verifier = LanguageVerifier(confidence_threshold=0.80)
    res = verifier.verify_language("Put the red ball in the box and tap on the picture.")
    assert res.decision == "verified"
    assert res.confidence >= 0.80

def test_language_verifier_low_confidence_review():
    verifier = LanguageVerifier(confidence_threshold=0.80)
    res = verifier.verify_language("xyz qwr plt")
    assert res.decision == "manual_review_required"
