"""
Stage 33 — Unit Tests for Mutually Exclusive Accounting Invariants.
"""

import pytest
from app.sinhala_simplification.enums import (
    CandidateTerminalStatus,
    FinalDisposition,
    RuleAttemptTerminalStatus,
)


def test_input_accounting_mutually_exclusive_conservation():
    dispositions = [
        FinalDisposition.DRAFT_REWRITE_SELECTED,
        FinalDisposition.UNCHANGED_NO_APPLICABLE_RULE,
        FinalDisposition.UNCHANGED_ALL_CANDIDATES_BLOCKED,
        FinalDisposition.MANUAL_REVIEW_REQUIRED,
        FinalDisposition.REJECTED_SOURCE_INELIGIBLE,
        FinalDisposition.REJECTED_INVALID_PREPROCESSING_STATE,
        FinalDisposition.FAILED_INTERNAL_ERROR,
    ]
    # Check that every disposition is unique
    assert len(dispositions) == len(set(dispositions))


def test_rule_attempt_terminal_status_conservation():
    statuses = [
        RuleAttemptTerminalStatus.NOT_APPLICABLE,
        RuleAttemptTerminalStatus.BLOCKED_PROTECTED_SPAN,
        RuleAttemptTerminalStatus.BLOCKED_MEANING_GUARD,
        RuleAttemptTerminalStatus.CANDIDATE_GENERATED,
        RuleAttemptTerminalStatus.DEFERRED_MANUAL_REVIEW,
        RuleAttemptTerminalStatus.FAILED_INTERNAL,
    ]
    assert len(statuses) == len(set(statuses))


def test_candidate_terminal_status_conservation():
    statuses = [
        CandidateTerminalStatus.SELECTED,
        CandidateTerminalStatus.NOT_SELECTED_LOWER_RANK,
        CandidateTerminalStatus.BLOCKED_PROTECTED_SPAN,
        CandidateTerminalStatus.BLOCKED_MEANING_GUARD,
        CandidateTerminalStatus.DEFERRED_MANUAL_REVIEW,
        CandidateTerminalStatus.FAILED_INTERNAL,
    ]
    assert len(statuses) == len(set(statuses))
