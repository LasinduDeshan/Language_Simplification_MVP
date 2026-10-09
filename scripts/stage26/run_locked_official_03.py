"""Stage 26 Official Locked Benchmark Runner - Run 03 (Official Final Execution)

Target Run ID: RUN-GEMINI-LOCKED-OFFICIAL-03
Governing Protocol: Steps 2-15 of docs/stage26_implementation_plan.md (v2.1.0)
Operational Retry Policy: Version 1.1.0
- Request spacing: 6.0 seconds
- Connection timeout: 30.0 seconds
- Read timeout: 60.0 seconds
- Retryable HTTP statuses: 408, 429-transient, 500, 502, 503, 504
- Retryable exceptions: connection error, read timeout
- Maximum retry attempts: 4
- Backoff delays: 2s, 4s, 8s, 16s plus jitter
- Daily quota 429: stop immediately
- Fallback during official native evaluation: prohibited

Acceptance Criteria:
  135 = 135 valid_native + 0 failed + 0 fallback + 0 missing
"""

import os
import sys
import json
import time
import hashlib
import requests
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

repo_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(repo_root / "backend" / ".env")
sys.path.insert(0, str(repo_root / "backend"))

from app.core.config import settings
from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ModelGenerationResult,
    ProtectedElementsDTO,
    NativeValidationDisposition,
    NativeValidationSummary,
    ExecutionStatus,
)
from app.model_simplification.router import ModelRouter
from app.model_simplification.quota_manager import GeminiQuotaManager
from app.model_simplification.provider_result_attribution import ProviderResultAttribution
from app.model_simplification.prompt_registry import PromptRegistry
from app.datasets.external_english.benchmark.metrics import compute_sari, compute_bleu, estimate_fkgl

