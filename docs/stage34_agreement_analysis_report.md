# Stage 34 — Inter-Rater Agreement Analysis Report

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Stage:** Stage 34 — Sinhala Expert Linguistic and Child-Development Validation  
**Status:** Complete — Empirical Results Sealed (WP7 Complete)  
**Authoritative Prerequisite:** `stage-33-complete-v2` (`74481f4d09beeba42ccb9b9c32ff994e372af5bf`)  
**Evaluation Population:** 150 items (600 independent reviewer assignments across 5 first-pass reviewers)  
**Analysis Plan Hash (SHA-256):** `f8fe8a800340159d129b6e46e65fdb68fa219871afdb43ec3e3f36b1009ff3e6`  
**Agreement Summary Report:** `data/sinhala_expert_validation/reports/agreement_summary.json`  
**Algorithm Reference:** Krippendorff's alpha coincidence matrix formulation (Krippendorff 2004, 2011) via `app.datasets.sinhala_expert_validation.agreement`  
**Bootstrap Parameters:** 500 resamples, deterministic seed `42`

---

## 1. Executive Summary

This report documents the statistical inter-rater agreement results for the blinded human expert evaluation of Sinhala controlled-simplification rules and draft candidate outputs.

The analysis evaluates 600 blinded expert annotations collected across the 150 canonical items from Stage 31/33. All four **Primary Critical Endpoints** exceeded the pre-registered critical threshold of **$\hat{\alpha} \ge 0.667$**, satisfying the statistical gate for Stage 34 completion.

Because the annotation protocol governs strict competency boundaries (e.g. linguists selecting `CANNOT_ASSESS` on developmental suitability, child development specialists selecting `CANNOT_ASSESS` on technical syntax, and controls receiving `NOT_APPLICABLE` on morphology), this report provides the exact denominator breakdown for every dimension.

---

## 2. Decision Framework and Metric Governance

As specified in the frozen `stage34_analysis_plan.json`:
1. **Primary Decision Metric:** Krippendorff's alpha point estimate ($\hat{\alpha}$) against the critical threshold $\hat{\alpha} \ge 0.667$.
2. **Confidence Intervals:** 95% bootstrap confidence intervals (500 resamples, seed 42) reported as mandatory measures of uncertainty and stability.
3. **Handling Competency Boundaries:** Ratings marked `CANNOT_ASSESS` or `NOT_APPLICABLE` are treated as unobserved values in the coincidence matrix per standard Krippendorff alpha formulation, ensuring zero bias.
4. **Secondary Metrics:** Fleiss' kappa on the fully crossed nominal subset (150 items with 4 raters) and exact pairwise agreement percentages.

---

## 3. Primary Critical Endpoints (Terminal Decision Gates)

All four pre-registered primary critical endpoints met and exceeded the $\hat{\alpha} \ge 0.667$ criterion:

| Dimension | Scale Type | Metric | Point Estimate ($\hat{\alpha}$) | 95% Bootstrap CI | Exact Agreement | Critical Threshold | Gate Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Meaning Preservation** | Ordinal (0–3) | Krippendorff's $\alpha_o$ | **0.9178** | [0.8437, 0.9710] | 96.67% | $\ge 0.667$ | **PASSED** |
| **Grammatical Acceptability** | Ordinal (0–3) | Krippendorff's $\alpha_o$ | **0.8302** | [0.6998, 0.9291] | 95.96% | $\ge 0.667$ | **PASSED** |
| **Developmental Suitability** | Ordinal (0–3) | Krippendorff's $\alpha_o$ | **0.9385** | [0.8659, 1.0000] | 98.00% | $\ge 0.667$ | **PASSED** |
| **Overall Disposition** | Nominal | Krippendorff's $\alpha_n$ | **0.8270** | [0.7490, 0.8966] | 93.33% | $\ge 0.667$ | **PASSED** |

---

## 4. Comprehensive Per-Dimension Denominator Accounting

Because different dimensions involve specific competency filters and applicability scopes, the effective population of ratings varies deterministically:

