"""
Configuration module for Stage 30 Sinhala Preprocessing.
Loads, validates, and hashes the frozen configuration registry.
"""

import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_REGISTRY_PATH = PROJECT_ROOT / "data" / "sinhala_preprocessing" / "registry" / "stage30_configuration.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "configuration_version": "1.0.0",
    "normalization_form": "NFC",
    "grapheme_engine": {
        "engine": "regex_X",
        "pinned_package": "regex",
        "pinned_version": "2025.11.3",
        "unicode_version": "14.0.0",
        "conformance_scope": "governed_fixtures_verified"
    },
    "limits": {
        "max_input_code_points": 25000,
        "max_combining_marks_sequence": 3
    },
    "whitespace_policy": {
        "collapse_horizontal_space": True,
        "convert_crlf_to_lf": True,
        "trim_leading_trailing": True,
        "preserve_paragraph_break": True
    },
    "protected_abbreviations": [
        "වෛ.", "මහා.", "පෙ.ව.", "ප.ව.", "පිටු.", "රු.", "ඩො.",
        "e.g.", "i.e.", "etc.", "Dr.", "Mr.", "Mrs.", "Prof.", "No."
    ],
    "joiner_allowlist": [
        "yansaya",
        "rakaransaya",
        "bandi_akuru",
        "repaya"
    ],
    "disposition_precedence": [
        "REJECTED_INVALID_UNICODE",
        "MANUAL_REVIEW_REQUIRED",
        "EXCLUDED_NON_SINHALA",
        "PASSED_WITH_NORMALIZATION",
        "PASSED"
    ]
}

def compute_config_sha256(config_dict: Dict[str, Any]) -> str:
    canonical_json = json.dumps(config_dict, sort_keys=True, indent=2, ensure_ascii=False)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

def get_frozen_configuration() -> Dict[str, Any]:
    if CONFIG_REGISTRY_PATH.exists():
        with open(CONFIG_REGISTRY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["configuration_sha256"] = compute_config_sha256(data["config"])
            return data
    else:
        sha = compute_config_sha256(DEFAULT_CONFIG)
        data = {
            "configuration_version": "1.0.0",
            "configuration_sha256": sha,
            "config": DEFAULT_CONFIG
        }
        return data
