"""
B5: Existing Offline Heuristic Fallback Adapter.
Wraps the Stage 23 deterministic offline fallback comparator with strict non-LLM attribution.
"""
from typing import Any, Dict, List, Optional
import time
from app.baseline_simplification.schemas import BaselineMethodId

class OfflineFallbackAdapter:
    """Deterministic offline fallback baseline adapter."""

    def __init__(self):
        self.method_id = BaselineMethodId.B5
        self.method_version = "1.0.0"
        self.generator_method = "deterministic_fallback"

    def simplify(self, text: str, **kwargs: Any) -> Dict[str, Any]:
        start = time.perf_counter()
        words = text.strip().split()
        simplified = " ".join(words[: min(len(words), 14)])
        if not simplified.endswith((".", "!", "?")):
            simplified += "."
        latency_ms = (time.perf_counter() - start) * 1000.0

        return {
            "output_text": simplified,
            "rules_applied": [{"rule_id": "FB-01-RULE-HEURISTIC-EXTRACT", "step": 1}],
            "operation_outcomes": [{"rule_id": "FB-01-RULE-HEURISTIC-EXTRACT", "outcome": "applied"}],
            "fallback_used": True,
            "latency_ms": latency_ms,
            "generator_method": self.generator_method,
            "requested_provider": "deterministic_fallback",
            "metrics_attributed_to": "deterministic_fallback",
        }
