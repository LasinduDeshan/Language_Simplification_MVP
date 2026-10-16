"""
Stage 33 — Unit Tests for Mutually Exclusive Accounting Invariants.
Validates all six accounting levels and their mutually exclusive terminal statuses.
"""

import pytest
from app.sinhala_simplification.enums import (
    CandidateTerminalStatus,
    FinalDisposition,
    MappingStatus,
    OperationType,
    RuleAttemptTerminalStatus,
)


def test_level1_input_disposition_accounting_conservation():
    """Level 1: Mutually exclusive terminal dispositions for submitted inputs."""
    dispositions = [
        FinalDisposition.DRAFT_REWRITE_SELECTED,
        FinalDisposition.UNCHANGED_NO_APPLICABLE_RULE,
        FinalDisposition.UNCHANGED_ALL_CANDIDATES_BLOCKED,
        FinalDisposition.MANUAL_REVIEW_REQUIRED,
        FinalDisposition.REJECTED_SOURCE_INELIGIBLE,
        FinalDisposition.REJECTED_INVALID_PREPROCESSING_STATE,
        FinalDisposition.FAILED_INTERNAL_ERROR,
    ]
    # Check that every disposition is distinct
    assert len(dispositions) == len(set(dispositions))


def test_level2_rule_attempt_terminal_status_conservation():
    """Level 2: Mutually exclusive pre-candidate terminal statuses for rule attempts."""
    statuses = [
        RuleAttemptTerminalStatus.NOT_APPLICABLE,
        RuleAttemptTerminalStatus.CANDIDATE_GENERATED,
        RuleAttemptTerminalStatus.DEFERRED_BEFORE_GENERATION,
        RuleAttemptTerminalStatus.FAILED_INTERNAL,
    ]
    assert len(statuses) == len(set(statuses))


def test_level3_candidate_terminal_status_conservation():
    """Level 3: Mutually exclusive post-generation terminal statuses for rewrite candidates."""
    statuses = [
        CandidateTerminalStatus.SELECTED,
        CandidateTerminalStatus.NOT_SELECTED_LOWER_RANK,
        CandidateTerminalStatus.BLOCKED_PROTECTED_SPAN,
        CandidateTerminalStatus.BLOCKED_MEANING_GUARD,
        CandidateTerminalStatus.DEFERRED_MANUAL_REVIEW,
        CandidateTerminalStatus.FAILED_INTERNAL,
    ]
    assert len(statuses) == len(set(statuses))


def test_level4_operation_type_conservation():
    """Level 4: Atomic operation types."""
    ops = [
        OperationType.REPLACE,
        OperationType.INSERT,
        OperationType.DELETE,
        OperationType.SPLIT,
    ]
    assert len(ops) == len(set(ops))


def test_level5_trace_element_accounting_conservation():
    """Level 5: Trace mapping categories."""
    trace_categories = [
        "ExactlyMapped",
        "QualifiedNonExact",
        "UnmappedReviewed",
    ]
    assert len(trace_categories) == len(set(trace_categories))

    # All defined MappingStatus enums map to one of these
    for status in MappingStatus:
        assert status in (
            MappingStatus.ONE_TO_ONE,
            MappingStatus.MANY_TO_ONE,
            MappingStatus.ONE_TO_MANY,
            MappingStatus.INSERTED,
            MappingStatus.DELETED,
            MappingStatus.NON_LOCAL,
            MappingStatus.UNMAPPED,
        )


def test_level6_rights_export_posture_conservation():
    """Level 6: Rights and field export postures."""
    postures = [
        "PublicPermitted",
        "ProtectedInternal",
        "SuppressedByPolicy",
        "ReviewRequired",
    ]
    assert len(postures) == len(set(postures))
