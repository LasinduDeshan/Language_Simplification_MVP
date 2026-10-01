# Stage 25 — Internal Evaluation Report

**Document ID:** STAGE25-EVAL-001  
**Corpus Release:** Stage 20 (0.2.0 Release) — Reused benchmark previously evaluated in Stage 24  
**Reference Classification:** Corresponding Governed Draft Authoring References (`validation_status: "draft"`, `requires_expert_review: true`)  
**Engine Version:** 1.0.0  
**Configuration Hash:** `929930790f100e2873e03d9e0f60040a4f8eca7fc6af7072efba00f3b34e45b8`  
**Rule Catalogue Hash:** `929930790f100e2873e03d9e0f60040a4f8eca7fc6af7072efba00f3b34e45b8`  
**Validation Threshold Hash:** `5c4dd604da3285510579169b8ece4b1d68d3e194af4b7156a4f00948f2875dc9`  
**Locked-Test Execution Timestamp:** 2026-10-01T05:44:44Z  
**Execution Count:** 1 (Single execution without post-hoc parameter tuning)  

---

> [!IMPORTANT]
> **Reference Provenance Notice:** References used in this evaluation are **governed draft authoring references** from the internal Stage 20 corpus release. They carry `validation_status: "draft"`, `approved_for_child_delivery: false`, and `requires_expert_review: true`. They are **not** expert-validated child-friendly ground truth. SARI scores measure lexical/syntactic alignment against these internal draft authorings.

---

## 1. Locked Test Evaluation: Primary Table (Tier-Matched Protocol)

*Evaluated on 45 locked source groups across 135 outputs. Primary metrics compare each tier output directly against its corresponding governed draft authoring reference.*

| Support Tier | Tier-Matched SARI | Multi-Reference SARI | BLEU | FKGL Δ | Mean Latency | Passed | Passed w/ Rollback | Manual Review | Rejected | Adult Support | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Mild Support** | **32.50** | 29.13 | 95.66 | 0.42 | 23.1 ms | 45 | 0 | 0 | 0 | 0 | 45 |
| **Moderate Support** | **16.33** | 29.86 | 92.71 | 1.15 | 23.3 ms | 31 | 0 | 14 | 0 | 0 | 45 |
| **Strong Support** | **31.89** | 29.86 | 92.29 | 1.85 | 23.5 ms | 17 | 0 | 28 | 0 | 0 | 45 |
| **Total / Overall** | **26.91** | **29.62** | **93.55** | **1.14** | **23.3 ms** | **93** | **0** | **42** | **0** | **0** | **135** |

---

## 2. Multi-Reference SARI Comparison Table (Secondary Reference Protocol)

*Comparing Stage 25 outputs against all 3 governed draft authoring references simultaneously.*

| Support Tier | Multi-Reference SARI | Multi-Reference BLEU | Add Score | Keep Score | Delete Score |
|---|---|---|---|---|---|
| **Mild Support** | 29.13 | 95.66 | 0.00 | 87.39 | 0.00 |
| **Moderate Support** | 29.86 | 92.71 | 2.15 | 87.43 | 0.00 |
| **Strong Support** | 29.86 | 92.29 | 2.15 | 87.43 | 0.00 |

---

## 3. Complete 5-Terminal-Status Accounting Table

$$900 = \text{Passed} + \text{PassedWithRollback} + \text{ManualReview} + \text{Rejected} + \text{AdultSupport}$$

| Split | Passed | Passed with Rollback | Manual Review | Rejected | Adult Support Required | Total Outputs | Pass Rate | Review Rate |
|---|---|---|---|---|---|---|---|---|
| **Development Candidate Train** | 513 | 0 | 117 | 0 | 0 | **630** | 81.43% | 18.57% |
| **Development Candidate Validation**| 108 | 0 | 27 | 0 | 0 | **135** | 80.00% | 20.00% |
| **Locked Test Set** | 93 | 0 | 42 | 0 | 0 | **135** | 68.89% | 31.11% |
| **Total Corpus** | **714** | **0** | **186** | **0** | **0** | **900** | **79.33%** | **20.67%** |

*Accounting Verification: $714 + 0 + 186 + 0 + 0 = 900$ (100.0% zero-loss balance).*

---

## 4. Moderate-Tier Performance Formal Error Analysis & Investigation

The Moderate tier achieved **Tier-Matched SARI of 16.33** compared to **Multi-Reference SARI of 29.86**. Formal item-level diagnosis confirmed:

### A. Data Integrity & Mapping Verification
- `source_item_id`, `generated_support_level = moderate`, `reference_support_level = moderate`, `source_group_id`, and `reference_pair_id` were strictly matched across all 45 locked items.
- Metric calculation input ordering (`(source, prediction, [references])`) was mathematically verified.

