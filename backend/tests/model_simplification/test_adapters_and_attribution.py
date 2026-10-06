"""
Tests for Stage 26 Adapters, Transparent Fallback, and Result Attribution.
"""
import pytest
from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ModelGenerationResult,
    ExecutionStatus,
    NativeValidationDisposition,
    NativeValidationSummary,
)
from app.model_simplification.adapters.stage25_adapter import Stage25ControlledAdapter
from app.model_simplification.adapters.mt5_adapter import MT5ModelAdapter
from app.model_simplification.adapters.mbart_adapter import MBARTModelAdapter
from app.model_simplification.adapters.gemini_adapter import GeminiModelAdapter
from app.model_simplification.provider_result_attribution import ProviderResultAttribution


def test_stage25_adapter_deterministic_generation():
    adapter = Stage25ControlledAdapter()
    req = ModelGenerationRequest(
        request_id="REQ-S25-01",
        text="Before you select the red circle, touch the blue square.",
        support_level="strong",
    )
    res = adapter.generate(req)
    assert res.execution_status == ExecutionStatus.LOCAL_NATIVE_INFERENCE
    assert res.fallback_used is False
    assert res.candidate_text is not None
    assert len(res.candidate_text) > 0


def test_mt5_adapter_fallback_attribution():
    adapter = MT5ModelAdapter()
    req = ModelGenerationRequest(
        request_id="REQ-MT5-01",
        text="Before jumping, raise your hand.",
        support_level="moderate",
    )
    res = adapter.generate(req)
    # When local weights are not loaded in unit test environment, fallback is used
    if res.fallback_used:
        assert res.execution_status == ExecutionStatus.STAGE25_FALLBACK
        assert res.fallback_provider == "stage25_rule_engine"
        
        # Attribution check: outcome must be classified as fallback_delivered, credited to stage25
        cat, provider = ProviderResultAttribution.classify_outcome(res)
        assert cat == ProviderResultAttribution.CAT_FALLBACK_DELIVERED
        assert provider == "stage25_rule_engine"
        assert provider != "huggingface_mt5"


def test_gemini_adapter_no_api_key_triggers_fallback():
    adapter = GeminiModelAdapter(api_key="")
    req = ModelGenerationRequest(
        request_id="REQ-GEMINI-01",
        text="Find the red ball.",
        support_level="mild",
    )
    res = adapter.generate(req)
    assert res.fallback_used is True
    assert res.fallback_provider == "stage25_rule_engine"
    cat, provider = ProviderResultAttribution.classify_outcome(res)
    assert cat == ProviderResultAttribution.CAT_FALLBACK_DELIVERED
    assert provider == "stage25_rule_engine"


def test_provider_attribution_mutual_exclusivity():
    cats = ProviderResultAttribution.ALL_CATEGORIES
    assert len(cats) == 5
    assert len(set(cats)) == 5
