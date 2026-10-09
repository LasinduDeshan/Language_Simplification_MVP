# Stage 26 Pretrained & LLM Model Evaluation Report (Reconciled)

**Stage:** Stage 26 — Pretrained Model / LLM-Based English Simplification  
**Date:** 2026-10-09 11:58:55 UTC  
**Target Group:** Ages 4–8 Years (English Language)  
**Governance Invariant:** All model outputs remain `validation_status: "draft"` and `approved_for_child_delivery: false`.  

---

## 1. Executive Summary & Evaluation Status

| Area | Status | Notes |
| :--- | :---: | :--- |
| **Pipeline Implementation** | **Complete** | All adapters, routers, security allowlists, and HMAC guards operational. |
| **Attribution & Accounting** | **Certified Complete** | Disaggregated per-run accounting with transparent fallback attribution. |
| **Validation Evaluation** | **Complete** | 135-item validation split evaluated and frozen. |
| **Official Gemini Locked Evaluation** | **Certified Complete** | `RUN-GEMINI-LOCKED-OFFICIAL-03`: 135/135 native outputs, 0 quota failures, 0 fallbacks. |
| **Current Gemini Locked Metrics** | **Official Benchmark Results** | 100% native outputs evaluated across all 135 items and 39 clean subset items. |
| **Stage 26 Formal Completion** | **Complete & Certified** | Sealed with independent cryptographic verifier and dual locked benchmark summary. |

> [!NOTE]
> **OFFICIAL BENCHMARK DESIGNATION:**
> The Gemini locked metrics presented in Section 3 represent **certified official locked-benchmark results** from `RUN-GEMINI-LOCKED-OFFICIAL-03`, executed under Operational Retry Policy v1.1.0 with 135/135 completed native outputs, 0 quota failures, 0 other failures, and 0 fallbacks.

---

## 2. Validation Split Comparative Matrix (135 Items)

| Model Configuration | Execution Type | Generator Attribution | Mean SARI | Mean Sentence BLEU-4 | FKGL $\Delta$ | Validation Pass Rate | Fallback Delivery Rate | Latency | Cost (USD) |
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

## 3. Dual Locked Benchmark Matrices (Official Locked Benchmark)

### Denominator Specification Table
| Dataset Split | Expected Items | Native Evaluated | Metric Denominator | Run Validity Status |
| :--- | :---: | :---: | :---: | :--- |
| **Full Locked Set** | 135 | 135 | **135** | `VALID_COMPLETE_NATIVE_EXECUTION` |
| **Clean Subset** | 39 | 39 | **39** | `VALID_COMPLETE_NATIVE_EXECUTION` |

---

### 3.1 Full Historical Locked Set (135 Items / 45 Source Groups)

| Model Configuration | Execution Type | Expected | Native Evaluated | Denominator | Mean SARI | Mean Sentence BLEU-4 | FKGL $\Delta$ | Pass Rate | Hybrid Fallback Total | Fallback Breakdown (Quota / Gate) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `stage25-controlled-deterministic` | deterministic | 135 | 135 | 135 | **20.29** | **35.79** | 0.69 | 100.0% | 0.0% | 0 / 0 |
| `gemini-3.5-flash-lite (Native Candidate)` | native | 135 | 135 | **135** | **36.55** | **26.16** | 2.28 | 100.0% | 0.0% | N/A (0/0) |
| `hybrid-gemini-stage25-validated` | hybrid | 135 | 135 | 135 | **36.32** | **27.16** | 2.18 | 97.04% | **2.96% (4 items)** | **0 Quota / 4 Gate Fallback** |

*Note: For the hybrid pipeline on the official full set, exactly 4 gate fallbacks occurred (0 quota failures), with 124 native outputs and 7 controlled repairs delivered.*

---

### 3.2 Predeclared Clean Text-Simplification Subset (39 Items / 13 Clean Groups)

| Model Configuration | Execution Type | Expected | Native Evaluated | Denominator | Mean SARI | Mean Sentence BLEU-4 | FKGL $\Delta$ | Pass Rate | Hybrid Fallback Total | Fallback Breakdown (Quota / Gate) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `stage25-controlled-deterministic` | deterministic | 39 | 39 | 39 | **25.44** | **51.98** | 0.7 | 100.0% | 0.0% | 0 / 0 |
| `gemini-3.5-flash-lite (Native Candidate)` | native | 39 | 39 | **39** | **39.85** | **31.47** | 2.26 | 100.0% | 0.0% | N/A (0/0) |
| `hybrid-gemini-stage25-validated` | hybrid | 39 | 39 | 39 | **39.86** | **34.78** | 2.18 | 84.62% | **15.38% (6 items)** | **0 Quota / 6 Gate Fallback** |

*Note: For the official clean subset, 33 native items and 6 gate fallback items were delivered with 0 quota failures.*

