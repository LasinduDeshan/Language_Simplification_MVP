"""Simplification baselines for benchmark evaluation on external datasets."""

import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple


class IdentitySimplifier:
    """Baseline 0: Identity baseline (copies source sentence directly)."""

    NAME = "identity_baseline"

    def simplify(self, text: str) -> Tuple[str, Dict[str, Any]]:
        start = time.perf_counter()
        latency_ms = (time.perf_counter() - start) * 1000.0
        return text, {
            "method": self.NAME,
            "latency_ms": latency_ms,
            "is_fallback": False,
            "is_valid": bool(text.strip()),
        }


class RuleBasedSimplifier:
    """Baseline 1: Deterministic rule-based simplifier applying lexical substitutions and syntactic shortening."""

    NAME = "rule_based_simplifier"

    # Core lexical substitution dictionary
    LEXICAL_MAP = {
        r"\bcommence\b": "start",
        r"\bcommenced\b": "started",
        r"\butilize\b": "use",
        r"\butilized\b": "used",
        r"\bapproximately\b": "about",
        r"\bsubsequently\b": "then",
        r"\binitiate\b": "start",
        r"\bterminated\b": "ended",
        r"\bdemonstrate\b": "show",
        r"\bdemonstrated\b": "showed",
        r"\bpurchase\b": "buy",
        r"\bpurchased\b": "bought",
        r"\bconstruct\b": "build",
        r"\bconstructed\b": "built",
        r"\bnumerous\b": "many",
        r"\bfacilitate\b": "help",
        r"\bassistance\b": "help",
        r"\bcomprehend\b": "understand",
        r"\bdiminish\b": "lessen",
        r"\beliminate\b": "remove",
        r"\bessential\b": "needed",
        r"\bindicate\b": "show",
        r"\bindicated\b": "showed",
        r"\bpredominantly\b": "mostly",
        r"\breside\b": "live",
        r"\bresided\b": "lived",
        r"\btransportation\b": "travel",
        r"\bvicinity\b": "area",
    }

    def simplify(self, text: str) -> Tuple[str, Dict[str, Any]]:
        start = time.perf_counter()
        adapted = text
        changes_applied = 0

        # 1. Apply lexical replacements
        for pattern, repl in self.LEXICAL_MAP.items():
            if re.search(pattern, adapted, re.IGNORECASE):
                adapted = re.sub(pattern, repl, adapted, flags=re.IGNORECASE)
                changes_applied += 1

        # 2. Syntactic / parenthetical clause reduction
        # Remove parenthetical clauses like (born 1950) or (which is located in ...)
        if "(" in adapted and ")" in adapted:
            adapted = re.sub(r"\s*\([^)]*\)", "", adapted)
            changes_applied += 1

        # 3. Clean up whitespace and punctuation
        adapted = " ".join(adapted.split())
        if adapted and not adapted.endswith((".", "!", "?")):
            adapted += "."

        latency_ms = (time.perf_counter() - start) * 1000.0
        return adapted, {
            "method": self.NAME,
            "latency_ms": latency_ms,
            "changes_applied": changes_applied,
            "is_fallback": False,
            "is_valid": bool(adapted.strip()),
        }


class GenericLLMSimplifier:
    """Baseline 2: Generic LLM / Gemini zero-shot baseline."""

    NAME = "llm_generic_baseline"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.is_live = bool(self.api_key)

    def simplify(self, text: str) -> Tuple[str, Dict[str, Any]]:
        start = time.perf_counter()
        
        # If API key is not set, use offline deterministic child-simplification proxy
        if not self.is_live:
            # Deterministic zero-shot simulation
            words = text.split()
            simplified = " ".join(words[: min(len(words), 14)])
            if not simplified.endswith((".", "!", "?")):
                simplified += "."
            latency_ms = (time.perf_counter() - start) * 1000.0
            return simplified, {
                "method": self.NAME,
                "latency_ms": latency_ms,
                "is_fallback": True,
                "is_valid": True,
                "note": "offline_deterministic_proxy_no_api_key",
            }

        # If live API key available, execute real query
        try:
            # Real LLM call
            from app.generation.llm_generator import GeminiGenerator
            gen = GeminiGenerator()
            res = gen.simplify_text(text)
            latency_ms = (time.perf_counter() - start) * 1000.0
            return res, {
                "method": self.NAME,
                "latency_ms": latency_ms,
                "is_fallback": False,
                "is_valid": bool(res.strip()),
            }
        except Exception as e:
            words = text.split()
            simplified = " ".join(words[: min(len(words), 14)]) + "."
            latency_ms = (time.perf_counter() - start) * 1000.0
            return simplified, {
                "method": self.NAME,
                "latency_ms": latency_ms,
                "is_fallback": True,
                "is_valid": True,
                "error": str(e),
            }
