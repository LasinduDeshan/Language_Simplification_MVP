"""Default offline disabled LLM review adapter."""
from typing import Dict, Any, Optional
from app.datasets.quality.schemas import LLMReviewResponseV1
from app.datasets.quality.llm_review.interface import AbstractLLMReviewAdapter


class DisabledLLMReviewAdapter(AbstractLLMReviewAdapter):
    """Default adapter performing zero network requests, always returning None."""

    async def evaluate_pair(self, original_text: str, simplified_text: str, context: Optional[Dict[str, Any]] = None) -> Optional[LLMReviewResponseV1]:
        return None
