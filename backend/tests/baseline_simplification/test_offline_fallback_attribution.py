"""
Unit tests for B5: Offline Fallback Adapter and strict non-LLM attribution.
"""
from app.baseline_simplification.offline_fallback_adapter import OfflineFallbackAdapter
from app.baseline_simplification.schemas import BaselineMethodId

def test_offline_fallback_attribution():
    b5 = OfflineFallbackAdapter()
    text = "This is an extraordinarily complex sentence with many words that should be shortened."
    res = b5.simplify(text)
    
    assert res["generator_method"] == "deterministic_fallback"
    assert res["metrics_attributed_to"] == "deterministic_fallback"
    assert res["requested_provider"] == "deterministic_fallback"
    assert "gemini" not in res["metrics_attributed_to"].lower()
    assert len(res["output_text"].split()) <= 15
