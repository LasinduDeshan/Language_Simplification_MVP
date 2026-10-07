"""
Stage 26 Cost and Token Tracker.
Calculates token counts and estimates API costs based on published Gemini pricing schedules.
"""
from typing import Dict, Any, Tuple


class CostTracker:
    """
    Estimates token counts and costs for LLM generations.
    """

    # Published Gemini 1.5 Flash Pricing (Per 1 Million Tokens)
    # Source: Google AI Studio Pricing (Retrieved 2026-10-01)
    PRICING_PER_MILLION = {
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
        "default": {"input": 0.075, "output": 0.30},
    }

    @classmethod
    def estimate_tokens(cls, text: str) -> int:
        """
        Estimates token count (approximately 1 token per 4 characters for English).
        """
        if not text:
            return 0
        return max(1, len(text) // 4 + 1)

    @classmethod
    def calculate_cost(cls, model_id: str, input_tokens: int, output_tokens: int) -> float:
        """
        Calculates estimated USD cost for input/output tokens.
        """
        rates = cls.PRICING_PER_MILLION.get(model_id, cls.PRICING_PER_MILLION["default"])
        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]
        return round(input_cost + output_cost, 8)
