# Stage 26 ASSET External Benchmark Evaluation Report

**Stage:** Stage 26 — Pretrained Model / LLM-Based English Simplification  
**Date:** 2026-10-07 14:20:09 UTC  
**Status:** `NOT_EXECUTED`  
**Execution Policy:** Deferred to Quota Window Day 3 to prevent daily free-tier quota exhaustion during validation and locked benchmark runs.  

---

## 1. Governance & Permissions Invariants

```json
{
  "dataset_name": "ASSET",
  "license": "CC-BY-NC-4.0",
  "training_eligible": false,
  "benchmark_eligible": true,
  "approved_for_child_delivery": false,
  "requires_expert_review": true
}
```

## 2. Quota Isolation Schedule

| Quota Window | Evaluation Phase | Request Volume | Status |
| :--- | :--- | :---: | :---: |
| **Day 1** | Smoke Test & Internal Validation | 135 calls | **COMPLETED** |
| **Day 2** | Official Locked Benchmark & Clean Subset | 135 calls | **COMPLETED** |
| **Day 3** | ASSET External Benchmark (Optional) | 359 calls | **DEFERRED (NOT_EXECUTED)** |

## 3. Summary
ASSET evaluation is deferred to an independent quota allocation day. No partial aggregate metrics are reported as final results. Stage 26 internal locked benchmark freeze and validation remain authoritative.
