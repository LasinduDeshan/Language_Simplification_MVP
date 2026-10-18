"""
Tests for Stage 36 development fixture calibration (WP7A).
Verifies that all 14 development fixtures produce their exact expected dispositions.
"""

import pytest

from app.sinhala_output_validation.calibration_fixtures import DEVELOPMENT_CALIBRATION_FIXTURES
from app.sinhala_output_validation.engine import validate_candidate
from app.sinhala_output_validation.schemas import (
    CandidateEnvelope,
    ExecutionMode,
    ProviderCondition,
)


@pytest.mark.parametrize("fixture", DEVELOPMENT_CALIBRATION_FIXTURES, ids=[f["fixture_id"] for f in DEVELOPMENT_CALIBRATION_FIXTURES])
def test_calibration_fixture_disposition(fixture):
    envelope = CandidateEnvelope(
        candidate_id=f"cand_{fixture['fixture_id'].lower()}",
        request_id=f"req_{fixture['fixture_id'].lower()}",
        source_record_id=f"rec_{fixture['fixture_id'].lower()}",
        source_text_ref=f"protected://sources/{fixture['fixture_id'].lower()}.txt",
        source_text_sha256_internal="a" * 64,
        candidate_text_ref=f"protected://candidates/{fixture['fixture_id'].lower()}.txt",
        candidate_text_sha256_internal="b" * 64,
        provider_condition=ProviderCondition.C0_RULE_BASELINE,
        execution_mode=ExecutionMode.RULE_ENGINE,
        generation_configuration_hash="calib_hash_1234567890",
        external_processing_authorized=False,
    )

    result = validate_candidate(
        source_text=fixture["source_text"],
        candidate_text=fixture["candidate_text"],
        envelope=envelope,
        context=fixture["context"].copy(),
        configuration_hash="calib_hash_1234567890",
    )

    actual_disp = (
        result.candidate_disposition.value
        if hasattr(result.candidate_disposition, "value")
        else result.candidate_disposition
    )
    expected_disp = (
        fixture["expected_disposition"].value
        if hasattr(fixture["expected_disposition"], "value")
        else fixture["expected_disposition"]
    )

    assert actual_disp == expected_disp, (
        f"Fixture {fixture['fixture_id']} failed: expected {expected_disp}, got {actual_disp}. "
        f"Findings: {[f.model_dump() for f in result.findings]}"
    )
