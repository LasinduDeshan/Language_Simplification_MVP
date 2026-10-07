"""
Protected meaning and child-safety validator supporting Dual-Mode evaluation (Internal vs ASSET).
"""
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import spacy
from app.baseline_simplification.schemas import (
    MeaningValidationStatus,
    FinalDisposition,
    ProtectedElementSource,
)

COMMON_COLORS = {
    "red", "blue", "green", "yellow", "black", "white",
    "orange", "purple", "pink", "brown", "gray", "grey"
}

NEGATION_TOKENS = {
    "not", "never", "no", "none", "without", "neither", "nor", "cannot", "n't"
}

NUMBER_WORDS = {
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "first", "second", "third"
}

class ProtectedMeaningValidator:
    """Validates that protected semantic elements (entities, numbers, colors, negation) are preserved."""

    def __init__(self, nlp: Optional[Any] = None):
        if nlp is not None:
            self.nlp = nlp
        else:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.nlp = spacy.blank("en")

    def extract_elements(self, text: str) -> Dict[str, Set[str]]:
        """Extracts entities, quantities, colors, and negation tokens using regex and spaCy."""
        text_lower = text.lower()
        doc = self.nlp(text)
        
        # 1. Entities
        entities = set()
        for ent in doc.ents:
            if ent.label_ in {"PERSON", "ORG", "GPE", "LOC", "DATE", "TIME"}:
                entities.add(ent.text.strip().lower())
        for token in doc:
            if token.pos_ == "PROPN":
                entities.add(token.text.strip().lower())

        # 2. Quantities / Numbers
        quantities = set(re.findall(r"\b\d+(?:\.\d+)?\b", text_lower))
        for word in NUMBER_WORDS:
            if re.search(rf"\b{re.escape(word)}\b", text_lower):
                quantities.add(word)

        # 3. Colors
        colors = set()
        for color in COMMON_COLORS:
            if re.search(rf"\b{re.escape(color)}\b", text_lower):
                colors.add(color)

        # 4. Negation tokens
        negations = set()
        for neg in NEGATION_TOKENS:
            if re.search(rf"\b{re.escape(neg)}\b", text_lower):
                negations.add(neg)

        return {
            "entities": entities,
            "quantities": quantities,
            "colors": colors,
            "negations": negations,
        }

    def validate(
        self,
        orig_text: str,
        simp_text: str,
        mode: ProtectedElementSource = ProtectedElementSource.AUTOMATED_EXTRACTOR_ONLY,
        governed_annotations: Optional[Dict[str, Any]] = None,
    ) -> Tuple[MeaningValidationStatus, FinalDisposition, List[str]]:
        """Validates simplification against original and returns (status, disposition, violations)."""
        violations: List[str] = []
        orig_elems = self.extract_elements(orig_text)
        simp_elems = self.extract_elements(simp_text)

        # If Internal mode, merge governed annotations
        if mode == ProtectedElementSource.GOVERNED_ANNOTATIONS_PLUS_EXTRACTOR and governed_annotations:
            gov_ents = governed_annotations.get("protected_entities", [])
            for ent in gov_ents:
                orig_elems["entities"].add(ent.strip().lower())
            gov_keys = governed_annotations.get("task_answer_keys", [])
            for key in gov_keys:
                if key.strip().lower() not in simp_text.lower():
                    violations.append(f"Missing governed task answer key: '{key}'")

        # 1. Entity Preservation
        missing_entities = orig_elems["entities"] - simp_elems["entities"]
        if missing_entities:
            # Check if partial substring match exists
            unmatched = set()
            simp_lower = simp_text.lower()
            for ent in missing_entities:
                if ent not in simp_lower:
                    unmatched.add(ent)
            if unmatched:
                violations.append(f"Missing protected entities: {sorted(list(unmatched))}")

        # 2. Quantity Preservation
        missing_quantities = orig_elems["quantities"] - simp_elems["quantities"]
        if missing_quantities:
            violations.append(f"Missing numbers/quantities: {sorted(list(missing_quantities))}")

        # 3. Color Preservation
        missing_colors = orig_elems["colors"] - simp_elems["colors"]
        if missing_colors:
            violations.append(f"Missing visual cue colors: {sorted(list(missing_colors))}")

        # 4. Negation Polarity Consistency
        orig_has_neg = len(orig_elems["negations"]) > 0
        simp_has_neg = len(simp_elems["negations"]) > 0
        if orig_has_neg != simp_has_neg:
            violations.append(
                f"Negation polarity inversion: original_negated={orig_has_neg}, simplified_negated={simp_has_neg}"
            )

        # Determine Status and Disposition
        if not violations:
            return MeaningValidationStatus.PASSED, FinalDisposition.AUTOMATIC_CHECK_PASSED, []
        
        # Check if violations warrant manual review vs automatic check failed
        # If only entity match is slightly uncertain vs hard quantity/negation mismatch
        if any("Negation polarity" in v or "Missing numbers/quantities" in v for v in violations):
            return MeaningValidationStatus.FAILED, FinalDisposition.AUTOMATIC_CHECK_FAILED, violations
        
        return MeaningValidationStatus.MANUAL_REVIEW_REQUIRED, FinalDisposition.MANUAL_REVIEW_REQUIRED, violations
