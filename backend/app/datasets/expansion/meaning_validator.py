"""
Stage 20 Meaning Preservation and Multidimensional Monotonicity Validator
Verifies that protected meaning units are intact and validates support progression.
"""
import re
from typing import Dict, Any, List

class MeaningValidator:
    def __init__(self):
        self.negation_words = {"not", "don't", "dont", "no", "never", "cannot", "can't", "cant", "without", "except"}

    def validate_meaning_units(self, original_text: str, simplified_text: str, protected_units: List[str]) -> Dict[str, Any]:
        orig_lower = original_text.lower()
        simp_lower = simplified_text.lower()
        
        missing_units = []
        for unit in protected_units:
            unit_norm = unit.lower().strip()
            # If unit is multiple words, check exact phrase or all words
            if unit_norm not in simp_lower:
                unit_words = unit_norm.split()
                if not all(w in simp_lower for w in unit_words):
                    missing_units.append(unit)

        # Check negation preservation
        orig_has_neg = any(re.search(r"\b" + re.escape(nw) + r"\b", orig_lower) for nw in self.negation_words)
        simp_has_neg = any(re.search(r"\b" + re.escape(nw) + r"\b", simp_lower) for nw in self.negation_words)
        
        negation_mismatch = (orig_has_neg != simp_has_neg)

        is_preserved = (len(missing_units) == 0 and not negation_mismatch)

        return {
            "is_preserved": is_preserved,
            "missing_meaning_units": missing_units,
            "negation_mismatch": negation_mismatch,
            "status": "passed" if is_preserved else "manual_review_required"
        }

    def validate_support_trio(self, source_text: str, mild_text: str, moderate_text: str, strong_text: str) -> Dict[str, Any]:
        """
        Evaluates multidimensional monotonicity across a complete Mild, Moderate, Strong trio.
        """
        # 1. Lexical estimation (avg word length & syllable approximation)
        def avg_word_len(text: str) -> float:
            words = re.findall(r"\b\w+\b", text)
            return sum(len(w) for w in words) / max(1, len(words))

        w_orig = avg_word_len(source_text)
        w_mild = avg_word_len(mild_text)
        w_mod = avg_word_len(moderate_text)
        w_strong = avg_word_len(strong_text)

        # 2. Step clarity check (strong should have steps/numbering or short direct commands)
        strong_has_steps = any(marker in strong_text.lower() for marker in ["1.", "first", "step", "then", "\n"])

        lexical_monotonic = (w_strong <= w_mod + 0.5) and (w_mod <= w_mild + 0.5)

        issues = []
        if not lexical_monotonic:
            issues.append("Lexical difficulty inversion: Strong tier contains higher average syllable/word complexity than Moderate/Mild")

        return {
            "lexical_monotonic": lexical_monotonic,
            "strong_step_clarity": strong_has_steps,
            "issues": issues,
            "status": "passed" if (lexical_monotonic and len(issues) == 0) else "manual_review_required"
        }
