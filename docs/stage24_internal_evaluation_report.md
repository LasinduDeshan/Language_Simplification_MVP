# Stage 24 — Internal English Corpus Evaluation Report

**Release Version:** 0.2.0  
**Evaluation Date:** 2026-09-30  
**Evaluation Unit:** One output per unique source group evaluated against 3 references (Mild, Moderate, Strong)  
**Total Source Groups Evaluated:** 45  
**Total Locked Test Outputs across B0–B5:** 270  

## 1. Locked Test Evaluation Results (45 Source Groups / 135 References)

| Method ID | Method Name | SARI (Overall) | SARI Add | SARI Keep | SARI Del | Corpus BLEU | FKGL Reduction (Δ) | Compression (Word) | Mean Latency | Passed Dispositions |
|---|---|---|---|---|---|---|---|---|---|---|
| **B0** | Identity Baseline | 12.27 | 0.00 | 36.82 | 0.00 | 49.72 | 0.00 | 1.00 | 3.3 µs (0.0033 ms) | 45/45 (100%) |
| **B1** | Lexical Substitution | 12.27 | 0.00 | 36.82 | 0.00 | 49.72 | 0.00 | 1.00 | 6196.3 µs (6.1963 ms) | 45/45 (100%) |
| **B2** | Sentence Splitting | 17.12 | 0.00 | 36.83 | 14.52 | 46.56 | 0.38 | 0.99 | 9232.7 µs (9.2327 ms) | 45/45 (100%) |
| **B3** | Syntactic Rules | 12.27 | 0.00 | 36.82 | 0.00 | 49.72 | 0.00 | 1.00 | 5045.2 µs (5.0452 ms) | 45/45 (100%) |
| **B4** | Combined Deterministic | 17.53 | 0.00 | 37.04 | 15.56 | 47.26 | 0.41 | 0.99 | 39568.1 µs (39.5681 ms) | 42/45 (93.3%) |
| **B5** | Existing Offline Fallback | 19.93 | 0.00 | 37.02 | 22.78 | 50.04 | 0.17 | 0.97 | 8.9 µs (0.0089 ms) | 45/45 (100%) |

## 2. B4 Disposition Accounting Breakdown
- **Passed:** 42 records (93.3%)
- **Manual Review Required:** 0 records (0.0%)
- **Failed:** 3 records (6.7%) — flagged by structural punctuation/fragment validation.
- **Quarantined:** 0 records (0.0%)
- **Accounting Balance:** $45 = 42 + 0 + 3 + 0$ (Zero Loss).
- **Metric Denominator Note:** SARI and BLEU were computed on all 45 generated outputs ($N=45$) with 42/45 passing the full structural quality gates.

## 3. Baseline Activation Coverage on Internal Locked Test Set

| Baseline | Changed Outputs | No-Change Rate | Rules Applied | Operations Reverted | Avg Operations / Changed Record | Activation Assessment |
|---|---|---|---|---|---|---|
| **B0 (Identity)** | 0 / 45 (0.0%) | 100.0% | 0 | 0 | 0.00 | Expected zero transform |
| **B1 (Lexical)** | 0 / 45 (0.0%) | 100.0% | 0 | 0 | 0.00 | Zero activation on locked test slice (lexicon vocabulary entries did not overlap locked test sentence tokens at target age <= 6) |
| **B2 (Splitting)** | 8 / 45 (17.8%) | 82.2% | 8 | 0 | 1.00 | Active structural splitting |
| **B3 (Syntax)** | 0 / 45 (0.0%) | 100.0% | 0 | 0 | 0.00 | Zero activation on locked test slice (no explicit passive agents 'by X' or nominalizations in locked test sentences) |
| **B4 (Combined)** | 8 / 45 (17.8%) | 82.2% | 8 | 0 | 1.00 | Active combined orchestration |
| **B5 (Fallback)** | 13 / 45 (28.9%) | 71.1% | 45 | 0 | 3.46 | Truncated 13 sentences > 14 words |

*Note on B1 and B3:* B1 and B3 are validated baseline architectures whose rule preconditions did not trigger on this specific 45-item locked test slice. They are reported transparently as having zero coverage on this test slice rather than demonstrated simplifications.
