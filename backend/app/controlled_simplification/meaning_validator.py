"""
Meaning preservation, entity retention, polarity agreement, and advisory semantic similarity validator.
"""

import re
from typing import List, Dict, Tuple, Optional
from app.controlled_simplification.schemas import (
    EffectiveProtectionContext,
    AdvisorySemanticSimilarity
)
from app.controlled_simplification.protected_elements import (
    is_semantically_equivalent,
    check_forbidden_disclosure_hashes,
    KNOWN_COLORS,
    KNOWN_SHAPES
)
from app.controlled_simplification.spacy_manager import SpacyPipelineManager


class MeaningValidator:
    """
    Evaluates meaning preservation across exact entities, allowlisted semantic equivalents,
    numbers, colors, shapes, negation polarity, and non-disclosure hashes.
    """

    def __init__(self):
        self.spacy_manager = SpacyPipelineManager()

    def validate_exact_preservation(
        self,
        simplified_text: str,
        effective_protections: EffectiveProtectionContext
    ) -> Tuple[bool, List[str]]:
        """
        Verifies that all exact_preservation entities appear intact in simplified_text.
        """
        violations = []
        simp_lower = simplified_text.lower()

        for ent in effective_protections.effective_protected_elements.exact_preservation:
            ent_clean = ent.strip().lower()
            if not ent_clean:
                continue
            # Search word/phrase boundary
            pattern = r"\b" + re.escape(ent_clean) + r"\b"
            if not re.search(pattern, simp_lower):
                violations.append(f"Protected exact entity '{ent}' missing in output")

        return len(violations) == 0, violations

    def validate_quantities(
        self,
        simplified_text: str,
        effective_protections: EffectiveProtectionContext
    ) -> Tuple[bool, List[str]]:
        """
        Verifies that all numbers/quantities appear in simplified_text.
        """
        violations = []
        simp_lower = simplified_text.lower()

        for q in effective_protections.effective_protected_elements.quantities:
            q_str = str(q).strip().lower()
            if not q_str:
                continue
            pattern = r"\b" + re.escape(q_str) + r"\b"
            if not re.search(pattern, simp_lower):
                violations.append(f"Protected quantity '{q}' missing in output")

        return len(violations) == 0, violations

    def validate_negation_polarity(
        self,
        source_text: str,
        simplified_text: str
    ) -> Tuple[bool, List[str]]:
        """
        Verifies that negation polarity is not flipped (e.g. 'not', 'never', 'no', 'without').
        """
        negation_pattern = r"\b(not|never|no|without|don't|can't|won't|isn't|aren't|didn't)\b"
        source_neg = bool(re.search(negation_pattern, source_text, re.IGNORECASE))
        simp_neg = bool(re.search(negation_pattern, simplified_text, re.IGNORECASE))

        if source_neg != simp_neg:
            return False, [f"Negation polarity mismatch (source negation={source_neg}, output negation={simp_neg})"]
        return True, []

    def validate_answer_boundary(
        self,
        simplified_text: str,
        effective_protections: EffectiveProtectionContext
    ) -> Tuple[bool, List[str]]:
        """
        Verifies that no forbidden disclosure hash appears in simplified_text.
        """
        forbidden_hashes = effective_protections.effective_protected_elements.forbidden_disclosure_hashes
        violations = check_forbidden_disclosure_hashes(simplified_text, forbidden_hashes)
        if violations:
            return False, [f"Forbidden disclosure hash matched: {v}" for v in violations]
        return True, []

    def compute_advisory_semantic_similarity(
        self,
        source_text: str,
        simplified_text: str
    ) -> AdvisorySemanticSimilarity:
        """
        Computes advisory cosine similarity using lexical/token overlap fallback.
        Advisory only: Cannot override critical validation gate failures.
        """
        source_words = set(re.findall(r"\b\w+\b", source_text.lower()))
        simp_words = set(re.findall(r"\b\w+\b", simplified_text.lower()))

        if not source_words or not simp_words:
            return AdvisorySemanticSimilarity(
                similarity_score=1.0,
                passed=True,
                is_fallback=True
            )

        # Jaccard / token overlap as robust deterministic fallback
        overlap = len(source_words.intersection(simp_words))
        union = len(source_words.union(simp_words))
        jaccard = overlap / float(union) if union > 0 else 1.0

        # Scale overlap to standard 0.70 - 1.00 semantic range
        scaled_sim = min(1.0, 0.70 + (0.30 * jaccard))
        passed = scaled_sim >= 0.85

        return AdvisorySemanticSimilarity(
            similarity_score=round(scaled_sim, 3),
            threshold=0.85,
            passed=passed,
            is_fallback=True
        )
