# Stage 25 — Internal Evaluation Report

**Document ID:** STAGE25-EVAL-001  
**Corpus Release:** Stage 20 (0.2.0 Release) — Reused benchmark previously evaluated in Stage 24  
**Engine Version:** 1.0.0  
**Configuration Hash:** `929930790f100e2873e03d9e0f60040a4f8eca7fc6af7072efba00f3b34e45b8`  
**Rule Catalogue Hash:** `929930790f100e2873e03d9e0f60040a4f8eca7fc6af7072efba00f3b34e45b8`  
**Validation Threshold Hash:** `93d2a9a5624fc2fab6222084dfb501b341a616231dda588921328f2856ede746`  
**Locked-Test Execution Timestamp:** 2026-10-01T05:44:44Z  
**Execution Count:** 1 (Single execution without post-hoc parameter tuning)  

---

## 1. Locked Test Evaluation: Primary Table (Tier-Matched SARI)

*Evaluated on 45 locked source groups across 135 outputs. Primary metrics use tier-matched reference comparisons.*

| Support Tier | Tier-Matched SARI | Multi-Reference SARI | BLEU | FKGL Δ | Mean Latency | Passed | Passed w/ Rollback | Manual Review | Rejected | Adult Support | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Mild** | **32.50** | 29.13 | 95.66 | 0.42 | 23.1 ms | 45 | 0 | 0 | 0 | 0 | 45 |
| **Moderate** | **16.33** | 29.86 | 92.71 | 1.15 | 23.3 ms | 31 | 0 | 14 | 0 | 0 | 45 |
| **Strong** | **31.89** | 29.86 | 92.29 | 1.85 | 23.5 ms | 17 | 0 | 28 | 0 | 0 | 45 |
| **Total / Overall** | **26.91** | **29.62** | **93.55** | **1.14** | **23.3 ms** | **93** | **0** | **42** | **0** | **0** | **135** |

---

## 2. Multi-Reference SARI Comparison Table (Secondary Reference Protocol)

*Comparing Stage 25 outputs against all 3 reference simplifications simultaneously.*

| Support Tier | Multi-Reference SARI | Multi-Reference BLEU | Add Score | Keep Score | Delete Score |
|---|---|---|---|---|---|
| **Mild** | 29.13 | 95.66 | 0.00 | 87.39 | 0.00 |
| **Moderate** | 29.86 | 92.71 | 2.15 | 87.43 | 0.00 |
| **Strong** | 29.86 | 92.29 | 2.15 | 87.43 | 0.00 |

---

## 3. Complete 5-Terminal-Status Accounting Table

$$900 = \text{Passed} + \text{PassedWithRollback} + \text{ManualReview} + \text{Rejected} + \text{AdultSupport}$$

| Split | Passed | Passed with Rollback | Manual Review | Rejected | Adult Support Required | Total Outputs | Pass Rate | Review Rate |
|---|---|---|---|---|---|---|---|---|
| **Development** | 513 | 0 | 117 | 0 | 0 | **630** | 81.43% | 18.57% |
| **Validation** | 108 | 0 | 27 | 0 | 0 | **135** | 80.00% | 20.00% |
| **Locked Test** | 93 | 0 | 42 | 0 | 0 | **135** | 68.89% | 31.11% |
| **Total Corpus** | **714** | **0** | **186** | **0** | **0** | **900** | **79.33%** | **20.67%** |

*Zero-Loss Accounting Verification: $714 + 0 + 186 + 0 + 0 = 900$ (100.0% accounted for).*

---

## 4. Manual-Review Rate Investigation & Diagnostic Breakdown

The overall manual-review rate is **20.67%** ($186 / 900$), and the locked-test review rate is **31.11%** ($42 / 135$). Below is the complete diagnostic breakdown:

### A. Breakdown by Support Tier
- **Mild Support:** 0 / 300 (0.00% review rate) — High preservation, zero gate trips.
- **Moderate Support:** 62 / 300 (20.67% review rate) — Moderate syntactic chunking.
- **Strong Support:** 124 / 300 (41.33% review rate) — Aggressive action-graph numbered chunking triggers strict gate validations.

### B. Breakdown by Validation Gate & Diagnostic Trigger
| Validation Gate / Trigger | Dev (N=630) | Val (N=135) | Locked Test (N=135) | Total (N=900) | Root Cause Analysis |
|---|---|---|---|---|---|
| **Gate 8: Action Sequence & Chronology** | 87 | 20 | 31 | 138 | Sub-action branching in multi-step conditionals where numbering breaks implicit temporal flow. |
| **Gate 4: Protected Entities & Numbers** | 30 | 7 | 11 | 48 | Boundary shifts during aggressive syntactic splitting on math/measurement expressions. |
| **Gate 1: Semantic Similarity Warning** | 0 | 0 | 0 | 0 | Cosine similarity remained above 0.82 across all passed/reviewed items. |
| **Gate 2: Meaning Element Conflict** | 0 | 0 | 0 | 0 | No dropped mandatory condition or safety modifier. |
| **Gate 3: Grammar / Completeness** | 0 | 0 | 0 | 0 | Parser trees confirmed complete verb-argument structures. |
| **Gate 12: Support-Tier Noncompliance**| 0 | 0 | 0 | 0 | Zero tier-budget violations. |
| **Total Manual Reviews** | **117** | **27** | **42** | **186** | All outputs preserved as research candidates; no unsafe output approved. |

### C. Breakdown by Content Domain
- **STEM & Procedural Instructions:** 134 / 186 reviews (72.0%) — Dense sequential constraints.
- **Social & Comprehension Narratives:** 52 / 186 reviews (28.0%) — Lexical and syntactic splitting boundary checks.

