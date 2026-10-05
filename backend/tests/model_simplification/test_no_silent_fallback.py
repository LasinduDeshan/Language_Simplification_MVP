"""
Tests for No Silent Fallback Policy and Attribution Integrity.
"""

from app.model_simplification.hybrid_pipeline import HybridSimplificationPipeline
from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ProtectedElements,
    SupportLevel,
    ProviderType
)
from app.model_simplification.adapters.gemini_adapter import GeminiModelAdapter


def test_no_silent_fallback_on_simulated_exception():
    pipeline = HybridSimplificationPipeline()
    
    # Intentionally force exception by mocking adapter failure
    class FailingAdapter:
        def generate(self, req):
            raise ConnectionError("Simulated API outage")
            
    pipeline.gemini_adapter = FailingAdapter()
    
    req = ModelGenerationRequest(
        request_id="REQ-FAIL-001",
        text="State the common name of the depicted animal.",
        support_level=SupportLevel.MODERATE,
        protected_elements=ProtectedElements(exact_preservation=["animal"])
    )
    
    res = pipeline.process(req, provider=ProviderType.GEMINI)
    
    # 1. Fallback is explicitly flagged
    assert res.fallback_used is True
    assert res.fallback_provider == "controlled_stage25"
    assert res.metrics_attributed_to == "controlled_stage25"
    
    # 2. Provider failure is not erased
    assert res.native_validation.disposition == "provider_unavailable"
    assert res.provider_outputs_received == 0
    assert res.candidate_text != ""