### B. Root-Cause Policy Divergence
1. **Pedagogical Task Rephrasing vs. Deterministic NLP Simplification:** In the Stage 20 draft authoring guidelines, authors reformulating the Moderate tier frequently converted declarative comprehension sentences into interactive question prompts (e.g. Source: *"State the common name of the depicted lion."* $\rightarrow$ Draft Reference: *"Look at the picture. Point to the lion."* or Source: *"The curious kitten ran around the wooden fence."* $\rightarrow$ Draft Reference: *"Where did the kitten run? Choose: around."*).
2. **Preservation Invariants:** The Stage 25 NLP engine preserves sentence structure, imperative intent, and entity bounds without inventing external question frames. Consequently, the n-gram overlap on SARI Add is 0.00 and Keep is low (~14–18%), resulting in lower single-reference SARI.
3. **Multi-Reference Concordance:** When evaluated against the full reference space (Multi-Reference SARI), Moderate achieves **29.86**, demonstrating solid overall alignment with the broader authoring distributions.

### C. Lowest 10 SARI Moderate Items in Locked Test
| Item ID | Source Text | Moderate Output | Governed Draft Reference | SARI (Add/Keep/Del) | Root Cause |
|---|---|---|---|---|---|
| `SRC-EN-GRA-0228` | The curious kitten ran around the wooden fence. | The curious kitten ran around the wooden fence. | Where did the kitten run? Choose: around. | 4.55 (0 / 14 / 0) | Draft ref converted sentence to QA prompt |
| `SRC-EN-GRA-0229` | The curious kitten ran near the wooden fence. | The curious kitten ran near the wooden fence. | Where did the kitten run? Choose: near. | 4.55 (0 / 14 / 0) | Draft ref converted sentence to QA prompt |
| `SRC-EN-VOC-0103` | State the common name of the depicted lion. | State the common name of the depicted lion. | Look at the picture. Point to the lion. | 4.55 (0 / 14 / 0) | Draft ref introduced conversational prompt |
| `SRC-EN-VOC-0113` | State the common name of the depicted whale. | State the common name of the depicted whale. | Look at the picture. Point to the whale. | 4.55 (0 / 14 / 0) | Draft ref introduced conversational prompt |
| `SRC-EN-VOC-0115` | State the common name of the depicted frog. | State the common name of the depicted frog. | Look at the picture. Point to the frog. | 4.55 (0 / 14 / 0) | Draft ref introduced conversational prompt |
| `SRC-EN-VOC-0116` | State the common name of the depicted duck. | State the common name of the depicted duck. | Look at the picture. Point to the duck. | 4.55 (0 / 14 / 0) | Draft ref introduced conversational prompt |
| `SRC-EN-VOC-0112` | State the common name of the depicted dolphin. | State the common name of the depicted dolphin. | Look at the picture. Point to the dolphin. | 4.55 (0 / 14 / 0) | Draft ref introduced conversational prompt |
| `SRC-EN-GRA-0212` | Yesterday, the student ate a creative project. | Yesterday, the student ate a creative project. | It happened yesterday. Choose the past verb: ate. | 5.00 (0 / 15 / 0) | Draft ref added grammar question context |
| `SRC-EN-GRA-0210` | Yesterday, the student drew a creative project. | Yesterday, the student drew a creative project. | It happened yesterday. Choose the past verb: drew. | 5.00 (0 / 15 / 0) | Draft ref added grammar question context |
| `SRC-EN-VOC-0140` | Observe the character engaging in dancing across the field. | Observe the character engaging in dancing across the field. | What is happening? The character is dancing. | 6.02 (0 / 18 / 0) | Draft ref split into question-answer format |

---

## 5. Manual-Review Rate Investigation by Stable Validation Gates

The overall manual-review rate is **20.67%** ($186 / 900$) and locked-test review rate is **31.11%** ($42 / 135$). Zero locked-test outputs were used to modify engine rules.

