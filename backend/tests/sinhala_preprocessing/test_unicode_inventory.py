"""
Tests for Stage 30 Character Inventory.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
INVENTORY_PATH = PROJECT_ROOT / "data" / "sinhala_preprocessing" / "registry" / "character_inventory.json"

def test_character_inventory_file_and_schema():
    assert INVENTORY_PATH.exists(), "character_inventory.json must exist"
    data = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))

    assert data["inventory_id"] == "STAGE30-SINHALA-CHAR-INVENTORY-V1"
    assert "characters" in data
    assert len(data["characters"]) >= 100

    required_keys = {
        "code_point", "unicode_name", "unicode_category",
        "script_or_block", "token_category", "allowed_context",
        "normalization_behavior", "review_behavior", "unicode_version"
    }

    blocks = set()
    for entry in data["characters"]:
        assert required_keys.issubset(entry.keys()), f"Missing keys in {entry}"
        blocks.add(entry["script_or_block"])

    # Must distinguish Sinhala block, Archaic numbers, and Arabic digits
    assert "Sinhala" in blocks
    assert "Sinhala Archaic Numbers" in blocks
    assert "Basic Latin" in blocks

def test_sinhala_block_and_lith_digits_distinction():
    data = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    chars_by_cp = {c["code_point"]: c for c in data["characters"]}

    # Independent vowel
    assert "U+0D85" in chars_by_cp
    assert chars_by_cp["U+0D85"]["allowed_context"] == "independent_vowel"

    # Consonant
    assert "U+0D9A" in chars_by_cp
    assert chars_by_cp["U+0D9A"]["allowed_context"] == "consonant"

    # Virama
    assert "U+0DCA" in chars_by_cp
    assert chars_by_cp["U+0DCA"]["allowed_context"] == "virama_al_lakuna"

    # Lith digit (must not be classified as vowel sign or combining mark)
    assert "U+0DE7" in chars_by_cp
    assert chars_by_cp["U+0DE7"]["token_category"] == "SINHALA_NUMBER"
    assert chars_by_cp["U+0DE7"]["allowed_context"] == "sinhala_lith_digit"

    # Archaic number
    assert "U+111E1" in chars_by_cp
    assert chars_by_cp["U+111E1"]["script_or_block"] == "Sinhala Archaic Numbers"
    assert chars_by_cp["U+111E1"]["token_category"] == "SINHALA_NUMBER"
