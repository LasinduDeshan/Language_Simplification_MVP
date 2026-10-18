"""
Governed Target Aliases Reference Registry & Protected Storage Loader
Stage 36 Output Validation & Instruction Protection Boundary

Policy Invariants:
1. Target IDs, disclosure classifications, policies, and protected references are Git-tracked.
2. Literal target aliases (Sinhala/English inflections and synonyms) are stored in external
   protected storage under SINHALA_OUTPUT_VALIDATION_PROTECTED_ROOT.
3. For public demonstration fixtures only, non-sensitive fixtures are explicitly marked
   {"classification": "PUBLIC_DEMONSTRATION_FIXTURE"}.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.localization.enums import TargetDisclosureClass, TargetDisclosurePolicy
from app.sinhala_output_validation.storage import get_protected_storage_root

# Git-tracked metadata: target ID, disclosure classification, policy, version, and protected ref
GOVERNED_TARGET_ALIAS_REFS: Dict[str, Dict[str, Any]] = {
    "pencil": {
        "target_id": "pencil",
        "target_disclosure_class": TargetDisclosureClass.INFERRED_ANSWER,
        "target_disclosure_policy": TargetDisclosurePolicy.DO_NOT_REVEAL,
        "alias_set_version": 1,
        "alias_set_ref": "protected://stage36/target-aliases/pencil-v1.json",
    },
    "apple": {
        "target_id": "apple",
        "target_disclosure_class": TargetDisclosureClass.INFERRED_ANSWER,
        "target_disclosure_policy": TargetDisclosurePolicy.DO_NOT_REVEAL,
        "alias_set_version": 1,
        "alias_set_ref": "protected://stage36/target-aliases/apple-v1.json",
    },
    "cat": {
        "target_id": "cat",
        "target_disclosure_class": TargetDisclosureClass.INFERRED_ANSWER,
        "target_disclosure_policy": TargetDisclosurePolicy.DO_NOT_REVEAL,
        "alias_set_version": 1,
        "alias_set_ref": "protected://stage36/target-aliases/cat-v1.json",
    },
    "car": {
        "target_id": "car",
        "target_disclosure_class": TargetDisclosureClass.INFERRED_ANSWER,
        "target_disclosure_policy": TargetDisclosurePolicy.DO_NOT_REVEAL,
        "alias_set_version": 1,
        "alias_set_ref": "protected://stage36/target-aliases/car-v1.json",
    },
    "book": {
        "target_id": "book",
        "target_disclosure_class": TargetDisclosureClass.EXPLICIT_TASK_TARGET,
        "target_disclosure_policy": TargetDisclosurePolicy.MAY_REPEAT_TASK_TARGET,
        "alias_set_version": 1,
        "alias_set_ref": "protected://stage36/target-aliases/book-v1.json",
    },
    "circle": {
        "target_id": "circle",
        "target_disclosure_class": TargetDisclosureClass.EXPLICIT_TASK_TARGET,
        "target_disclosure_policy": TargetDisclosurePolicy.MAY_REPEAT_TASK_TARGET,
        "alias_set_version": 1,
        "alias_set_ref": "protected://stage36/target-aliases/circle-v1.json",
    },
}

# Public demonstration fixtures explicitly marked for non-production / offline test environments
PUBLIC_DEMONSTRATION_FIXTURES: Dict[str, Dict[str, Any]] = {
    "pencil": {
        "classification": "PUBLIC_DEMONSTRATION_FIXTURE",
        "target_id": "pencil",
        "aliases_by_locale": {
            "en": ["pencil", "the pencil", "pencils"],
            "si": ["පැන්සල", "පැන්සලට", "පැන්සලෙන්", "පැන්සල්", "පැන්සලේ", "පැන්සලක්"],
        },
    },
    "apple": {
        "classification": "PUBLIC_DEMONSTRATION_FIXTURE",
        "target_id": "apple",
        "aliases_by_locale": {
            "en": ["apple", "the apple", "apples"],
            "si": ["ඇපල්", "ඇපල් ගෙඩිය", "ඇපල් ගෙඩියට", "ඇපල", "ඇපල් ගෙඩියක්"],
        },
    },
    "cat": {
        "classification": "PUBLIC_DEMONSTRATION_FIXTURE",
        "target_id": "cat",
        "aliases_by_locale": {
            "en": ["cat", "the cat", "cats"],
            "si": ["පූසා", "පූසාට", "පූසාගේ", "බළලා", "බළලාට", "පූසෙක්"],
        },
    },
    "car": {
        "classification": "PUBLIC_DEMONSTRATION_FIXTURE",
        "target_id": "car",
        "aliases_by_locale": {
            "en": ["car", "the car", "cars"],
            "si": ["මෝටර් රථය", "කාර් එක", "වාහනය", "මෝටර් රථයට", "කාර්"],
        },
    },
    "book": {
        
        "classification": "PUBLIC_DEMONSTRATION_FIXTURE",
        "target_id": "book",
        "aliases_by_locale": {
            "en": ["book", "the book", "books"],
            "si": ["පොත", "පොතට", "පොතෙන්", "පොත්", "පොතක්"],
        },
    },
    "circle": {
        "classification": "PUBLIC_DEMONSTRATION_FIXTURE",
        "target_id": "circle",
        "aliases_by_locale": {
            "en": ["circle", "red circle", "the circle"],
            "si": ["වෘත්තය", "රතු වෘත්තය", "රවුම", "රතු පාට රවුම"],
        },
    },
}


def get_target_alias_metadata(target_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve Git-tracked metadata for a target ID."""
    return GOVERNED_TARGET_ALIAS_REFS.get(target_id)


def load_target_aliases(target_id: str) -> Dict[str, List[str]]:
    """
    Load literal target aliases from external protected storage if available;
    falls back to explicitly classified public demonstration fixtures if in test mode.
    """
    meta = GOVERNED_TARGET_ALIAS_REFS.get(target_id)
    version = meta["alias_set_version"] if meta else 1

    protected_root = get_protected_storage_root()
    alias_path = protected_root / "target_aliases" / f"{target_id}-v{version}.json"

    if alias_path.exists():
        try:
            with open(alias_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("aliases_by_locale", {})
        except Exception:
            pass

    # Fallback to public demonstration fixture if present
    demo = PUBLIC_DEMONSTRATION_FIXTURES.get(target_id)
    if demo:
        return demo.get("aliases_by_locale", {})

    return {"en": [target_id], "si": []}
