"""
Stage 34 — Freeze Configuration and Hashes Script (WP3)
Computes SHA-256 hashes of rubric, reason codes, and analysis plan,
freezing them into stage34_configuration.json.
"""

import hashlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_DIR = PROJECT_ROOT / "data" / "sinhala_expert_validation" / "registry"
CONFIG_FILE = REGISTRY_DIR / "stage34_configuration.json"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def freeze_configuration():
    rubric_file = REGISTRY_DIR / "rubric.json"
    reason_codes_file = REGISTRY_DIR / "reason_codes.json"
    analysis_plan_file = REGISTRY_DIR / "stage34_analysis_plan.json"

    assert rubric_file.exists(), "Missing rubric.json"
    assert reason_codes_file.exists(), "Missing reason_codes.json"
    assert analysis_plan_file.exists(), "Missing stage34_analysis_plan.json"
    assert CONFIG_FILE.exists(), "Missing stage34_configuration.json"

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    config["frozen_hashes"] = {
        "rubric_hash": compute_sha256(rubric_file),
        "reason_codes_hash": compute_sha256(reason_codes_file),
        "analysis_plan_hash": compute_sha256(analysis_plan_file),
        "consent_version_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    }
    config["configuration_frozen"] = True

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print("Stage 34 configuration frozen successfully:")
    for k, v in config["frozen_hashes"].items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    freeze_configuration()
