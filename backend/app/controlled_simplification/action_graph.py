"""
Action Graph representation, temporal unrolling, and atomic step chunking for educational instructions.
"""

import re
from typing import List, Optional, Tuple
from app.controlled_simplification.schemas import (
    ActionNode,
    ActionGraph,
    ModifierNode,
    ModifierCriticality
)
from app.controlled_simplification.protected_elements import SAFETY_CRITICAL_MODIFIERS
from app.controlled_simplification.spacy_manager import SpacyPipelineManager


class ActionGraphBuilder:
    """
    Constructs and manipulates structured Action Graphs from instructional English sentences.
    Handles temporal dependency inversion (e.g. 'Before X, do Y') and atomic step formatting.
    """

    def __init__(self):
        self.spacy_manager = SpacyPipelineManager()

    def build_graph(self, text: str) -> ActionGraph:
        """
        Parse text into an ActionGraph containing ordered ActionNodes.
        """
        clean_text = text.strip()
        doc = self.spacy_manager.get_doc(clean_text)

        # Check if text is already formatted as numbered steps (e.g. '1. ...\n2. ...')
        lines = [l.strip() for l in clean_text.split("\n") if l.strip()]
        if len(lines) > 1 and all(re.match(r"^\d+[\.\)]", l) for l in lines):
            actions = [self._parse_clause_to_node(l, sequence=i+1) for i, l in enumerate(lines)]
            return ActionGraph(
                actions=actions,
                has_temporal_inversion=False,
                is_multi_step=True
            )

        # Check for temporal inversion patterns like "Before doing X, do Y" or "Before X, Y"
        match_before = re.match(r"^before\s+(.+?),\s*(.+)$", clean_text, re.IGNORECASE)
        match_after = re.match(r"^after\s+(.+?),\s*(.+)$", clean_text, re.IGNORECASE)

        if match_before:
            clause1 = match_before.group(1).strip()  # Event that happens SECOND
            clause2 = match_before.group(2).strip()  # Event that happens FIRST

            node1 = self._parse_clause_to_node(clause2, sequence=1)
            node2 = self._parse_clause_to_node(clause1, sequence=2)

            return ActionGraph(
                actions=[node1, node2],
                has_temporal_inversion=True,
                is_multi_step=True
            )

        if match_after:
            clause1 = match_after.group(1).strip()  # Event that happens FIRST
            clause2 = match_after.group(2).strip()  # Event that happens SECOND

            node1 = self._parse_clause_to_node(clause1, sequence=1)
            node2 = self._parse_clause_to_node(clause2, sequence=2)

            return ActionGraph(
                actions=[node1, node2],
                has_temporal_inversion=False,
                is_multi_step=True
            )

        # Check for coordinated actions joined by "and then", "then", "and"
        parts = re.split(r",?\s+(?:and\s+then|then|and\s+after\s+that)\s+", clean_text, flags=re.IGNORECASE)
        if len(parts) > 1:
            actions = [self._parse_clause_to_node(p.strip(), sequence=i+1) for i, p in enumerate(parts) if p.strip()]
            return ActionGraph(
                actions=actions,
                has_temporal_inversion=False,
                is_multi_step=len(actions) > 1
            )

        # Single action sentence
        single_node = self._parse_clause_to_node(clean_text, sequence=1)
        return ActionGraph(
            actions=[single_node],
            has_temporal_inversion=False,
            is_multi_step=False
        )

    def _parse_clause_to_node(self, clause: str, sequence: int) -> ActionNode:
        """
        Parse a single clause into an ActionNode with verb, object, relation, modifiers.
        """
        # Clean leading numbering or bullet artifacts
        cleaned = re.sub(r"^\d+[\.\)]\s*", "", clause).strip()
        doc = self.spacy_manager.get_doc(cleaned)

        root_verb = ""
        direct_obj = ""
        relation = None
        ref_obj = None
        modifiers: List[ModifierNode] = []

        # Find main verb
        for token in doc:
            if token.pos_ == "VERB" or (token.dep_ == "ROOT" and token.pos_ in {"VERB", "AUX"}):
                root_verb = token.lemma_.lower()
                break
        if not root_verb:
            # Fallback to first word if imperative
            first_word = cleaned.split()[0].lower() if cleaned.split() else "do"
            root_verb = first_word

        # Find direct object, prepositions, and modifiers
        for token in doc:
            t_lower = token.text.lower()
            if token.dep_ in {"dobj", "attr", "pobj"} and not direct_obj:
                direct_obj = token.text
            if token.pos_ == "ADP" and t_lower in {"in", "inside", "on", "under", "into", "to", "behind", "above"}:
                relation = t_lower
                # Try finding pobj
                for child in token.children:
                    if child.dep_ == "pobj":
                        ref_obj = child.text
            if token.pos_ == "ADV" and token.dep_ in {"advmod", "manner"}:
                if t_lower in SAFETY_CRITICAL_MODIFIERS:
                    modifiers.append(ModifierNode(text=t_lower, criticality=ModifierCriticality.SAFETY_CRITICAL))
                else:
                    modifiers.append(ModifierNode(text=t_lower, criticality=ModifierCriticality.OPTIONAL_STYLE))

        return ActionNode(
            sequence=sequence,
            verb=root_verb,
            object=direct_obj,
            relation=relation,
            reference_object=ref_obj,
            modifiers=modifiers,
            raw_clause=cleaned
        )

    def format_to_text(self, graph: ActionGraph, force_numbered: bool = False) -> str:
        """
        Format ActionGraph into surface text.
        Single action: direct sentence.
        Multi-action (or force_numbered): numbered atomic lines.
        """
        if not graph.actions:
            return ""

        if not graph.is_multi_step and not force_numbered:
            # Single action: return as single declarative/imperative sentence
            node = graph.actions[0]
            clause = node.raw_clause or ""
            # Ensure proper capitalization and ending period
            if clause:
                clause = clause[0].upper() + clause[1:]
                if not clause.endswith((".", "!", "?")):
                    clause += "."
            return clause

        # Multi-step: format with numbered lines
        lines = []
        for i, node in enumerate(graph.actions, 1):
            clause = node.raw_clause or f"{node.verb} {node.object}".strip()
            # Clean leading conjunctions and gerunds into imperatives
            clause = self._normalize_to_imperative(clause)
            if not clause.endswith((".", "!", "?")):
                clause += "."
            lines.append(f"{i}. {clause}")

        return "\n".join(lines)

    def _normalize_to_imperative(self, clause: str) -> str:
        """
        Converts clauses like 'placing the red ball' into 'Place the red ball'
        and cleans leading adverbs or conjunctions.
        """
        c = re.sub(r"^(then|and|also|next|first)\s+", "", clause, flags=re.IGNORECASE).strip()

        # Convert gerunds at start: 'placing the ball' -> 'Put the ball' or 'Place the ball'
        words = c.split()
        if words:
            first = words[0].lower()
            if first.endswith("ing"):
                # Simple lemmatization heuristic
                base = first[:-3]
                if base.endswith("plac"):
                    base = "place"
                elif base.endswith("t"):
                    base = base  # e.g. selecting -> select
                words[0] = base
            words[0] = words[0].capitalize()
            c = " ".join(words)

        return c
