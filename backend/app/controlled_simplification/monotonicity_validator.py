"""
Multidimensional support monotonicity validator.
Evaluates composite complexity metrics across Original, Mild, Moderate, and Strong tiers.
"""

import re
from typing import Dict, List, Tuple, Any
from app.controlled_simplification.schemas import SupportLevel
from app.controlled_simplification.spacy_manager import SpacyPipelineManager


class MonotonicityValidator:
    """
    Evaluates whether linguistic complexity decreases monotonically from Original -> Mild -> Moderate -> Strong.
    Uses a multidimensional composite suite rather than raw FKGL alone to avoid single-metric distortions.
    """

    def __init__(self):
        self.spacy_manager = SpacyPipelineManager()

    def compute_complexity_vector(self, text: str) -> Dict[str, float]:
        """
        Computes the composite complexity vector for a piece of text.
        """
        clean_text = text.strip()
        doc = self.spacy_manager.get_doc(clean_text)

        # 1. Words and sentences
        words = [t for t in doc if not t.is_punct and not t.is_space]
        word_count = max(1, len(words))
        sentences = list(doc.sents)
        sentence_count = max(1, len(sentences))

        # 2. Mean Clause Length (words / sentences)
        mcl = word_count / float(sentence_count)

        # 3. Difficult word ratio (words with >= 3 syllables or length > 6)
        difficult_words = [w for w in words if len(w.text) > 6]
        dwr = len(difficult_words) / float(word_count)

        # 4. Max dependency depth
        def get_depth(token):
            depth = 0
            curr = token
            while curr.head != curr:
                depth += 1
                curr = curr.head
            return depth

        max_dep_depth = max([get_depth(t) for t in doc], default=0)

        # 5. Composite complexity index
        # Normalized weighted index (lower is simpler)
        composite_index = (0.40 * mcl) + (0.35 * (dwr * 10)) + (0.25 * max_dep_depth)

        return {
            "word_count": float(word_count),
            "sentence_count": float(sentence_count),
            "mean_clause_length": round(mcl, 2),
            "difficult_word_ratio": round(dwr, 3),
            "max_dependency_depth": float(max_dep_depth),
            "composite_complexity_index": round(composite_index, 3)
        }

    def verify_tier_progression(
        self,
        orig_text: str,
        mild_text: str,
        mod_text: str,
        strong_text: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Verifies that composite complexity satisfies:
        Complexity(Strong) <= Complexity(Moderate) <= Complexity(Mild) <= Complexity(Original)
        """
        v_orig = self.compute_complexity_vector(orig_text)
        v_mild = self.compute_complexity_vector(mild_text)
        v_mod = self.compute_complexity_vector(mod_text)
        v_strong = self.compute_complexity_vector(strong_text)

        idx_orig = v_orig["composite_complexity_index"]
        idx_mild = v_mild["composite_complexity_index"]
        idx_mod = v_mod["composite_complexity_index"]
        idx_strong = v_strong["composite_complexity_index"]

        # Allow small epsilon tolerance for identical scores
        eps = 0.05
        mild_le_orig = idx_mild <= (idx_orig + eps)
        mod_le_mild = idx_mod <= (idx_mild + eps)
        strong_le_mod = idx_strong <= (idx_mod + eps)

        is_monotonic = mild_le_orig and mod_le_mild and strong_le_mod

        return is_monotonic, {
            "original_index": idx_orig,
            "mild_index": idx_mild,
            "moderate_index": idx_mod,
            "strong_index": idx_strong,
            "mild_le_orig": mild_le_orig,
            "mod_le_mild": mod_le_mild,
            "strong_le_mod": strong_le_mod,
            "is_monotonic": is_monotonic
        }
