# Stage 28A Milestone Completion Record (v3 Reconciled)

**Milestone:** Stage 28A — Preliminary English Model and Simplification Comparison  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Completion Date:** 2026-10-14 04:50:57 UTC  
**Initial Completion Tag:** `stage-28a-complete` (preserved historical checkpoint)  
**First Supplementary Tag:** `stage-28a-complete-v2` (preserved intermediate checkpoint)  
**Authoritative Supplementary Tag:** `stage-28a-complete-v3`  
**Prerequisite Tag:** `stage-27-infrastructure-complete-v3` (resolving to commit `22eb001`)  
**Start Tag:** `stage-28a-start` (at prerequisite baseline commit `22eb001`)  

---

## 1. Canonical Candidate Profile Designations
- **Best frozen Stage 24 baseline:** **B4 (Combined Deterministic Baseline)** — Canonical Stage 28A SARI: **24.11** (post-FKGL: 2.82, BLEU-4: 54.55, p95 latency: 71.7 ms, $0.00 billable cost). *(Note: Stage 24 historical baseline reported 36.84 under an earlier non-EASSE tokenization/reference aggregation protocol).*
- **Best offline controlled system:** **C1 (Stage 25 Controlled Engine)** — Canonical Stage 28A SARI: **25.44** (post-FKGL: 3.44, BLEU-4: 59.92, 100% entity and negation preservation, $0.00 billable cost). *(Note: Stage 25 historical report evaluated under an earlier non-EASSE reference protocol).*
- **Best request-level governed automated pipeline:** **H1 (Governed Hybrid Pipeline)** — Canonical Stage 28A SARI: **39.48**, evaluated across all 39 requests, including 28 native Gemini deliveries, 1 safety fallback, and 10 provider fallbacks.
- **Diagnostic native LLM evaluation:** **G1 Native-Only (Partial, $n=29/39$)** — Canonical Stage 28A SARI: **40.65** (post-FKGL: 1.90, BLEU-4: 38.94), evaluating strictly the 29 items receiving native LLM responses without fallback imputation.

## 2. SARI Numerical Reconciliation
All Stage 28A SARI values derive from one canonical results artifact (`stage28a_clean_subset_comparison.csv` under pinned EASSE 0.2.4 protocol). Statistical differences match identically:
$$\text{B0 Identity Baseline} = 14.38$$
$$\text{B4} - \text{B0} = 24.11 - 14.38 = +9.73$$
$$\text{C1} - \text{B0} = 25.44 - 14.38 = +11.07$$
$$\text{H1} - \text{B0} = 39.48 - 14.38 = +25.10$$
$$\text{G1 (matched)} - \text{B0 (matched)} = 40.65 - 14.06 = +26.59$$
$$\text{H1} - \text{C1} = 39.48 - 25.44 = +14.04$$

## 3. Qualified Safety & Governance Statement
- No distractor leakage was detected by the configured automated checks across $n=39$ clean-subset outputs.
- Expert validated: `false`
- Child suitability demonstrated: `false`
- Approved for child delivery: `false`

```text
Stage 28A automated comparison: COMPLETE
Stage 27 human expert validation: PENDING
Stage 28B expert-aligned comparison: DEFERRED
Child-delivery approval: FALSE
```
