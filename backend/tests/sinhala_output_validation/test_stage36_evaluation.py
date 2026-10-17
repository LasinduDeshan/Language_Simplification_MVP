"""
Governed evaluation test suite for Stage 36 (WP8).
Executes frozen pipeline across the 16 declared evaluation fixtures and reconciles
the 9-level accounting framework.
"""

import hashlib
import json
from pathlib import Path
import pytest

from app.sinhala_output_validation.calibration_fixtures import DEVELOPMENT_CALIBRATION_FIXTURES
from app.sinhala_output_validation.engine import GovernedFallbackOrchestrator
from app.sinhala_output_validation.evaluation_fixtures import GOVERNED_FINAL_EVALUATION_FIXTURES
from app.sinhala_output_validation.schemas import (
    CandidateEnvelope,
    ExecutionMode,
    ProviderCondition,
    RequestFinalOutcome,
)
from app.sinhala_output_validation.storage import (
    CryptographicAuditLogger,
    ENV_PROTECTED_ROOT,
    write_protected_content,
)

FROZEN_CONFIG_HASH = "7175125fbb32459a8f41100007c13c37994a1063ffb04b745414bd58a22aaaf6"


def test_fixtures_zero_overlap_verification():
    """Verify that development calibration fixtures and final evaluation fixtures have 0 overlap."""
    dev_ids = {f["fixture_id"] for f in DEVELOPMENT_CALIBRATION_FIXTURES}
    eval_ids = {f["fixture_id"] for f in GOVERNED_FINAL_EVALUATION_FIXTURES}
    assert len(dev_ids & eval_ids) == 0, f"ID overlap detected: {dev_ids & eval_ids}"

    dev_src = {hashlib.sha256(f["source_text"].encode("utf-8")).hexdigest() for f in DEVELOPMENT_CALIBRATION_FIXTURES}
    eval_src = {hashlib.sha256(f["source_text"].encode("utf-8")).hexdigest() for f in GOVERNED_FINAL_EVALUATION_FIXTURES}
    assert len(dev_src & eval_src) == 0, "Source text hash overlap detected between dev and eval fixtures!"

    dev_cand = {hashlib.sha256(f["candidate_text"].encode("utf-8")).hexdigest() for f in DEVELOPMENT_CALIBRATION_FIXTURES}
    eval_cand = {hashlib.sha256(f["primary_text"].encode("utf-8")).hexdigest() for f in GOVERNED_FINAL_EVALUATION_FIXTURES}
    assert len(dev_cand & eval_cand) == 0, "Candidate text hash overlap detected between dev and eval fixtures!"



@pytest.fixture
def test_storage(tmp_path, monkeypatch):
    root = tmp_path / "protected_eval_root"
    root.mkdir()
    monkeypatch.setenv(ENV_PROTECTED_ROOT, str(root))
    return root


