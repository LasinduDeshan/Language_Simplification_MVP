"""
Tests for Stage 30 Unicode Validation.
"""

from app.sinhala_preprocessing.validator import validate_unicode_text
from app.sinhala_preprocessing.schemas import QualityFlag, TerminalDisposition

def test_clean_sinhala_validation():
    text = "අම්මා මට ආදරෙයි."
    res = validate_unicode_text(text)
    assert res.is_valid is True
    assert res.disposition is None
    assert len(res.flags) == 0

def test_replacement_character_rejection():
    text = "මම \uFFFD යමි."
    res = validate_unicode_text(text)
    assert res.is_valid is False
    assert res.disposition == TerminalDisposition.REJECTED_INVALID_UNICODE
    assert res.reason_code == "PREEXISTING_REPLACEMENT_CHARACTER"
    assert QualityFlag.REPLACEMENT_CHARACTER_PRESENT in res.flags

def test_prohibited_control_rejection():
    # Null byte
    res1 = validate_unicode_text("මම\u0000පාසල් යමි.")
    assert res1.is_valid is False
    assert res1.disposition == TerminalDisposition.REJECTED_INVALID_UNICODE
    assert res1.reason_code == "PROHIBITED_CONTROL_CHARACTER"

    # Bell control character
    res2 = validate_unicode_text("අම්මා\u0007ආදරෙයි.")
    assert res2.is_valid is False
    assert res2.disposition == TerminalDisposition.REJECTED_INVALID_UNICODE
    assert res2.reason_code == "PROHIBITED_CONTROL_CHARACTER"

    # Bidi override U+202E
    res3 = validate_unicode_text("පොත \u202Eකියවන්න.")
    assert res3.is_valid is False
    assert res3.disposition == TerminalDisposition.REJECTED_INVALID_UNICODE
    assert res3.reason_code == "PROHIBITED_CONTROL_CHARACTER"

def test_unattached_combining_mark_review():
    # Combining vowel sign at index 0
    text = "\u0DCFම්මා"
    res = validate_unicode_text(text)
    assert res.disposition == TerminalDisposition.MANUAL_REVIEW_REQUIRED
    assert res.reason_code == "COMBINING_SEQUENCE_REVIEW"
    assert QualityFlag.COMBINING_SEQUENCE_REVIEW in res.flags

def test_excessive_combining_marks_review():
    # > 3 consecutive combining marks
    text = "ක\u0DCA\u0DCF\u0DCA\u0DCF"
    res = validate_unicode_text(text)
    assert res.disposition == TerminalDisposition.MANUAL_REVIEW_REQUIRED
    assert QualityFlag.COMBINING_SEQUENCE_REVIEW in res.flags

def test_empty_input_validation():
    res = validate_unicode_text("   \n\t  ")
    assert res.is_valid is False
    assert res.disposition == TerminalDisposition.MANUAL_REVIEW_REQUIRED
    assert QualityFlag.EMPTY_AFTER_DERIVED_WHITESPACE in res.flags
