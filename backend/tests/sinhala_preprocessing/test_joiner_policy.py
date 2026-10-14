"""
Tests for Stage 30 ZWJ/ZWNJ Joiner Policy.
"""

from app.sinhala_preprocessing.pipeline import preprocess_sinhala_text
from app.sinhala_preprocessing.schemas import QualityFlag, TerminalDisposition

def test_allowlisted_joiner_contexts_passed():
    # Yansaya
    rec_y = preprocess_sinhala_text("ව්‍යාපාරය")
    assert QualityFlag.JOINER_PRESENT in rec_y.quality_flags
    assert QualityFlag.UNEXPECTED_JOINER_CONTEXT not in rec_y.quality_flags
    assert rec_y.final_disposition in (TerminalDisposition.PASSED, TerminalDisposition.PASSED_WITH_NORMALIZATION)

    # Rakaransaya
    rec_r = preprocess_sinhala_text("ක්‍රමය")
    assert QualityFlag.JOINER_PRESENT in rec_r.quality_flags
    assert QualityFlag.UNEXPECTED_JOINER_CONTEXT not in rec_r.quality_flags
    assert rec_r.final_disposition in (TerminalDisposition.PASSED, TerminalDisposition.PASSED_WITH_NORMALIZATION)

    # Repaya
    rec_rep = preprocess_sinhala_text("ධර්‍මය")
    assert QualityFlag.JOINER_PRESENT in rec_rep.quality_flags
    assert QualityFlag.UNEXPECTED_JOINER_CONTEXT not in rec_rep.quality_flags

def test_unexpected_joiner_context_review():
    # Isolated ZWJ at string end
    rec_iso = preprocess_sinhala_text("පාසල\u200D")
    assert QualityFlag.JOINER_PRESENT in rec_iso.quality_flags
    assert QualityFlag.UNEXPECTED_JOINER_CONTEXT in rec_iso.quality_flags
    assert rec_iso.final_disposition == TerminalDisposition.MANUAL_REVIEW_REQUIRED
    assert rec_iso.disposition_reason_code == "UNEXPECTED_JOINER_CONTEXT"

    # Joiner must not be silently stripped from raw text
    assert "\u200D" in rec_iso.raw_text
