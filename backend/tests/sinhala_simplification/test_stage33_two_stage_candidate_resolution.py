"""
Stage 33 — Unit Tests for Two-Stage Candidate Resolution Architecture.
Verifies that candidate filtering and candidate ranking are decoupled and that
blocked candidates never participate in ranking.
"""

import pytest
from app.sinhala_simplification.candidate_filter import CandidateEligibilityFilter
from app.sinhala_simplification.candidate_ranker import CandidateRanker
from app.sinhala_simplification.enums import CandidateTerminalStatus, GuardType, OperationType, RuleType
from app.sinhala_simplification.rule_registry import GovernedRuleDefinition
from app.sinhala_simplification.schemas import (
    CodePointSpan,
    GuardResult,
    ProtectedSpan,
    RewriteCandidate,
    SimplificationRule,
    TransformationOperation,
)


def test_blocked_candidates_eliminated_before_ranking():
    cand_filter = CandidateEligibilityFilter()
    cand_ranker = CandidateRanker()

    source = "මෙම පොත 2024 වසරේ පළ විය."

    # Candidate 1: valid eligible candidate
    cand1 = RewriteCandidate(
        candidate_id="CAND-01",
        request_id="REQ-01",
        rule_id="SI-LEX-SUB-0001",
        candidate_text_internal="මෙම පොත 2024 වසරේ නිකුත් විය.",
        candidate_sha256_internal="a" * 64,
        operations=[],
        guard_results={},
        all_guards_passed=False,
        terminal_status=CandidateTerminalStatus.NOT_SELECTED_LOWER_RANK
    )

    # Candidate 2: invalid candidate altering the number 2024 to 2025
    cand2 = RewriteCandidate(
        candidate_id="CAND-02",
        request_id="REQ-01",
        rule_id="SI-LEX-SUB-0002",
        candidate_text_internal="මෙම පොත 2025 වසරේ පළ විය.",
        candidate_sha256_internal="b" * 64,
        operations=[],
        guard_results={},
        all_guards_passed=False,
        terminal_status=CandidateTerminalStatus.NOT_SELECTED_LOWER_RANK
    )

    eligible, eliminated = cand_filter.filter_candidates([cand1, cand2], source, [])

    # CAND-02 must be eliminated due to number mismatch
    assert len(eligible) == 1
    assert eligible[0].candidate_id == "CAND-01"
    assert len(eliminated) == 1
    assert eliminated[0].candidate_id == "CAND-02"
    assert eliminated[0].terminal_status == CandidateTerminalStatus.BLOCKED_MEANING_GUARD

    # Ranking must only receive CAND-01
    rule1 = GovernedRuleDefinition(
        SimplificationRule(
            rule_id="SI-LEX-SUB-0001",
            rule_version=1,
            rule_type=RuleType.LEXICAL_SUBSTITUTION,
            authoring_method="technical_rule_authoring",
            author_id_or_team="stage33_technical_team",
            evidence_type="test",
            evidence_refs=["REF1"],
            rights_profile_refs=["RP1"],
            source_pattern_ref="sref",
            target_template_ref="tref",
            priority=100
        ),
        "source", "target"
    )

    selected, ranked = cand_ranker.rank_candidates(eligible, {"SI-LEX-SUB-0001": rule1}, source)
    assert selected is not None
    assert selected.candidate_id == "CAND-01"
    assert selected.terminal_status == CandidateTerminalStatus.SELECTED
