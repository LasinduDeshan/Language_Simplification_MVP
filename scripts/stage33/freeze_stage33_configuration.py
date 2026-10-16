"""
Stage 33 — Configuration Freeze Script.
Seals the Stage 33 simplification configuration before locked evaluation.
"""

import hashlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / "data" / "sinhala_simplification" / "registry" / "stage33_configuration.json"


def freeze_configuration():
    assert CONFIG_FILE.exists(), f"Configuration file not found: {CONFIG_FILE}"
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["status"] = "FROZEN_FOR_LOCKED_EVALUATION"
    data["frozen_at"] = "2026-10-16T14:00:00Z"
    data["sealed_by"] = "REV-GOV-01"

    config_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
    config_sha = hashlib.sha256(config_bytes).hexdigest()
    data["configuration_sha256"] = config_sha

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Stage 33 configuration successfully frozen and sealed.")
    print(f"Configuration SHA256: {config_sha}")


if __name__ == "__main__":
    freeze_configuration()
