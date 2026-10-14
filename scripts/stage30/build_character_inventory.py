"""
Stage 30 Character Inventory Builder (WP1)
Builds the comprehensive, governed Sinhala and associated character inventory:
- Sinhala block: U+0D80–U+0DFF
- Sinhala Archaic Numbers: U+111E1–U+111F4
- Arabic / ASCII digits: U+0030–U+0039
- Format / Joiner controls: U+200D, U+200C
- Whitespace and punctuation
Generates:
- data/sinhala_preprocessing/registry/character_inventory.json
- docs/stage30_sinhala_character_inventory.csv
"""

import csv
import json
import unicodedata
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_DIR = PROJECT_ROOT / "data" / "sinhala_preprocessing" / "registry"
DOCS_DIR = PROJECT_ROOT / "docs"

JSON_OUTPUT = REGISTRY_DIR / "character_inventory.json"
CSV_OUTPUT = DOCS_DIR / "stage30_sinhala_character_inventory.csv"

def classify_character(cp: int) -> dict:
    char = chr(cp)
    hex_code = f"U+{cp:04X}"
    try:
        uname = unicodedata.name(char)
    except ValueError:
        return None  # Unassigned in Unicode

    category = unicodedata.category(char)
    u_version = unicodedata.unidata_version

    # Block and classification logic
    if 0x0D80 <= cp <= 0x0DFF:
        script_or_block = "Sinhala"
        if 0x0D82 <= cp <= 0x0D83:
            token_category = "SINHALA_WORD"
            allowed_context = "anusvara_visarga"
            norm_behavior = "preserved_nfc"
            review_behavior = "standard_processing"
        elif 0x0D85 <= cp <= 0x0D96:
            token_category = "SINHALA_WORD"
            allowed_context = "independent_vowel"
            norm_behavior = "preserved_nfc"
            review_behavior = "standard_processing"
        elif 0x0D9A <= cp <= 0x0DC6:
            token_category = "SINHALA_WORD"
            allowed_context = "consonant"
            norm_behavior = "preserved_nfc"
            review_behavior = "standard_processing"
        elif cp == 0x0DCA:
            token_category = "SINHALA_WORD"
            allowed_context = "virama_al_lakuna"
            norm_behavior = "preserved_nfc"
            review_behavior = "standard_processing"
        elif 0x0DCF <= cp <= 0x0DF3:
            token_category = "SINHALA_WORD"
            allowed_context = "dependent_vowel_sign"
            norm_behavior = "composite_composed"
            review_behavior = "standard_processing"
        elif cp == 0x0DF4:
            token_category = "PUNCTUATION"
            allowed_context = "sinhala_punctuation_kunddaliya"
            norm_behavior = "preserved_nfc"
            review_behavior = "standard_processing"
        elif 0x0DE6 <= cp <= 0x0DEF:
            token_category = "SINHALA_NUMBER"
            allowed_context = "sinhala_lith_digit"
            norm_behavior = "preserved_nfc"
            review_behavior = "standard_processing"
        else:
            token_category = "SINHALA_WORD"
            allowed_context = "sinhala_other"
            norm_behavior = "preserved_nfc"
            review_behavior = "context_check"

    elif 0x111E1 <= cp <= 0x111F4:
        script_or_block = "Sinhala Archaic Numbers"
        token_category = "SINHALA_NUMBER"
        allowed_context = "archaic_number"
        norm_behavior = "preserved_nfc"
        review_behavior = "context_check"

    elif 0x0030 <= cp <= 0x0039:
        script_or_block = "Basic Latin"
        token_category = "ARABIC_NUMBER"
        allowed_context = "standard_digit"
        norm_behavior = "preserved_nfc"
        review_behavior = "standard_processing"

    elif cp in (0x200D, 0x200C):
        script_or_block = "General Punctuation"
        token_category = "FORMAT_CONTROL"
        allowed_context = "allowlisted_joiner" if cp == 0x200D else "allowlisted_non_joiner"
        norm_behavior = "preserved_nfc"
        review_behavior = "context_check"

    elif cp in (0x0020, 0x00A0, 0x000A, 0x000D):
        script_or_block = "Whitespace / Controls"
        token_category = "WHITESPACE"
        allowed_context = "governed_whitespace"
        norm_behavior = "normalized_space_or_lf"
        review_behavior = "standard_processing"

    elif cp in (0x002E, 0x003F, 0x0021, 0x002C, 0x003B, 0x003A, 0x0028, 0x0029, 0x005B, 0x005D, 0x0022, 0x0027, 0x002D):
        script_or_block = "Basic Latin"
        token_category = "PUNCTUATION"
        allowed_context = "sentence_or_token_delimiter"
        norm_behavior = "preserved_nfc"
        review_behavior = "standard_processing"

    else:
        return None

    return {
        "code_point": hex_code,
        "unicode_name": uname,
        "unicode_category": category,
        "script_or_block": script_or_block,
        "token_category": token_category,
        "allowed_context": allowed_context,
        "normalization_behavior": norm_behavior,
        "review_behavior": review_behavior,
        "unicode_version": u_version
    }

def build_inventory():
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    records = []

    # 1. Sinhala block
    for cp in range(0x0D80, 0x0E00):
        rec = classify_character(cp)
        if rec:
            records.append(rec)

    # 2. Sinhala Archaic Numbers
    for cp in range(0x111E1, 0x111F5):
        rec = classify_character(cp)
        if rec:
            records.append(rec)

    # 3. Arabic digits
    for cp in range(0x0030, 0x003A):
        rec = classify_character(cp)
        if rec:
            records.append(rec)

    # 4. Joiner controls
    for cp in (0x200D, 0x200C):
        rec = classify_character(cp)
        if rec:
            records.append(rec)

    # 5. Governed whitespace
    for cp in (0x0020, 0x00A0, 0x000A, 0x000D):
        rec = classify_character(cp)
        if rec:
            records.append(rec)

    # 6. Common punctuation
    for cp in (0x002E, 0x003F, 0x0021, 0x002C, 0x003B, 0x003A, 0x0028, 0x0029, 0x005B, 0x005D, 0x0022, 0x0027, 0x002D):
        rec = classify_character(cp)
        if rec:
            records.append(rec)

    # Write JSON output
    inventory_data = {
        "inventory_id": "STAGE30-SINHALA-CHAR-INVENTORY-V1",
        "description": "Governed character inventory for Sinhala normalization, segmentation and tokenization",
        "unicode_version": unicodedata.unidata_version,
        "total_characters": len(records),
        "characters": records
    }
    JSON_OUTPUT.write_text(json.dumps(inventory_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Write CSV output
    fieldnames = [
        "code_point",
        "unicode_name",
        "unicode_category",
        "script_or_block",
        "token_category",
        "allowed_context",
        "normalization_behavior",
        "review_behavior",
        "unicode_version"
    ]
    with open(CSV_OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(r)

    print(f"Character inventory generated:")
    print(f"  JSON: {JSON_OUTPUT} ({len(records)} entries)")
    print(f"  CSV:  {CSV_OUTPUT} ({len(records)} entries)")

if __name__ == "__main__":
    build_inventory()
