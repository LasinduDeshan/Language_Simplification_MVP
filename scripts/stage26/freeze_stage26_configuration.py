"""
Stage 26 Configuration Freeze.
Freezes model registry, prompt templates, generation parameters, validation thresholds,
routing rules, clean subset manifests, and Stage 25 comparator hashes into an immutable JSON artifact.
"""
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "backend"))

from app.model_simplification.registry import ModelRegistry
from app.model_simplification.prompt_registry import PromptRegistry


def compute_file_sha256(filepath: Path) -> str:
    if not filepath.exists():
        return ""
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def main():
    registry = ModelRegistry()
    csv_out = repo_root / "docs" / "stage26_model_registry.csv"
    registry.export_csv(csv_out)

    prompt_out = repo_root / "docs" / "stage26_prompt_registry.md"
    with open(prompt_out, "w", encoding="utf-8") as f:
        f.write(PromptRegistry.export_markdown())

    manifest_file = repo_root / "data" / "model_simplification" / "registry" / "stage26_training_eligibility_manifest.json"

    models = registry.list_models()
    freeze_data = {
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "resolved_model_id": "gemini-3.5-flash-lite",
        "prompt_registry_version": PromptRegistry.VERSION,
        "prompt_registry_sha256": compute_file_sha256(prompt_out),
        "model_registry_sha256": compute_file_sha256(csv_out),
        "clean_manifest_sha256": compute_file_sha256(manifest_file),
        "generation_parameters": {
            "temperature": 0.2,
            "max_output_tokens": 256,
            "decoding_strategy": "greedy_sampling",
        },
        "validation_thresholds": {
            "similarity_threshold": 0.85,
            "max_sentence_length_mild": 20,
            "max_sentence_length_moderate": 15,
            "max_sentence_length_strong": 10,
        },
        "retry_policy": {
            "max_retries": 3,
            "initial_backoff_seconds": 2.0,
            "rate_limit_rpm": 12,
            "min_request_delay_seconds": 5.0,
            "daily_quota_max": 480,
            "daily_safety_reserve": 20,
        },
        "fallback_policy": {
            "fallback_provider": "stage25_rule_engine",
            "attribution_mode": "explicit_separate_accounting",
            "fallback_on_429": True,
            "fallback_on_rejection": True,
        },
        "stage25_comparator_commit": "6b785502b860d4e93d2d31b86bd653c33a210ac9",
        "registered_models": [
            {
                "model_id": m.model_id,
                "provider": m.provider,
                "repo_or_endpoint": m.repo_or_endpoint,
                "intended_mode": m.intended_mode,
                "config_hash": m.config_hash,
            }
            for m in models
        ],
    }

    freeze_file = repo_root / "data" / "model_simplification" / "registry" / "stage26_configuration_freeze.json"
    freeze_file.parent.mkdir(parents=True, exist_ok=True)
    with open(freeze_file, "w", encoding="utf-8") as f:
        json.dump(freeze_data, f, indent=2)

    freeze_hash = compute_file_sha256(freeze_file)

    print("=" * 65)
    print("STAGE 26 CONFIGURATION FREEZE COMPLETE")
    print("=" * 65)
    print(f"[+] Model Registry CSV:     {csv_out}")
    print(f"[+] Prompt Registry MD:     {prompt_out}")
    print(f"[+] Config Freeze JSON:     {freeze_file}")
    print(f"[+] Config Freeze SHA-256:  {freeze_hash}")
    print("=" * 65)


if __name__ == "__main__":
    main()
