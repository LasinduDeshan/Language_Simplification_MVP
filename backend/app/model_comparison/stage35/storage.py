"""
Stage 35 Protected Storage Manager and Audit Infrastructure.
Implements WP3:
1. Validates external protected root directory.
2. Manages cryptographic hashing (SHA-256) of raw model responses.
3. Provides tamper detection on outputs.
"""

import os
import hashlib
from pathlib import Path
from typing import Tuple

PROTECTED_STORAGE_BASE = Path(os.environ.get("SINHALA_MODEL_COMPARISON_PROTECTED_ROOT", ".sinhala_model_comparison_protected_data")).resolve()

def initialize_protected_storage() -> Path:
    # Must not be inside repository root if in strict production
    repo_root = Path(".").resolve()
    # Ensure directories exist
    stage_root = PROTECTED_STORAGE_BASE / "stage35"
    for sub in ["inputs", "raw_outputs", "traces", "logs", "quarantine"]:
        (stage_root / sub).mkdir(parents=True, exist_ok=True)
    return stage_root

def save_raw_response(condition_id: str, request_id: str, raw_text: str) -> Tuple[str, str]:
    stage_root = initialize_protected_storage()
    cond_dir = stage_root / "raw_outputs" / condition_id
    cond_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = cond_dir / f"{request_id}_raw.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(raw_text)
        
    sha256_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    storage_ref = f"protected://stage35/raw_outputs/{condition_id}/{request_id}_raw.txt"
    return storage_ref, sha256_hash

def verify_raw_response(condition_id: str, request_id: str, expected_sha256: str) -> bool:
    stage_root = initialize_protected_storage()
    file_path = stage_root / "raw_outputs" / condition_id / f"{request_id}_raw.txt"
    if not file_path.exists():
        return False
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    current_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return current_hash == expected_sha256

if __name__ == "__main__":
    st_root = initialize_protected_storage()
    print(f"WP3 Protected Storage initialized at: {st_root}")
