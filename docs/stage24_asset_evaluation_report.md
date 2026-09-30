# Stage 24 — ASSET Benchmark Evaluation Report

**Dataset:** Official ASSET Test Set (359 source groups, 10 references each)  
**Evaluation Date:** 2026-09-30  
**Target Age Configuration:** Fixed Generic Age Band `4-8`  
**Meaning Validation Mode:** Automated Extractor Only  
**Total Outputs across B0–B5:** 2,154  

## 1. ASSET Benchmark Results (359 Source Groups / 3,590 References)

| Method ID | Method Name | SARI (Overall) | SARI Add | SARI Keep | SARI Del | Corpus BLEU | FKGL Reduction (Δ) | Compression (Word) | Mean Latency (ms) | Passed Rate |
|---|---|---|---|---|---|---|---|---|---|---|
| **B0** | Identity Baseline | 50.20 | 0.00 | 95.38 | 55.22 | 92.56 | 0.00 | 1.00 | 0.00 | 100.0% |
| **B1** | Lexical Substitution | 50.31 | 0.01 | 95.35 | 55.57 | 92.44 | 0.02 | 1.00 | 5.22 | 100.0% |
| **B2** | Sentence Splitting | 45.36 | 0.23 | 93.77 | 42.07 | 89.88 | 1.31 | 0.99 | 9.57 | 99.7% |
| **B3** | Syntactic Rules | 50.20 | 0.00 | 95.38 | 55.22 | 92.56 | 0.00 | 1.00 | 5.37 | 100.0% |
| **B4** | Combined Deterministic | 45.19 | 0.25 | 93.66 | 41.67 | 89.79 | 1.36 | 0.99 | 37.07 | 96.7% |
| **B5** | Existing Offline Fallback | 34.85 | 0.00 | 80.92 | 23.64 | 86.39 | 1.92 | 0.79 | 0.01 | 57.7% |

## 2. Parity & Rights Governance
- Direct EASSE mathematical parity verified: $\Delta = 0.000000$ points on 0–100 scale (well within tolerance $\Delta < 0.05$).
- Non-reconstructable metadata only released; raw ASSET text remains Git-ignored.
- Outputs are not approved for direct child delivery (`approved_for_child_delivery: false`).
