# Stage 24 — Internal English Corpus Evaluation Report

**Release Version:** 0.2.0  
**Evaluation Date:** 2026-09-30  
**Evaluation Unit:** One output per unique source group evaluated against 3 references (Mild, Moderate, Strong)  
**Total Source Groups Evaluated:** 45  
**Total Locked Test Outputs across B0–B5:** 270  

## 1. Locked Test Evaluation Results (45 Source Groups / 135 References)

| Method ID | Method Name | SARI (Overall) | SARI Add | SARI Keep | SARI Del | Corpus BLEU | FKGL Reduction (Δ) | Compression (Word) | Passed Dispositions |
|---|---|---|---|---|---|---|---|---|---|
| **B0** | Identity Baseline | 21.52 | 0.00 | 57.34 | 7.22 | 49.72 | 0.00 | 1.00 | 45/45 (100%) |
| **B1** | Lexical Substitution | 21.52 | 0.00 | 57.34 | 7.22 | 49.72 | 0.00 | 1.00 | 45/45 (100%) |
| **B2** | Sentence Splitting | 23.66 | 0.00 | 56.30 | 14.68 | 46.56 | 0.38 | 0.99 | 45/45 (100%) |
| **B3** | Syntactic Rules | 21.52 | 0.00 | 57.34 | 7.22 | 49.72 | 0.00 | 1.00 | 45/45 (100%) |
| **B4** | Combined Deterministic | 24.07 | 0.00 | 56.49 | 15.72 | 47.26 | 0.41 | 0.99 | 42/45 (93.3%) |
| **B5** | Existing Offline Fallback | 27.23 | 0.00 | 57.25 | 24.44 | 50.04 | 0.17 | 0.97 | 45/45 (100%) |

## 2. Key Findings
- **B4 (Combined Deterministic)** achieves the highest structural SARI (24.07) among transparent rule pipelines with a +0.41 FKGL grade-level reduction.
- **B2 (Sentence Splitting)** successfully chunks complex compounds into shorter sentences while preserving imperatives.
- **Zero Leakage:** Confirmed zero leakage across locked test set (45 source groups) and zero unaccounted outputs.
