# Stage 28A Governance and Scope Document

**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Language:** English  
**Evaluation Phase:** `stage_28a_preliminary_automated_comparison`  
**Target Users:** Children aged 4–8  
**Expert Validated:** `false`  
**Approved for Child Delivery:** `false`  
**Requires Expert Review:** `true`  
**Stage 27 Human-Validation Status:** `pending`  
**Release 0.3.0 Used:** `false`  

---

## 1. Governance Boundary Statement
Stage 28A performs a strictly preliminary, automated comparison of English simplification methods using frozen benchmarks, automated metrics (EASSE-style SARI, SacreBLEU, FKGL), deterministic safety gates, and rights-governed external benchmarks.

Human expert educational suitability and child-delivery appropriateness have **NOT** yet been established. Automated metrics do not constitute clinical or educational proof of developmental child suitability.

## 2. Invariants & Commitments
- **Ancestry Verification:** Verified `stage-26-complete-v5` is an ancestor of `stage-28a-start` (`git merge-base --is-ancestor`, exit code 0).
- **Execution Non-Duplication:** Executed 135 unique locked items once. The predeclared 39-item clean subset was derived from those same outputs without additional model calls.
- **Provider Metadata:** Pinned from live provider discovery: `models/gemini-3.5-flash-lite`, version `3.5-flash-lite-07-2026`, raw metadata response hash `8256ff86f539f0d3301a9ebd99369fc514baf7e6c81bf9eb6e0fb7a6e0c128d5`.
- **System Designations:**
  - Best frozen Stage 24 baseline: **B4 (Combined Deterministic)**
  - Best offline controlled system: **C1 (Stage 25 Controlled Engine)**
  - Best overall automated candidate: **H1 (Governed Hybrid Pipeline)**
- **Safety Qualification:** No distractor leakage was detected by the configured automated checks across $n=39$ clean-subset outputs.
- **Stage 27 Status:** Human validation remains pending ethics clearance; Release 0.3.0 is ungenerated.
