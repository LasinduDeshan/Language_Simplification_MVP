# Stage 35 Model Selection and Fallback Record

**Stage:** Stage 35 — Comparative Evaluation of Gemini, mT5, and mBART for Sinhala Simplification  
**Final Decision:** `NO_MODEL_SELECTED_FROM_DRY_RUN`  
**Empirical Minimum-Gate Eligibility:** `NOT ESTABLISHED`  
**Operational Status:** `C0_RULE_BASELINE` retained pending authorized empirical evaluation  
**Child Delivery Approval:** `FALSE`  

---

## 1. Decision Rationale

Under the controlled offline simulation pipeline validation run:
1. **Real Gemini Execution (`C1`):** `NOT EXECUTED`. The simulated responses intentionally violated protected spans to verify validator rejection logic. This is an adapter and pipeline diagnostic finding, not an empirical model evaluation.
2. **Real mT5 Execution (`C2`):** `NOT ESTABLISHED`. Pinned checkpoint weights (`google/mt5-base`) were not loaded, and simulated no-op responses were returned.
3. **Real mBART Execution (`C3`):** `NOT ESTABLISHED`. Pinned checkpoint weights (`facebook/mbart-large-50-many-to-many-mmt`) were not loaded, and simulated no-op responses were returned.
4. **Empirical Gate Clearance:** Because zero empirical model responses were collected, empirical minimum-gate eligibility is `NOT ESTABLISHED` for all evaluated neural models.

---

## 2. Fallback Baseline Retention

In accordance with frozen decision policy `data/model_comparison/stage35/registry/stage35_eligibility_and_decision_thresholds.json`:
- No neural model candidate is selected or promoted.
- The sealed Stage 33 rule baseline (`C0_RULE_BASELINE`) is retained as the authoritative operational baseline for Sinhala text simplification.
- All downstream systems must continue routing simplification requests to the rule engine.
- Direct delivery to children (`approved_for_child_delivery`) remains strictly `FALSE`.
