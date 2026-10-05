"""
Stage 26: Common Model Adapter Protocol.
"""

from typing import Protocol
from .schemas import ModelGenerationRequest, ModelGenerationResult


class SimplificationModelAdapter(Protocol):
    """
    Common provider-neutral interface for pretrained and LLM simplification models.
    """
    def generate(self, request: ModelGenerationRequest) -> ModelGenerationResult:
        """
        Executes controlled simplification for the given request.
        """
        ...
