"""
Tests for exact decoded Unicode code-point sequence equality and replacement character detection.
"""
from app.localization.unicode_guards import (
    extract_code_points,
    verify_code_point_equality,
    has_replacement_character
)

def test_sinhala_code_point_extraction():
    # 'ක' is U+0D9A
    # '්' (virama) is U+0DCA
    text = "ක්"
    cps = extract_code_points(text)
    assert cps == ["U+0D9A", "U+0DCA"]

def test_sinhala_zwj_rakaransaya_code_points():
    # 'ක්‍ර' = U+0D9A (ක) + U+0DCA (al-lakuna) + U+200D (ZWJ) + U+0DBB (ර)
    text = "ක්‍ර"
    cps = extract_code_points(text)
    assert cps == ["U+0D9A", "U+0DCA", "U+200D", "U+0DBB"]

def test_code_point_equality_verification():
    text1 = "ශ්‍රී ලංකා"
    text2 = "ශ්‍රී ලංකා"
    matches, in_cps, out_cps = verify_code_point_equality(text1, text2)
    assert matches
    assert in_cps == out_cps

    # Altered text
    text3 = "ශ්‍රී ලංකාව"
    matches, _, _ = verify_code_point_equality(text1, text3)
    assert not matches

def test_replacement_character_guard():
    clean_text = "ආයුබෝවන්"
    assert not has_replacement_character(clean_text)

    corrupted_text = "ආයුබෝ\uFFFDන්"
    assert has_replacement_character(corrupted_text)
