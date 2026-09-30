"""
Unit tests for B1: Lexical Substitution Baseline.
"""
from app.baseline_simplification.lexical_baseline import LexicalSubstitutionBaseline

def test_lexical_substitution_with_age_gating():
    b1 = LexicalSubstitutionBaseline()
    
    # "habitat" -> "home"
    text = "The polar bear lives in an Arctic habitat."
    res_young = b1.simplify(text, target_content_age=6)
    assert "home" in res_young["output_text"].lower()
    assert len(res_young["rules_applied"]) > 0

    # "beneath" -> "under"
    text2 = "The ball is beneath the table."
    res2 = b1.simplify(text2, target_content_age=6)
    assert "under" in res2["output_text"].lower()

def test_lexical_substitution_protects_entities_and_casing():
    b1 = LexicalSubstitutionBaseline()
    text = "Beneath the bed was a miniature toy."
    res = b1.simplify(text, target_content_age=6)
    # Capitalization matched
    assert res["output_text"].startswith("Under")
    assert "tiny" in res["output_text"].lower()
