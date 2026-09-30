"""
Unit tests for B2: Sentence Splitting Baseline.
"""
from app.baseline_simplification.sentence_split_baseline import SentenceSplitBaseline

def test_sentence_splitting_compound_conjunction():
    b2 = SentenceSplitBaseline()
    text = "The dog barked loudly and the cat ran away."
    res = b2.simplify(text)
    out = res["output_text"]
    assert "The dog barked loudly." in out
    assert "The cat ran away." in out
    assert len(res["rules_applied"]) > 0

def test_sentence_splitting_does_not_create_fragments():
    b2 = SentenceSplitBaseline()
    # Simple list should not be split into invalid fragments
    text = "She likes apples and oranges."
    res = b2.simplify(text)
    assert res["output_text"] == text
    assert len(res["rules_applied"]) == 0
