# Stage 35 Cost, Latency, and Resource Report

**Stage:** Stage 35 — Comparative Evaluation of Gemini, mT5, and mBART for Sinhala Simplification  
**Accounting Ledger Reference:** `data/model_comparison/stage35/evaluations/stage35_accounting_summary.json`  

---

## 1. Operational Resource Accounting (Level 7)

In strict compliance with research accounting standards, simulated latency and synthetic token counts must NOT be represented as measured operational resource usage. Level 7 is formally reconciled as follows:

$$\text{Total Attempts} = 47$$
$$\text{EmpiricalUsageRecorded} = 0$$
$$\text{SimulationNotApplicable} = 47$$
$$\text{Missing} = 0$$
$$\text{Unaccounted} = 0$$

$$\text{Total Attempts (47)} = 0 \text{ EmpiricalUsageRecorded} + 47 \text{ SimulationNotApplicable} + 0 \text{ Missing}$$

---

## 2. Condition-by-Condition Operational Status

| Condition | Attempts | Execution Mode | Measured Empirical Latency | Measured Token / GPU Usage | Level 7 Status |
|---|---|---|---|---|---|
| `C0_RULE_BASELINE` | 13 | `SIMULATED_RESPONSE` | NOT_APPLICABLE | NOT_APPLICABLE | `SimulationNotApplicable` (13) |
| `C1_GEMINI_ZERO_SHOT` | 8 | `SIMULATED_RESPONSE` | NOT_APPLICABLE | NOT_APPLICABLE | `SimulationNotApplicable` (8) |
| `C2_MT5_ZERO_SHOT` | 13 | `SIMULATED_RESPONSE` | NOT_APPLICABLE | NOT_APPLICABLE | `SimulationNotApplicable` (13) |
| `C3_MBART_ZERO_SHOT` | 13 | `SIMULATED_RESPONSE` | NOT_APPLICABLE | NOT_APPLICABLE | `SimulationNotApplicable` (13) |
| **Total** | **47** | — | **0 Recorded** | **0 Recorded** | **47 SimulationNotApplicable** |

---

## 3. Empirical Cost and Latency Notice
Because live cloud API requests to Gemini were disabled during offline testing, zero financial expenditure was incurred against Google Cloud billing. Genuine GPU compute hours and inference latency across local mT5 and mBART models will be measured when live execution is authorized under genuine model weights.
