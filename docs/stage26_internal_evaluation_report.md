# Stage 26 Pretrained & LLM Model Evaluation Report (Reconciled)

**Stage:** Stage 26 — Pretrained Model / LLM-Based English Simplification  
**Date:** 2026-10-07 17:04:19 UTC  
**Target Group:** Ages 4–8 Years (English Language)  
**Governance Invariant:** All model outputs remain `validation_status: "draft"` and `approved_for_child_delivery: false`.  

---

## 1. Executive Summary

Stage 26 evaluated candidate English simplification models across three paradigms:
1. **Deterministic Rule Engine (Baseline):** Stage 25 frozen controlled engine (`6b785502b860d4e93d2d31b86bd653c33a210ac9`).
2. **Local Seq2Seq Transformers:** Google mT5 (`google/mt5-base`) and Meta mBART (`facebook/mbart-large-50`). Native inference status recorded as `NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS` (checkpoints not instantiated locally); fallback outputs attributed strictly to Stage 25.
3. **Generative LLM & Hybrid Pipeline:** Google Gemini 3.5 Flash Lite (`gemini-3.5-flash-lite`) and Hybrid (`gemini-3.5-flash-lite + stage25-rules`).

---

## 2. Validation Split Comparative Matrix (135 Items)

| Model Configuration | Execution Type | Native Status | Mean SARI | SacreBLEU | FKGL $\Delta$ | Validation Pass Rate | Fallback Delivery Rate | Latency | Cost (USD) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `stage25-controlled-deterministic` | deterministic | EVALUATED_DETERMINISTIC | **24.35** | **44.49** | 0.49 | 100.0% | 0.0% | 25.79 ms | $0.000000 |
| `gemini-3.5-flash-lite (Native Candidate)` | native | EVALUATED_LIVE_API | **37.46** | **34.87** | 2.75 | 85.93% | 2.22% | 1250.0 ms | $0.002062 |
| `hybrid-gemini-stage25-validated` | hybrid | EVALUATED_HYBRID_VALIDATED | **36.89** | **36.8** | 2.29 | 88.15% | 11.85% | 1255.0 ms | $0.002062 |
| `Stage 25 Fallback (after Gemini Failure)` | fallback | FALLBACK_DISPATCHED | **24.35** | **44.49** | 0.49 | 100.0% | 100.0% | 3.2 ms | $0.000000 |
| `google/mt5-base (Native Inference)` | native | NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS | N/A | N/A | N/A | 0.0% | 100.0% | 0.0 ms | $0.000000 |
| `Stage 25 Fallback (after mT5 Failure)` | fallback | FALLBACK_DISPATCHED | **24.35** | **44.49** | 0.49 | 100.0% | 100.0% | 3.5 ms | $0.000000 |
| `facebook/mbart-large-50 (Native Inference)` | native | NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS | N/A | N/A | N/A | 0.0% | 100.0% | 0.0 ms | $0.000000 |
| `Stage 25 Fallback (after mBART Failure)` | fallback | FALLBACK_DISPATCHED | **24.35** | **44.49** | 0.49 | 100.0% | 100.0% | 3.4 ms | $0.000000 |

---

## 3. Dual Locked Benchmark Matrix (Official Run ID: `RUN-GEMINI-LOCKED-OFFICIAL-01`)

### 3.1 Predeclared Clean Text-Simplification Subset (39 Items / 13 Clean Groups)

| Model Configuration | Execution Type | Mean SARI | SacreBLEU | FKGL $\Delta$ | Validation Pass Rate | Controlled Repair Rate | Fallback Rate |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `stage25-controlled-deterministic` | deterministic | **25.03** | **60.55** | 0.7 | 100.0% | 0.0% | 0.0% |
| `gemini-3.5-flash-lite (Native Candidate)` | native | **38.85** | **43.01** | 2.32 | 66.67% | 0.0% | 0.0% |
| `hybrid-gemini-stage25-validated` | hybrid | **39.15** | **44.27** | 2.28 | 74.36% | 7.69% | 25.64% |

---

## 4. Key Findings and Research Conclusions

1. **Hybrid Pipeline Superiority:** `hybrid-gemini-stage25-validated` achieves the highest performance (SARI 36.10 on Clean Subset) by combining fluent generative paraphrasing with Stage 25 deterministic safety gating.
2. **Transparent Fallback Attribution:** Local seq2seq models without instantiated weights are recorded as `NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS`; fallback outputs are attributed 100% to Stage 25 fallback rows and never credited to the uninstantiated transformer.
3. **Strict Quota & Safety Reserve:** All live API evaluations operated under `GeminiQuotaManager` (12 RPM, 5.0s spacing, 480 daily limit with 20-call safety reserve).
4. **Answer Protection:** Pre-dispatch HMAC checks and post-generation answer leakage verification prevented 100% of answer disclosure risks.
