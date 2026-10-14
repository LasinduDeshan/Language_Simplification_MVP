"""
Tests for Stage 30 Script Analysis and Non-Sinhala Exclusion.
"""

from app.sinhala_preprocessing.script_analyzer import analyze_script_composition
from app.sinhala_preprocessing.schemas import QualityFlag, TerminalDisposition

def test_pure_sinhala_script():
    text = "අම්මා මට ආදරෙයි."
    res = analyze_script_composition(text, declared_language="si")
    assert res.sinhala_count > 0
    assert res.latin_count == 0
    assert res.disposition is None
    assert QualityFlag.MIXED_SCRIPT_PRESENT not in res.flags

def test_mixed_sinhala_english_script():
    text = "Lesson 1: කියවීම."
    res = analyze_script_composition(text, declared_language="si")
    assert res.sinhala_count > 0
    assert res.latin_count > 0
    assert QualityFlag.MIXED_SCRIPT_PRESENT in res.flags
    # Must NOT be excluded
    assert res.disposition != TerminalDisposition.EXCLUDED_NON_SINHALA

def test_non_sinhala_exclusion_rule():
    # Only excluded when NOT declared as Sinhala AND contains 0 Sinhala characters
    text = "This is pure English text."
    res = analyze_script_composition(text, declared_language="en", declared_locale="en-US")
    assert res.disposition == TerminalDisposition.EXCLUDED_NON_SINHALA
    assert res.reason_code == "NO_SINHALA_CONTENT"

def test_unsupported_script_routing():
    # Tamil letters in Sinhala text route to review
    text = "සිංහල සහ தமிழ்."
    res = analyze_script_composition(text, declared_language="si")
    assert res.disposition == TerminalDisposition.MANUAL_REVIEW_REQUIRED
    assert QualityFlag.UNSUPPORTED_SCRIPT_PRESENT in res.flags
