"""
B2: Sentence Splitting Baseline.
Splits compound sentences at safe coordinating and subordinate conjunctions while preserving discourse order and rejecting fragments.
"""
import re
from typing import Any, Dict, List, Optional, Tuple
import spacy
from app.baseline_simplification.schemas import BaselineMethodId
from app.baseline_simplification.output_validator import OutputValidator

class SentenceSplitBaseline:
    """Splits compound sentences at coordinating or subordinate boundaries with strict fragment checking."""

    def __init__(self, nlp: Optional[Any] = None):
        self.method_id = BaselineMethodId.B2
        self.method_version = "1.0.0"
        
        if nlp is not None:
            self.nlp = nlp
        else:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.nlp = spacy.blank("en")
        
        self.validator = OutputValidator(nlp=self.nlp)
        self.coord_conjs = {"and", "but", "so"}
        self.subord_conjs = {"because", "when", "after", "while"}

    def _split_sentence(self, sent_text: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Attempts to split a single compound sentence into two valid sentences."""
        doc = self.nlp(sent_text)
        
        # Look for splitting opportunities at coordinating conjunctions or subordinate clauses
        for i, token in enumerate(doc):
            tok_lower = token.text.lower()
            
            # Case 1: Coordinating conjunction (e.g. ", and", " and ")
            if tok_lower in self.coord_conjs and token.pos_ in {"CCONJ", "SCONJ"} and 3 <= i < len(doc) - 3:
                left_tokens = [t.text_with_ws for t in doc[:i]]
                right_tokens = [t.text_with_ws for t in doc[i+1:]]
                
                left_str = "".join(left_tokens).strip().rstrip(",;").strip()
                right_str = "".join(right_tokens).strip()
                
                # Format sentences
                if not left_str.endswith((".", "!", "?")):
                    left_str += "."
                right_str = right_str[0].upper() + right_str[1:] if right_str else ""
                if not right_str.endswith((".", "!", "?")):
                    right_str += "."

                # Validate both clauses
                valid_l, _ = self.validator.validate_sentence(left_str)
                valid_r, _ = self.validator.validate_sentence(right_str)
                
                if valid_l and valid_r:
                    return f"{left_str} {right_str}", {
                        "rule_id": "SPLIT-01-COORD-CONJ",
                        "conjunction": tok_lower,
                        "clause1": left_str,
                        "clause2": right_str,
                    }

            # Case 2: Subordinate conjunction (e.g. ", because", " because ")
            if tok_lower in self.subord_conjs and token.pos_ in {"SCONJ", "ADV"} and 3 <= i < len(doc) - 3:
                left_tokens = [t.text_with_ws for t in doc[:i]]
                right_tokens = [t.text_with_ws for t in doc[i+1:]]
                
                left_str = "".join(left_tokens).strip().rstrip(",;").strip()
                right_str = "".join(right_tokens).strip()
                
                if not left_str.endswith((".", "!", "?")):
                    left_str += "."
                right_str = right_str[0].upper() + right_str[1:] if right_str else ""
                if not right_str.endswith((".", "!", "?")):
                    right_str += "."

                valid_l, _ = self.validator.validate_sentence(left_str)
                valid_r, _ = self.validator.validate_sentence(right_str)
                
                if valid_l and valid_r:
                    return f"{left_str} {right_str}", {
                        "rule_id": "SPLIT-02-SUBORD-CLAUSE",
                        "conjunction": tok_lower,
                        "clause1": left_str,
                        "clause2": right_str,
                    }

        return None, None

    def simplify(self, text: str, **kwargs: Any) -> Dict[str, Any]:
        """Performs sentence splitting across all candidate sentences in the input."""
        cleaned = text.strip()
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]
        if not sentences:
            sentences = [cleaned]

        output_sentences: List[str] = []
        rules_applied: List[Dict[str, Any]] = []
        operation_outcomes: List[Dict[str, Any]] = []

        for sent in sentences:
            split_res, split_details = self._split_sentence(sent)
            if split_res and split_details:
                output_sentences.append(split_res)
                rules_applied.append({
                    "rule_id": split_details["rule_id"],
                    "step": len(rules_applied) + 1,
                    "details": split_details,
                })
                operation_outcomes.append({
                    "rule_id": split_details["rule_id"],
                    "outcome": "applied",
                })
            else:
                output_sentences.append(sent)

        result_text = " ".join(output_sentences).strip()
        return {
            "output_text": result_text,
            "rules_applied": rules_applied,
            "operation_outcomes": operation_outcomes,
            "fallback_used": False,
        }
