"""Tests for LLM advisory boundaries, privacy guards, and offline fallbacks."""
import asyncio
from app.datasets.quality.llm_review.disabled_adapter import DisabledLLMReviewAdapter
from app.datasets.quality.llm_review.gemini_adapter import GeminiLLMReviewAdapter


def test_disabled_adapter_returns_none():
    adapter = DisabledLLMReviewAdapter()
    res = asyncio.run(adapter.evaluate_pair("Complex text", "Simple text"))
    assert res is None


def test_interaction_export_blocked_from_llm():
    """Interaction export layer must be blocked from LLM transmission."""
    adapter = GeminiLLMReviewAdapter(api_key="mock_key")
    res = asyncio.run(adapter.evaluate_pair(
        original_text="Private text",
        simplified_text="Private simple",
        context={"dataset_layer": "interaction_exports"}
    ))
    assert res is None
