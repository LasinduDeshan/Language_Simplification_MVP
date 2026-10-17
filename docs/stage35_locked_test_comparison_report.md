# Stage 35 Locked-Test Comparison Report (Dry-Run Execution)

**Stage:** Stage 35 — Comparative Evaluation of Gemini, mT5, and mBART for Sinhala Simplification  
**Execution Nature:** Controlled Offline Simulation Dry Run  
**Results Ledger Reference:** `data/model_comparison/stage35/evaluations/stage35_locked_evaluation_results.json`  
**Accounting Ledger Reference:** `data/model_comparison/stage35/evaluations/stage35_accounting_summary.json`  

---

## 1. Execution Summary and Mode Reconciliation

The Stage 35 dry run executed the full 9-level comparative pipeline across the locked test split:

$$\text{Total Attempts} = 47$$
$$\text{Real Provider Attempts} = 0$$
$$\text{Real Local-Model Attempts} = 0$$
$$\text{Simulated Attempts} = 47$$
$$\text{Cached Attempts} = 0$$
$$\text{Empirical Responses} = 0$$

All 47 executions operated under simulated offline execution modes to validate data contracts, pipeline adapters, and accounting reconciliations without consuming external API credits or requiring local GPU cluster allocation.

---

## 2. Condition-by-Condition Execution Findings

| Condition | Executions Started | Execution Mode | Valid Unchanged | Rejected Protected Span | Terminal Failures | Empirical Finding |
|---|---|---|---|---|---|---|
| `C0_RULE_BASELINE` | 13 | `SIMULATED_RESPONSE` | 13 | 0 | 0 | Deterministic pipeline baseline |
| `C1_GEMINI_ZERO_SHOT` | 8 (5 blocked) | `SIMULATED_RESPONSE` | 0 | 8 | 0 | Pipeline test outcome (not Gemini capability) |
| `C2_MT5_ZERO_SHOT` | 13 | `SIMULATED_RESPONSE` | 13 | 0 | 0 | Simulated no-op (not mT5 capability) |
| `C3_MBART_ZERO_SHOT` | 13 | `SIMULATED_RESPONSE` | 13 | 0 | 0 | Simulated no-op (not mBART capability) |
| **Total** | **47** | — | **39** | **8** | **0** | **Infrastructure Dry-Run Validated** |

---

## 3. Methodological and Capability Attestations

### 3.1 Condition C1 (Gemini)
The 8 rejected protected-span outcomes observed under Condition C1 represent a controlled pipeline test fixture intentionally introduced to verify the validator's span-preservation rejection logic. They do NOT reflect an empirical evaluation or capability limitation of Google's Gemini models.
- **Real Gemini Execution:** `NOT EXECUTED`.

### 3.2 Condition C2 (mT5)
The 13 valid-unchanged responses observed under Condition C2 represent simulated offline fallbacks. The pinned model weights (`google/mt5-base`, revision `2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f`) were not loaded into GPU memory, and genuine model inference did not run.
- **Execution Mode:** `SIMULATED_RESPONSE`.
- **Real Local Inference:** `NOT ESTABLISHED`.
- **Cached Empirical Response:** `NOT_APPLICABLE`.

### 3.3 Condition C3 (mBART)
The 13 valid-unchanged responses observed under Condition C3 represent simulated offline fallbacks. The pinned model weights (`facebook/mbart-large-50-many-to-many-mmt`, revision `e30b6cb8eb0d43a0b73cab73c7676b9863223a30`) were not loaded into GPU memory, and genuine model inference did not run.
- **Execution Mode:** `SIMULATED_RESPONSE`.
- **Real Local Inference:** `NOT ESTABLISHED`.
- **Cached Empirical Response:** `NOT_APPLICABLE`.

---

## 4. Stage Verdict and Decision
- **Stage Decision:** `NO_MODEL_SELECTED_FROM_DRY_RUN`
- **Empirical Minimum-Gate Eligibility:** `NOT ESTABLISHED`
- **Operational Baseline:** `C0_RULE_BASELINE` retained pending authorized empirical evaluation.
- **Approved for Child Delivery:** `FALSE`.
