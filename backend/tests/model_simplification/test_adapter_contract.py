"""
Tests for Model Simplification Adapters and Contracts.
"""

import pytest
from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ModelGenerationResult,
    SupportLevel,
    ProtectedElements,
    ProviderType
)
from app.model_simplification.adapters.stage25_adapter import Stage25ModelAdapter
from app.model_simplification.adapters.gemini_adapter import GeminiModelAdapter
from app.model_simplification.adapters.mt5_adapter import Mt5ModelAdapter
from app.model_simplification.adapters.mbart_adapter import MbartModelAdapter


def test_adapter_contract_stage25():
    adapter = Stage25ModelAdapter()
    req = ModelGenerationRequest(
        request_id="REQ-TEST-001",
        text="Identify the depicted cat.",
        support_level=SupportLevel.MODERATE,
        protected_elements=ProtectedElements(exact_preservation=["cat"])
    )
    res = adapter.generate(req)
    assert isinstance(res, ModelGenerationResult)
    assert res.request_id == "REQ-TEST-001"
    assert res.requested_provider == "controlled_stage25"
    assert res.candidate_text != ""
    assert res.metrics_attributed_to == "controlled_stage25"


def test_adapter_contract_gemini():
    adapter = GeminiModelAdapter()
    req = ModelGenerationRequest(
        request_id="REQ-TEST-002",
        text="Before placing the red ball inside the box, select the smaller blue object.",
        support_level=SupportLevel.STRONG,
        protected_elements=ProtectedElements(exact_preservation=["red", "blue", "ball", "box"])
    )
    res = adapter.generate(req)
    assert isinstance(res, ModelGenerationResult)
    assert res.requested_provider == "gemini"
    assert res.resolved_model != ""
    assert res.candidate_text != ""
    assert res.input_token_count > 0
    assert res.output_token_count > 0
    assert res.estimated_cost_usd is not None


def test_adapter_contract_mt5_and_mbart():
    mt5 = Mt5ModelAdapter()
    mbart = MbartModelAdapter()
    
    req = ModelGenerationRequest(
        request_id="REQ-TEST-003",
        text="Identify and state the name of the depicted domestic animal.",
        support_level=SupportLevel.MILD
    )
    
    res_mt5 = mt5.generate(req)
    assert res_mt5.requested_provider == "mt5"
    assert "google/mt5-small" in res_mt5.configured_model
    assert res_mt5.candidate_text != ""

    res_mbart = mbart.generate(req)
    assert res_mbart.requested_provider == "mbart"
    assert "facebook/mbart-large-50" in res_mbart.configured_model
    assert res_mbart.candidate_text != ""
