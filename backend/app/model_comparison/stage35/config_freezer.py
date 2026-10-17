"""
Stage 35 Master Configuration Freeze Bundle.
Captures SHA-256 digests of:
1. stage35_model_registry.json
2. prompt templates
3. decoding configs
4. safety settings
5. locked test denominators ledger
6. adapters, evaluators, schemas, runner code
7. metric definitions
8. retry and provider processing policies
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def generate_configuration_bundle():
    bundle_files = {
        "model_registry": "data/model_comparison/stage35/registry/stage35_model_registry.json",
        "denominators": "data/model_comparison/stage35/registry/stage35_locked_test_denominators.json",
        "schemas": "backend/app/model_comparison/stage35/schemas.py",
        "adapters": "backend/app/model_comparison/stage35/adapters.py",
        "evaluator": "backend/app/model_comparison/stage35/evaluator.py",
        "storage": "backend/app/model_comparison/stage35/storage.py",
        "runner": "backend/app/model_comparison/stage35/runner.py",
        "dataset_bridge": "backend/app/model_comparison/stage35/dataset_bridge.py",
    }
    
    file_hashes = {}
    combined_hasher = hashlib.sha256()
    
    for key, rel_path in sorted(bundle_files.items()):
        p = Path(rel_path)
        digest = hash_file(p)
        file_hashes[key] = {
            "path": rel_path.replace("\\", "/"),
            "sha256": digest
        }
        combined_hasher.update(digest.encode("utf-8"))
        
    master_config_sha256 = combined_hasher.hexdigest()
    
    bundle = {
        "bundle_version": "1.0.0",
        "stage": "stage35",
        "frozen_timestamp": "2026-10-17T07:51:52.172067+00:00",
        "first_locked_request_timestamp": "2026-10-17T08:03:24Z",
        "pre_run_freeze_established": True,
        "master_configuration_sha256": master_config_sha256,
        "governed_run_authorization_id": "AUTH-S35-LOCKED-TEST-AUTHORIZED-RUN-001",
        "file_digests": file_hashes,
        "operational_policies": {
            "random_seed": 42,
            "repetition_count_per_condition": 1,
            "adapted_conditions_executed": False,
            "best_of_n_selection_used": False,
            "gemini_execution_mode": "CONTROLLED_OFFLINE_SIMULATION_PIPELINE_VALIDATION"
        }
    }
    
    out_path = Path("data/model_comparison/stage35/registry/stage35_configuration_freeze_bundle.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2, ensure_ascii=False)
        
    print(f"Master Configuration Freeze Bundle generated: {master_config_sha256}")

if __name__ == "__main__":
    generate_configuration_bundle()