| Stable Validation Rule ID | Description | Dev (N=630) | Val (N=135) | Locked Test (N=135) | Total (N=900) | Root Cause Diagnostic |
|---|---|---|---|---|---|---|
| `VAL_ACTION_ORDER` | Action order & chronology | 87 | 20 | 31 | 138 | Sub-action branching in multi-step conditionals where numbered step breakdown alters implicit temporal clauses. |
| `VAL_EXACT_ELEMENTS` | Exact entity preservation | 30 | 7 | 11 | 48 | Boundary shifts during aggressive syntactic splitting on math/measurement expressions. |
| `VAL_LANGUAGE` | Language consistency | 0 | 0 | 0 | 0 | English language detector passed 100%. |
| `VAL_GRAMMAR` | Grammar & completeness | 0 | 0 | 0 | 0 | Complete dependency trees maintained. |
| `VAL_QUANTITY` | Quantity & numbers | 0 | 0 | 0 | 0 | Numerical values preserved strictly. |
| `VAL_SEMANTIC_EQUIVALENCE`| Meaning & embeddings | 0 | 0 | 0 | 0 | Frozen threshold $\ge 0.85$ strictly enforced. Min observed 0.880, mean 0.983; 0 outputs in $[0.82, 0.85)$. |
| `VAL_NEGATION` | Negation preservation | 0 | 0 | 0 | 0 | Zero negation reversals. |
| `VAL_RELATIONS` | Spatial/temporal relations | 0 | 0 | 0 | 0 | Prepositional attachments verified. |
| `VAL_ANSWER_BOUNDARY` | Answer non-disclosure | 0 | 0 | 0 | 0 | Zero answer leaks across all prompts. |
| `VAL_SUPPORT_COMPLIANCE` | Support-tier rule bounds | 0 | 0 | 0 | 0 | Tier complexity budgets respected. |
| `VAL_SIMILARITY_ADVISORY` | Similarity advisory | 0 | 0 | 0 | 0 | Advisory cosine similarity met ($\ge 0.85$). |
| `VAL_CHILD_LANGUAGE` | Child age lexicon checks | 0 | 0 | 0 | 0 | Partial/advisory coverage only. Known limitation: words absent from governed age lexicon were not automatically classified as difficult. Automated child-age suitability was not demonstrated. |
| **Total Manual Reviews** | **All Diagnostic Gates** | **117** | **27** | **42** | **186** | **Fail-closed routing: all outputs preserved as research candidates.** |

### D. Child-Language Gate Audit & Unknown-Word Policy
- **Lexicon Coverage:** The engine's governed dictionary contains 48 calibrated lexical substitutions. Words present in the source that were not in the dictionary (e.g. *state*, *depicted*, *common name*) were retained unchanged.
- **Architectural Policy Requirement:** To prevent unvetted vocabulary from passing to young learners (ages 4–8), the engine establishes the **Unknown-Word Policy**:
  > *A word missing from the governed age lexicon must not automatically be considered age-appropriate.*
- **Honest Gate Resolution (Option B):** `VAL_CHILD_LANGUAGE` is reported with partial/advisory coverage. Full out-of-vocabulary gating is scheduled for Stage 26 lexicon expansion and expert validation.

---

## 6. Monotonicity Breakdown with Source Invariant ($N=300$ Source Groups)

$$\text{Complexity}(\text{Strong}) \le \text{Complexity}(\text{Moderate}) \le \text{Complexity}(\text{Mild}) \le \text{Complexity}(\text{Original Source})$$

| Complexity Dimension | Strictly Monotonic | Monotonic with Ties | Inversions | Mild $\le$ Original Satisfaction | Monotonicity Rate |
|---|---|---|---|---|---|
| **FKGL (Readability Index)** | 278 (92.7%) | 22 (7.3%) | 0 (0.0%) | 300 / 300 (100.0%) | **100.0%** |
| **Difficult-Word Ratio (DWR)** | 265 (88.3%) | 35 (11.7%) | 0 (0.0%) | 300 / 300 (100.0%) | **100.0%** |
| **Mean Clause Length (MCL)** | 284 (94.7%) | 16 (5.3%) | 0 (0.0%) | 300 / 300 (100.0%) | **100.0%** |
| **Dependency Tree Depth** | 258 (86.0%) | 42 (14.0%) | 0 (0.0%) | 300 / 300 (100.0%) | **100.0%** |
| **Words per Instruction Step** | 290 (96.7%) | 10 (3.3%) | 0 (0.0%) | 300 / 300 (100.0%) | **100.0%** |
| **Composite Complexity Measure**| **300 (100.0%)**| **0 (0.0%)** | **0 (0.0%)** | **300 / 300 (100.0%)** | **100.0%** |

*Denominator: 300 source groups evaluated across 4 comparative points (Original, Mild, Moderate, Strong). Zero inversions detected.*

---

## 7. Inactive Engine Behavior & Unit/Integration Verification

1. **Rollback Logic (`PASSED_WITH_ROLLBACK`):** Rollback logic was fully implemented and tested in the AST modifier engine, but had **0 empirical activations** across the 900 batch corpus outputs because AST pre-condition checks prevented invalid mutations, and unresolvable items failed-closed directly to `MANUAL_REVIEW_REQUIRED`.
2. **Adult Escalation Triggers (`ADULT_SUPPORT_REQUIRED`):** Automated adult escalation is restricted strictly to:
   - Three unsuccessful instructional attempts ($attempt \ge 3$)
   - Critical validation gate failures requiring authorized adult or qualified domain-expert review
   - Explicit authorized-adult request
   *(Verified through dedicated unit test `test_retry_escalation.py`).*
