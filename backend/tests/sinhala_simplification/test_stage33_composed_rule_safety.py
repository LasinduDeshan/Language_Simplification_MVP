"""
Stage 33 — Unit Tests for Multi-Rule Composition Safety & Atomic Policy.
Validates that:
1. Pipeline enforces atomic single-rule candidate generation policy.
2. Composed transformations cannot bypass meaning-preservation guards.
"""

from app.sinhala_simplification.candidate_filter import CandidateEligibilityFilter
from app.sinhala_simplification.enums import (
    CandidateTerminalStatus,
    MappingStatus,
    OperationType,
    ProtectedSpanCategory,
)
from app.sinhala_simplification.pipeline import SimplificationPipeline
from app.sinhala_simplification.schemas import (
    CodePointSpan,
    ProtectedSpan,
    RewriteCandidate,
    RewriteRequest,
    RightsProfileBinding,
    TransformationOperation,
)
from app.sinhala_simplification.storage import compute_sha256


def test_atomic_single_rule_candidate_policy():
    """Verify that all generated candidates apply exactly one rule (atomic policy)."""
    pipeline = SimplificationPipeline()
    pipeline.initialize()

    req = RewriteRequest(
        request_id="SI-TEST-COMP-001",
        record_id="SI-PILOT-000001",
        source_storage_ref="data/sinhala_external/corpus/canonical_analytical_corpus.jsonl#record_id=SI-PILOT-000001",
        source_sha256_internal=compute_sha256("නමුත් මේ හේතුවෙන් පිළිබඳව"),
        stage30_configuration_hash="0" * 64,
        stage31_split_manifest_hash="0" * 64,
        stage32_configuration_hash="0" * 64,
        stage32_lexicon_manifest_hash="0" * 64,
        stage33_configuration_hash="0" * 64,
        rights_profile_ids_and_versions=[
            RightsProfileBinding(rights_profile_id="RP-SRC-SI-001", rights_profile_version=1)
        ],
        partition="train"
    )

    # Text contains triggers for multiple rules (නමුත්, මේ හේතුවෙන්, පිළිබඳව)
    text = "නමුත් මේ හේතුවෙන් පිළිබඳව පරීක්ෂා කරයි."
    final_rec, attempts, candidates, operations = pipeline.process_request(req, text)

    # In Stage 33, each candidate must be atomic (exactly 1 rule and exactly 1 operation)
    for cand in candidates:
        assert len(cand.operations) == 1, (
            f"Candidate {cand.candidate_id} violated atomic rule policy: "
            f"found {len(cand.operations)} operations"
        )


def test_composed_transformations_cannot_bypass_meaning_guards():
    """Verify that jointly composed transformations fail closed if any meaning guard is violated."""
    filter_engine = CandidateEligibilityFilter()

    # Source contains a protected entity and negation
    source_text = "කොළඹ නගරයේ තවදුරටත් වර්ෂාව නැත."
    protected_spans = [
        ProtectedSpan(
            span_id="PROT-01",
            category=ProtectedSpanCategory.NAMED_ENTITY,
            span=CodePointSpan(start_code_point=0, end_code_point=5, text="කොළඹ"),
            text="කොළඹ",
            detector_rule_id="DET-NER-01",
            detector_version=1,
            confidence=1.0,
            allowlist_override=False
        )
    ]

    # Hypothetical composed candidate:
    # Op 1: Replaces 'කොළඹ' (protected) with 'නගරය'
    # Op 2: Replaces 'තවදුරටත්' with 'තවත්' (in negation scope)
    cand_text = "නගරය නගරයේ තවත් වර්ෂාව නැත."
    op1 = TransformationOperation(
        operation_id="OP-COMP-01",
        operation_type=OperationType.REPLACE,
        rule_id="SI-LEX-SUB-0001",
        raw_source_spans=[CodePointSpan(start_code_point=0, end_code_point=5, text="කොළඹ")],
        normalized_source_spans=[CodePointSpan(start_code_point=0, end_code_point=5, text="කොළඹ")],
        output_spans=[CodePointSpan(start_code_point=0, end_code_point=5, text="නගරය")],
        mapping_status=MappingStatus.ONE_TO_ONE,
        mapping_exact=True,
        before_hash_internal=compute_sha256("කොළඹ"),
        after_hash_internal=compute_sha256("නගරය"),
        before_text_internal="කොළඹ",
        after_text_internal="නගරය"
    )
    op2 = TransformationOperation(
        operation_id="OP-COMP-02",
        operation_type=OperationType.REPLACE,
        rule_id="SI-LEX-SUB-0002",
        raw_source_spans=[CodePointSpan(start_code_point=12, end_code_point=21, text="තවදුරටත්")],
        normalized_source_spans=[CodePointSpan(start_code_point=12, end_code_point=21, text="තවදුරටත්")],
        output_spans=[CodePointSpan(start_code_point=12, end_code_point=16, text="තවත්")],
        mapping_status=MappingStatus.ONE_TO_ONE,
        mapping_exact=True,
        before_hash_internal=compute_sha256("තවදුරටත්"),
        after_hash_internal=compute_sha256("තවත්"),
        before_text_internal="තවදුරටත්",
        after_text_internal="තවත්"
    )

    composed_candidate = RewriteCandidate(
        candidate_id="SI-CAND-COMPOSITE-001",
        request_id="SI-REQ-COMP-01",
        rule_id="SI-COMPOSITE-01",
        candidate_text_internal=cand_text,
        candidate_sha256_internal=compute_sha256(cand_text),
        operations=[op1, op2],
        applied_rule_ids=["SI-LEX-SUB-0001", "SI-LEX-SUB-0002"],
        guard_results={},
        all_guards_passed=False,
        terminal_status=CandidateTerminalStatus.NOT_SELECTED_LOWER_RANK
    )

    eligible, eliminated = filter_engine.filter_candidates([composed_candidate], source_text, protected_spans)

    # Must be strictly eliminated before guard evaluation
    assert len(eligible) == 0, "Composite candidate unexpectedly passed eligibility filter"
    assert len(eliminated) == 1, "Composite candidate was not eliminated"
    elim_cand = eliminated[0]
    assert elim_cand.terminal_status == CandidateTerminalStatus.BLOCKED_MEANING_GUARD
    assert "VIOLATED_ATOMIC_RULE_POLICY" in elim_cand.guard_results["ATOMIC_RULE_POLICY"].reason_codes