class TestGovernedEvaluation:
    @pytest.mark.parametrize(
        "fixture",
        GOVERNED_FINAL_EVALUATION_FIXTURES,
        ids=[f["fixture_id"] for f in GOVERNED_FINAL_EVALUATION_FIXTURES]
    )
    def test_fixture_evaluation(self, fixture, test_storage):
        src_bytes = fixture["source_text"].encode("utf-8")
        cand_bytes = fixture["primary_text"].encode("utf-8")

        src_uri, src_hash = write_protected_content(
            "sources", f"{fixture['fixture_id'].lower()}_src.txt", src_bytes
        )
        cand_uri, cand_hash = write_protected_content(
            "candidates", f"{fixture['fixture_id'].lower()}_cand.txt", cand_bytes
        )

        envelope_data = {
            "candidate_id": f"cand_{fixture['fixture_id'].lower()}",
            "request_id": f"req_{fixture['fixture_id'].lower()}",
            "source_record_id": f"rec_{fixture['fixture_id'].lower()}",
            "source_text_ref": src_uri,
            "source_text_sha256_internal": src_hash,
            "candidate_text_ref": cand_uri,
            "candidate_text_sha256_internal": cand_hash,
            "provider_condition": ProviderCondition.C1_GEMINI_EXPERIMENTAL,
            "execution_mode": ExecutionMode.SIMULATED,
            "generation_configuration_hash": FROZEN_CONFIG_HASH,
            "external_processing_authorized": False,
            "simulation_only": True,
        }
        envelope_data.update(fixture.get("primary_envelope_override", {}))
        primary_envelope = CandidateEnvelope(**envelope_data)

        orchestrator = GovernedFallbackOrchestrator(configuration_hash=FROZEN_CONFIG_HASH)
        res, trace = orchestrator.process_request(
            request_id=primary_envelope.request_id,
            source_record_id=primary_envelope.source_record_id,
            source_text=fixture["source_text"],
            primary_envelope=primary_envelope,
            primary_candidate_text=fixture["primary_text"],
            context=fixture["context"].copy(),
            rule_simplifier=fixture["rule_simplifier"],
        )

        expected_outcome = fixture["expected_final_outcome"]
        actual_outcome = trace.final_outcome

        assert actual_outcome == expected_outcome, (
            f"Fixture {fixture['fixture_id']} outcome mismatch: expected {expected_outcome}, got {actual_outcome}. "
            f"Transitions: {[s.model_dump() for s in trace.fallback_steps]}. "
            f"Findings: {[f.model_dump() for f in res.findings]}"
        )

        # Invariant checks
        assert res.approved_for_child_delivery is False
        assert res.approved_for_unsupervised_child_delivery is False
        assert res.requires_expert_review is True

    def test_full_level7_accounting_reconciliation(self, test_storage):
        """
        Executes all 16 fixtures and reconciles Level 7 mathematical accounting:
        RegisteredRequests = SelectedOutputs + AbstentionsNoOutput + Unaccounted
        SelectedOutputs = PrimarySelected + RuleFallbackSelected + UnchangedResearchOnly
        AbstentionsNoOutput = ManualReviewNoOutput + RejectedNoOutput + FailedInternalNoOutput
        Assert Unaccounted == 0 and ChildDeliveryApproved == 0.
        """
        orchestrator = GovernedFallbackOrchestrator(configuration_hash=FROZEN_CONFIG_HASH)
        audit_logger = CryptographicAuditLogger(log_filename="governed_evaluation_audit.jsonl")

        registered_requests = len(GOVERNED_FINAL_EVALUATION_FIXTURES)
        primary_selected = 0
        rule_fallback_selected = 0
        unchanged_research_only = 0
        manual_review_no_output = 0
        rejected_no_output = 0
        failed_internal_no_output = 0

        for fixture in GOVERNED_FINAL_EVALUATION_FIXTURES:
            src_bytes = fixture["source_text"].encode("utf-8")
            cand_bytes = fixture["primary_text"].encode("utf-8")

            src_uri, src_hash = write_protected_content(
                "sources", f"acc_{fixture['fixture_id'].lower()}_src.txt", src_bytes
            )
            cand_uri, cand_hash = write_protected_content(
                "candidates", f"acc_{fixture['fixture_id'].lower()}_cand.txt", cand_bytes
            )

            envelope_data = {
                "candidate_id": f"cand_acc_{fixture['fixture_id'].lower()}",
                "request_id": f"req_acc_{fixture['fixture_id'].lower()}",
                "source_record_id": f"rec_acc_{fixture['fixture_id'].lower()}",
                "source_text_ref": src_uri,
                "source_text_sha256_internal": src_hash,
                "candidate_text_ref": cand_uri,
                "candidate_text_sha256_internal": cand_hash,
                "provider_condition": ProviderCondition.C1_GEMINI_EXPERIMENTAL,
                "execution_mode": ExecutionMode.SIMULATED,
                "generation_configuration_hash": FROZEN_CONFIG_HASH,
                "external_processing_authorized": False,
                "simulation_only": True,
            }
            envelope_data.update(fixture.get("primary_envelope_override", {}))
            primary_envelope = CandidateEnvelope(**envelope_data)

            res, trace = orchestrator.process_request(
                request_id=primary_envelope.request_id,
                source_record_id=primary_envelope.source_record_id,
                source_text=fixture["source_text"],
                primary_envelope=primary_envelope,
                primary_candidate_text=fixture["primary_text"],
                context=fixture["context"].copy(),
                rule_simplifier=fixture["rule_simplifier"],
            )

            audit_logger.log_event("REQUEST_EVALUATED", {
                "request_id": trace.request_id,
                "final_outcome": trace.final_outcome,
                "transitions": trace.total_fallback_transitions,
            })

            outcome = trace.final_outcome
            if outcome == RequestFinalOutcome.PRIMARY_CANDIDATE_SELECTED.value:
                primary_selected += 1
            elif outcome == RequestFinalOutcome.RULE_FALLBACK_SELECTED.value:
                rule_fallback_selected += 1
            elif outcome == RequestFinalOutcome.UNCHANGED_SOURCE_SELECTED_FOR_RESEARCH_ONLY.value:
                unchanged_research_only += 1
            elif outcome == RequestFinalOutcome.MANUAL_REVIEW_NO_OUTPUT.value:
                manual_review_no_output += 1
            elif outcome == RequestFinalOutcome.REJECTED_NO_OUTPUT.value:
                rejected_no_output += 1
            elif outcome == RequestFinalOutcome.FAILED_INTERNAL_NO_OUTPUT.value:
                failed_internal_no_output += 1

        selected_outputs = primary_selected + rule_fallback_selected + unchanged_research_only
        abstentions_no_output = manual_review_no_output + rejected_no_output + failed_internal_no_output
        unaccounted = registered_requests - (selected_outputs + abstentions_no_output)

        assert registered_requests == 16
        assert primary_selected == 3
        assert rule_fallback_selected == 7
        assert unchanged_research_only == 2
        assert selected_outputs == 12
        assert manual_review_no_output == 2
        assert rejected_no_output == 2
        assert failed_internal_no_output == 0
        assert abstentions_no_output == 4
        assert unaccounted == 0

        # Audit log verification
        is_valid, log_count, err = audit_logger.verify_log_integrity()
        assert is_valid is True
        assert log_count == 16
        assert err is None
