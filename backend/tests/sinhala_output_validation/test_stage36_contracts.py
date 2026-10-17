"""
Unit tests for Stage 36 data contracts, schemas, enums, and safety invariants.
Verifies fail-closed validation, extra="forbid", rights inheritance, and non-negotiable child safety defaults.
"""

import pytest
from pydantic import ValidationError

from app.sinhala_output_validation.schemas import (
    AutomatedValidationStatus,
    CandidateDisposition,
    CandidateEnvelope,
    EvidenceClass,
    ExecutionMode,
    ExecutionOutcome,
    FallbackStep,
    FallbackTransitionType,
    GovernanceStatusContract,
    ProviderCondition,
    RequestFinalOutcome,
    RequestTrace,
    SeverityLevel,
    SpanCategory,
    TextSpan,
    ValidationResult,
    ValidatorFinding,
)


class TestTextSpan:
    def test_valid_span(self):
        span = TextSpan(start=0, end=10, text="0123456789")
        assert span.start == 0
        assert span.end == 10
        assert span.text == "0123456789"

    def test_invalid_negative_start(self):
        with pytest.raises(ValidationError):
            TextSpan(start=-1, end=5)

    def test_invalid_end_equal_to_start(self):
        with pytest.raises(ValidationError):
            TextSpan(start=5, end=5)

    def test_invalid_end_less_than_start(self):
        with pytest.raises(ValidationError):
            TextSpan(start=10, end=5)

    def test_forbid_extra_fields(self):
        with pytest.raises(ValidationError):
            TextSpan(start=0, end=5, unexpected_field="disallowed")


class TestCandidateEnvelope:
    @pytest.fixture
    def valid_envelope_data(self):
        return {
            "candidate_id": "cand_001",
            "request_id": "req_001",
            "source_record_id": "rec_001",
            "source_text_ref": "protected://sources/rec_001.txt",
            "source_text_sha256_internal": "a" * 64,
            "candidate_text_ref": "protected://candidates/cand_001.txt",
            "candidate_text_sha256_internal": "b" * 64,
            "provider_condition": ProviderCondition.C0_RULE_BASELINE,
            "execution_mode": ExecutionMode.RULE_ENGINE,
            "generation_configuration_hash": "c" * 32,
            "external_processing_authorized": False,
            "fallback_depth": 0,
        }

    def test_valid_envelope(self, valid_envelope_data):
        envelope = CandidateEnvelope(**valid_envelope_data)
        assert envelope.candidate_id == "cand_001"
        assert envelope.fallback_depth == 0
        assert envelope.external_processing_authorized is False

    def test_invalid_sha256(self, valid_envelope_data):
        data = valid_envelope_data.copy()
        data["source_text_sha256_internal"] = "not_a_valid_sha256_hex"
        with pytest.raises(ValidationError):
            CandidateEnvelope(**data)

    def test_invalid_fallback_depth(self, valid_envelope_data):
        data = valid_envelope_data.copy()
        data["fallback_depth"] = 4  # max is 3
        with pytest.raises(ValidationError):
            CandidateEnvelope(**data)

    def test_gemini_real_provider_requires_external_processing_auth(self, valid_envelope_data):
        data = valid_envelope_data.copy()
        data["provider_condition"] = ProviderCondition.C1_GEMINI_EXPERIMENTAL
        data["execution_mode"] = ExecutionMode.REAL_PROVIDER
        data["external_processing_authorized"] = False
        with pytest.raises(ValidationError, match="external_processing_authorized must be True"):
            CandidateEnvelope(**data)

    def test_gemini_real_provider_with_auth_succeeds(self, valid_envelope_data):
        data = valid_envelope_data.copy()
        data["provider_condition"] = ProviderCondition.C1_GEMINI_EXPERIMENTAL
        data["execution_mode"] = ExecutionMode.REAL_PROVIDER
        data["external_processing_authorized"] = True
        envelope = CandidateEnvelope(**data)
        assert envelope.external_processing_authorized is True

    def test_forbid_extra_envelope_fields(self, valid_envelope_data):
        data = valid_envelope_data.copy()
        data["rogue_metadata"] = "injected"
        with pytest.raises(ValidationError):
            CandidateEnvelope(**data)


