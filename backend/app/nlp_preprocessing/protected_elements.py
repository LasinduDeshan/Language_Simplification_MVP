"""
Stage 21 Protected Elements & Linguistic Entity Aligner Module
Extracts numbers, quantities, negation, spatio-temporal connectives, and aligns human protected units.
"""
import re
from typing import List, Dict, Any, Set
from app.nlp_preprocessing.schemas import SentenceRecord, ProtectedMeaningFeatures

class ProtectedElementExtractor:
    def __init__(self):
        self.negation_patterns = [
            r"\bnot\b", r"\bnever\b", r"\bno\b", r"\bwithout\b", r"\bexcept\b",
            r"\botherwise\b", r"\bif not\b", r"\bdon't\b", r"\bdont\b", r"\bcannot\b", r"\bcan't\b"
        ]
        self.number_words = {
            "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
            "first", "second", "third", "fourth", "multiple", "several", "pair", "all", "both"
        }
        self.spatial_prepositions = {
            "under", "above", "beside", "between", "behind", "in", "on", "inside", "outside",
            "across", "through", "around", "near", "along", "toward", "against", "beneath", "beyond", "underneath"
        }
        self.temporal_connectives = {
            "before", "after", "first", "then", "next", "finally", "yesterday", "earlier", "later", "while", "when"
        }
        self.common_colors = {
            "red", "blue", "yellow", "green", "orange", "purple", "white", "black", "brown", "gray", "silver", "gold"
        }

    def extract_features(self, sentences: List[SentenceRecord], protected_meaning_units: List[str]) -> ProtectedMeaningFeatures:
        all_text = " ".join(s.text for s in sentences)
        lower_text = all_text.lower()

        # 1. Negation markers
        negation_markers = []
        for pat in self.negation_patterns:
            matches = re.findall(pat, lower_text)
            negation_markers.extend(matches)
        negation_markers = sorted(list(set(negation_markers)))

        # 2. Quantity numbers
        quantity_numbers = []
        # Digits
        digits = re.findall(r"\b\d+\b", all_text)
        quantity_numbers.extend(digits)
        # Number words
        for tok in re.findall(r"\b[a-zA-Z]+\b", lower_text):
            if tok in self.number_words:
                quantity_numbers.append(tok)
        quantity_numbers = sorted(list(set(quantity_numbers)))

        # 3. Spatial prepositions & temporal connectives
        found_spatial = []
        found_temporal = []
        found_actions = []
        named_entities = []

        for sent in sentences:
            for tok in sent.tokens:
                w_lower = tok.text.lower()
                if w_lower in self.spatial_prepositions:
                    found_spatial.append(w_lower)
                if w_lower in self.temporal_connectives:
                    found_temporal.append(w_lower)
                if tok.pos == "VERB" and not tok.is_stop:
                    found_actions.append(tok.lemma)
                if w_lower in self.common_colors:
                    named_entities.append({"text": tok.text, "category": "COLOR"})
                if tok.pos == "PROPN":
                    named_entities.append({"text": tok.text, "category": "PERSON_OR_PLACE"})

        found_spatial = sorted(list(set(found_spatial)))
        found_temporal = sorted(list(set(found_temporal)))
        found_actions = sorted(list(set(found_actions)))

        # 4. Alignment of human-authored protected meaning units
        aligned_units = []
        for unit in protected_meaning_units:
            u_clean = unit.strip()
            if not u_clean:
                continue
            u_lower = u_clean.lower()
            
            # Check presence in text
            is_present = u_lower in lower_text
            if not is_present:
                u_words = u_lower.split()
                is_present = all(w in lower_text for w in u_words)
                
            aligned_units.append({
                "protected_unit": u_clean,
                "is_aligned": is_present,
                "status": "aligned" if is_present else "unaligned_warning"
            })

        return ProtectedMeaningFeatures(
            negation_markers=negation_markers,
            quantity_numbers=quantity_numbers,
            named_entities=named_entities,
            spatial_prepositions=found_spatial,
            temporal_connectives=found_temporal,
            action_verbs=found_actions,
            aligned_protected_units=aligned_units
        )
