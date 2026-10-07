"""
Unit tests for Action Graph representation, temporal unrolling, and step numbering.
"""

import pytest
from app.controlled_simplification.action_graph import ActionGraphBuilder
from app.controlled_simplification.action_graph_validator import ActionGraphValidator
from app.controlled_simplification.schemas import ModifierCriticality


def test_temporal_inversion_unrolling():
    """'Before X, do Y' should be re-ordered to 1. Y, 2. X."""
    builder = ActionGraphBuilder()
    text = "Before placing the red ball inside the box, carefully select the smaller blue object."
    graph = builder.build_graph(text)

    assert graph.has_temporal_inversion is True
    assert graph.is_multi_step is True
    assert len(graph.actions) == 2

    # First action must be 'select' (or 'pick'), second must be 'place' (or 'put')
    assert "select" in graph.actions[0].verb.lower() or "pick" in graph.actions[0].verb.lower()
    assert "place" in graph.actions[1].verb.lower() or "put" in graph.actions[1].verb.lower()

    formatted = builder.format_to_text(graph, force_numbered=True)
    assert "1." in formatted
    assert "2." in formatted


def test_single_step_instruction_not_numbered():
    """A single-action instruction must not be numbered."""
    builder = ActionGraphBuilder()
    text = "Pick up the blue ball."
    graph = builder.build_graph(text)

    assert graph.is_multi_step is False
    formatted = builder.format_to_text(graph, force_numbered=False)
    assert not formatted.startswith("1.")
    assert formatted.endswith(".")


def test_safety_critical_modifier_preservation():
    """Safety-critical modifiers like 'gently' must be verified by the action validator."""
    builder = ActionGraphBuilder()
    validator = ActionGraphValidator()

    src_text = "Place the glass on the table gently."
    simp_missing_mod = "Put the glass on the table."

    src_graph = builder.build_graph(src_text)
    simp_graph = builder.build_graph(simp_missing_mod)

    valid, violations = validator.validate_sequence_preservation(src_graph, simp_graph)
    assert valid is False
    assert any("Safety-critical modifier" in v for v in violations)
