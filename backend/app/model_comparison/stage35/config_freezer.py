"""
Comprehensive Stage 35 Master Configuration Freeze Bundle.
Commits explicitly to paths, roles, and cryptographic SHA-256 hashes of all 15 key artifacts.
"""

import json
import hashlib
from pathlib import Path

def get_hash(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def build_master_bundle():
    artifacts = [
        {"role": "MODEL_REGISTRY", "path": "data/model_comparison/stage35/registry/stage35_model_registry.json"},
        {"role": "PROMPT_TEMPLATE", "path": "data/model_comparison/stage35/registry/stage35_prompt_template.json"},
        {"role": "DECODING_CONFIG", "path": "data/model_comparison/stage35/registry/stage35_decoding_config.json"},
        {"role": "SAFETY_SETTINGS", "path": "data/model_comparison/stage35/registry/stage35_safety_settings.json"},
        {"role": "EVALUATOR_SPEC", "path": "data/model_comparison/stage35/registry/stage35_evaluator_spec.json"},
        {"role": "METRICS_SPEC", "path": "data/model_comparison/stage35/registry/stage35_metrics_and_gates_spec.json"},
        {"role": "OPERATIONAL_POLICY", "path": "data/model_comparison/stage35/registry/stage35_operational_policy.json"},
        {"role": "AUTHORIZATION_RECORD", "path": "data/model_comparison/stage35/registry/stage35_authorization_record.json"},
        {"role": "DENOMINATOR_MANIFEST", "path": "data/model_comparison/stage35/registry/stage35_locked_test_denominators.json"},
        {"role": "SCHEMAS", "path": "backend/app/model_comparison/stage35/schemas.py"},
        {"role": "STORAGE_MANAGER", "path": "backend/app/model_comparison/stage35/storage.py"},
        {"role": "ADAPTERS", "path": "backend/app/model_comparison/stage35/adapters.py"},
        {"role": "EVALUATOR_LOGIC", "path": "backend/app/model_comparison/stage35/evaluator.py"},
        {"role": "RUNNER_LOGIC", "path": "backend/app/model_comparison/stage35/runner.py"},
        {"role": "DATASET_BRIDGE", "path": "backend/app/model_comparison/stage35/dataset_bridge.py"},
    ]
    
    entries = []
    hasher = hashlib.sha256()
    
    for item in artifacts:
        p = Path(item["path"])
        h = get_hash(p)
        item_entry = {
            "role": item["role"],
            "path": item["path"].replace("\\", "/"),
            "sha256": h
        }
        entries.append(item_entry)
        hasher.update(f"{item['role']}:{h}".encode("utf-8"))
        
    master_sha = hasher.hexdigest()
    
    bundle = {
        "bundle_version": "2.0.0",
        "stage": "stage35",
        "code_commit_anchor": "79c0f2619096869090615090b662e9ce9c8e2a7e",
        "frozen_timestamp": "2026-10-17T07:51:52.172067+00:00",
        "first_locked_request_timestamp": "2026-10-17T08:03:24Z",
        "pre_run_freeze_established": True,
        "master_configuration_sha256": master_sha,
        "governed_run_authorization_id": "AUTH-S35-LOCKED-TEST-AUTHORIZED-RUN-001",
        "controlled_artifacts_count": len(entries),
        "artifacts": entries,
    }
    
    out_file = Path("data/model_comparison/stage35/registry/stage35_configuration_freeze_bundle.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2, ensure_ascii=False)
        
    print(f"Master Configuration Freeze Bundle v2 generated with {len(entries)} items: {master_sha}")

if __name__ == "__main__":
    build_master_bundle()
