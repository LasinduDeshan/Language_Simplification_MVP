"""
Stage 26 Generation Service.
Coordinates privacy sanitization, collision checking, model dispatch, hybrid validation,
and provider attribution. Enforces all mandatory Stage 26 governance invariants.
"""
from typing import Dict, Any, Optional, List
from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ModelGenerationResult,
    ProtectedElementsDTO,
    NativeValidationDisposition,
)
from app.model_simplification.router import ModelRouter
from app.model_simplification.provider_result_attribution import ProviderResultAttribution
from app.model_simplification.cost_tracker import CostTracker


class ModelSimplificationService:
    """
    High-level orchestrator for pretrained and LLM English simplification experiments.
    """

    MANDATORY_GOVERNANCE = {
        "validation_status": "draft",
        "research_eligible": False,
        "approved_for_child_delivery": False,
        "requires_expert_review": True,
    }

    def __init__(self, router: Optional[ModelRouter] = None):
        self.router = router or ModelRouter()

    def simplify(
        self,
        request: ModelGenerationRequest,
        model_id: str = "gemini-1.5-flash-prompted",
        protected_answers: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Executes generation, applies hybrid validation, attaches governance invariants,
        and classifies delivery outcome.
        """
        result = self.router.route_and_generate(
            request=request,
            model_id=model_id,
            protected_answers=protected_answers,
        )

        outcome_category, effective_provider = ProviderResultAttribution.classify_outcome(result)

        # Assemble governed response dictionary
        response = {
            "request_id": result.request_id,
            "requested_provider": result.requested_provider,
            "configured_model": result.configured_model,
            "resolved_model": result.resolved_model,
            "model_resolution_status": result.model_resolution_status,
            "execution_status": result.execution_status.value,
            "provider_calls_attempted": result.provider_calls_attempted,
            "candidate_text": result.candidate_text,
            "native_validation": result.native_validation.model_dump() if result.native_validation else None,
            "latency_ms": result.latency_ms,
            "input_token_count": result.input_token_count,
            "output_token_count": result.output_token_count,
            "estimated_cost": result.estimated_cost,
            "fallback_used": result.fallback_used,
            "fallback_provider": result.fallback_provider,
            "generator_method": result.generator_method,
            "accounting_outcome": outcome_category,
            "effective_delivery_provider": effective_provider,
            "governance": dict(self.MANDATORY_GOVERNANCE),
        }

        return response
