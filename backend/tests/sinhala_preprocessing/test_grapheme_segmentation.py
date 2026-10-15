"""
Tests for Stage 30 Grapheme Segmentation.
"""

from app.sinhala_preprocessing.graphemes import (
    PINNED_METADATA,
    count_graphemes,
    get_grapheme_spans,
    segment_graphemes
)

def test_pinned_grapheme_metadata():
    assert PINNED_METADATA["engine"] == "regex_X"
    assert PINNED_METADATA["pinned_package"] == "regex"
    assert PINNED_METADATA["conformance_scope"] == "governed_fixtures_verified"

def test_sinhala_grapheme_cluster_counts():
    # Base letter + virama + letter
    assert count_graphemes("අම්මා") == 3

    # Rakaransaya forms 2 extended grapheme clusters under regex \X
    assert count_graphemes("ශ්‍රී") == 2

    # Yansaya forms 2 extended grapheme clusters under regex \X
    assert count_graphemes("ව්‍යා") == 2

    # Phrase
    assert count_graphemes("ශ්‍රී ලංකා") == 5

def test_grapheme_spans_monotonic_and_continuous():
    text = "ශ්‍රී ලංකා"
    spans = get_grapheme_spans(text)
    assert len(spans) == 5

    prev_end = 0
    for start, end in spans:
        assert start == prev_end
        assert end > start
        prev_end = end
    assert prev_end == len(text)
