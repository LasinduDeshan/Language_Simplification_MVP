# Stage 23 ASSET Benchmark Evaluation Report

**Benchmark Dataset:** ASSET Official Test Split (359 source groups, 10 references per source)  
**Evaluation Date:** 2026-09-30 07:06:53 UTC  
**Evaluation Harness:** `ASSETBenchmarkRunner`  

---

## 1. Primary Benchmark Results (Test Split)

| System / Method | Evaluated Outputs | Status | SARI (Overall) | SARI Add | SARI Keep | SARI Del | BLEU | Semantic Similarity Proxy | FKGL Reduction | Avg Latency (ms) | Fallback Rate |
|---|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Identity baseline** | 359 | Valid | 50.20 | 0.00 | 95.38 | 55.22 | 91.39 | 92.66 | 0.00 | 0.000 | 0.0% |
| **Rule-based simplifier** | 359 | Valid | 46.98 | 0.67 | 93.21 | 47.06 | 91.17 | 92.62 | 0.24 | 0.065 | 0.0% |
| **Gemini LLM** | 0 | Not evaluated—API unavailable/offline | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| **Deterministic offline fallback** | 359 | Valid fallback baseline | 32.88 | 0.00 | 78.34 | 20.31 | 87.45 | 82.02 | 2.30 | 0.003 | 100.0% |

---

## 2. Provider Evaluation Attribution

```json
{
  "evaluated_outputs": 0,
  "evaluation_status": "Not evaluated\u2014API unavailable/offline",
  "requested_provider": "gemini",
  "provider_calls_attempted": 0,
  "provider_outputs_received": 0,
  "fallback_outputs_generated": 359,
  "provider_evaluation_status": "not_evaluated_offline",
  "metrics_attributed_to": "deterministic_fallback",
  "sari": null,
  "bleu": null,
  "semantic_similarity_proxy": null,
  "fkgl_reduction": null,
  "avg_latency_ms": null
}
```

---

## 3. Metric Definitions & Reproducibility Specifications

1. **SARI Metric Formulation (Xu et al., TACL 2016 / EASSE standard):**
   - Implements multi-reference 1-gram to 4-gram Add, Keep, and Delete arithmetic mean.
   - Evaluated against all 10 references per source sentence.
2. **Semantic Similarity Proxy Specification:**
   - **Algorithm:** Maximum token-level harmonic F1 overlap against reference sets.
   - **Scale:** [0, 100].
   - **Limitations:** Lexical unigram harmonic similarity; does not compute RoBERTa-large contextual embeddings; cannot be compared directly with published BERTScore results.
3. **EASSE Direct Evaluation Command:**
   ```powershell
   easse evaluate `
     -t custom `
     -m sari bleu fkgl `
     --orig_sents_path data/external_english/asset/raw/asset.test.orig `
     --refs_sents_paths data/external_english/asset/raw/asset.test.simp.0 data/external_english/asset/raw/asset.test.simp.1 data/external_english/asset/raw/asset.test.simp.2 data/external_english/asset/raw/asset.test.simp.3 data/external_english/asset/raw/asset.test.simp.4 data/external_english/asset/raw/asset.test.simp.5 data/external_english/asset/raw/asset.test.simp.6 data/external_english/asset/raw/asset.test.simp.7 data/external_english/asset/raw/asset.test.simp.8 data/external_english/asset/raw/asset.test.simp.9 `
     --sys_sents_path <system-output>
   ```
