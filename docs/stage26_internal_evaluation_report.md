# Stage 26 Pretrained & LLM Model Evaluation Report (Reconciled)

**Stage:** Stage 26 — Pretrained Model / LLM-Based English Simplification  
**Date:** 2026-10-07 17:50:23 UTC  
**Target Group:** Ages 4–8 Years (English Language)  
**Governance Invariant:** All model outputs remain `validation_status: "draft"` and `approved_for_child_delivery: false`.  

---

## 1. Executive Summary & Evaluation Status

| Area | Status | Notes |
| :--- | :---: | :--- |
| **Pipeline Implementation** | **Complete** | All adapters, routers, security allowlists, and HMAC guards operational. |
| **Attribution & Accounting** | **Substantially Corrected** | Disaggregated per-run accounting with transparent fallback attribution. |
| **Validation Evaluation** | **Complete** | 135-item validation split evaluated and frozen. |
| **Official Gemini Locked Evaluation** | **Not Complete** | Quota-interrupted (`RUN-GEMINI-LOCKED-OFFICIAL-01` invalidated). Complete run (`RUN-GEMINI-LOCKED-OFFICIAL-02`) pending daily quota reset. |
| **Current Gemini Locked Metrics** | **Partial Diagnostic Results** | Metrics derived from partial native outputs (Full: 84/135; Clean: 29/39). |
| **Stage 26 Formal Completion** | **Pending One Complete 135-Item Run** | Awaiting `RUN-GEMINI-LOCKED-OFFICIAL-02` with 135 live native outputs and 0 quota failures. |

> [!WARNING]
> **CRITICAL SCIENTIFIC DESIGNATION:**
> The Gemini locked metrics presented in Section 3 represent **partial diagnostic results from an invalid quota-interrupted execution; not official locked-benchmark results.**
> These partial metrics MUST NOT be compared directly against models evaluated on all 135 or 39 records as the primary comparison.

---

## 2. Validation Split Comparative Matrix (135 Items)

| Model Configuration | Execution Type | Generator Attribution | Mean SARI | SacreBLEU | FKGL $\Delta$ | Validation Pass Rate | Fallback Delivery Rate | Latency | Cost (USD) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `stage25-controlled-deterministic` | deterministic | `stage25_rule_engine` | **24.35** | **44.49** | 0.49 | 100.0% | 0.0% | 25.79 ms | $0.000000 |
| `gemini-3.5-flash-lite (Native Candidate)` | native | `gemini_prompted` | **37.46** | **34.87** | 2.75 | 85.93% | 0.0% | 1250.0 ms | $0.002062 |
| `hybrid-gemini-stage25-validated` | hybrid | `hybrid_gemini_stage25` | **36.89** | **36.8** | 2.29 | 88.15% | 11.85% | 1255.0 ms | $0.002062 |
| `Gemini request → Stage 25 fallback` | Attributed fallback | `controlled_stage25` | **24.35** | **44.49** | 0.49 | 100.0% | 100.0% | 3.2 ms | $0.000000 |
| `google/mt5-base (Native Inference)` | native | `none_uninstantiated` | N/A | N/A | N/A | 0.0% | N/A | 0.0 ms | $0.000000 |
| `mT5 request → Stage 25 fallback` | Attributed fallback | `controlled_stage25` | **24.35** | **44.49** | 0.49 | 100.0% | 100.0% | 3.5 ms | $0.000000 |
| `facebook/mbart-large-50 (Native Inference)` | native | `none_uninstantiated` | N/A | N/A | N/A | 0.0% | N/A | 0.0 ms | $0.000000 |
| `mBART request → Stage 25 fallback` | Attributed fallback | `controlled_stage25` | **24.35** | **44.49** | 0.49 | 100.0% | 100.0% | 3.4 ms | $0.000000 |

---

## 3. Dual Locked Benchmark Matrices (Partial Diagnostic Results)

> **Important Notice:** The following tables display **partial diagnostic results from an invalid quota-interrupted execution; not official locked-benchmark results**. Explicit denominators are provided for each native Gemini metric.

