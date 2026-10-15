"""
Frozen Stage 31 Configuration Loader and Hash Verifier.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "sinhala_external" / "registry" / "stage31_configuration.json"
EXPECTED_CONFIG_SHA256 = "53aa0a8aa7ccc226f17107a18ee024dd85e71ad5776388650ee973a60bc1ef40"

def get_frozen_stage31_configuration() -> Dict[str, Any]:
    """Loads and cryptographically verifies the frozen Stage 31 configuration."""
    raw_bytes = CONFIG_PATH.read_bytes()
    actual_hash = hashlib.sha256(raw_bytes).hexdigest()
    if actual_hash != EXPECTED_CONFIG_SHA256:
        raise RuntimeError(
            f"Stage 31 configuration drift detected! Expected SHA-256 {EXPECTED_CONFIG_SHA256}, got {actual_hash}"
        )
    data = json.loads(raw_bytes.decode("utf-8"))
    data["configuration_sha256"] = actual_hash
    return data
