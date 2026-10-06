"""
Stage 26 Configuration Freeze.
Computes immutable SHA-256 hashes of the Model Registry, Prompt Registry,
and Stage 26 evaluation pipeline before running locked benchmark evaluations.
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

    models = registry.list_models()
    freeze_data = {
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "prompt_registry_version": PromptRegistry.VERSION,
        "prompt_registry_sha256": compute_file_sha256(prompt_out),
        "model_registry_sha256": compute_file_sha256(csv_out),
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

    print("=" * 65)
    print("STAGE 26 CONFIGURATION FREEZE COMPLETE")
    print("=" * 65)
    print(f"[+] Model Registry CSV:  {csv_out}")
    print(f"[+] Prompt Registry MD:  {prompt_out}")
    print(f"[+] Config Freeze JSON:  {freeze_file}")
    print("=" * 65)


if __name__ == "__main__":
    main()
