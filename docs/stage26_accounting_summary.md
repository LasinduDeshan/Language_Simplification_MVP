# Stage 26 Accounting & Category Reconciliation Summary

**Stage:** Stage 26 — Pretrained Model / LLM-Based English Simplification  
**Date:** 2026-10-06 17:47:45 UTC  
**Overall Status:** `ALL RECONCILED (100% MUTUALLY EXCLUSIVE)`  

---

## 1. Accounting Invariants Verified

1. **Final Outcomes Invariant:**
   $$\text{FinalOutcomes} = \text{NativeDelivered} + \text{RepairDelivered} + \text{FallbackDelivered} + \text{ManualReviewRequired} + \text{Rejected} = \text{TotalSamples}$$
2. **Successful Draft Deliveries:**
   $$\text{SuccessfulDraftDeliveries} = \text{NativeDelivered} + \text{RepairDelivered} + \text{FallbackDelivered}$$
3. **Transparent Attribution:**
   Fallback deliveries are strictly attributed to the fallback provider (`stage25_rule_engine`) and 0 fallback outputs are credited to failed/unloaded generative providers.

---

## 2. Reconciled Run-Level Accounting Table

| Run / Model Identifier | Total Units | Native Del. | Repair Del. | Fallback Del. | Manual Review | Rejected | Sum | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `val_stage25-controlled-deterministic` | 135 | 108 | 0 | 0 | 0 | 27 | 135 | **RECONCILED** |
| `val_mt5-base-zero-shot` | 135 | 0 | 0 | 135 | 0 | 0 | 135 | **RECONCILED** |
| `val_mbart-large-50-zero-shot` | 135 | 0 | 0 | 135 | 0 | 0 | 135 | **RECONCILED** |
| `full_historical_locked_set_stage25-controlled-deterministic` | 135 | 93 | 0 | 0 | 0 | 42 | 135 | **RECONCILED** |
| `full_historical_locked_set_mt5-base-zero-shot` | 135 | 0 | 0 | 135 | 0 | 0 | 135 | **RECONCILED** |
| `full_historical_locked_set_mbart-large-50-zero-shot` | 135 | 0 | 0 | 135 | 0 | 0 | 135 | **RECONCILED** |
| `full_historical_locked_set_gemini-1.5-flash-prompted` | 135 | 79 | 5 | 49 | 0 | 2 | 135 | **RECONCILED** |
| `full_historical_locked_set_hybrid-gemini-stage25-validated` | 135 | 0 | 0 | 135 | 0 | 0 | 135 | **RECONCILED** |
| `clean_text_simplification_subset_stage25-controlled-deterministic` | 39 | 27 | 0 | 0 | 0 | 12 | 39 | **RECONCILED** |
| `clean_text_simplification_subset_mt5-base-zero-shot` | 39 | 0 | 0 | 39 | 0 | 0 | 39 | **RECONCILED** |
| `clean_text_simplification_subset_mbart-large-50-zero-shot` | 39 | 0 | 0 | 39 | 0 | 0 | 39 | **RECONCILED** |
| `clean_text_simplification_subset_gemini-1.5-flash-prompted` | 39 | 0 | 0 | 39 | 0 | 0 | 39 | **RECONCILED** |
| `clean_text_simplification_subset_hybrid-gemini-stage25-validated` | 39 | 0 | 0 | 39 | 0 | 0 | 39 | **RECONCILED** |

---

## 3. Governance Conclusion

Every audited evaluation unit reconciles with 100% mutual exclusivity. Zero output ambiguity or missing records exist across all evaluated splits.
