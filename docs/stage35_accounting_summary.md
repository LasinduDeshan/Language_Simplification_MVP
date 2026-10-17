# Stage 35 Ten-Level Zero-Loss Accounting Summary

**Stage:** Stage 35 — Comparative Evaluation of Gemini, mT5, and mBART for Sinhala Simplification  
**Ledger Reference:** `data/model_comparison/stage35/evaluations/stage35_accounting_summary.json`  
**Verdict:** `INFRASTRUCTURE_DRY_RUN_VALIDATED_EMPIRICAL_EVALUATION_NOT_ESTABLISHED`  

---

## 1. Zero-Loss Reconciled Equations (Levels 1–10)

### Level 1: Input Item Denominators
$$\text{Registered Inputs (13)} = 8 \text{ Primary Common} + 5 \text{ Local-Only} + 0 \text{ Unaccounted}$$

### Level 2: Potential Pairs and Execution Eligibility
With 13 test inputs and 4 conditions:
$$\text{Potential Condition-Input Pairs} = 13 \times 4 = 52$$
$$52 \text{ Potential Pairs} = 47 \text{ Eligible Executions} + 5 \text{ Disclosure-Blocked Pairs}$$
$$47 \text{ Eligible Executions} = 47 \text{ Started} + 0 \text{ Not Started} + 0 \text{ Unaccounted}$$

### Level 3: Execution Attempts and Simulation Reconciliation
$$47 \text{ Total Attempts} = 0 \text{ Real Provider} + 0 \text{ Real Local Model} + 47 \text{ Simulated} + 0 \text{ Cached}$$
$$\text{Empirical Responses} = 0$$
$$\text{Pipeline Test Succeeded} = 47, \quad \text{Failures} = 0, \quad \text{Unaccounted} = 0$$

### Level 4: Responses vs Terminal Failures
$$\text{Executions Started (47)} = 47 \text{ Selected Responses} + 0 \text{ Terminal Failures} + 0 \text{ Unaccounted}$$

### Level 5A: Selected Response Dispositions
$$47 \text{ Selected Responses} = 0 \text{ Valid Changed} + 39 \text{ Valid Unchanged} + 8 \text{ Rejected Protected Span} + 0 \text{ Other} + 0 \text{ Unaccounted}$$

### Level 5B: Terminal Execution Failure Dispositions
$$0 \text{ Terminal Failures} = 0 \text{ Refused} + 0 \text{ Timeout} + 0 \text{ Rate Limit} + 0 \text{ Provider Error} + 0 \text{ Local Crash} + 0 \text{ Unaccounted}$$

### Level 6: Metric Cell Accounting
$$\text{Expected Metric Cells} = 47 \times 5 = 235$$
$$235 \text{ Expected} = 235 \text{ Diagnostic Cells Computed} + 0 \text{ Eligible Comparison Cells} + 0 \text{ Missing} + 0 \text{ Unaccounted}$$

### Level 7: Operational Resource Accounting
$$47 \text{ Total Attempts} = 0 \text{ EmpiricalUsageRecorded} + 47 \text{ SimulationNotApplicable} + 0 \text{ Missing} + 0 \text{ Unaccounted}$$

### Level 8: Statistical Comparison Accounting
$$\text{Pairwise Comparisons} = \binom{4}{2} = 6$$
$$6 = 6 \text{ Dry-Run Comparison Computations} + 0 \text{ Empirical Comparisons} + 6 \text{ Comparisons Not Estimable} + 0 \text{ Unaccounted}$$

### Level 9: Condition and Stage-Level Decisions
$$\text{Registered Conditions (4)} = 1 \text{ Selected Fallback (C0)} + 1 \text{ Ineligible Critical Gate (C1)} + 2 \text{ Insufficient Effect (C2, C3)} + 0 \text{ Unaccounted}$$
- **Stage Decision:** `NO_MODEL_SELECTED_FROM_DRY_RUN`
- **Empirical Minimum-Gate Eligibility:** `NOT ESTABLISHED`
- **Retained Baseline:** `C0_RULE_BASELINE`
- **Approved for Child Delivery:** `FALSE`

### Level 10: Human Evidence Accounting
$$\text{Execution Mode} = \text{AUTOMATED\_TECHNICAL\_ONLY}$$
$$\text{Human Evaluation Status} = \text{NOT\_APPLICABLE\_AUTOMATED\_TECHNICAL\_ONLY}$$
$$\text{Stage 35 Human Assignments} = 0$$

---

## 2. Condition-by-Condition Matrix

| Level / Metric | C0 (Rule Baseline) | C1 (Gemini) | C2 (mT5) | C3 (mBART) | Total | Unaccounted |
|---|---|---|---|---|---|---|
| L1 Registered Inputs | 13 | 8 (Common) | 13 | 13 | 13 | 0 |
| L2 Executions Started | 13 | 8 | 13 | 13 | 47 | 0 |
| L2 Disclosure Blocked | 0 | 5 | 0 | 0 | 5 | 0 |
| L3 Simulated Attempts | 13 | 8 | 13 | 13 | 47 | 0 |
| L3 Real Attempts | 0 | 0 | 0 | 0 | 0 | 0 |
| L4 Selected Responses | 13 | 8 | 13 | 13 | 47 | 0 |
| L4 Terminal Failures | 0 | 0 | 0 | 0 | 0 | 0 |
| L5A Valid Responses | 13 | 0 | 13 | 13 | 39 | 0 |
| L5A Rejected Responses | 0 | 8 | 0 | 0 | 8 | 0 |
| L6 Diagnostic Cells | 65 | 40 | 65 | 65 | 235 | 0 |
| L7 Usage Recorded | 0 | 0 | 0 | 0 | 0 | 0 |
| L7 Sim Not Applicable | 13 | 8 | 13 | 13 | 47 | 0 |
