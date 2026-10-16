"""
Stage 33 — Unit Tests for Constrained Subject Recovery.
Verifies that ambiguous subject recovery is routed to manual review rather than inventing referents.
"""

import pytest
from app.sinhala_simplification.candidate_filter import CandidateEligibilityFilter
from app.sinhala_simplification.enums import CandidateTerminalStatus, RuleAttemptTerminalStatus
from app.sinhala_simplification.protected_spans import ProtectedSpanDetector
from app.sinhala_simplification.rule_registry import RuleRegistry
from app.sinhala_simplification.sentence_splitter import SentenceSplitterEngine


def test_ambiguous_subject_recovery_routes_to_review():
    registry = RuleRegistry()
    registry.load_registry()
    rule = registry.get_rule("SI-SNT-SPL-0001")  # සහ splitting
    assert rule is not None

    detector = ProtectedSpanDetector()
    # Sentence where second clause has no clear subject and first clause is empty/pronounless
    text = "කරති සහ සිටිති කියා කියයි."
    spans = detector.detect_spans(text)

    engine = SentenceSplitterEngine()
    results = engine.evaluate_rule(rule, text, "REQ-005", spans, 1, 1)

    assert len(results) == 1
    attempt, cand = results[0]
    assert attempt.terminal_status == RuleAttemptTerminalStatus.CANDIDATE_GENERATED
    assert cand is not None

    # Stage 1 filter routes to DEFERRED_MANUAL_REVIEW or BLOCKED_MEANING_GUARD
    filter_engine = CandidateEligibilityFilter()
    eligible, eliminated = filter_engine.filter_candidates([cand], text, spans)
    assert len(eligible) == 0
    assert len(eliminated) == 1
    assert eliminated[0].terminal_status in (
        CandidateTerminalStatus.DEFERRED_MANUAL_REVIEW,
        CandidateTerminalStatus.BLOCKED_MEANING_GUARD
    )
