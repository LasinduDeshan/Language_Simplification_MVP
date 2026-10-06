"""
Tests for Stage 26 Prompt Registry and Versioned Templates.
"""
from app.model_simplification.prompt_registry import PromptRegistry


def test_prompt_registry_templates():
    for tier in ["mild", "moderate", "strong"]:
        prompt = PromptRegistry.get_prompt(
            text="Please identify the green triangle.",
            support_level=tier,
            exact_preservation=["triangle", "green"],
        )
        assert "triangle" in prompt
        assert "green" in prompt
        assert "Original Text:" in prompt
        assert "STRICT INVARIANT: Do NOT reveal" in prompt


def test_prompt_registry_export():
    md = PromptRegistry.export_markdown()
    assert "# Stage 26 Prompt Registry" in md
    assert "Mild Tier" in md
    assert "Moderate Tier" in md
    assert "Strong Tier" in md
