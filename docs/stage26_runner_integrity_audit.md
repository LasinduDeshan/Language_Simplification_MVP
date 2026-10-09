# Stage 26 Runner Integrity and Code Modification Audit

**Date / Timestamp:** 2026-10-09T00:25:00Z  
**Branch:** `feature/stage26-v2`  
**Target Execution Run:** `RUN-GEMINI-LOCKED-OFFICIAL-02`  
**Governing Standard:** Steps 2–15 of `docs/stage26_implementation_plan.md` (v2.1.0)

---

## 1. Runner Code Hashes

| Code State | Commit / File State | SHA-256 Hash |
| :--- | :--- | :--- |
| **Execution Start Hash** | Commit `168c753` (`scripts/stage26/run_locked_official_02.py`) | `a603d0a106c3d6c0637514f80b50bba76fdf79d556a47cae1f5e2c6d91e86a0b` |
| **Current Runner Hash** | Working Tree (`scripts/stage26/run_locked_official_02.py`) | `b780d383640cf356acae7a45ade87ecd0ff57c2ca374f9860913a4c8f92d9cf1` |

---

## 2. Exact Files Changed

During the execution of `RUN-GEMINI-LOCKED-OFFICIAL-02`, three repository files had modifications:

1. **`scripts/stage26/run_locked_official_02.py`**
   - Added `flush=True` and updated progress interval logging (`idx % 5 == 0`).
   - Extended preflight probe with retry logic and separate event recording (`stage26_preflight_event.json`).
   - Updated post-execution proof calculation to dynamically verify counts from completed ledger entries rather than static assignments.
   - Appended automatic regeneration of comparison tables upon verified completion.

2. **`backend/app/model_simplification/adapters/gemini_adapter.py`**
   - Recorded the exact frozen configuration hash `8db764ac5f19c27b1fa31543b1e1f53884629692b2e1f6243ab759eee5003779` in the ledger serialization instead of `"cfg_frozen_stage26"`.

3. **`scripts/stage26/generate_model_comparison.py`**
   - Added conditional logic to distinguish official 135/39 complete runs from partial quota-interrupted diagnostic runs in table row formatting.

---

## 3. Invariance Confirmation (Zero Inference Changes)

We explicitly confirm that across all files:
- **Model Inference**: 100% unchanged (`gemini-3.5-flash-lite`, temperature `0.2`, top_p `0.95`, maxOutputTokens `256`).
- **Prompt Engineering**: 100% unchanged (Prompt Registry hash `a5ae1df8457684181c117695d3cd6885a4b9d4102ab837ba0f236348a4226a85`).
- **Model Parameters**: 100% unchanged.
- **Payload Serialization**: 100% unchanged (Zero answer disclosure, PII scrubbing, privacy hashing).
- **Validation Pipeline**: 100% unchanged (Hybrid pipeline gates, repair algorithms, semantic similarity thresholds).

**Formal Statement:**
> **Only post-execution proof generation, logging cadence, and diagnostic result labeling were modified. Zero changes were made to prompt generation, inference parameters, or response validation.**

Because the active Python process executed bytecode loaded into memory at startup, and because all file modifications were strictly confined to post-execution auditing and proof generation, the active inference execution completed all 135 items without model disruption.

---

## 4. Enhanced Native Output Validation Criteria

In addition to HTTP 200, every native model output was independently validated against the following invariant:

```python
valid_native_output = (
    entry.get("http_status") == 200
    and entry.get("native_output_received") is True
    and entry.get("fallback_used") is False
    and isinstance(entry.get("output_text"), str)
    and bool(entry["output_text"].strip())
    and entry.get("finish_reason") not in {"SAFETY", "RECITATION", "BLOCKED"}
    and entry.get("resolved_model") == "gemini-3.5-flash-lite"
)
```

- Raw output text is never stored in the proof file; keyed SHA-256 hashes are recorded in `data/model_simplification/results/locked_test/run_gemini_locked_official_02_independent_proof.json`.
- Full raw evaluation outputs remain preserved in the protected result store at `data/model_simplification/results/locked_test/locked_gemini_ledger_official_02.json`.

---

## 5. Clean Subset Manifest Freezing

The clean text-simplification subset is strictly frozen against the predeclared manifest:
- **Manifest Path:** `data/model_simplification/registry/stage26_clean_subset_manifest.json`
- **Expected Items:** 39
- **Expected Source Groups:** 13
- **Manifest SHA-256:** `4a9e0f8096ca914303b94cf93a49fad7de2feec80b1a24c6fc734586051c1a8c`

Clean subset results were sliced strictly using these predeclared identifiers.

---

## 6. Independent Post-Execution Verifier Results

The independent post-execution verifier (`scripts/stage26/verify_locked_run_invariants.py`) evaluated all 135 ledger entries:

| Verification Metric | Value | Invariant Requirement | Pass / Fail |
| :--- | :--- | :--- | :--- |
| **Total Ledger Entries** | 135 | 135 | PASS |
| **Unique Logical Keys** | 135 | 135 | PASS |
| **Duplicate Items** | 0 | 0 | PASS |
| **Missing Items** | 0 | 0 | PASS |
| **Daily Quota Failures (429)** | 0 | 0 | PASS |
| **Completed Valid Native Outputs** | 132 | 135 | **FAIL (132/135)** |
| **Other / Network Failures** | 3 | 0 | **FAIL (3 items)** |
| **Clean Subset Completed Native** | 39 | 39 | PASS (39/39) |
| **Final Run Certification** | `INVALID_EXECUTION — NETWORK_OR_PROVIDER_FAILURE` | `VALID_COMPLETE_NATIVE_EXECUTION` | **GATED** |

### Failed Item Dissection (Transient Network / Provider Errors)
1. **`SRC-EN-GRA-0212_mild`** (Request `LOCKED-OFFICIAL02-067`): HTTP 500, `HTTPSConnectionPool... Read timed out. (read timeout=30)`
2. **`SRC-EN-COM-0319_moderate`** (Request `LOCKED-OFFICIAL02-113`): HTTP 503, `HTTPSConnectionPool... Read timed out. (read timeout=30)`
3. **`SRC-EN-GRA-0210_strong`** (Request `LOCKED-OFFICIAL02-130`): HTTP 503, `This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.` (UNAVAILABLE)

*Note: None of the 3 failed items belong to the 39-item clean text-simplification subset (`clean_subset_completed_native: 39/39`).*

### Strict Invariant Enforcement
Because 3 items experienced transient network/provider timeouts, the run completed with **132/135 native outputs**, failing the strict $135/135$ complete execution invariant. Per protocol, official metrics are **not** published from this run, and the run is classified as an invalid diagnostic run.
