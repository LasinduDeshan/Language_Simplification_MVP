"""
Tests for Controlled Surface Repair Module.
"""

from app.model_simplification.controlled_surface_repair import apply_controlled_surface_repair


def test_surface_repair_markdown_fences():
    text_with_fence = "```text\n1. Pick the blue ball.\n2. Put it in the box.\n```"
    repaired, changed = apply_controlled_surface_repair(text_with_fence)
    assert changed is True
    assert "```" not in repaired
    assert repaired == "1. Pick the blue ball.\n2. Put it in the box."


def test_surface_repair_casing_and_punctuation():
    bad_text = "1. pick the ball.. \n2. put it inside??"
    repaired, changed = apply_controlled_surface_repair(bad_text)
    assert changed is True
    assert ".." not in repaired
    assert "??" not in repaired
    assert "1. Pick" in repaired
    assert "2. Put" in repaired


def test_surface_repair_no_op_on_clean_text():
    clean_text = "1. Pick the blue ball.\n2. Put it in the box."
    repaired, changed = apply_controlled_surface_repair(clean_text)
    assert changed is False
    assert repaired == clean_text
