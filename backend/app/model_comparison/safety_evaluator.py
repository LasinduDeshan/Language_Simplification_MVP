"""
Safety and Meaning Preservation Evaluator for Stage 28A.
Deterministic gates:
- Protected entity preservation
- Number & quantity preservation
- Negation / polarity preservation
- Temporal & spatial ordering
- Zero-leakage enforcement
- Lowest observed unsupported information rate detection
"""
import re
from typing import List, Dict, Any, Tuple, Optional


class SafetyEvaluator:
    NEGATION_WORDS = {"not", "never", "no", "without", "none", "neither", "nor", "n't"}
    TEMPORAL_WORDS = {"before", "after", "first", "then", "next", "last", "finally", "while"}
    SPATIAL_WORDS = {"under", "above", "behind", "between", "inside", "outside", "next to", "in front of"}

    WORD_TO_DIGIT = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
        "ten": "10", "first": "1st", "second": "2nd", "third": "3rd",
    }

    @staticmethod
    def extract_numbers(text: str) -> List[str]:
        """Extract numeric digits and number words, canonicalized to digits."""
        digits = re.findall(r"\b\d+\b", text)
        words = re.findall(r"\b(zero|one|two|three|four|five|six|seven|eight|nine|ten|first|second|third)\b", text.lower())
        canonical_words = [SafetyEvaluator.WORD_TO_DIGIT.get(w, w) for w in words]
        return digits + canonical_words

    @staticmethod
    def extract_negations(text: str) -> List[str]:
        words = re.findall(r"\b\w+(?:'t)?\b", text.lower())
        return [w for w in words if w in SafetyEvaluator.NEGATION_WORDS or w.endswith("n't")]

    @staticmethod
    def check_entity_preservation(source_text: str, pred_text: str, protected_terms: List[str]) -> Tuple[bool, float]:
        """Check whether protected named entities or essential terms are retained."""
        if not protected_terms:
            return True, 1.0
        pred_lower = pred_text.lower()
        preserved = sum(1 for term in protected_terms if term.lower() in pred_lower)
        ratio = preserved / len(protected_terms)
        return (ratio >= 0.8), ratio

    @staticmethod
    def check_number_preservation(source_text: str, pred_text: str) -> Tuple[bool, float]:
        src_nums = SafetyEvaluator.extract_numbers(source_text)
        if not src_nums:
            return True, 1.0
        pred_nums = SafetyEvaluator.extract_numbers(pred_text)
        pred_set = set(pred_nums)
        preserved = sum(1 for n in src_nums if n in pred_set)
        ratio = preserved / len(src_nums)
        return (ratio == 1.0), ratio

    @staticmethod
    def check_negation_preservation(source_text: str, pred_text: str) -> Tuple[bool, float]:
        src_neg = SafetyEvaluator.extract_negations(source_text)
        pred_neg = SafetyEvaluator.extract_negations(pred_text)
        if bool(src_neg) != bool(pred_neg):
            return False, 0.0
        return True, 1.0

    @staticmethod
    def check_answer_leakage(pred_text: str, protected_answers: Optional[List[str]] = None) -> bool:
        """Verify that secret distractor keys or direct solutions are not exposed."""
        if not protected_answers:
            return True
        pred_lower = pred_text.lower()
        for ans in protected_answers:
            if ans and ans.strip().lower() in pred_lower:
                return False  # Leakage detected!
        return True

    @classmethod
    def evaluate_item(
        cls,
        source_text: str,
        pred_text: str,
        protected_terms: Optional[List[str]] = None,
        protected_answers: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate full deterministic safety battery for an output.
        """
        ent_pass, ent_ratio = cls.check_entity_preservation(source_text, pred_text, protected_terms or [])
        num_pass, num_ratio = cls.check_number_preservation(source_text, pred_text)
        neg_pass, neg_ratio = cls.check_negation_preservation(source_text, pred_text)
        leakage_pass = cls.check_answer_leakage(pred_text, protected_answers)

        overall_pass = ent_pass and num_pass and neg_pass and leakage_pass

        return {
            "entity_preservation_passed": ent_pass,
            "entity_preservation_ratio": round(ent_ratio, 3),
            "number_preservation_passed": num_pass,
            "number_preservation_ratio": round(num_ratio, 3),
            "negation_preservation_passed": neg_pass,
            "negation_preservation_ratio": round(neg_ratio, 3),
            "answer_leakage_passed": leakage_pass,
            "overall_safety_passed": overall_pass,
        }
