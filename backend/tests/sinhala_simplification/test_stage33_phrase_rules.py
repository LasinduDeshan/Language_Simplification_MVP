"""
Stage 33 — Unit Tests for Phrase-Level Substitution Rules.
"""

import pytest
from app.sinhala_simplification.enums import MappingStatus, RuleAttemptTerminalStatus
from app.sinhala_simplification.phrase_rules import PhraseRuleEngine
from app.sinhala_simplification.protected_spans import ProtectedSpanDetector
from app.sinhala_simplification.rule_registry import RuleRegistry


def test_phrase_rule_longest_match():
    registry = RuleRegistry()
    registry.load_registry()
    rule = registry.get_rule("SI-PHR-SUB-0001")  # මේ හේතුවෙන් -> මේ නිසා
    assert rule is not None

    detector = ProtectedSpanDetector()
    text = "මේ හේතුවෙන් පාසල වැසිණි."
    spans = detector.detect_spans(text)

    engine = PhraseRuleEngine()
    results = engine.evaluate_rule(rule, text, "REQ-003", spans, 1, 1)

    assert len(results) == 1
    attempt, cand = results[0]
    assert attempt.terminal_status == RuleAttemptTerminalStatus.CANDIDATE_GENERATED
    assert cand is not None
    assert cand.candidate_text_internal == "මේ නිසා පාසල වැසිණි."
    assert cand.operations[0].mapping_status == MappingStatus.MANY_TO_ONE
    assert cand.operations[0].mapping_exact is True
