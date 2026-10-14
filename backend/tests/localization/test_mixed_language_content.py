"""
Tests for mixed English-Sinhala rendering, numbers, and directionality.
"""
from app.localization.unicode_guards import extract_code_points, verify_code_point_equality

def test_mixed_sinhala_english_sequence():
    mixed = "Level 1: සිංහල කියවීම (Reading)"
    matches, in_cps, out_cps = verify_code_point_equality(mixed, mixed)
    assert matches
    assert "U+004C" in in_cps  # 'L'
    assert "U+0D9A" in in_cps  # 'ක'

def test_sinhala_with_arabic_and_sinhala_digits():
    mixed_num = "පිටුව 45 (අංක 123)"
    matches, in_cps, out_cps = verify_code_point_equality(mixed_num, mixed_num)
    assert matches
    assert "U+0034" in in_cps  # '4'
    assert "U+0035" in in_cps  # '5'
