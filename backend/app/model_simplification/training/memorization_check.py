"""
Stage 26 Memorization & Overfitting Check.
Compares model outputs against exact training targets to compute exact memorization rate.
"""
from typing import List, Dict, Any, Tuple


class MemorizationChecker:
    """
    Audits generated outputs against training set targets to measure verbatim memorization.
    """

    @classmethod
    def check_memorization(
        cls,
        eval_samples: List[Dict[str, Any]],
        training_targets: List[str],
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calculates percentage of eval candidate outputs that match any training target verbatim.
        Returns (memorization_rate, matched_instances).
        """
        norm_targets = {t.strip().lower() for t in training_targets if t}
        matches = []

        for item in eval_samples:
            cand = item.get("candidate_text", "").strip().lower()
            if cand in norm_targets:
                matches.append(item)

        total = max(1, len(eval_samples))
        rate = len(matches) / total
        return round(rate, 4), matches
