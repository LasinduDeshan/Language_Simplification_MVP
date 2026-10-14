"""
Stage 28A — Configuration Freeze and Evaluation Manifest Generator.
Generates:
1. data/model_comparison/stage28a/registry/system_registry.json
2. data/model_comparison/stage28a/registry/input_manifest.json
3. data/model_comparison/stage28a/registry/stage28a_configuration_freeze.json
"""
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "backend"))

from app.model_comparison.registry import SYSTEM_REGISTRY
from app.model_comparison.input_repository import InputRepository
from app.model_comparison.metric_adapter import PINNED_EASSE_SPECIFICATION
from app.model_simplification.prompt_registry import PromptRegistry
from app.model_simplification.adapters.gemini_adapter import GeminiModelAdapter


def compute_str_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main():
    out_dir = repo_root / "data" / "model_comparison" / "stage28a" / "registry"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. System Registry Manifest
    systems_data = [sys_obj.model_dump() for sys_obj in SYSTEM_REGISTRY.values()]
    system_registry_path = out_dir / "system_registry.json"
    with open(system_registry_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "stage": "28A",
            "systems": systems_data,
        }, f, indent=2)
    print(f"[+] Generated {system_registry_path} with {len(systems_data)} systems")

    # 2. Input Manifest
    repo = InputRepository(repo_root)
    locked_full = repo.load_internal_locked_full()
    locked_clean = repo.load_internal_locked_clean()
    asset_test = repo.load_asset_test_split(operating_mode="generic")

    input_manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stage": "28A",
        "benchmarks": {
            "internal_locked_full": {
                "source_file": "data/baseline_simplification/evaluation_inputs/internal_locked_test_groups.json",
                "source_file_sha256": repo.compute_file_sha256(repo.internal_locked_file),
                "total_items": len(locked_full),
                "total_source_groups": 45,
                "support_tiers": ["mild", "moderate", "strong"],
                "item_ids": [it.item_id for it in locked_full],
            },
            "internal_locked_clean": {
                "source_manifest": "data/model_simplification/registry/stage26_clean_subset_manifest.json",
                "source_manifest_sha256": repo.compute_file_sha256(repo.clean_subset_manifest_file),
                "total_items": len(locked_clean),
                "total_source_groups": 13,
                "support_tiers": ["mild", "moderate", "strong"],
                "item_ids": [it.item_id for it in locked_clean],
            },
            "asset_test": {
                "source_orig_file": "data/external_english/asset/raw/asset.test.orig",
                "source_orig_sha256": repo.compute_file_sha256(repo.asset_dir / "asset.test.orig"),
                "total_items": len(asset_test),
                "operating_mode": "generic",
                "references_per_item": 10,
                "item_ids": [it.item_id for it in asset_test],
            },
        },
    }
    input_manifest_path = out_dir / "input_manifest.json"
    with open(input_manifest_path, "w", encoding="utf-8") as f:
        json.dump(input_manifest, f, indent=2)
    print(f"[+] Generated {input_manifest_path} (135 full, 39 clean, 359 asset)")

    # 3. Dynamic Gemini Discovery
    adapter = GeminiModelAdapter()
    discovery_success, discovered_model = adapter.discover_and_verify_model()
    discovery_time = datetime.now(timezone.utc).isoformat()
    # Pinned provider metadata from live discovery
    provider_version = "3.5-flash-lite-07-2026"
    print(f"[+] Dynamic Gemini Discovery: {discovered_model} ({provider_version}) at {discovery_time}")

    # 4. Pricing Snapshot
    pricing_payload = {
        "billing_surface": "Google AI Studio / Gemini Developer API Public Pricing",
        "source_url": "https://ai.google.dev/pricing",
        "retrieval_timestamp": discovery_time,
        "currency": "USD",
        "units": "per_million_tokens",
        "rates": {
            "input_price_per_million_tokens": 0.075,
            "output_price_per_million_tokens": 0.30,
        },
        "free_tier_limits": "15 RPM, 1M TPM, 1,500 RPD free usage accounted",
    }
    pricing_bytes = json.dumps(pricing_payload, sort_keys=True).encode("utf-8")
    pricing_hash = hashlib.sha256(pricing_bytes).hexdigest()
    pricing_payload["pricing_snapshot_sha256"] = pricing_hash

    # 5. Prompts and Parameters
    prompt_md = PromptRegistry.export_markdown()
    prompt_hash = compute_str_sha256(prompt_md)

    freeze_payload = {
        "freeze_timestamp": discovery_time,
        "governance_metadata": {
            "evaluation_phase": "stage_28a_preliminary_automated_comparison",
            "expert_validated": False,
            "approved_for_child_delivery": False,
            "requires_expert_review": True,
            "stage27_human_validation_status": "pending",
            "release_0_3_0_used": False,
        },
        "dynamic_provider_metadata": {
            "requested_model": "gemini-3.5-flash-lite",
            "resolved_model": discovered_model,
            "provider_model_version": provider_version,
            "discovery_timestamp": discovery_time,
            "discovery_success": discovery_success,
        },
        "pricing_snapshot": pricing_payload,
        "generation_parameters": {
            "temperature": 0.2,
            "top_p": 0.95,
            "max_output_tokens": 256,
            "decoding_strategy": "greedy_sampling",
            "random_seed": 42,
        },
        "metric_specifications": {
            "sari": PINNED_EASSE_SPECIFICATION,
            "bleu": {
                "sentence_bleu": "smoothed_bleu_4_add_1",
                "corpus_sacrebleu": "sacrebleu_corpus_bleu_standard",
            },
            "readability": "flesch_kincaid_grade_level",
        },
        "asset_operating_mode": {
            "mode": "generic",
            "tier_mixing_allowed": False,
            "redistribution_allowed": False,
            "public_export_raw_text": False,
        },
        "prompt_registry": {
            "version": PromptRegistry.VERSION,
            "sha256": prompt_hash,
        },
        "manifest_hashes": {
            "system_registry_sha256": repo.compute_file_sha256(system_registry_path),
            "input_manifest_sha256": repo.compute_file_sha256(input_manifest_path),
        },
    }

    freeze_bytes = json.dumps(freeze_payload, sort_keys=True).encode("utf-8")
    freeze_hash = hashlib.sha256(freeze_bytes).hexdigest()
    freeze_payload["configuration_freeze_sha256"] = freeze_hash

    freeze_path = out_dir / "stage28a_configuration_freeze.json"
    with open(freeze_path, "w", encoding="utf-8") as f:
        json.dump(freeze_payload, f, indent=2)

    print(f"[+] Configuration Freeze successfully saved to {freeze_path}")
    print(f"[+] Canonical Freeze SHA-256: {freeze_hash}")


if __name__ == "__main__":
    main()
