"""
Validation of action graphs, chronological action order, and modifier retention.
"""

from typing import Tuple, List, Optional
from app.controlled_simplification.schemas import ActionGraph, ActionNode, ModifierCriticality
from app.controlled_simplification.protected_elements import is_semantically_equivalent


class ActionGraphValidator:
    """
    Validates that a simplified output retains all core actions, correct chronological execution order,
    and all safety-critical modifiers from the original Action Graph.
    """

    def validate_sequence_preservation(
        self,
        source_graph: ActionGraph,
        simplified_graph: ActionGraph
    ) -> Tuple[bool, List[str]]:
        """
        Check that all source action nodes are represented in simplified_graph in proper order.
        """
        violations: List[str] = []

        if not source_graph.actions:
            return True, []

        # If source is multi-step, simplified must represent all steps
        if source_graph.is_multi_step and len(simplified_graph.actions) < len(source_graph.actions):
            violations.append(
                f"Action count mismatch: expected {len(source_graph.actions)} steps, got {len(simplified_graph.actions)}"
            )

        # Verify action verb equivalence and order
        source_verbs = [n.verb.lower() for n in source_graph.actions]
        simplified_verbs = [n.verb.lower() for n in simplified_graph.actions]

        matched_idx = 0
        for s_verb in source_verbs:
            found = False
            for j in range(matched_idx, len(simplified_verbs)):
                simp_v = simplified_verbs[j]
                if simp_v == s_verb or is_semantically_equivalent(s_verb, simp_v):
                    found = True
                    matched_idx = j + 1
                    break
            if not found:
                violations.append(f"Action '{s_verb}' missing or executed out of sequence in simplified output")

        # Verify safety-critical modifiers
        for s_node in source_graph.actions:
            for mod in s_node.modifiers:
                if mod.criticality == ModifierCriticality.SAFETY_CRITICAL:
                    # Look for modifier text across simplified actions
                    mod_text = mod.text.lower()
                    found_mod = False
                    for simp_node in simplified_graph.actions:
                        simp_clause = (simp_node.raw_clause or "").lower()
                        if mod_text in simp_clause:
                            found_mod = True
                            break
                    if not found_mod:
                        violations.append(f"Safety-critical modifier '{mod.text}' was removed")

        is_valid = len(violations) == 0
        return is_valid, violations
