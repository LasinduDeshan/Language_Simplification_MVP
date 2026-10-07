"""
Unit tests for automatic protected element extraction and merge invariants.
"""

import pytest
from app.controlled_simplification.protected_element_extractor import ProtectedElementExtractor
from app.controlled_simplification.schemas import ProtectedElementsConfig


def test_auto_extraction_of_colors_shapes_numbers():
    extractor = ProtectedElementExtractor()
    text = "Place the 3 red balls inside the large blue box gently."
    detected = extractor.extract_from_text(text)

    # Colors & Shapes
    assert "red" in detected["colors"]
    assert "blue" in detected["colors"]
    assert "box" in detected["shapes"]
    assert "ball" in detected["exact_preservation"] or "balls" in detected["exact_preservation"]

    # Numbers
    assert "3" in detected["quantities"]

    # Safety modifier
    assert any(m["text"] == "gently" and m["criticality"] == "safety_critical" for m in detected["modifiers"])


def test_caller_cannot_remove_auto_detected_protections():
    """Caller provided config cannot remove auto-detected protections."""
    extractor = ProtectedElementExtractor()
    text = "Find the 2 yellow circles."

    # Caller passes empty exact_preservation
    caller_cfg = ProtectedElementsConfig(
        exact_preservation=[],
        quantities=[]
    )

    merged = extractor.merge_with_caller_constraints(text, caller_cfg)
    # The auto-detected 'yellow' and 'circle' and '2' must remain in effective protections
    effective_exact = merged.effective_protected_elements.exact_preservation
    effective_quant = merged.effective_protected_elements.quantities

    assert "yellow" in effective_exact
    assert "circle" in effective_exact
    assert "2" in effective_quant
