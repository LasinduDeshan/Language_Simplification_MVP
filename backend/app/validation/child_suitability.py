import re
from typing import Dict, Any, List, Optional

class ChildSuitabilityChecker:
    """
    Validates child-suitability, developmental safety, and length constraints for task instructions.
    Enforces:
    - Zero punitive/harsh vocabulary
    - Strict isolation of clinical/diagnostic jargon
    - Developmental sentence length constraints (<= 8-10 words target, <= 12 words maximum)
    - Syntactic complexity limits
    """

    PROHIBITED_PUNITIVE_TERMS = [
        "wrong", "incorrect", "bad", "failed", "fail", "mistake", "error",
        "you failed", "try harder", "you did not listen", "not right", "poor",
        "unacceptable", "stupid", "silly", "shame", "foolish"
    ]

    PROHIBITED_CLINICAL_TERMS = [
        "dld", "disorder", "impairment", "risk score", "percentile", "deficit",
        "pathology", "receptive", "expressive language", "developmental delay",
        "diagnosis", "clinical", "at-risk", "moderate risk", "high risk",
        "special needs", "therapy", "intervention"
    ]

    COMPLEX_CONJUNCTIONS = ["and", "but", "because", "although", "before", "after", "while", "since"]

    def _split_sentences(self, text: str) -> List[str]:
        """Splits instruction text into individual clauses/sentences."""
        if not text:
            return []
        # Split on terminal punctuation or linebreaks
        parts = re.split(r"[.!?\n]+", text)
        return [p.strip() for p in parts if p.strip()]

    def check_suitability(
        self,
        instruction: str,
        supportive_message: Optional[str] = None,
        target_age: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Validates safety, tone, and length of instruction.
        Returns:
            child_suitable: bool
            safety_valid: bool
            sentence_length_valid: bool
            average_words_per_sentence: float
            maximum_words_in_sentence: int
            violations: List[str]
            warnings: List[str]
        """
        violations: List[str] = []
        warnings: List[str] = []

        combined_text = (instruction + " " + (supportive_message or "")).lower()

        # 1. Check Punitive Terms
        for term in self.PROHIBITED_PUNITIVE_TERMS:
            # Word boundary search
            pattern = rf"\b{re.escape(term)}\b"
            if re.search(pattern, combined_text):
                violations.append(f"prohibited_punitive_term: '{term}'")

        # 2. Check Clinical / Diagnostic Terminology
        for term in self.PROHIBITED_CLINICAL_TERMS:
            pattern = rf"\b{re.escape(term)}\b"
            if re.search(pattern, combined_text):
                violations.append(f"clinical_terminology_leakage: '{term}'")

        # 3. Sentence Length & Complexity
        sentences = self._split_sentences(instruction)
        word_counts = [len(s.split()) for s in sentences] if sentences else [0]

        max_words = max(word_counts) if word_counts else 0
        avg_words = sum(word_counts) / len(word_counts) if word_counts else 0.0

        # Hard limit: maximum 12 words per sentence
        sentence_length_valid = True
        if max_words > 12:
            sentence_length_valid = False
            violations.append(f"sentence_length_exceeded: maximum sentence has {max_words} words (limit is 12)")
        elif max_words > 10:
            warnings.append(f"sentence_length_target_warning: sentence has {max_words} words (target is <= 10)")

        # Syntactic complexity: count conjunctions in individual sentences
        for s in sentences:
            tokens = [t.lower() for t in re.findall(r"\b\w+\b", s)]
            conj_count = sum(1 for t in tokens if t in self.COMPLEX_CONJUNCTIONS)
            if conj_count >= 3:
                warnings.append(f"high_syntactic_complexity: sentence contains {conj_count} clausal conjunctions")

        # 4. Supportive Message Tone
        if supportive_message:
            supp_lower = supportive_message.lower()
            for term in self.PROHIBITED_PUNITIVE_TERMS:
                if re.search(rf"\b{re.escape(term)}\b", supp_lower):
                    violations.append(f"supportive_message_punitive_term: '{term}'")

        safety_valid = len([v for v in violations if "prohibited" in v or "clinical" in v]) == 0
        child_suitable = safety_valid and sentence_length_valid

        return {
            "child_suitable": child_suitable,
            "safety_valid": safety_valid,
            "sentence_length_valid": sentence_length_valid,
            "average_words_per_sentence": round(avg_words, 2),
            "maximum_words_in_sentence": max_words,
            "violations": violations,
            "warnings": warnings
        }

child_suitability_checker = ChildSuitabilityChecker()
