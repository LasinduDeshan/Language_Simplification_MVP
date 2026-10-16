"""
Stage 33 — Unit Tests for Meaning-Critical Protected Spans.
"""

import pytest
from app.sinhala_simplification.enums import ProtectedSpanCategory
from app.sinhala_simplification.protected_spans import ProtectedSpanDetector


def test_protected_span_categories():
    detector = ProtectedSpanDetector()
    text = "වසර 2024 දී රුපියල් 500 ක් ගෙවන්න. (විස්තර බලන්න) https://example.com “හොඳයි” කියා කීවේය."
    spans = detector.detect_spans(text)

    categories = {ps.category for ps in spans}
    assert ProtectedSpanCategory.NUMBER_NUMERIC in categories
    assert ProtectedSpanCategory.CURRENCY in categories
    assert ProtectedSpanCategory.PARENTHETICAL_REFERENCE in categories
    assert ProtectedSpanCategory.IDENTIFIER_CODE_URL in categories
    assert ProtectedSpanCategory.QUOTATION_DIRECT_SPEECH in categories


def test_stage32_review_vocabulary_protection():
    detector = ProtectedSpanDetector()
    text = "මෙම පරිසරයේ ඇති අනතුරු සහ රෝග ගැන සලකන්න."
    spans = detector.detect_spans(text)

    review_spans = [ps for ps in spans if ps.category == ProtectedSpanCategory.STAGE32_REVIEW_REQUIRED_VOCABULARY]
    assert len(review_spans) == 2
    words = {ps.text for ps in review_spans}
    assert "අනතුරු" in words
    assert "රෝග" in words