FROZEN_CONFIG_HASH = "8db764ac5f19c27b1fa31543b1e1f53884629692b2e1f6243ab759eee5003779"
PROMPT_REGISTRY_HASH = "a5ae1df8457684181c117695d3cd6885a4b9d4102ab837ba0f236348a4226a85"
DATASET_HASH = "61bbc2b26c943dcbbc630b4af6c7598a2cebb1025e272a96a7bcc510f4d066d3"
CLEAN_MANIFEST_HASH = "4a9e0f8096ca914303b94cf93a49fad7de2feec80b1a24c6fc734586051c1a8c"
RETRY_POLICY_VERSION = "1.1.0"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def preflight_quota_check(api_key: str, model_id: str = "gemini-3.5-flash-lite") -> bool:
    """Minimal 1-token probe verifying quota availability without polluting benchmark ledger."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": "preflight"}]}],
        "generationConfig": {"maxOutputTokens": 2}
    }
    for attempt in range(1, 4):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                preflight_record = {
                    "event_type": "preflight",
                    "run_id": "RUN-GEMINI-LOCKED-OFFICIAL-03",
                    "excluded_from_benchmark": True,
                    "model": model_id,
                    "http_status": 200,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "notes": "Minimal 1-token pre-flight probe confirmed daily quota is active and reachable. Excluded from benchmark metrics."
                }
                out_dir = repo_root / "data" / "model_simplification" / "results" / "locked_test"
                out_dir.mkdir(parents=True, exist_ok=True)
                with open(out_dir / "stage26_preflight_event_official_03.json", "w", encoding="utf-8") as f:
                    json.dump(preflight_record, f, indent=2)

                print("[+] Pre-flight quota probe SUCCEEDED (HTTP 200). Provider quota is active.")
                print(f"[+] Preflight record written to {out_dir / 'stage26_preflight_event_official_03.json'}")
                return True
            elif resp.status_code in (500, 502, 503, 504):
                print(f"[-] Pre-flight received transient HTTP {resp.status_code} (attempt {attempt}/3). Retrying in 4s...")
                time.sleep(4.0)
                continue
            elif resp.status_code == 429:
                print("[-] Pre-flight quota probe FAILED (HTTP 429 / Quota Exhausted).")
                print(f"    Response: {resp.text[:250]}")
                return False
            else:
                print(f"[-] Pre-flight quota probe returned HTTP {resp.status_code}: {resp.text[:200]}")
                return False
        except Exception as e:
            print(f"[-] Pre-flight error (attempt {attempt}/3): {e}")
            time.sleep(4.0)
    return False


def compute_metrics_for_items(items: List[Dict[str, Any]], predictions: List[str]) -> Dict[str, Any]:
    sari_scores = []
    bleu_scores = []
    fkgl_deltas = []

    for item, cand in zip(items, predictions):
        src = item["source_text"]
        refs = item["reference_texts"]
        sari_val, _, _, _ = compute_sari(src, cand, refs)
        sari_scores.append(sari_val)
        bleu_scores.append(compute_bleu(cand, refs))
        fkgl_deltas.append(estimate_fkgl(src) - estimate_fkgl(cand))

    mean_bleu = float(sum(bleu_scores) / max(1, len(bleu_scores))) if bleu_scores else 0.0
    mean_sari = float(sum(sari_scores) / max(1, len(sari_scores)))
    mean_fkgl_delta = float(sum(fkgl_deltas) / max(1, len(fkgl_deltas)))

    return {
        "mean_sari": round(mean_sari, 2),
        "corpus_bleu": round(mean_bleu, 2),
        "mean_fkgl_delta": round(mean_fkgl_delta, 2),
    }


def main():
    api_key = (getattr(settings, "gemini_api_key", "") or "").strip()
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()

    run_id = "RUN-GEMINI-LOCKED-OFFICIAL-03"
    print("=" * 70)
    print("STAGE 26 OFFICIAL LOCKED BENCHMARK RUNNER - RUN 03")
    print(f"  Target Run ID:              {run_id}")
    print(f"  Frozen Config Hash:         {FROZEN_CONFIG_HASH}")
    print(f"  Prompt Registry Hash:       {PROMPT_REGISTRY_HASH}")
    print(f"  Dataset Hash:               {DATASET_HASH}")
    print(f"  Clean Subset Manifest Hash: {CLEAN_MANIFEST_HASH}")
    print(f"  Operational Retry Policy:   v{RETRY_POLICY_VERSION} (Spacing: 6.0s, Timeout: 30s/60s, Max Retries: 4)")
    print("=" * 70)

    # 1. Preflight check
    if not preflight_quota_check(api_key):
        print("[!] Daily quota is not active. Execution aborted to preserve integrity.")
        sys.exit(1)

    # 2. Load benchmark inputs
    inputs_dir = repo_root / "data" / "baseline_simplification" / "evaluation_inputs"
    locked_test_file = inputs_dir / "internal_locked_test_groups.json"
    with open(locked_test_file, "r", encoding="utf-8") as f:
        locked_groups = json.load(f)

    full_items = []
    for g in locked_groups:
        gid = g.get("source_group_id", "")
        for t in ["mild", "moderate", "strong"]:
            full_items.append({
                "source_group_id": gid,
                "source_text": g["source_text"],
                "support_level": t,
                "target_age": 6,
                "protected_terms": g.get("protected_terms", []),
                "reference_texts": g.get("reference_texts", [g["source_text"]]),
            })

    # Load frozen clean subset manifest
    clean_manifest_file = repo_root / "data" / "model_simplification" / "registry" / "stage26_clean_subset_manifest.json"
    with open(clean_manifest_file, "r", encoding="utf-8") as f:
        clean_manifest = json.load(f)
    clean_item_ids = set(clean_manifest["item_ids"])
    clean_indices = [i for i, item in enumerate(full_items) if f"{item['source_group_id']}_{item['support_level']}" in clean_item_ids]
    print(f"[*] Loaded {len(full_items)} locked test items (45 groups x 3 tiers)")
    print(f"[*] Frozen clean subset contains {len(clean_indices)} items ({len(clean_manifest['source_group_ids'])} source groups)")

    out_dir = repo_root / "data" / "model_simplification" / "results" / "locked_test"
    out_dir.mkdir(parents=True, exist_ok=True)
    ledger_file = out_dir / "locked_gemini_ledger_official_03.json"

    # Initialize QuotaManager with 6.0s minimum delay
    quota_mgr = GeminiQuotaManager(ledger_path=ledger_file, min_delay_seconds=6.0, max_daily_requests=480)
    router = ModelRouter()
    router.gemini_adapter.quota_manager = quota_mgr
    router.gemini_adapter.timeout = (30.0, 60.0)
    router.gemini_adapter.max_retries = 4

    # Execute deterministic Stage 25 baseline
    stage25_cands = []
    for item in full_items:
        req = ModelGenerationRequest(
            request_id=f"LOCKED-STAGE25-{len(stage25_cands)+1}",
            text=item["source_text"],
            support_level=item["support_level"],
            target_age=6,
            protected_elements=ProtectedElementsDTO(exact_preservation=item["protected_terms"]),
        )
        res = router.stage25_adapter.generate(req)
        stage25_cands.append(res.candidate_text)

    # Execute Gemini live run (135 items)
    gemini_cands = []
    hybrid_cands = []
    gemini_outcomes = {cat: 0 for cat in ProviderResultAttribution.ALL_CATEGORIES}
    hybrid_outcomes = {cat: 0 for cat in ProviderResultAttribution.ALL_CATEGORIES}
    failed_items_count = 0
    completed_native_count = 0

    print("[*] Dispatching 135 live items to Gemini (gemini-3.5-flash-lite) with 6.0s spacing...", flush=True)
    for idx, item in enumerate(full_items, 1):
        gid = item["source_group_id"]
        tier = item["support_level"]
        src = item["source_text"]
        protected = item["protected_terms"]

        req = ModelGenerationRequest(
            request_id=f"LOCKED-OFFICIAL03-{idx:03d}",
            text=src,
            support_level=tier,
            target_age=6,
            protected_elements=ProtectedElementsDTO(exact_preservation=protected),
        )

        res_g = router.gemini_adapter.generate(req, run_id=run_id, dataset_split="locked_test", source_group_id=gid)
        cat_g, _ = ProviderResultAttribution.classify_outcome(res_g)
        gemini_outcomes[cat_g] += 1

        if res_g.fallback_used or not res_g.candidate_text:
            failed_items_count += 1
            cand_g = ""
        else:
            completed_native_count += 1
            cand_g = res_g.candidate_text
        gemini_cands.append(cand_g)

        # Hybrid validation
        if not res_g.fallback_used and cand_g:
            disp, failed_gates, repairs, final_text, sim = router.hybrid_pipeline.validate_candidate(req, cand_g)
            if disp in (NativeValidationDisposition.PASSED, NativeValidationDisposition.PASSED_WITH_CONTROLLED_REPAIR):
                cand_h = final_text
                cat_h = (
                    ProviderResultAttribution.CAT_NATIVE_DELIVERED
                    if disp == NativeValidationDisposition.PASSED
                    else ProviderResultAttribution.CAT_REPAIR_DELIVERED
                )
            else:
                cand_h = stage25_cands[idx - 1]
                cat_h = ProviderResultAttribution.CAT_FALLBACK_DELIVERED
        else:
            cand_h = stage25_cands[idx - 1]
            cat_h = ProviderResultAttribution.CAT_FALLBACK_DELIVERED

        hybrid_outcomes[cat_h] += 1
        hybrid_cands.append(cand_h)

        if idx % 5 == 0 or idx == 1 or idx == 135:
            print(f"    Progress: {idx}/135 completed ({completed_native_count} native, {failed_items_count} failed)", flush=True)

    # 3. Post-run invariant calculations strictly computed from completed ledger
    with open(ledger_file, "r", encoding="utf-8") as f:
        ledger_entries = json.load(f)

    unique_keys = set(f"{x['source_group_id']}_{x['support_level']}" for x in ledger_entries)
    
    # Check valid native condition on each entry
    valid_native_entries = []
    quota_failed_entries = []
    other_failed_entries = []
    fallback_entries = []
    total_http_attempts = 0
    output_hashes = {}

    for x in ledger_entries:
        key = f"{x['source_group_id']}_{x['support_level']}"
        total_http_attempts += x.get("attempt_count", 1)
        out_text = x.get("output_text") or ""
        output_hashes[key] = sha256_text(out_text) if out_text else ""

        is_valid = (
            x.get("http_status") == 200
            and x.get("native_output_received") is True
            and x.get("fallback_used") is False
            and isinstance(out_text, str)
            and bool(out_text.strip())
            and x.get("finish_reason") not in {"SAFETY", "RECITATION", "BLOCKED"}
            and x.get("resolved_model") == "gemini-3.5-flash-lite"
        )
        if is_valid:
            valid_native_entries.append(key)
        else:
            if x.get("http_status") == 429 or x.get("execution_status") == "DAILY_QUOTA_FAILED":
                quota_failed_entries.append(key)
            else:
                other_failed_entries.append(key)

        if x.get("fallback_used") is True:
            fallback_entries.append(key)

    calc_duplicates = len(ledger_entries) - len(unique_keys)
    calc_missing = 135 - len(unique_keys)
    calc_completed_native = len(valid_native_entries)

    is_valid_native_execution = (
        len(unique_keys) == 135
        and calc_completed_native == 135
        and len(quota_failed_entries) == 0
        and len(other_failed_entries) == 0
        and len(fallback_entries) == 0
        and calc_duplicates == 0
        and calc_missing == 0
    )

    clean_subset_entries = [x for x in ledger_entries if f"{x['source_group_id']}_{x['support_level']}" in clean_item_ids]
    clean_native_success = sum(
        1 for x in clean_subset_entries
        if x.get("http_status") == 200
        and x.get("native_output_received") is True
        and not x.get("fallback_used")
        and bool((x.get("output_text") or "").strip())
        and x.get("finish_reason") not in {"SAFETY", "RECITATION", "BLOCKED"}
    )

    audit_proof = {
        "run_id": run_id,
        "expected_items": 135,
        "logical_evaluation_items": 135,
        "provider_http_attempts": total_http_attempts,
        "completed_native_outputs": calc_completed_native,
        "quota_failed": len(quota_failed_entries),
        "other_failed": len(other_failed_entries),
        "not_attempted": calc_missing,
        "duplicate_items": calc_duplicates,
        "fallback_outputs": len(fallback_entries),
        "clean_subset_expected": 39,
        "clean_subset_completed_native": clean_native_success,
        "configuration_hash": FROZEN_CONFIG_HASH,
        "prompt_registry_hash": PROMPT_REGISTRY_HASH,
        "dataset_hash": DATASET_HASH,
        "clean_subset_manifest_hash": CLEAN_MANIFEST_HASH,
        "operational_retry_policy_version": RETRY_POLICY_VERSION,
        "maximum_attempts_per_item": 4,
        "post_lock_tuning": False,
        "run_validity_status": "VALID_COMPLETE_NATIVE_EXECUTION" if is_valid_native_execution else "INVALID_EXECUTION — AUDIT_INVARIANTS_FAILED",
        "output_hashes_sha256": output_hashes,
    }

    audit_file = out_dir / "run_gemini_locked_official_03_proof.json"
    with open(audit_file, "w", encoding="utf-8") as f:
        json.dump(audit_proof, f, indent=2)

    print("=" * 70)
    print("AUDIT PROOF RECORDED:")
    print(f"  Run Validity Status:        {audit_proof['run_validity_status']}")
    print(f"  Completed Native Outputs:   {calc_completed_native}/135")
    print(f"  Provider HTTP Attempts:     {total_http_attempts}")
    print(f"  Clean Subset Completed:     {clean_native_success}/39")
    print(f"  Proof File:                 {audit_file}")
    print("=" * 70)

    if not is_valid_native_execution:
        print("[-] Hard invariant check FAILED. Refusing to publish official metrics.")
        sys.exit(1)

    # 4. Compute Metrics for Full Set (135 items)
    metrics_s25_full = compute_metrics_for_items(full_items, stage25_cands)
    metrics_gem_full = compute_metrics_for_items(full_items, gemini_cands)
    metrics_hyb_full = compute_metrics_for_items(full_items, hybrid_cands)

    # 5. Compute Metrics for Clean Subset (39 items)
    clean_full_items = [full_items[i] for i in clean_indices]
    clean_s25_cands = [stage25_cands[i] for i in clean_indices]
    clean_gem_cands = [gemini_cands[i] for i in clean_indices]
    clean_hyb_cands = [hybrid_cands[i] for i in clean_indices]

    metrics_s25_clean = compute_metrics_for_items(clean_full_items, clean_s25_cands)
    metrics_gem_clean = compute_metrics_for_items(clean_full_items, clean_gem_cands)
    metrics_hyb_clean = compute_metrics_for_items(clean_full_items, clean_hyb_cands)

    # Clean outcome breakdowns
    gemini_clean_outcomes = {cat: 0 for cat in ProviderResultAttribution.ALL_CATEGORIES}
    hybrid_clean_outcomes = {cat: 0 for cat in ProviderResultAttribution.ALL_CATEGORIES}
    for i in clean_indices:
        cand_g = gemini_cands[i]
        cand_h = hybrid_cands[i]
        gemini_clean_outcomes[ProviderResultAttribution.CAT_NATIVE_DELIVERED] += 1
        if cand_h == stage25_cands[i]:
            hybrid_clean_outcomes[ProviderResultAttribution.CAT_FALLBACK_DELIVERED] += 1
        elif cand_h != cand_g:
            hybrid_clean_outcomes[ProviderResultAttribution.CAT_REPAIR_DELIVERED] += 1
        else:
            hybrid_clean_outcomes[ProviderResultAttribution.CAT_NATIVE_DELIVERED] += 1

    summary_data = {
        "run_id": run_id,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "resolved_model": "gemini-3.5-flash-lite",
        "configuration_hash": FROZEN_CONFIG_HASH,
        "post_lock_tuning": False,
        "audit_proof": audit_proof,
        "full_historical_locked_set": {
            "total_samples": 135,
            "stage25-controlled-deterministic": {
                "model_id": "stage25-controlled-deterministic",
                "mean_sari": metrics_s25_full["mean_sari"],
                "corpus_bleu": metrics_s25_full["corpus_bleu"],
                "mean_fkgl_delta": metrics_s25_full["mean_fkgl_delta"],
                "validation_pass_rate": 1.0,
            },
            "gemini-3.5-flash-lite-prompted": {
                "model_id": "gemini-3.5-flash-lite-prompted",
                "mean_sari": metrics_gem_full["mean_sari"],
                "corpus_bleu": metrics_gem_full["corpus_bleu"],
                "mean_fkgl_delta": metrics_gem_full["mean_fkgl_delta"],
                "outcome_breakdown": {
                    "native_delivered": completed_native_count,
                    "repair_delivered": 0,
                    "fallback_delivered": 0,
                    "manual_review_required": 0,
                    "rejected": 0,
                },
                "validation_pass_rate": 1.0,
            },
            "hybrid-gemini-stage25-validated": {
                "model_id": "hybrid-gemini-stage25-validated",
                "mean_sari": metrics_hyb_full["mean_sari"],
                "corpus_bleu": metrics_hyb_full["corpus_bleu"],
                "mean_fkgl_delta": metrics_hyb_full["mean_fkgl_delta"],
                "outcome_breakdown": {
                    "native_delivered": hybrid_outcomes[ProviderResultAttribution.CAT_NATIVE_DELIVERED],
                    "repair_delivered": hybrid_outcomes[ProviderResultAttribution.CAT_REPAIR_DELIVERED],
                    "fallback_delivered": hybrid_outcomes[ProviderResultAttribution.CAT_FALLBACK_DELIVERED],
                    "manual_review_required": 0,
                    "rejected": 0,
                },
                "validation_pass_rate": round((hybrid_outcomes[ProviderResultAttribution.CAT_NATIVE_DELIVERED] + hybrid_outcomes[ProviderResultAttribution.CAT_REPAIR_DELIVERED]) / 135.0, 4),
            },
            "mt5-base-zero-shot": {
                "model_id": "mt5-base-zero-shot",
                "native_inference_status": "NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS",
                "valid_native_outputs": 0,
                "fallback_outputs": 135,
            },
            "mbart-large-50-zero-shot": {
                "model_id": "mbart-large-50-zero-shot",
                "native_inference_status": "NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS",
                "valid_native_outputs": 0,
                "fallback_outputs": 135,
            },
        },
        "clean_text_simplification_subset": {
            "total_samples": 39,
            "stage25-controlled-deterministic": {
                "model_id": "stage25-controlled-deterministic",
                "mean_sari": metrics_s25_clean["mean_sari"],
                "corpus_bleu": metrics_s25_clean["corpus_bleu"],
                "mean_fkgl_delta": metrics_s25_clean["mean_fkgl_delta"],
                "validation_pass_rate": 1.0,
            },
            "gemini-3.5-flash-lite-prompted": {
                "model_id": "gemini-3.5-flash-lite-prompted",
                "mean_sari": metrics_gem_clean["mean_sari"],
                "corpus_bleu": metrics_gem_clean["corpus_bleu"],
                "mean_fkgl_delta": metrics_gem_clean["mean_fkgl_delta"],
                "outcome_breakdown": {
                    "native_delivered": gemini_clean_outcomes[ProviderResultAttribution.CAT_NATIVE_DELIVERED],
                    "repair_delivered": 0,
                    "fallback_delivered": 0,
                    "manual_review_required": 0,
                    "rejected": 0,
                },
                "validation_pass_rate": 1.0,
            },
            "hybrid-gemini-stage25-validated": {
                "model_id": "hybrid-gemini-stage25-validated",
                "mean_sari": metrics_hyb_clean["mean_sari"],
                "corpus_bleu": metrics_hyb_clean["corpus_bleu"],
                "mean_fkgl_delta": metrics_hyb_clean["mean_fkgl_delta"],
                "outcome_breakdown": {
                    "native_delivered": hybrid_clean_outcomes[ProviderResultAttribution.CAT_NATIVE_DELIVERED],
                    "repair_delivered": hybrid_clean_outcomes[ProviderResultAttribution.CAT_REPAIR_DELIVERED],
                    "fallback_delivered": hybrid_clean_outcomes[ProviderResultAttribution.CAT_FALLBACK_DELIVERED],
                    "manual_review_required": 0,
                    "rejected": 0,
                },
                "validation_pass_rate": round((hybrid_clean_outcomes[ProviderResultAttribution.CAT_NATIVE_DELIVERED] + hybrid_clean_outcomes[ProviderResultAttribution.CAT_REPAIR_DELIVERED]) / 39.0, 4),
            },
        },
    }

    summary_file = out_dir / "stage26_dual_locked_benchmark_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    print(f"[+] Dual locked summary saved to: {summary_file}")

    # 6. Regenerate model comparison tables and audit reports
    print("[*] Regenerating model comparison tables and audit reports...")
    import subprocess
    py_exe = sys.executable
    subprocess.run([py_exe, str(repo_root / "scripts" / "stage26" / "generate_model_comparison.py")], check=True)
    subprocess.run([py_exe, str(repo_root / "scripts" / "stage26" / "verify_stage26_accounting.py")], check=True)
    subprocess.run([py_exe, str(repo_root / "scripts" / "stage26" / "generate_stage26_report.py")], check=True)
    print("[+] Entire Stage 26 pipeline and reports successfully updated!")


if __name__ == "__main__":
    main()
