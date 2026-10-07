"""Interface definition for advisory LLM quality review adapters."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.datasets.quality.schemas import LLMReviewResponseV1


class AbstractLLMReviewAdapter(ABC):
    """Abstract adapter providing optional advisory evaluations on dataset text pairs."""

    @abstractmethod
    async def evaluate_pair(self, original_text: str, simplified_text: str, context: Optional[Dict[str, Any]] = None) -> Optional[LLMReviewResponseV1]:
        """
        Evaluates an original-simplified pair.
        Returns LLMReviewResponseV1 or None if review is disabled / unavailable.
        """
        raise NotImplementedError
