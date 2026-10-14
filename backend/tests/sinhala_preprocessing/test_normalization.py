"""
Tests for Stage 30 Normalization (NFC and Whitespace).
"""

from app.sinhala_preprocessing.normalizer import normalize_nfc, normalize_whitespace
from app.sinhala_preprocessing.schemas import MappingStatus

def test_canonical_nfc_no_change():
    text = "ශ්‍රී ලංකා"
    nfc, ops = normalize_nfc(text)
    assert nfc == text
    assert len(ops) == 0

def test_whitespace_normalization():
    raw = "  ළමයා   පාසල්  යයි.\r\nගුරුවරයා   උගන්වයි.  "
    norm, ops = normalize_whitespace(raw)
    assert norm == "ළමයා පාසල් යයි.\nගුරුවරයා උගන්වයි."
    assert len(ops) == 1
    op = ops[0]
    assert op.operation_type == "WHITESPACE_NORMALIZATION"
    assert op.changed is True
    assert op.raw_spans[0].start_code_point == 0
    assert op.raw_spans[0].end_code_point == len(raw)
    assert op.normalized_spans[0].start_code_point == 0
    assert op.normalized_spans[0].end_code_point == len(norm)
    assert op.mapping_status == MappingStatus.MANY_TO_ONE
