"""
Stage 33 — Unit Tests for Qualified Transformation Traces.
"""

import pytest
from app.sinhala_simplification.enums import MappingStatus, OperationType
from app.sinhala_simplification.schemas import CodePointSpan
from app.sinhala_simplification.trace_builder import TraceBuilder


def test_qualified_trace_attributes():
    span_in = CodePointSpan(start_code_point=5, end_code_point=12, text="පිළිබඳව")
    span_out = CodePointSpan(start_code_point=5, end_code_point=9, text="ගැන")

    op_local = TraceBuilder.create_operation(
        operation_id="OP-001",
        operation_type=OperationType.REPLACE,
        rule_id="SI-LEX-SUB-0001",
        raw_source_spans=[span_in],
        normalized_source_spans=[span_in],
        output_spans=[span_out],
        mapping_status=MappingStatus.ONE_TO_ONE,
        mapping_exact=True,
        before_text="පිළිබඳව",
        after_text="ගැන"
    )

    assert op_local.mapping_status == MappingStatus.ONE_TO_ONE
    assert op_local.mapping_exact is True

    op_split = TraceBuilder.create_operation(
        operation_id="OP-002",
        operation_type=OperationType.SPLIT,
        rule_id="SI-SNT-SPL-0001",
        raw_source_spans=[span_in],
        normalized_source_spans=[span_in],
        output_spans=[span_out],
        mapping_status=MappingStatus.NON_LOCAL,
        mapping_exact=False,
        before_text="සහ",
        after_text=". "
    )

    assert op_split.mapping_status == MappingStatus.NON_LOCAL
    assert op_split.mapping_exact is False
