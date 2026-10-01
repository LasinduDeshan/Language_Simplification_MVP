"""
Automatic extraction of protected elements and merger with caller-provided constraints.
"""

import re
from typing import Dict, Any, List, Set, Optional, Tuple
from app.controlled_simplification.schemas import (
    ProtectedElementsConfig,
    EffectiveProtectionContext,
    SemanticEquivalenceRule,
    ModifierCriticality,
    ModifierNode
)
from app.controlled_simplification.protected_elements import (
    KNOWN_COLORS,
    KNOWN_SHAPES,
    SAFETY_CRITICAL_MODIFIERS,
    DEFAULT_SEMANTIC_EQUIVALENCE_MAP
)
from app.controlled_simplification.spacy_manager import SpacyPipelineManager


class ProtectedElementExtractor:
    """
    Extracts protected entities, numbers, perceptual attributes, and modifiers from English text.
    Merges auto-detected elements with caller-supplied constraints, ensuring caller metadata
    never silently removes automatically detected safety protections.
    """

    def __init__(self):
        self.spacy_manager = SpacyPipelineManager()

    def extract_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract protected elements from text using spaCy linguistic parsing.
        """
        doc = self.spacy_manager.get_doc(text)

        exact_entities: Set[str] = set()
        quantities: Set[str] = set()
        colors: Set[str] = set()
        shapes: Set[str] = set()
        relations: Set[str] = set()
        modifiers: List[ModifierNode] = []

        # 1. Named entities
        for ent in doc.ents:
            if ent.label_ in {"CARDINAL", "QUANTITY", "PERCENT", "MONEY"}:
                quantities.add(ent.text.strip().lower())
            elif ent.label_ in {"PERSON", "GPE", "ORG", "LOC", "FAC", "PRODUCT", "EVENT"}:
                exact_entities.add(ent.text.strip().lower())

        # 2. Token-level analysis (colors, shapes, numbers, adverbs, relations)
        for token in doc:
            t_lower = token.text.lower()
            # Numbers / digits / cardinals
            if token.pos_ == "NUM" or token.like_num or re.match(r"^\d+(\.\d+)?$", token.text):
                quantities.add(t_lower)

            # Colors
            if t_lower in KNOWN_COLORS or token.lemma_.lower() in KNOWN_COLORS:
                c_val = token.lemma_.lower() if token.lemma_.lower() in KNOWN_COLORS else t_lower
                colors.add(c_val)
                exact_entities.add(c_val)

            # Shapes / perceptual entities
            if t_lower in KNOWN_SHAPES or token.lemma_.lower() in KNOWN_SHAPES:
                s_val = token.lemma_.lower() if token.lemma_.lower() in KNOWN_SHAPES else t_lower
                shapes.add(s_val)
                exact_entities.add(s_val)

            # Nouns (head entities)
            if token.pos_ in {"NOUN", "PROPN"} and token.dep_ in {"dobj", "pobj", "nsubj", "attr", "conj"}:
                exact_entities.add(token.lemma_.lower())

            # Spatial / temporal prepositions
            if t_lower in {"before", "after", "inside", "outside", "underneath", "beneath", "above", "behind", "between", "adjacent"}:
                relations.add(t_lower)

            # Adverbs / modifiers
            if token.pos_ == "ADV" and token.dep_ in {"advmod", "manner"}:
                if t_lower in SAFETY_CRITICAL_MODIFIERS:
                    modifiers.append(ModifierNode(text=t_lower, criticality=ModifierCriticality.SAFETY_CRITICAL))
                else:
                    modifiers.append(ModifierNode(text=t_lower, criticality=ModifierCriticality.OPTIONAL_STYLE))

        return {
            "exact_preservation": sorted(list(exact_entities)),
            "quantities": sorted(list(quantities)),
            "colors": sorted(list(colors)),
            "shapes": sorted(list(shapes)),
            "relations": sorted(list(relations)),
            "modifiers": [m.model_dump() for m in modifiers]
        }

    def merge_with_caller_constraints(
        self,
        text: str,
        caller_config: Optional[ProtectedElementsConfig]
    ) -> EffectiveProtectionContext:
        """
        Merge auto-extracted elements with caller-provided constraints.
        Enforces that caller metadata cannot remove auto-detected protections.
        """
        detected = self.extract_from_text(text)
        conflicts: List[str] = []

        # Start with detected items
        effective_exact = set(detected["exact_preservation"])
        effective_quantities = set(detected["quantities"])
        effective_semantic_rules: Dict[str, Set[str]] = {
            src: set(alw) for src, alw in DEFAULT_SEMANTIC_EQUIVALENCE_MAP.items()
        }
        forbidden_refs: Set[str] = set()
        forbidden_hashes: Set[str] = set()

        if caller_config:
            # Caller can add additional exact elements
            for item in caller_config.exact_preservation:
                effective_exact.add(item.strip().lower())

            # Caller can add additional quantities
            for q in caller_config.quantities:
                effective_quantities.add(str(q).strip().lower())

            # Caller can augment semantic equivalence rules
            for rule in caller_config.semantic_equivalence_allowed:
                src = rule.source.strip().lower()
                if src not in effective_semantic_rules:
                    effective_semantic_rules[src] = set()
                for alw in rule.allowed:
                    effective_semantic_rules[src].add(alw.strip().lower())

            # Caller forbidden disclosure hashes
            for r in caller_config.forbidden_disclosure_refs:
                forbidden_refs.add(r.strip())
            for h in caller_config.forbidden_disclosure_hashes:
                forbidden_hashes.add(h.strip())

        # Compile final effective config
        compiled_semantic_rules = [
            SemanticEquivalenceRule(source=src, allowed=sorted(list(alws)))
            for src, alws in sorted(effective_semantic_rules.items())
        ]

        effective_config = ProtectedElementsConfig(
            exact_preservation=sorted(list(effective_exact)),
            semantic_equivalence_allowed=compiled_semantic_rules,
            quantities=sorted(list(effective_quantities)),
            forbidden_disclosure_refs=sorted(list(forbidden_refs)),
            forbidden_disclosure_hashes=sorted(list(forbidden_hashes))
        )

        return EffectiveProtectionContext(
            detected_protected_elements=detected,
            effective_protected_elements=effective_config,
            protection_conflicts=conflicts
        )
