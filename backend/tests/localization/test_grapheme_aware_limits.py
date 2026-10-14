"""
Tests for grapheme cluster limit calculation vs raw code units.
"""
from app.localization.unicode_guards import count_grapheme_clusters, validate_grapheme_length

def test_grapheme_count_vs_code_units():
    # 'ක්‍ෂ' (Bandi akuru ksha):
    # Consists of 4 code points: U+0D9A (ක) + U+0DCA (al) + U+200D (ZWJ) + U+0DC2 (ෂ)
    # len("ක්‍ෂ") is 4, but under Unicode UAX #29 / Intl.Segmenter it is 2 grapheme clusters (ක+al+ZWJ, ෂ)
    ksha = "ක්‍ෂ"
    assert len(ksha) == 4
    graphemes = count_grapheme_clusters(ksha)
    assert graphemes == 2

def test_multi_grapheme_sinhala_word():
    # 'අම්මා' (am-ma)
    # අ (U+0D85) -> 1
    # ම් (U+0DB8 + U+0DCA) -> 1
    # මා (U+0DB8 + U+0DCF) -> 1
    # Total graphemes: 3. Length in UTF-16 code units: 5.
    text = "අම්මා"
    assert len(text) == 5
    assert count_grapheme_clusters(text) == 3

def test_validate_grapheme_length():
    text = "අම්මා"  # 3 graphemes
    valid, count = validate_grapheme_length(text, max_graphemes=5)
    assert valid
    assert count == 3

    valid, count = validate_grapheme_length(text, max_graphemes=2)
    assert not valid
    assert count == 3
