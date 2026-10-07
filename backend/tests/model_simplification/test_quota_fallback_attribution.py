"""
Unit tests for explicit fallback attribution when quota is exceeded or provider fails.
"""
from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ModelGenerationResult,
    ExecutionStatus,
    NativeValidationDisposition,
    NativeValidationSummary,
)
from app.model_simplification.provider_result_attribution import ProviderResultAttribution


def test_quota_fallback_attribution_is_explicit():
    # Construct a result where Gemini failed due to quota and Stage 25 was returned
    res = ModelGenerationResult(
        request_id="GENREQ-TEST-429",
        requested_provider="gemini",
        configured_model="gemini-3.5-flash-lite",
        resolved_model="gemini-3.5-flash-lite",
        model_resolution_status="fallback_invoked",
        execution_status=ExecutionStatus.STAGE25_FALLBACK,
        provider_calls_attempted=1,
        candidate_text="The doctor gave the medicine.",
        native_validation=NativeValidationSummary(
            disposition=NativeValidationDisposition.PROVIDER_UNAVAILABLE,
            failed_gates=["live_provider_exhausted_or_failed"],
            similarity_score=0.95,
        ),
        latency_ms=35.0,
        fallback_used=True,
        fallback_provider="stage25_rule_engine",
        generator_method="controlled_stage25_fallback",
        prompt_template_version="2.1.0",
    )

    cat, eff_provider = ProviderResultAttribution.classify_outcome(res)
    assert cat == ProviderResultAttribution.CAT_FALLBACK_DELIVERED
    assert eff_provider == "stage25_rule_engine"
    assert res.fallback_used is True
    assert res.execution_status == ExecutionStatus.STAGE25_FALLBACK
