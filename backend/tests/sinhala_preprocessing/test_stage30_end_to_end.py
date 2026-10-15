"""
End-to-End Integration Tests for Stage 30 Preprocessing Pipeline.
"""

from app.sinhala_preprocessing.pipeline import preprocess_sinhala_text
from app.sinhala_preprocessing.schemas import TerminalDisposition

def test_e2e_clean_sinhala():
    raw = "අම්මා මට ආදරෙයි. තාත්තා පොත් ගෙනෙයි."
    rec = preprocess_sinhala_text(raw, record_id="E2E-001")
    assert rec.final_disposition == TerminalDisposition.PASSED
    assert len(rec.sentences) == 2
    assert len(rec.tokens) > 0
    assert rec.approved_for_child_delivery is False

def test_e2e_whitespace_normalization():
    raw = "  ළමයා   පාසල්  යයි.\r\nගුරුවරයා   උගන්වයි.  "
    rec = preprocess_sinhala_text(raw, record_id="E2E-002")
    assert rec.final_disposition == TerminalDisposition.PASSED_WITH_NORMALIZATION
    assert rec.normalization_changed is True
    assert "\r" not in rec.normalized_text

def test_e2e_invalid_unicode_fail_closed():
    raw = "අම්මා \uFFFD ආදරෙයි."
    rec = preprocess_sinhala_text(raw, record_id="E2E-003")
    assert rec.final_disposition == TerminalDisposition.REJECTED_INVALID_UNICODE
    assert rec.disposition_reason_code == "PREEXISTING_REPLACEMENT_CHARACTER"

def test_e2e_non_sinhala_exclusion():
    raw = "This is strictly English text without Sinhala."
    rec = preprocess_sinhala_text(raw, record_id="E2E-004", language="en", locale="en-US")
    assert rec.final_disposition == TerminalDisposition.EXCLUDED_NON_SINHALA
    assert rec.disposition_reason_code == "NO_SINHALA_CONTENT"
