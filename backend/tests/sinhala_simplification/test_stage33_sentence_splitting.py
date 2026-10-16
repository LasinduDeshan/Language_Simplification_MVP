"""
Stage 33 — Unit Tests for Sentence Splitting Rules.
"""

import pytest
from app.sinhala_simplification.enums import MappingStatus, RuleAttemptTerminalStatus
from app.sinhala_simplification.protected_spans import ProtectedSpanDetector
from app.sinhala_simplification.rule_registry import RuleRegistry
from app.sinhala_simplification.sentence_splitter import SentenceSplitterEngine


def test_sentence_split_at_conjunction():
    registry = RuleRegistry()
    registry.load_registry()
    rule = registry.get_rule("SI-SNT-SPL-0001")  # සහ splitting
    assert rule is not None

    detector = ProtectedSpanDetector()
    text = "ළමයි සෙල්ලම් කරති සහ ගුරුවරු බලා සිටිති."
    spans = detector.detect_spans(text)

    engine = SentenceSplitterEngine()
    results = engine.evaluate_rule(rule, text, "REQ-004", spans, 1, 1)

    assert len(results) == 1
    attempt, cand = results[0]
    assert attempt.terminal_status == RuleAttemptTerminalStatus.CANDIDATE_GENERATED
    assert cand is not None
    assert cand.candidate_text_internal == "ළමයි සෙල්ලම් කරති. ගුරුවරු බලා සිටිති."
    assert cand.operations[0].mapping_status == MappingStatus.NON_LOCAL
    assert cand.operations[0].mapping_exact is False