class TestValidationResultAndInvariants:
    @pytest.fixture
    def base_result_data(self):
        return {
            "validation_result_id": "val_001",
            "candidate_id": "cand_001",
            "configuration_hash": "d" * 32,
            "execution_outcome": ExecutionOutcome.COMPLETED,
            "candidate_disposition": CandidateDisposition.ACCEPTED_TECHNICAL_RESEARCH_CANDIDATE,
            "automated_validation_status": AutomatedValidationStatus.COMPLETED,
            "completed_validator_count": 9,
            "expected_validator_count": 9,
            "critical_gate_passed": True,
            "fallback_required": False,
        }

    def test_valid_completed_result(self, base_result_data):
        res = ValidationResult(**base_result_data)
        assert res.execution_outcome == ExecutionOutcome.COMPLETED
        assert res.candidate_disposition == CandidateDisposition.ACCEPTED_TECHNICAL_RESEARCH_CANDIDATE
        assert res.approved_for_child_delivery is False
        assert res.approved_for_unsupervised_child_delivery is False

    def test_completed_outcome_requires_disposition(self, base_result_data):
        data = base_result_data.copy()
        data["candidate_disposition"] = None
        with pytest.raises(ValidationError, match="candidate_disposition is required when execution_outcome is COMPLETED"):
            ValidationResult(**data)

    def test_failed_internal_outcome_forbids_disposition(self, base_result_data):
        data = base_result_data.copy()
        data["execution_outcome"] = ExecutionOutcome.FAILED_INTERNAL
        data["candidate_disposition"] = CandidateDisposition.REJECTED_CONFIGURATION_OR_PROVENANCE
        with pytest.raises(ValidationError, match="candidate_disposition must be None when execution_outcome is FAILED_INTERNAL"):
            ValidationResult(**data)

    def test_child_delivery_flag_cannot_be_set_true(self, base_result_data):
        data = base_result_data.copy()
        data["approved_for_child_delivery"] = True
        with pytest.raises(ValidationError, match="Stage 36 automated validation can never set child delivery flags to True"):
            ValidationResult(**data)

    def test_unsupervised_child_delivery_flag_cannot_be_set_true(self, base_result_data):
        data = base_result_data.copy()
        data["approved_for_unsupervised_child_delivery"] = True
        with pytest.raises(ValidationError, match="Stage 36 automated validation can never set child delivery flags to True"):
            ValidationResult(**data)


class TestGovernanceStatusContract:
    def test_default_values(self):
        contract = GovernanceStatusContract()
        assert contract.language == "si"
        assert contract.locale == "si-LK"
        assert contract.script == "Sinh"
        assert contract.validation_status == "draft"
        assert contract.automated_validation_status == AutomatedValidationStatus.NOT_STARTED
        assert contract.completed_validator_count == 0
        assert contract.expected_validator_count == 9
        assert contract.expert_validated_for_this_output is False
        assert contract.research_eligible is False
        assert contract.approved_for_child_delivery is False
        assert contract.approved_for_unsupervised_child_delivery is False
        assert contract.requires_expert_review is True


class TestFallbackAndTrace:
    def test_valid_fallback_step(self):
        step = FallbackStep(
            step_number=1,
            transition_type=FallbackTransitionType.TO_RULE_BASELINE,
            from_candidate_id="cand_001",
            to_candidate_id="cand_002",
            triggering_reason_code="REJ_PROT_SPAN_MISSING",
        )
        assert step.step_number == 1
        assert step.transition_type == FallbackTransitionType.TO_RULE_BASELINE

    def test_valid_request_trace(self):
        trace = RequestTrace(
            request_id="req_001",
            source_record_id="rec_001",
            final_outcome=RequestFinalOutcome.RULE_FALLBACK_SELECTED,
            primary_candidate_id="cand_001",
            selected_candidate_id="cand_002",
            total_fallback_transitions=1,
            fallback_steps=[
                FallbackStep(
                    step_number=1,
                    transition_type=FallbackTransitionType.TO_RULE_BASELINE,
                    from_candidate_id="cand_001",
                    to_candidate_id="cand_002",
                    triggering_reason_code="REJ_PROT_SPAN_MISSING",
                )
            ]
        )
        assert trace.final_outcome == RequestFinalOutcome.RULE_FALLBACK_SELECTED
        assert len(trace.fallback_steps) == 1
