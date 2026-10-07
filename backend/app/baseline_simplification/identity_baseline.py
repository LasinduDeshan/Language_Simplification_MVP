"""
B0: Identity Baseline implementation.
Returns canonical input unchanged as the zero-simplification lower-bound benchmark.
"""
from typing import Any, Dict, List, Optional
from app.baseline_simplification.schemas import BaselineMethodId

class IdentityBaseline:
    """Returns the input text unchanged."""
    
    def __init__(self):
        self.method_id = BaselineMethodId.B0
        self.method_version = "1.0.0"

    def simplify(self, text: str, **kwargs: Any) -> Dict[str, Any]:
        cleaned = text.strip()
        return {
            "output_text": cleaned,
            "rules_applied": [],
            "operation_outcomes": [],
            "fallback_used": False,
        }
