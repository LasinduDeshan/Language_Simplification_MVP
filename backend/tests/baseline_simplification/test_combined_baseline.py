"""
Unit tests for B4: Combined Deterministic Baseline Pipeline and Rollback.
"""
from app.baseline_simplification.combined_baseline import CombinedDeterministicBaseline
from app.baseline_simplification.schemas import FinalDisposition, MeaningValidationStatus

def test_combined_baseline_full_pipeline():
    b4 = CombinedDeterministicBaseline()
    # Passive + nominalization + complex vocabulary
    text = "The Arctic habitat was built by Sam and he made a decision to stay."
    res = b4.simplify(text, target_content_age=6)
    
    out = res["output_text"]
    assert "Sam" in out
    assert "decided" in out
    assert res["quality_disposition"] == FinalDisposition.AUTOMATIC_CHECK_PASSED
    assert res["meaning_validation_status"] == MeaningValidationStatus.PASSED

def test_combined_baseline_preserves_negation():
    b4 = CombinedDeterministicBaseline()
    text = "The small cat did not eat the fish."
    res = b4.simplify(text, target_content_age=6)
    assert "not" in res["output_text"].lower()
    assert res["meaning_validation_status"] == MeaningValidationStatus.PASSED
