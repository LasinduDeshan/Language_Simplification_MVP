"""
Tier-calibrated lexical substitution and morphological repair operations.
"""

import re
from typing import Dict, List, Set, Tuple, Optional
from app.controlled_simplification.schemas import EffectiveProtectionContext
from app.controlled_simplification.protected_elements import (
    DEFAULT_SEMANTIC_EQUIVALENCE_MAP,
    is_semantically_equivalent
)
from app.controlled_simplification.spacy_manager import SpacyPipelineManager


# Governed child-friendly word replacement dictionary with target acquisition age
CHILD_LEXICON_SUBSTITUTIONS: Dict[str, Tuple[str, int]] = {
    # difficult_word: (simple_replacement, base_age)
    "select": ("pick", 4),
    "choose": ("pick", 4),
    "purchase": ("buy", 5),
    "obtain": ("get", 4),
    "receive": ("get", 5),
    "commence": ("start", 4),
    "terminate": ("stop", 4),
    "construct": ("build", 5),
    "fabricate": ("make", 4),
    "demonstrate": ("show", 5),
    "indicate": ("show", 5),
    "examine": ("look at", 5),
    "inspect": ("check", 5),
    "utilize": ("use", 5),
    "attempt": ("try", 4),
    "require": ("need", 4),
    "possess": ("have", 4),
    "assist": ("help", 4),
    "inquire": ("ask", 4),
    "comprehend": ("understand", 6),
    "discover": ("find", 4),
    "locate": ("find", 4),
    "position": ("put", 4),
    "place": ("put", 4),
    "underneath": ("under", 4),
    "beneath": ("under", 4),
    "adjacent": ("next to", 6),
    "inside": ("in", 4),
    "outside": ("out", 4),
    "smaller": ("smaller", 4),
    "larger": ("bigger", 4),
    "enormous": ("big", 4),
    "gigantic": ("big", 4),
    "tiny": ("small", 4),
    "difficult": ("hard", 5),
    "complex": ("hard", 6),
    "simple": ("easy", 4),
    "rapidly": ("fast", 4),
    "immediately": ("right now", 5),
    "subsequently": ("then", 5),
    "initially": ("first", 5),
    "eventually": ("in the end", 6),
    "object": ("thing", 4),
    "vehicle": ("car", 4),
    "residence": ("house", 5),
    "individual": ("person", 5),
    "juvenile": ("child", 5),
    "apparel": ("clothes", 5),
    "beverage": ("drink", 4),
    "nourishment": ("food", 5),
}


class LexicalSimplifier:
    """
    Applies tier-calibrated lexical replacements while preserving protected entities and grammatical agreement.
    """

    def __init__(self):
        self.spacy_manager = SpacyPipelineManager()

    def simplify_lexicon(
        self,
        text: str,
        target_content_age: int,
        age_offset: int,
        effective_protections: EffectiveProtectionContext
    ) -> Tuple[str, List[Dict[str, str]]]:
        """
        Substitutes difficult words in text according to target_content_age + age_offset threshold.
        """
        doc = self.spacy_manager.get_doc(text)
        exact_protected = set(effective_protections.effective_protected_elements.exact_preservation)
        quantities_protected = set(str(q).lower() for q in effective_protections.effective_protected_elements.quantities)

        replacements_made: List[Dict[str, str]] = []
        tokens_out: List[str] = []

        for token in doc:
            t_lower = token.text.lower()
            lemma = token.lemma_.lower()

            # Guard: If token is in exact protection set, never substitute
            if t_lower in exact_protected or lemma in exact_protected or t_lower in quantities_protected:
                tokens_out.append(token.text)
                continue

            # Check substitution dictionary
            sub_candidate = None
            if t_lower in CHILD_LEXICON_SUBSTITUTIONS:
                repl, repl_age = CHILD_LEXICON_SUBSTITUTIONS[t_lower]
                sub_candidate = (repl, repl_age)
            elif lemma in CHILD_LEXICON_SUBSTITUTIONS:
                repl, repl_age = CHILD_LEXICON_SUBSTITUTIONS[lemma]
                sub_candidate = (repl, repl_age)

            if sub_candidate:
                repl_word, repl_age = sub_candidate
                # Check if word is considered difficult under the tier threshold
                # Higher tier (Strong offset=-1) replaces more aggressively
                effective_threshold_age = target_content_age + age_offset
                if repl_age <= effective_threshold_age:
                    # Match casing
                    if token.text.isupper():
                        final_repl = repl_word.upper()
                    elif token.text.istitle():
                        final_repl = repl_word.capitalize()
                    else:
                        final_repl = repl_word

                    tokens_out.append(final_repl)
                    replacements_made.append({"source": token.text, "replacement": final_repl})
                    continue

            tokens_out.append(token.text)

        # Reconstruct string with whitespace preservation
        reconstructed = self._detokenize(doc, tokens_out)
        repaired = self.repair_morphology(reconstructed)
        return repaired, replacements_made

    def repair_morphology(self, text: str) -> str:
        """
        Repairs English grammatical surface forms (a vs an, capitalization, spacing).
        """
        # 1. Fix 'a' vs 'an'
        text = re.sub(r"\ba\s+([aeiouAEIOU]\w*)", r"an \1", text)
        text = re.sub(r"\ban\s+([^aeiouAEIOU\s]\w*)", r"a \1", text)

        # 2. Fix capitalization at start of sentences and steps
        lines = text.split("\n")
        fixed_lines = []
        for line in lines:
            line_str = line.strip()
            if not line_str:
                fixed_lines.append("")
                continue
            # Check if line starts with step number (e.g. '1. pick ...')
            match_step = re.match(r"^(\d+[\.\)]\s*)([a-z])(.*)$", line_str)
            if match_step:
                prefix = match_step.group(1)
                first_char = match_step.group(2).upper()
                rest = match_step.group(3)
                fixed_lines.append(f"{prefix}{first_char}{rest}")
            else:
                fixed_lines.append(line_str[0].upper() + line_str[1:])

        rejoined = "\n".join(fixed_lines)

        # 3. Clean up multiple spaces and trailing spaces
        rejoined = re.sub(r"[ \t]+", " ", rejoined)
        return rejoined

    def _detokenize(self, doc, token_texts: List[str]) -> str:
        """
        Recombines tokens matching original whitespace and punctuation.
        """
        out = ""
        for orig_token, repl_text in zip(doc, token_texts):
            out += repl_text + orig_token.whitespace_
        return out.strip()
