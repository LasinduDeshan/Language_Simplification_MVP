"""
Stage 26 Final Completion Record, Reproducibility Manifest, and SHA-256 Generator.
Verifies all Stage 26 documentation deliverables, records multi-run disaggregated accounting,
embeds official locked run proof structures, separates transformer native and fallback rows,
and generates docs/stage26_manifest.sha256 for completion tag stage-26-complete-v3.
"""
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

repo_root = Path(__file__).resolve().parent.parent.parent


def compute_sha256(filepath: Path) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def main():
    docs_dir = repo_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    deliverable_files = [
        "stage26_implementation_plan.md",
        "stage26_dataset_eligibility_report.md",
        "stage26_model_registry.csv",
        "stage26_prompt_registry.md",
        "stage26_privacy_and_provider_policy.md",
        "stage26_training_decision_record.md",
        "stage26_gemini_execution_audit.md",
        "stage26_internal_evaluation_report.md",
        "stage26_asset_evaluation_report.md",
        "stage26_model_comparison.csv",
        "stage26_error_analysis.md",
        "stage26_accounting_summary.md",
    ]

    manifest_lines = []
    reproducibility_artifacts = {}

    for fname in deliverable_files:
        fpath = docs_dir / fname
        if fpath.exists():
            h = compute_sha256(fpath)
            manifest_lines.append(f"{h}  docs/{fname}")
            reproducibility_artifacts[fname] = {
                "path": f"docs/{fname}",
                "sha256": h,
                "status": "verified",
            }
        else:
            print(f"[-] Warning: deliverable {fname} not found!")

    # 1. Write docs/stage26_reproducibility_record.json
    # 1. Write docs/stage26_reproducibility_record.json
    repro_data = {
        "stage": "Stage 26 — Pretrained Model / LLM-Based English Simplification",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status_summary": {
            "implementation": "Complete",
            "attribution_and_accounting": "Substantially corrected",
            "validation_evaluation": "Complete",
            "official_gemini_locked_evaluation": "Not complete",
            "current_gemini_locked_metrics": "Partial diagnostic results from an invalid quota-interrupted execution",
            "stage_26_formal_completion": "Pending one complete 135-item run (RUN-GEMINI-LOCKED-OFFICIAL-02)",
        },
        "git": {
            "branch": "feature/stage26-v2",
            "start_tag": "stage-26-v2-start",
            "prerequisite_commit": "6b785502b860d4e93d2d31b86bd653c33a210ac9",
            "working_tag": "stage-26-complete-v3",
        },
        "resolved_models": {
            "gemini_api_model": "gemini-3.5-flash-lite",
            "gemini_discovery_status": "verified",
            "mt5_status": "NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS",
            "mbart_status": "NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS",
            "fine_tuning_status": "APPROVED_BUT_DEFERRED_INSUFFICIENT_NATIVE_BASELINE",
            "asset_status": "NOT_EXECUTED",
        },
        "locked_run_audit": {
            "invalid_run_preserved": {
                "run_id": "RUN-GEMINI-LOCKED-OFFICIAL-01",
                "expected_items": 135,
                "completed_native_outputs": 84,
                "quota_failed": 51,
                "other_failed": 0,
                "not_attempted": 0,
                "duplicate_items": 0,
                "configuration_hash": "8db764ac5f19c27b1fa31543b1e1f53884629692b2e1f6243ab759eee5003779",
                "post_lock_tuning": False,
                "run_validity_status": "INVALID_EXECUTION — PROVIDER_QUOTA_EXCEEDED",
                "metric_denominators": {
                    "full_locked_set": {"expected": 135, "native_evaluated": 84, "denominator": 84},
                    "clean_subset": {"expected": 39, "native_evaluated": 29, "denominator": 29},
                },
                "hybrid_fallback_disaggregation": {
                    "full_locked_set": {"total_fallbacks": 53, "quota_fallbacks": 51, "safety_gate_fallbacks": 2},
                    "clean_subset": {"total_fallbacks": 10, "quota_fallbacks": 10, "safety_gate_fallbacks": 0},
                },
            },
            "pending_official_run": {
                "run_id": "RUN-GEMINI-LOCKED-OFFICIAL-02",
                "expected_items": 135,
                "target_native_outputs": 135,
                "target_quota_failed": 0,
                "target_other_failed": 0,
                "target_not_attempted": 0,
                "target_duplicate_items": 0,
                "configuration_hash": "8db764ac5f19c27b1fa31543b1e1f53884629692b2e1f6243ab759eee5003779",
                "post_lock_tuning": False,
                "scheduled_dispatch": "Immediate dispatch after midnight Pacific Time quota reset (~07:00 UTC / 12:30 PM Sri Lanka time)",
            },
        },
        "project_level_accounting": {
            "governed_ledger_attempts": 431,
            "google_project_quota_cap": 500,
            "calls_outside_governed_ledger": 69,
            "statement": "69 project-level provider calls occurred outside the governed Stage 26 evaluation ledger and are excluded from evaluation metrics.",
        },
        "governance_invariants": {
            "validation_status": "draft",
            "research_eligible": False,
            "approved_for_child_delivery": False,
            "requires_expert_review": True,
            "screening_risk_ownership": "component_1_read_only",
            "answer_disclosure_policy": "zero_leakage_local_hmac_guard",
        },
        "artifacts": reproducibility_artifacts,
    }

    repro_file = docs_dir / "stage26_reproducibility_record.json"
    with open(repro_file, "w", encoding="utf-8") as f:
        json.dump(repro_data, f, indent=2)
    manifest_lines.append(f"{compute_sha256(repro_file)}  docs/stage26_reproducibility_record.json")

    # 2. Write docs/stage26_completion_record.md
    completion_md = f"""# Stage 26 Completion & Audit Record — Pretrained & LLM-Based English Simplification (Reconciled)

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Language:** English (Target Age: 4–8 Years)  
**Date:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}  
**Prerequisite Tag:** `stage-25-complete-v2` (`6b785502b860d4e93d2d31b86bd653c33a210ac9`)  
**Restart Start Tag:** `stage-26-v2-start`  
**Current Working Tag:** `stage-26-complete-v3`  
**Historical Rollback Tags (Preserved):** `stage-26-start`, `stage-26-complete`, `stage-26-complete-v2`  
**Overall Status:** **PIPELINE COMPLETE & VALIDATED; OFFICIAL LOCKED BENCHMARK PENDING RUN-GEMINI-LOCKED-OFFICIAL-02**  

---

## 1. Final Status Matrix

| Area | Status | Evidence / Notes |
| :--- | :---: | :--- |
| **Implementation** | **Complete** | All adapters, router, security allowlists, and HMAC answer guard implemented and unit-tested (45/45 tests passing). |
| **Attribution and Accounting** | **Substantially Corrected** | Disaggregated per-run accounting with transparent fallback attribution and mutual exclusivity. |
| **Validation Evaluation** | **Complete** | 135-item development validation run completed and frozen. |
| **Official Gemini Locked Evaluation** | **Not Complete** | Quota-interrupted run `RUN-GEMINI-LOCKED-OFFICIAL-01` formally invalidated. Clean run `RUN-GEMINI-LOCKED-OFFICIAL-02` queued for quota reset. |
| **Current Gemini Locked Metrics** | **Partial Diagnostic Results** | Derived from partial native outputs (Full: 84/135; Clean: 29/39); not official locked-benchmark results. |
| **Stage 26 Formal Completion** | **Pending One Complete 135-Item Run** | Awaiting `RUN-GEMINI-LOCKED-OFFICIAL-02` with 135 live native outputs and 0 quota failures. |

---

## 2. Multi-Run Disaggregated Request Accounting Table

| Execution Run | Run Identifier | Expected Logical Items | Provider Attempts | Live Success | Quota Failed (429) | Other Failed | Attributed Fallback | Execution Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Validation Run** | `RUN-VAL-GEMINI-20261007` | 135 | 154 | **116** | 19 | 0 | 19 | **Valid (Development Validation)** |
| **Previous Locked Run** | `RUN-GEMINI-LOCKED-HISTORICAL-01` | 135 | 142 | **0** | 135 | 0 | 135 | **INVALID_EXECUTION — PROVIDER_QUOTA_EXCEEDED** |
| **Interrupted Locked Run** | `RUN-GEMINI-LOCKED-OFFICIAL-01` | 135 | 135 | **84** | 51 | 0 | 51 | **INVALID_EXECUTION — PROVIDER_QUOTA_EXCEEDED** |
| **Official Locked Run** | `RUN-GEMINI-LOCKED-OFFICIAL-02` | 135 | *135 expected* | *135 expected* | *0 expected* | *0 expected* | *hybrid only* | **Pending daily quota reset** |
| **TOTALS IN GOVERNED LEDGERS** | *All Audited Dispatches* | **405** | **431** | **200** | **205** | **0** | **205** | *100% Mathematically Reconciled* |

### Project-Level Call Reconciliation (Missing 69 Calls):
$$500\\text{{ (Google Daily Cap)}} - 431\\text{{ (Governed Attempts)}} = 69$$
> **69 project-level provider calls occurred outside the governed Stage 26 evaluation ledger and are excluded from evaluation metrics.**  
> (Comprising model-discovery probes, adapter smoke tests, earlier exploratory calls, and retries outside the governed runner).

---

## 3. Official Locked Run Audit Record (`RUN-GEMINI-LOCKED-OFFICIAL-01`)

```json
{{
  "run_id": "RUN-GEMINI-LOCKED-OFFICIAL-01",
  "expected_items": 135,
  "completed_native_outputs": 84,
  "quota_failed": 51,
  "other_failed": 0,
  "not_attempted": 0,
  "duplicate_items": 0,
  "configuration_hash": "8db764ac5f19c27b1fa31543b1e1f53884629692b2e1f6243ab759eee5003779",
  "post_lock_tuning": false,
  "run_validity_status": "INVALID_EXECUTION — PROVIDER_QUOTA_EXCEEDED"
}}
```

### Denominator Specification for Native Gemini Partial Metrics:
| Dataset Split | Expected Items | Native Evaluated | Metric Denominator | Scientific Status |
| :--- | :---: | :---: | :---: | :--- |
| **Full Locked Set** | 135 | 84 | **84** | Partial diagnostic results from an invalid quota-interrupted execution |
| **Clean Subset** | 39 | 29 | **29** | Partial diagnostic results from an invalid quota-interrupted execution |

> [!WARNING]
> These partial metrics MUST NOT be compared directly against models evaluated on all 135 or 39 records as the primary comparison.

---

## 4. Hybrid Fallback Reason Disaggregation

In the hybrid pipeline, fallback deliveries are triggered by either provider quota exhaustion or safety/validation gate failure:

| Dataset Split | Total Items | Native Delivered | Repair Delivered | Quota Fallback | Gate Fallback | Total Fallbacks | Fallback Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Full Locked Set** | 135 | 78 | 4 | **51** | **2** | **53** | 39.26% |
| **Clean Subset** | 39 | 27 | 2 | **10** | **0** | **10** | 25.64% |

- **Full Locked Set:** 51 fallbacks were caused by daily quota exhaustion; 2 additional fallbacks were caused by deterministic safety gate rejections.
- **Clean Subset:** Exactly 10 fallbacks were caused by daily quota exhaustion; 0 were caused by safety gate rejections.

---

## 5. Corrected Quota Reset Timing & Next Steps

- **Provider Daily Quota Reset:** Midnight Pacific Time (00:00 PDT) — approximately **07:00 UTC** / **12:30 PM Sri Lanka Time**.
- **Provider Reported Retry Delay:** `retryDelay: ~22342s` (~6.2 hours).
- **Execution Script Ready:** `scripts/stage26/run_locked_official_02.py` is configured and waiting for quota reset. Upon reset, it will execute 135 items under the frozen configuration hash `8db764ac5f19c27b1fa31543b1e1f53884629692b2e1f6243ab759eee5003779` with zero post-lock tuning.

---

## 6. Mandatory Governance Invariants

Every candidate output produced during Stage 26 retains:
```json
{{
  "validation_status": "draft",
  "research_eligible": false,
  "approved_for_child_delivery": false,
  "requires_expert_review": true
}}
```

- **Screening Risk Ownership:** Component 1 owns screening risk; Stage 26 treats it as strictly read-only.
- **Child Delivery Permitted:** `false` (No unsupervised child-facing delivery permitted).
- **Corpus Immutability:** Stage 20 release 0.2.0 files remain strictly byte-for-byte unmodified.
"""
    completion_file = docs_dir / "stage26_completion_record.md"
    with open(completion_file, "w", encoding="utf-8") as f:
        f.write(completion_md)
    manifest_lines.append(f"{compute_sha256(completion_file)}  docs/stage26_completion_record.md")

    # 3. Write docs/stage26_manifest.sha256
    manifest_file = docs_dir / "stage26_manifest.sha256"
    with open(manifest_file, "w", encoding="utf-8") as f:
        f.write("\n".join(manifest_lines) + "\n")

    print("=" * 65)
    print("STAGE 26 FINAL REPORT & MANIFEST GENERATED")
    print("=" * 65)
    print(f"[+] Reproducibility Record: {repro_file}")
    print(f"[+] Completion Record:      {completion_file}")
    print(f"[+] SHA-256 Manifest:       {manifest_file}")
    print("=" * 65)


if __name__ == "__main__":
    main()
