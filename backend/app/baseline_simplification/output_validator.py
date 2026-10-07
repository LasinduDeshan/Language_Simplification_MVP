"""
Output structural and grammar validator for baseline simplifications.
"""
import re
from typing import Any, List, Optional, Tuple
import spacy

class OutputValidator:
    """Validates structural soundness, fragment prevention, and grammar formatting."""

    def __init__(self, nlp: Optional[Any] = None):
        if nlp is not None:
            self.nlp = nlp
        else:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.nlp = spacy.blank("en")

    def is_valid_imperative(self, doc: Any) -> bool:
        """Checks if a clause/sentence is a valid short imperative command (e.g. 'Sit down.', 'Look here.')."""
        if len(doc) == 0:
            return False
        # First word should be a base verb or particle
        first_token = doc[0]
        if first_token.pos_ in {"VERB", "AUX"} or first_token.tag_ in {"VB", "VBP"}:
            return True
        # Or starts with 'please' followed by verb
        if first_token.text.lower() == "please" and len(doc) > 1 and doc[1].pos_ in {"VERB", "AUX"}:
            return True
        return False

    def validate_sentence(self, sentence_text: str) -> Tuple[bool, List[str]]:
        """Validates an individual sentence for subject-verb completeness or valid imperative."""
        issues: List[str] = []
        cleaned = sentence_text.strip()
        if not cleaned:
            return False, ["Empty sentence"]

        # Minimum length
        words = re.findall(r"\b\w+\b", cleaned)
        if len(words) < 2:
            return False, [f"Sentence too short ({len(words)} tokens): '{cleaned}'"]

        doc = self.nlp(cleaned)
        
        # Check if imperative
        if self.is_valid_imperative(doc):
            return True, []

        # Check for presence of finite verb / predicate
        has_verb = any(token.pos_ in {"VERB", "AUX"} for token in doc)
        if not has_verb:
            issues.append(f"Missing verb/predicate in sentence: '{cleaned}'")

        # Check for subject or pronoun
        has_subj = any("subj" in token.dep_ or token.pos_ in {"PRON", "PROPN", "NOUN"} for token in doc)
        if not has_subj and not self.is_valid_imperative(doc):
            issues.append(f"Missing grammatical subject in non-imperative sentence: '{cleaned}'")

        return len(issues) == 0, issues

    def validate_text(self, text: str) -> Tuple[bool, List[str]]:
        """Validates overall text formatting, capitalization, and sentence structures."""
        issues: List[str] = []
        cleaned = text.strip()
        if not cleaned:
            return False, ["Output text is completely empty"]

        # Split into sentences
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]
        if not sentences:
            # If no terminal punctuation, treat entire text as single sentence
            sentences = [cleaned]

        for s in sentences:
            valid_s, s_issues = self.validate_sentence(s)
            if not valid_s:
                issues.extend(s_issues)

        # Check terminal punctuation on full text
        if cleaned and cleaned[-1] not in {".", "!", "?"}:
            issues.append("Missing terminal punctuation at end of output")

        return len(issues) == 0, issues
