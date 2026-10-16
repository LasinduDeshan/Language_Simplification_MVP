"""
Stage 33 — Unit Tests for Lexical Substitution Rules.
"""

import pytest
from app.sinhala_simplification.candidate_filter import CandidateEligibilityFilter
from app.sinhala_simplification.enums import CandidateTerminalStatus, RuleAttemptTerminalStatus
from app.sinhala_simplification.lexical_rules import LexicalRuleEngine
from app.sinhala_simplification.protected_spans import ProtectedSpanDetector
from app.sinhala_simplification.rule_registry import RuleRegistry


def test_lexical_rule_substitution():
    registry = RuleRegistry()
    registry.load_registry()
    rule = registry.get_rule("SI-LEX-SUB-0001")  # පිළිබඳව -> ගැන
    assert rule is not None

    detector = ProtectedSpanDetector()
    text = "මෙම පොත පිළිබඳව සාකච්ඡා කරමු."
    spans = detector.detect_spans(text)

    engine = LexicalRuleEngine()
    results = engine.evaluate_rule(rule, text, "REQ-001", spans, 1, 1)

    assert len(results) == 1
    attempt, cand = results[0]
    assert attempt.terminal_status == RuleAttemptTerminalStatus.CANDIDATE_GENERATED
    assert cand is not None
    assert cand.candidate_text_internal == "මෙම පොත ගැන සාකච්ඡා කරමු."
    assert cand.operations[0].mapping_exact is True


def test_lexical_rule_negation_blocking():
    registry = RuleRegistry()
    registry.load_registry()
    rule = registry.get_rule("SI-LEX-SUB-0002")  # තවදුරටත් -> තවත්
    assert rule is not None

    detector = ProtectedSpanDetector()
    text = "ඔහු තවදුරටත් නැත."  # "no longer" idiom
    spans = detector.detect_spans(text)

    engine = LexicalRuleEngine()
    results = engine.evaluate_rule(rule, text, "REQ-002", spans, 1, 1)

    assert len(results) == 1
    attempt, cand = results[0]
    assert attempt.terminal_status == RuleAttemptTerminalStatus.CANDIDATE_GENERATED
    assert cand is not None

    # Stage 1 filter blocks the candidate under negation scope guard
    filter_engine = CandidateEligibilityFilter()
    eligible, eliminated = filter_engine.filter_candidates([cand], text, spans)
    assert len(eligible) == 0
    assert len(eliminated) == 1
    assert eliminated[0].terminal_status == CandidateTerminalStatus.BLOCKED_MEANING_GUARD
    assert "WITHIN_NEGATION_SCOPE" in eliminated[0].guard_results["NEGATION_PRESERVATION"].reason_codes
