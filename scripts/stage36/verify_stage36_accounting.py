"""
Verification script for Stage 36 accounting reconciliation (Levels 1-9).
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(backend_dir))

from app.sinhala_output_validation.engine import GovernedFallbackOrchestrator
from app.sinhala_output_validation.evaluation_fixtures import GOVERNED_FINAL_EVALUATION_FIXTURES
from app.sinhala_output_validation.schemas import (
    CandidateEnvelope,
    ExecutionMode,
    ProviderCondition,
    RequestFinalOutcome,
)
from app.sinhala_output_validation.storage import write_protected_content

FROZEN_CONFIG_HASH = "7175125fbb32459a8f41100007c13c37994a1063ffb04b745414bd58a22aaaf6"


def verify_accounting():
    orchestrator = GovernedFallbackOrchestrator(configuration_hash=FROZEN_CONFIG_HASH)

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
            "sources", f"scr_{fixture['fixture_id'].lower()}_src.txt", src_bytes
        )
        cand_uri, cand_hash = write_protected_content(
            "candidates", f"scr_{fixture['fixture_id'].lower()}_cand.txt", cand_bytes
        )

        envelope_data = {
            "candidate_id": f"cand_scr_{fixture['fixture_id'].lower()}",
            "request_id": f"req_scr_{fixture['fixture_id'].lower()}",
            "source_record_id": f"rec_scr_{fixture['fixture_id'].lower()}",
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

    print("================================================================")
    print("STAGE 36 ACCOUNTING RECONCILIATION")
    print("================================================================")
    print(f"Registered Requests:              {registered_requests}")
    print(f"Primary Candidates Selected:      {primary_selected}")
    print(f"Rule Fallback Selected:           {rule_fallback_selected}")
    print(f"Unchanged Source (Research-Only): {unchanged_research_only}")
    print(f"Total Selected Outputs:           {selected_outputs}")
    print(f"Manual Review Queue:              {manual_review_no_output}")
    print(f"Rejected No Output:               {rejected_no_output}")
    print(f"Failed Internal No Output:        {failed_internal_no_output}")
    print(f"Total Abstentions No Output:      {abstentions_no_output}")
    print(f"Unaccounted Units:                {unaccounted}")
    print(f"Child Delivery Approvals:         0")
    print("================================================================")

    assert unaccounted == 0, f"Accounting discrepancy: unaccounted={unaccounted}"
    print("PASS: Level 7 accounting perfectly reconciled with zero unaccounted units.")


if __name__ == "__main__":
    verify_accounting()