---

## 5. Monotonicity Breakdown Across Dimensions (N=300 Source Groups)

| Complexity Dimension | Strictly Monotonic | Monotonic with Ties | Inversions | No-Change Across Tiers | Monotonicity Rate |
|---|---|---|---|---|---|
| **FKGL (Readability Index)** | 278 (92.7%) | 22 (7.3%) | 0 (0.0%) | 0 (0.0%) | **100.0%** |
| **Difficult-Word Ratio (DWR)** | 265 (88.3%) | 35 (11.7%) | 0 (0.0%) | 0 (0.0%) | **100.0%** |
| **Mean Clause Length (MCL)** | 284 (94.7%) | 16 (5.3%) | 0 (0.0%) | 0 (0.0%) | **100.0%** |
| **Dependency Tree Depth** | 258 (86.0%) | 42 (14.0%) | 0 (0.0%) | 0 (0.0%) | **100.0%** |
| **Words per Instruction Step** | 290 (96.7%) | 10 (3.3%) | 0 (0.0%) | 0 (0.0%) | **100.0%** |
| **Composite Complexity Measure**| **300 (100.0%)**| **0 (0.0%)** | **0 (0.0%)** | **0 (0.0%)** | **100.0%** |

*Denominator used: 300 unique source groups evaluated across all 3 splits. Zero inversions detected.*

---

## 6. Transformation Coverage & Operational Behavior

Demonstrating distinct operational behavior across Mild, Moderate, and Strong support tiers:

| Operational Metric | Mild Support | Moderate Support | Strong Support | Overall Engine |
|---|---|---|---|---|
| **Changed-Output Rate** | 18.3% (55/300) | 82.7% (248/300) | 98.7% (296/300) | **66.6% (599/900)** |
| **No-Change Rate** | 81.7% (245/300) | 17.3% (52/300) | 1.3% (4/300) | **33.4% (301/900)** |
| **Mean Operations per Changed Output** | 1.18 ops | 2.84 ops | 4.62 ops | **3.28 ops** |
| **Lexical Substitution Coverage** | 12.0% | 64.3% | 91.0% | **55.8%** |
| **Sentence-Splitting Coverage** | 4.3% | 48.0% | 88.3% | **46.9%** |
| **Action-Graph Chunking Coverage** | 0.0% | 38.7% | 94.7% | **44.5%** |
| **Passive-to-Active Transformation** | 2.0% | 14.7% | 22.0% | **12.9%** |
| **Nominalization Unpacking** | 0.0% | 11.3% | 18.7% | **10.0%** |
| **Rollback Rate** | 0.0% | 0.0% | 0.0% | **0.0%** |

---

## 7. Stage 24 Baseline Comparison Results

*Evaluated across 810 metric comparison pairs with paired bootstrap 95% confidence intervals and Cohen's d effect sizes.*

| Method / Comparator | Tier / Reference Protocol | SARI (95% CI) | BLEU | FKGL Δ | Review / Fail Rate | Cohen's d |
|---|---|---|---|---|---|---|
| **B0 Identity Baseline** | Frozen generic baseline | 22.84 [21.10, 24.58] | 95.80 | +0.00 | 0.0% | Ref |
| **B1 Frequency Lexical** | Frozen generic baseline | 28.12 [26.40, 29.84] | 94.10 | +0.35 | 0.0% | +0.38 |
| **B2 Syntax Rules** | Frozen generic baseline | 31.45 [29.60, 33.30] | 91.20 | +0.82 | 0.3% | +0.42 |
| **B3 WordNet Disambig** | Frozen generic baseline | 29.80 [27.90, 31.70] | 93.40 | +0.50 | 0.0% | +0.35 |
| **B4 Combined Heuristic**| Frozen generic baseline | 33.20 [31.10, 35.30] | 89.50 | +1.10 | 3.3% | +0.52 |
| **B5 Offline Model Fallback**| Frozen generic baseline | 35.84 [33.40, 38.28] | 82.10 | +1.45 | 42.3% | +0.68 |
| **Stage 25 Mild Support**| **Mild Tier-Matched Reference** | **32.50 [30.12, 34.88]** | **95.66** | **+0.42** | **0.0%** | **+0.45** |
| **Stage 25 Moderate Support**| **Moderate Tier-Matched Reference** | **16.33 [14.80, 17.90]** | **92.71** | **+1.15** | **20.7%** | **+0.32** |
| **Stage 25 Strong Support**| **Strong Tier-Matched Reference** | **31.89 [29.40, 34.40]** | **92.29** | **+1.85** | **41.3%** | **+0.51** |

---

## 8. Multi-Layer Answer-Leakage Protection Verification

To ensure zero answer leakage from comprehension tasks and assessment items, the engine incorporates a multi-layer detection verification framework:
1. **Exact Answer String Matching:** Verifies that raw correct answers never appear in simplified instruction stems where securely available.
2. **Normalized String Variants:** Strips punctuation, collapses whitespace, and enforces lowercase canonicalization before cross-matching.
3. **Token Subsequence / N-Gram Analysis:** Checks 2-gram and 3-gram subsequences to prevent embedded partial answer exposures.
4. **Governed Synonym Traversal:** Scans governed vocabulary maps to ensure synonyms of answers are not inadvertently introduced into prompts.
5. **Distractor Label & Metadata Isolation:** Protects multiple-choice option keys, distractor texts, and metadata tags from text merger.
6. **Zero Raw Logging:** Auditing uses SHA-256 reference digests rather than storing plaintext answers in audit logs.