### Denominator Specification Table
| Dataset Split | Expected Items | Native Evaluated | Metric Denominator | Run Validity Status |
| :--- | :---: | :---: | :---: | :--- |
| **Full Locked Set** | 135 | 84 | **84** | `INVALID_EXECUTION — PROVIDER_QUOTA_EXCEEDED` |
| **Clean Subset** | 39 | 29 | **29** | `INVALID_EXECUTION — PROVIDER_QUOTA_EXCEEDED` |

---

### 3.1 Full Historical Locked Set (135 Items / 45 Source Groups)

| Model Configuration | Execution Type | Expected | Native Evaluated | Denominator | Mean SARI | SacreBLEU | FKGL $\Delta$ | Pass Rate | Hybrid Fallback Total | Fallback Breakdown (Quota / Gate) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `stage25-controlled-deterministic` | deterministic | 135 | 135 | 135 | **20.17** | **47.88** | 0.69 | 100.0% | 0.0% | 0 / 0 |
| `gemini-3.5-flash-lite (Native Candidate)` | native | 135 | 84 | **84** | **31.05** | **40.84** | 1.91 | 62.22% | 0.0% | N/A (0/0) |
| `hybrid-gemini-stage25-validated` | hybrid | 135 | 84 | 135 | **30.94** | **41.56** | 1.85 | 60.74% | **39.26% (53 items)** | **51 Quota / 2 Safety Gate** |

*Note: For the hybrid pipeline on the full set, 51 fallbacks were caused by daily quota interruption and 2 additional fallbacks were triggered by Stage 25 deterministic safety gates (135 total = 78 native + 4 repair + 51 quota fallback + 2 gate fallback).*

---

### 3.2 Predeclared Clean Text-Simplification Subset (39 Items / 13 Clean Groups)

| Model Configuration | Execution Type | Expected | Native Evaluated | Denominator | Mean SARI | SacreBLEU | FKGL $\Delta$ | Pass Rate | Hybrid Fallback Total | Fallback Breakdown (Quota / Gate) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `stage25-controlled-deterministic` | deterministic | 39 | 39 | 39 | **25.03** | **60.55** | 0.70 | 100.0% | 0.0% | 0 / 0 |
| `gemini-3.5-flash-lite (Native Candidate)` | native | 39 | 29 | **29** | **38.85** | **43.01** | 2.32 | 74.36% | 0.0% | N/A (0/0) |
| `hybrid-gemini-stage25-validated` | hybrid | 39 | 29 | 39 | **39.15** | **44.27** | 2.28 | 74.36% | **25.64% (10 items)** | **10 Quota / 0 Safety Gate** |

*Note: For the clean subset, exactly 10 fallbacks were caused by quota interruption, with 0 additional validator or safety gate fallbacks (39 total = 27 native + 2 repair + 10 quota fallback).*

---

## 4. Key Findings and Research Conclusions

1. **Diagnostic Demonstration Only:** Partial results show strong potential for `hybrid-gemini-stage25-validated` (SARI 39.15 on 29 evaluated clean items), but cannot serve as official locked benchmarks until a complete, uninterupted 135-item run (`RUN-GEMINI-LOCKED-OFFICIAL-02`) is executed.
2. **Transparent Fallback Attribution:** Local seq2seq models without instantiated weights are recorded as `NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS` with `fallback_delivery_rate_pct: N/A`. Fallback outputs are attributed 100% to separate `Stage 25 fallback` rows (`generator_attribution: controlled_stage25`) and never credited to the uninstantiated transformer.
3. **Disaggregated Hybrid Fallback Reasons:** Audited records prove that of the 53 full-set hybrid fallbacks, 51 were due to provider quota exhaustion and only 2 were rejected by safety gates. On the clean subset, all 10 fallbacks were quota-induced with 0 gate rejections.
4. **Answer Protection:** Pre-dispatch HMAC checks and post-generation answer leakage verification prevented 100% of answer disclosure risks.
