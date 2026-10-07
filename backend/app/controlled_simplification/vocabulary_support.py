"""
Deterministic vocabulary support definitions and contextual examples.
Loaded exclusively from governed expert-authored templates.
"""

from typing import List, Dict, Optional, Set
from app.controlled_simplification.schemas import VocabularyExplanation


# Governed child-friendly micro-definitions and contextual illustrative examples
GOVERNED_VOCABULARY_DICTIONARY: Dict[str, Dict[str, str]] = {
    "select": {
        "simplified_term": "pick",
        "simple_definition": "choose one thing from a group",
        "example": "Pick the blue block from the box."
    },
    "choose": {
        "simplified_term": "pick",
        "simple_definition": "decide which one you want",
        "example": "Pick your favorite color."
    },
    "locate": {
        "simplified_term": "find",
        "simple_definition": "look and see where something is",
        "example": "Find the red star on the page."
    },
    "purchase": {
        "simplified_term": "buy",
        "simple_definition": "pay money to get something",
        "example": "Buy an apple at the store."
    },
    "construct": {
        "simplified_term": "build",
        "simple_definition": "put pieces together to make something",
        "example": "Build a tall tower with blocks."
    },
    "examine": {
        "simplified_term": "look at",
        "simple_definition": "look very closely at something",
        "example": "Look at the bug on the leaf."
    },
    "position": {
        "simplified_term": "put",
        "simple_definition": "place something in a spot",
        "example": "Put the cup on the table."
    },
    "utilize": {
        "simplified_term": "use",
        "simple_definition": "work with a tool or object",
        "example": "Use the crayon to color."
    },
    "demonstrate": {
        "simplified_term": "show",
        "simple_definition": "show how to do something",
        "example": "Show how high you can jump."
    },
    "terminate": {
        "simplified_term": "stop",
        "simple_definition": "bring something to an end",
        "example": "Stop when you hear the bell."
    },
    "commence": {
        "simplified_term": "start",
        "simple_definition": "begin doing something",
        "example": "Start drawing now."
    },
    "underneath": {
        "simplified_term": "under",
        "simple_definition": "below or under something",
        "example": "Look under the blanket."
    },
    "adjacent": {
        "simplified_term": "next to",
        "simple_definition": "right beside something",
        "example": "Sit next to your friend."
    }
}


class VocabularySupportProvider:
    """
    Extracts governed vocabulary definitions and examples for complex domain words.
    """

    def get_explanations_for_text(
        self,
        text: str,
        policy: str = "selected"
    ) -> List[VocabularyExplanation]:
        """
        Identify complex terms in text and return approved vocabulary explanations.
        Policy:
          - 'top_difficult': max 1 most difficult word
          - 'selected': up to 2 essential domain words
          - 'all_complex': all detected matching vocabulary items
        """
        if policy == "none":
            return []

        words_in_text = set(w.lower() for w in text.split())
        explanations: List[VocabularyExplanation] = []

        for term, data in GOVERNED_VOCABULARY_DICTIONARY.items():
            if term in words_in_text or f"{term}ing" in words_in_text or f"{term}ed" in words_in_text or f"{term}s" in words_in_text:
                explanations.append(VocabularyExplanation(
                    word=term,
                    simplified_term=data.get("simplified_term"),
                    simple_definition=data["simple_definition"],
                    example=data["example"],
                    source="governed_lexicon"
                ))

        if policy == "top_difficult":
            return explanations[:1]
        elif policy == "selected":
            return explanations[:2]
        return explanations
