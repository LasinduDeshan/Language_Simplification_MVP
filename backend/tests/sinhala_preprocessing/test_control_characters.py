"""
Tests for Stage 30 Prohibited Control Characters.
"""

from app.sinhala_preprocessing.pipeline import preprocess_sinhala_text
from app.sinhala_preprocessing.schemas import QualityFlag, TerminalDisposition

def test_prohibited_controls_rejection():
    # Null byte \0
    rec_null = preprocess_sinhala_text("මම\0පාසල් යමි.")
    assert rec_null.final_disposition == TerminalDisposition.REJECTED_INVALID_UNICODE
    assert rec_null.disposition_reason_code == "PROHIBITED_CONTROL_CHARACTER"
    assert QualityFlag.PROHIBITED_CONTROL_PRESENT in rec_null.quality_flags

    # C0 control character \x07 (bell)
    rec_bell = preprocess_sinhala_text("අම්මා\x07ආදරෙයි.")
    assert rec_bell.final_disposition == TerminalDisposition.REJECTED_INVALID_UNICODE
    assert rec_bell.disposition_reason_code == "PROHIBITED_CONTROL_CHARACTER"

    # Bidi override \u202E
    rec_bidi = preprocess_sinhala_text("පොත \u202Eකියවන්න.")
    assert rec_bidi.final_disposition == TerminalDisposition.REJECTED_INVALID_UNICODE
    assert rec_bidi.disposition_reason_code == "PROHIBITED_CONTROL_CHARACTER"

    # C1 control character U+0085 (NEXT LINE)
    rec_nel = preprocess_sinhala_text("ගෙදර\u0085යමු.")
    assert rec_nel.final_disposition == TerminalDisposition.REJECTED_INVALID_UNICODE
    assert rec_nel.disposition_reason_code == "PROHIBITED_CONTROL_CHARACTER"
    assert QualityFlag.PROHIBITED_CONTROL_PRESENT in rec_nel.quality_flags

def test_governed_whitespace_allowed():
    # Ordinary spaces, tabs, newlines, carriage returns, and NBSP are allowed
    text = "මම\tපාසල්\r\nයමි.\u00A0හොඳයි."
    rec = preprocess_sinhala_text(text)
    assert rec.final_disposition != TerminalDisposition.REJECTED_INVALID_UNICODE
    assert QualityFlag.PROHIBITED_CONTROL_PRESENT not in rec.quality_flags
