"""
Unit tests for field-specific invisible-character and control-character policy.
"""
import pytest
from app.localization.enums import FieldCategory
from app.localization.invisible_characters import (
    validate_field_controls,
    escape_controls_for_log,
    DENYLISTED_CHARS
)

def test_identifier_rejects_denylisted_controls():
    # ZWJ U+200D must be rejected in identifiers
    valid, err, detected = validate_field_controls("user\u200Dname", FieldCategory.IDENTIFIER)
    assert not valid
    assert "U+200D" in err

    # RTL override U+202E must be rejected
    valid, err, detected = validate_field_controls("id_\u202Etest", FieldCategory.IDENTIFIER)
    assert not valid
    assert "U+202E" in err

    # Normal clean identifier passes
    valid, err, _ = validate_field_controls("clean_id_123", FieldCategory.IDENTIFIER)
    assert valid
    assert err is None

def test_educational_text_preserves_legitimate_zwj():
    # Legitimate Sinhala Yansaya with ZWJ: ව්‍යවස්ථාව
    text_with_zwj = "ව්‍යවස්ථාව"
    valid, err, detected = validate_field_controls(text_with_zwj, FieldCategory.EDUCATIONAL_TEXT)
    assert valid
    assert err is None
    assert "U+200D" in detected

def test_educational_text_rejects_bidi_overrides():
    # RTL override in educational text must be flagged and rejected
    bad_text = "පාඩම \u202Eව්‍යාජ"
    valid, err, detected = validate_field_controls(bad_text, FieldCategory.EDUCATIONAL_TEXT)
    assert not valid
    assert "U+202E" in err

def test_technical_fixture_preserves_all():
    fixture_text = "test\u200B\u200D\u202E"
    valid, err, detected = validate_field_controls(fixture_text, FieldCategory.TECHNICAL_FIXTURE)
    assert valid
    assert len(detected) == 3

def test_log_escaping():
    raw_log = "Error in user\u200Dname with \u202E"
    escaped = escape_controls_for_log(raw_log)
    assert "\\u200d" in escaped
    assert "\\u202e" in escaped
    assert "\u200D" not in escaped
