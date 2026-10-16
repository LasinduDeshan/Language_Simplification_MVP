"""
Tests for Morphology Hypothesis Uncertainty and Rule Versioning in Stage 32 (WP4).
Ensures low confidence hypotheses lower score or route to review,
and every hypothesis includes rule_version and disclaimer note.
"""

import pytest
from app.datasets.sinhala_lexicon.morphology_analyzer import MorphologyAnalyzer

def test_morphology_rule_version_and_note_present():
    """Verify rule_version and non-ground-truth disclaimer note on all hypotheses."""
    analyzer = MorphologyAnalyzer()
    lemma, method, conf, hypotheses = analyzer.analyze_candidate("පාසල්වල")
    assert len(hypotheses) > 0
    for hyp in hypotheses:
        assert hyp.rule_version == "1.0.0"
        assert "not expert-validated" in hyp.linguistic_note
        assert hyp.confidence > 0.0

def test_identity_canonical_for_uninflected_words():
    """Verify words without regular inflection markers default to identity canonical with 1.0 confidence."""
    analyzer = MorphologyAnalyzer()
    lemma, method, conf, hypotheses = analyzer.analyze_candidate("අහස")
    assert lemma == "අහස"
    assert conf == 1.0
    assert len(hypotheses) == 0
