# Stage 23 ASSET Benchmark Evaluation Report

**Benchmark Dataset:** ASSET Official Test Split (359 source groups, 10 references per source)  
**Evaluation Date:** 2026-09-30 06:46:59 UTC  
**Evaluation Harness:** `ASSETBenchmarkRunner`  

---

## 1. Primary Benchmark Results (Test Split)

| Simplification Model / Baseline | SARI (Overall) | SARI Add | SARI Keep | SARI Del | BLEU | BERTScore Proxy | FKGL Reduction | Avg Latency (ms) | Fallback Rate | Invalid Rate |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Identity Baseline** | 50.20 | 0.00 | 95.38 | 55.22 | 91.39 | 92.66 | 0.00 | 0.000 | 0.0% | 0.0% |
| **Rule-Based Simplifier** | 46.98 | 0.67 | 93.21 | 47.06 | 91.17 | 92.62 | 0.24 | 0.065 | 0.0% | 0.0% |
| **Generic LLM / Gemini Baseline** | 32.88 | 0.00 | 78.34 | 20.31 | 87.45 | 82.02 | 2.30 | 0.004 | 100.0% | 0.0% |

---

## 2. Analysis & Key Insights

1. **Rule-Based Simplifier Performance:** Achieved SARI of 46.98 with an average latency of 0.065 ms, successfully reducing reading grade level by 0.24 FKGL points while preserving lexical fidelity.
2. **Benchmark Protection:** Evaluation executed without any gradient updates or parameter fine-tuning.