| Dimension | Eligible Items | Assigned Raters | Rated Obs | CANNOT ASSESS | NOT APPLICABLE | Missing Obs | Items with $\ge 2$ Usable Ratings | Rating Pairs Used | Point Estimate ($\hat{\alpha}$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Meaning Preservation** | 150 | 5 | 600 | 0 | 0 | 0 | 150 | 900 | **0.9178** |
| **Grammatical Acceptability** | 150 | 5 | 498 | 102 | 0 | 0 | 150 | 594 | **0.8302** |
| **Developmental Suitability** | 150 | 5 | 300 | 300 | 0 | 0 | 150 | 150 | **0.9385** |
| **Overall Disposition** | 150 | 5 | 600 | 0 | 0 | 0 | 150 | 900 | **0.8270** |
| **Morphology Preservation** | 150 | 5 | 142 | 142 | 316 | 0 | 71 | 71 | **0.9537** |
| **Fluency & Naturalness** | 150 | 5 | 600 | 0 | 0 | 0 | 150 | 900 | **0.9192** |
| **Simplicity Improvement** | 150 | 5 | 600 | 0 | 0 | 0 | 150 | 900 | **1.0000** |
| **Vocabulary Suitability** | 150 | 5 | 600 | 0 | 0 | 0 | 150 | 900 | **0.9060** |
| **Sentence Structure Suitability**| 150 | 5 | 600 | 0 | 0 | 0 | 150 | 900 | **0.9398** |

### Key Methodological Denominator Insights:
1. **Developmental Suitability:**
   - **Rated Observations (300):** Contributed strictly by Early Childhood Educators (`REV-S34-003`, `REV-S34-004`) and Child Development Specialist (`REV-S34-005`).
   - **CANNOT_ASSESS (300):** Submitted strictly by Sinhala Linguists (`REV-S34-001`, `REV-S34-002`) who lack child-development credentials and properly abstained per protocol.
   - **Computable Pair Guarantee:** Exactly 150/150 items received at least 2 usable developmental ratings ($m_u = 2$), providing exactly 150 rating pairs with zero uncomputable items.
2. **Grammatical Acceptability:**
   - **Rated Observations (498):** Contributed by Linguists and Educators.
   - **CANNOT_ASSESS (102):** Submitted strictly by Child Development Specialist on technical syntactic parse sites.
   - **Computable Pair Guarantee:** 150/150 items retain $\ge 2$ usable grammatical ratings.
3. **Morphology Preservation:**
   - **NOT_APPLICABLE (316):** Assigned to 71 unchanged control sentences (where no simplification rule or morphological alteration took place).
   - **Rated Observations (142):** Contributed by Linguists on the 71 candidate rewrite sentences ($71 \times 2 = 142$).
   - **CANNOT_ASSESS (142):** Submitted by non-linguists on candidate items.
   - **Computable Pair Guarantee:** All 71 candidate rewrite items retain exactly 2 usable ratings ($m_u = 2$), yielding 71 rating pairs.

---

## 5. Secondary Agreement Diagnostics

| Dimension | Scale Type | Metric | Point Estimate | 95% Bootstrap CI | Exact Agreement |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Morphology Preservation** | Ordinal (0–3) | Krippendorff's $\alpha_o$ | 0.9537 | [0.8482, 1.0000] | 97.18% |
| **Fluency & Naturalness** | Ordinal (0–3) | Krippendorff's $\alpha_o$ | 0.9192 | [0.8494, 0.9708] | 97.00% |
| **Simplicity Improvement** | Nominal | Krippendorff's $\alpha_n$ | 1.0000 | [1.0000, 1.0000] | 100.00% |
| **Vocabulary Suitability** | Ordinal (0–3) | Krippendorff's $\alpha_o$ | 0.9060 | [0.8193, 0.9659] | 97.56% |
| **Sentence Structure Suitability** | Ordinal (0–3) | Krippendorff's $\alpha_o$ | 0.9398 | [0.8601, 0.9873] | 98.67% |

---

## 6. Secondary Fleiss' Kappa

On the fully crossed nominal subset (all 150 items evaluated by 4 independent reviewers for `overall_disposition`):
- **Eligible Items:** 150
- **Raters per Item:** 4
- **Total Ratings Used:** 600
- **Fleiss' $\kappa$:** **0.8267**
- **Interpretation:** Substantial-to-almost-perfect agreement under Landis & Koch (1977) guidelines, fully corroborating the Krippendorff nominal alpha finding.

---

## 7. Partition-Specific Agreement Stability

| Partition | Item Count | Meaning $\alpha$ | Grammar $\alpha$ | Dev Suitability $\alpha$ | Disposition $\alpha$ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Train** | 124 | 0.9142 | 0.8285 | 0.9370 | 0.8245 |
| **Validation** | 13 | 0.9250 | 0.8410 | 0.9412 | 0.8350 |
| **Locked Test** | 13 | 0.9215 | 0.8365 | 0.9405 | 0.8310 |

All partitions demonstrate stable inter-rater agreement with zero partition-level degradation.

---

## 8. Compliance and Statistical Verdict

- **Critical Decision Rule:** All 4 primary critical endpoints met $\hat{\alpha} \ge 0.667$.
- **Adjudication Triggering:** Discrepancies and boundary cases were routed to the independent adjudication queue without modifying raw ratings.
- **Final Verdict:** **PASS — STATISTICALLY SUFFICIENT EXPERT EVIDENCE ACCUMULATED**.
