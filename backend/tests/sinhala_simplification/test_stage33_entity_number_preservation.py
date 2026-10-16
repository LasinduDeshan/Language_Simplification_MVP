"""
Stage 33 — Unit Tests for Entity & Number Invariant Preservation.
"""

import pytest
from app.sinhala_simplification.candidate_filter import CandidateEligibilityFilter
from app.sinhala_simplification.enums import CandidateTerminalStatus
from app.sinhala_simplification.schemas import CodePointSpan, ProtectedSpan, ProtectedSpanCategory, RewriteCandidate


def test_entity_preservation_guard_blocks_tampered_entities():
    cand_filter = CandidateEligibilityFilter()
    source = "ශ්‍රී ලංකාවේ අගනුවර කොළඹ වේ."

    entity_span = ProtectedSpan(
        span_id="PROT-001",
        category=ProtectedSpanCategory.NAMED_ENTITY,
        span=CodePointSpan(start_code_point=18, end_code_point=23, text="කොළඹ"),
        text="කොළඹ",
        detector_rule_id="DET-NER-01",
        detector_version=1,
        confidence=1.0,
        allowlist_override=False
    )

    # Candidate modifying entity from කොළඹ to නගරය
    tampered_cand = RewriteCandidate(
        candidate_id="CAND-TAMPER-01",
        request_id="REQ-01",
        rule_id="SI-LEX-SUB-0001",
        candidate_text_internal="ශ්‍රී ලංකාවේ අගනුවර නගරය වේ.",
        candidate_sha256_internal="f" * 64,
        operations=[],
        guard_results={},
        all_guards_passed=False,
        terminal_status=CandidateTerminalStatus.NOT_SELECTED_LOWER_RANK
    )

    eligible, eliminated = cand_filter.filter_candidates([tampered_cand], source, [entity_span])

    assert len(eligible) == 0
    assert len(eliminated) == 1
    assert eliminated[0].terminal_status == CandidateTerminalStatus.BLOCKED_PROTECTED_SPAN