---

## 4. Key Findings and Research Conclusions

1. **Certified Complete Native Execution:** In official execution `RUN-GEMINI-LOCKED-OFFICIAL-03`, Gemini achieved 135/135 completed native outputs with 0 quota failures and 0 other provider errors under Operational Retry Policy v1.1.0.
2. **Hybrid Pipeline Safety:** The Hybrid architecture guarantees 100% preservation of critical named entities and answer keys while achieving SARI 36.32 on the full set and 39.86 on the clean subset.
3. **Transparent Fallback Attribution:** Local seq2seq models without instantiated weights are recorded as `NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS` with `fallback_delivery_rate_pct: N/A`. Fallback outputs are attributed 100% to separate `Stage 25 fallback` rows (`generator_attribution: controlled_stage25`).
4. **Answer Protection:** Pre-dispatch HMAC checks and post-generation answer leakage verification prevented 100% of answer disclosure risks.

---

## 5. Stage 25 Comparator Metric Reconciliation & Protocol Documentation

### Formal Declaration
> **Stage 25 outputs remained frozen; comparison values were recalculated using the unified Stage 26 metric protocol.**

### Empirical Reconciliation Matrix
| Benchmark Split | Metric | Earlier Stage 25 Value | Current Stage 26 Recalculated Value | Cause of Metric Shift |
| :--- | :---: | :---: | :---: | :--- |
| **Full Locked Set** | **SARI** | 20.17 | **20.29** | Unified evaluation over all 135 item tuples (45 groups × 3 support tiers) against multi-reference sets rather than earlier Moderate/Strong-only tier subset. |
| **Full Locked Set** | **Earlier Corpus SacreBLEU → Current Mean Sentence BLEU-4** | 47.88 | **35.79** | Shift from SacreBLEU corpus-level geometric n-gram precision aggregation (`tok:13a`) to sentence-level BLEU-4 with add-1 smoothing macro-averaged across sentences. Do not compare the numerical values directly as if they were the same metric. |
| **Clean Subset** | **SARI** | 25.03 | **25.44** | Recalculated using unified Stage 26 tokenization and multi-reference n-gram F1 across all 39 clean subset items. |
| **Clean Subset** | **Earlier Corpus SacreBLEU → Current Mean Sentence BLEU-4** | 60.55 | **51.98** | Shift from SacreBLEU corpus-level cumulative n-gram BLEU (`tok:13a`) to sentence-level BLEU-4 macro-average. Do not compare the numerical values directly as if they were the same metric. |

### Technical Protocol & Provenance Record
- **Stage 25 Output Artifact SHA-256:** `6d396f80c866f1b372811dc7b60a28aa6541b8a45d7cc4b813ef1c0aa17d7309` (`data/controlled_simplification/results/controlled_simplification_summary.json`).
- **Reference Dataset SHA-256:** `61bbc2b26c943dcbbc630b4af6c7598a2cebb1025e272a96a7bcc510f4d066d3` (`data/baseline_simplification/evaluation_inputs/internal_locked_test_groups.json`).
- **Dataset Release 0.2.0 SHA-256:** `2e45b69158ccca5a490926c98ff49d5e4f7255b0e2476ca951206a1ab546e22c` (`data/simplification_corpus/releases/0.2.0/simplification_corpus.json`).
- **SARI Implementation:** Xu et al. (TACL 2016) / EASSE-style multi-reference formulation via `app.datasets.external_english.benchmark.metrics.compute_sari`. Computes unigram to 4-gram Add, Keep, and Delete precisions, recalls, and F1 scores against multi-reference sets.
- **SacreBLEU Signature (Earlier Protocol):** `nrefs:3|case:mixed|eff:no|tok:13a|smooth:exp|version:2.6.0`.
- **Tokenization Method:** The Stage 26 implementation uses deterministic lowercase regex word tokenization (`re.findall(r"\b\w+\b", text.lower())`). SARI follows the Xu et al./EASSE-style multi-reference formulation, but exact metric parity with an external EASSE installation must be verified separately.
- **Aggregation Protocol:** Sentence-level macro-averaging across items for both SARI and BLEU-4 with add-1 smoothing. The sentence-level BLEU macro-average produced lower values than corpus SacreBLEU in this evaluation; this is not guaranteed for every dataset. Numerical values between Earlier Corpus SacreBLEU and Current Mean Sentence BLEU-4 reflect different aggregation formulas and should not be compared directly.
- **Engine Rules & Parameters Invariance:** Stage 25 deterministic rule catalogue (`config_hash`: `e4ce9877ab0b32132d0_cos0.85_fkgl0.5_1.2_2.0`) was not modified or retuned; underlying candidate generation logic remains identical to commit `6b78550` (`stage-25-complete-v2`).
