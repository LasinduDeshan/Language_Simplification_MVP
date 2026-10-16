"""
Stage 33 — Unit Tests for Negation and Modality Preservation.
"""

import pytest
from app.sinhala_simplification.enums import ProtectedSpanCategory
from app.sinhala_simplification.protected_spans import ProtectedSpanDetector


def test_negation_marker_detection():
    detector = ProtectedSpanDetector()
    text = "ඔහු පාසල් ගියේ නැත. ඇය කෑම කෑවේ නැහැ."
    spans = detector.detect_spans(text)

    neg_spans = [ps for ps in spans if ps.category == ProtectedSpanCategory.NEGATION_MARKER]
    assert len(neg_spans) == 2
    assert "නැත" in [ps.text for ps in neg_spans]
    assert "නැහැ" in [ps.text for ps in neg_spans]


def test_modality_condition_detection():
    detector = ProtectedSpanDetector()
    text = "ඔබට එය කළ හැකිය. වැසි වසී නම් නොයන්න."
    spans = detector.detect_spans(text)

    mod_spans = [ps for ps in spans if ps.category == ProtectedSpanCategory.MODALITY_CONDITION]
    assert len(mod_spans) == 2
    assert "හැකිය" in [ps.text for ps in mod_spans]
    assert "නම්" in [ps.text for ps in mod_spans]