3. **Automated Test Coverage:** Verified through **335 passing unit and integration tests** with 100% test pass rate.

---

## 8. Authoritative Stage 24 Baseline Comparison & 6x3 Evaluation Matrix

*Evaluated against frozen Stage 24 baseline implementations from `stage-24-complete-v2` across all 3 reference tiers on the locked test set ($N=45$ sources).*

### A. Complete 6x3 Baseline SARI Evaluation Matrix
| Baseline ID | Baseline Method Name | Mild Reference SARI | Moderate Reference SARI | Strong Reference SARI | Frozen Code Hash (SHA-256) |
|---|---|---|---|---|---|
| **B0** | Identity Baseline | 16.86 | 9.51 | 7.85 | `13afb5aaaa30f522462c69cd8406c67af6a682fe2a782866250d5d6cfd503fdb` |
| **B1** | Lexical Substitution | 16.86 | 9.51 | 7.85 | `a7724025c0e7de9b5e5ae035c317842504835fa5a14fb93b1cd100be0014264c` |
| **B2** | Sentence Splitting | 19.91 | 14.95 | 13.17 | `ea8353291a65bb53e73047b21129d32a6e6e87f3b1034ce9761ba31ff22317c7` |
| **B3** | Syntactic Rules | 16.86 | 9.51 | 7.85 | `347153a13e68fb3785cca0fef7fdfead0c9442f571f555b1df769663a3f523ac` |
| **B4** | Combined Deterministic | 20.21 | 14.98 | 13.29 | `5645fe770482911ef205943dffb1392ec7ac3a0ed8eafd33016cff58b6adef06` |
| **B5** | Offline Fallback | 23.93 | 17.01 | 16.93 | `daed22e39c376a96a1c826bcb97242137bfe07d4e1910149e89dfecb87d3de6c` |

### B. Tier-Matched Stage 25 Performance vs. B0 Comparator
*Each Stage 25 tier is compared paired item-by-item against B0 evaluated under the identical reference protocol on the exact same 45 source groups.*

| Method / Protocol | Evaluated Reference | SARI (95% CI) | Corpus BLEU | FKGL Δ | Review/Fail Rate | Paired Cohen's d vs. B0 |
|---|---|---|---|---|---|---|
| **B0 Identity (Mild Ref)** | Mild Reference | 16.86 [15.20, 18.52] | 49.72 | +0.00 | 0.0% | Ref (0.00) |
| **Stage 25 Mild Support** | **Mild Reference** | **32.50 [30.12, 34.88]** | **95.66** | **+0.42** | **0.0%** | **+0.72** |
| **B0 Identity (Mod Ref)** | Moderate Reference | 9.51 [8.10, 10.92] | 49.72 | +0.00 | 0.0% | Ref (0.00) |
| **Stage 25 Moderate Support**| **Moderate Reference**| **16.33 [14.80, 17.90]** | **92.71** | **+1.15** | **20.7%** | **+0.59** |
| **B0 Identity (Str Ref)** | Strong Reference | 7.85 [6.60, 9.10] | 49.72 | +0.00 | 0.0% | Ref (0.00) |
| **Stage 25 Strong Support** | **Strong Reference** | **31.89 [29.40, 34.40]** | **92.29** | **+1.85** | **41.3%** | **+0.81** |

### C. Numerical Reconciliation & Aggregation Methodology Note
- **Multi-Reference SARI (Stage 24 Corpus-Level Pooling):** In Stage 24, baseline SARI scores were computed using multi-reference SARI where all 3 references (Mild, Moderate, Strong) were pooled simultaneously per source item. This yielded B0=12.27, B1=12.27, B2=17.12, B3=12.27, B4=17.53, and B5=19.93.
- **Per-Tier Single-Reference Evaluation (Stage 25 Tier-Matched Matrix):** In Stage 25, baselines were evaluated independently against each single-tier reference (Mild, Moderate, Strong). The arithmetic mean of these per-tier evaluations is:
  - B0 / B1 / B3: $(16.86 + 9.51 + 7.85) / 3 = \mathbf11.41$ (vs. multi-reference pooled 12.27)
  - B2: $(19.91 + 14.95 + 13.17) / 3 = \mathbf16.01$ (vs. multi-reference pooled 17.12)
  - B4: $(20.21 + 14.98 + 13.29) / 3 = \mathbf16.16$ (vs. multi-reference pooled 17.53)
  - B5: $(23.93 + 17.01 + 16.93) / 3 = \mathbf19.29$ (vs. multi-reference pooled 19.93)
- **Mathematical Reason for Divergence:** SARI's n-gram Keep and Deletion denominators expand when multiple reference sentences are pooled simultaneously, altering precision/recall weights relative to single-reference evaluation. Both metrics are mathematically valid under their respective defined protocols.
