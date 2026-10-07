"""
Syntactic restructuring operations: passive-to-active conversion, nominalization unpacking, clause splitting.
"""

import re
from typing import Tuple, List, Optional
from app.controlled_simplification.spacy_manager import SpacyPipelineManager


# Common nominalization patterns mapped to simplified active verbs
NOMINALIZATION_MAP = {
    r"\bmake\s+(?:a\s+)?selection\b": "pick",
    r"\bmake\s+(?:a\s+)?choice\b": "choose",
    r"\btake\s+(?:a\s+)?look\s+at\b": "look at",
    r"\bgive\s+(?:an?\s+)?explanation\b": "explain",
    r"\bperform\s+(?:an?\s+)?examination\s+of\b": "check",
    r"\bhave\s+(?:a\s+)?discussion\b": "talk",
    r"\bcarry\s+out\s+(?:an?\s+)?investigation\b": "find out"
}


class SyntacticSimplifier:
    """
    Applies deterministic syntactic transformations to reduce clause depth and improve readability.
    """

    def __init__(self):
        self.spacy_manager = SpacyPipelineManager()

    def unpack_nominalizations(self, text: str) -> Tuple[str, bool]:
        """
        Replaces nominalized verb phrases with simple active verbs.
        """
        modified = False
        res = text
        for pattern, replacement in NOMINALIZATION_MAP.items():
            if re.search(pattern, res, flags=re.IGNORECASE):
                res = re.sub(pattern, replacement, res, flags=re.IGNORECASE)
                modified = True
        return res, modified

    def convert_passive_to_active(self, text: str) -> Tuple[str, bool]:
        """
        Converts passive voice with explicit 'by [agent]' into active voice.
        Example: 'The red ball was placed in the box by Leo.' -> 'Leo placed the red ball in the box.'
        """
        # Pattern: [Subject] was/were [Verb-ed] [prep phrase] by [Agent]
        pattern = r"^(The\s+[\w\s]+?)\s+(?:was|were)\s+([\w]+ed|put|set|taken|given)\s+(.*?)\s+by\s+([\w\s]+?)[\.\?!]?$"
        match = re.match(pattern, text.strip(), re.IGNORECASE)

        if match:
            patient = match.group(1).strip()
            verb = match.group(2).strip()
            prep_phrase = match.group(3).strip()
            agent = match.group(4).strip()

            # Active construction: Agent verb patient prep_phrase.
            active_text = f"{agent.capitalize()} {verb} {patient.lower()}"
            if prep_phrase:
                active_text += f" {prep_phrase}"
            active_text += "."
            return active_text, True

        return text, False

    def split_coordinated_clauses(self, text: str, repeat_subject: bool = True) -> Tuple[str, bool]:
        """
        Splits coordinated sentences joined by 'and', 'but', 'then' into separate sentences,
        re-inserting the primary subject if repeat_subject is True.
        """
        # Only split if sentence contains coordinating conjunction between clauses
        parts = re.split(r",\s+(?:and\s+then|then|and|but)\s+", text.strip(), flags=re.IGNORECASE)
        if len(parts) <= 1:
            return text, False

        doc = self.spacy_manager.get_doc(parts[0])
        subject_text = ""
        for token in doc:
            if "subj" in token.dep_:
                subject_text = token.text
                break

        split_sentences = []
        for i, part in enumerate(parts):
            p = part.strip()
            if not p:
                continue
            # Capitalize
            p = p[0].upper() + p[1:]
            # Ensure subject if second part starts with a verb and repeat_subject is True
            if i > 0 and repeat_subject and subject_text:
                part_doc = self.spacy_manager.get_doc(p)
                first_token = part_doc[0] if len(part_doc) > 0 else None
                if first_token and first_token.pos_ == "VERB" and "subj" not in [t.dep_ for t in part_doc]:
                    p = f"{subject_text.capitalize()} {p.lower()}"

            if not p.endswith((".", "!", "?")):
                p += "."
            split_sentences.append(p)

        return " ".join(split_sentences), True
