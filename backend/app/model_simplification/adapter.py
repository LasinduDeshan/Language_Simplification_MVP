"""
Stage 26 Common Model Adapter Protocol.
"""
from typing import Protocol, runtime_checkable
from app.model_simplification.schemas import ModelGenerationRequest, ModelGenerationResult


@runtime_checkable
class SimplificationModelAdapter(Protocol):
    """
    Common provider-neutral protocol implemented by all simplification adapters:
    Gemini, mT5, mBART, and Stage 25 deterministic fallback.
    """

    def generate(self, request: ModelGenerationRequest) -> ModelGenerationResult:
        """
        Executes generation for the given request and returns standardized ModelGenerationResult.
        """
        ...
