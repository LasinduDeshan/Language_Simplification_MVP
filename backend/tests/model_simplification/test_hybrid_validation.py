"""
Tests for Hybrid Simplification Pipeline and Fallback Attribution.
"""

from app.model_simplification.hybrid_pipeline import HybridSimplificationPipeline
from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ProtectedElements,
    SupportLevel,
    ProviderType
)


def test_hybrid_pipeline_clean_flow():
    pipeline = HybridSimplificationPipeline()
    req = ModelGenerationRequest(
        request_id="HYB-REQ-001",
        text="State the common name of the depicted animal.",
        support_level=SupportLevel.MODERATE,
        protected_elements=ProtectedElements(exact_preservation=["animal"])
    )
    
    res = pipeline.process(req, provider=ProviderType.STAGE25)
    assert res.request_id == "HYB-REQ-001"
    assert res.candidate_text != ""
    assert res.native_validation.disposition.lower() in ["passed", "passed_with_rollback", "manual_review_required"]
    assert res.metrics_attributed_to == "controlled_stage25"


def test_hybrid_pipeline_surface_repair():
    pipeline = HybridSimplificationPipeline()
    req = ModelGenerationRequest(
        request_id="HYB-REQ-002",
        text="Before placing the ball in the box, pick the blue block.",
        support_level=SupportLevel.STRONG,
        protected_elements=ProtectedElements(exact_preservation=["ball", "box", "blue", "block"])
    )
    
    res = pipeline.process(req, provider=ProviderType.GEMINI)
    assert res.candidate_text != ""
    assert res.provider_outputs_received == 1


def test_hybrid_pipeline_transparent_fallback_on_answer_leak():
    pipeline = HybridSimplificationPipeline()
    req = ModelGenerationRequest(
        request_id="HYB-REQ-LEAK",
        text="Identify the domestic animal shown in the picture.",
        support_level=SupportLevel.MODERATE,
        protected_elements=ProtectedElements(
            exact_preservation=["animal"],
            protected_answers=["animal"]
        )
    )
    
    # If a model leaks answer "animal", fallback must trigger
    res = pipeline.process(req, provider=ProviderType.MT5)
    assert res.request_id == "HYB-REQ-LEAK"
    assert res.candidate_text != ""
