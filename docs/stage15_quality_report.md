# Stage 15 — Automated Dataset Quality Validation Report

**Run ID:** `VAL-20260924-6feab751`  
**Generated Date:** 2026-09-24 15:35:00 UTC  
**Target Scope:** English MVP, Children Aged 4–8  
**Quality Rule-Set Version:** `1.0.0`  
**Dataset Schema Version:** `1.0.0`  

---

## 1. Executive Summary & Disposition Breakdown

| Metric / Disposition | Count | Percentage |
| :--- | :---: | :---: |
| **Total Evaluated Records** | **268** | **100.0%** |
| `automatic_check_passed` | 218 | 81.3% |
| `automatic_check_failed` | 19 | 7.1% |
| `manual_review_required` | 31 | 11.6% |
| `quarantined` | 0 | 0.0% |
| **Unaccounted Records** | **0** | **0.0%** |

---

## 2. Layer-by-Layer Verification

1. **Adaptation Test Set (40 activities)**:
   - Evaluated for 4-domain classification, Component 1 & AR ownership boundaries, distractor validity, and support tier progression.
   - Child-safe serialization verified for 0% answer key leakage.

2. **Simplification Corpus (210 draft pairs)**:
   - Evaluated for meaning unit preservation, negation consistency, quantity retention, and text length ratios.
   - All 210 pairs strictly locked to `validation_status="draft"`, `research_eligible=false`, `approved_for_child_delivery=false`.

3. **Lexicon Repository (18 entries)**:
   - Evaluated for headword uniqueness, part-of-speech compatibility, acyclic replacement chains, and child-friendly explanations.

4. **Interaction Export Allowlist**:
   - Privacy scanners confirmed zero PII, zero direct identifiers, and immutable Component 1 screening risk snapshots.

---

## 3. Governance Invariants

- [x] Advisory status: Automated validation does not grant child-delivery or research approval.
- [x] Zero silent drops: $\text{Input} = \text{Passed} + \text{Failed} + \text{Review} + \text{Quarantined}$.
- [x] Protected answer boundary: Zero evaluation keys exposed in child serializers.
- [x] Privacy isolation: Private text and review logs placed in Git-ignored directory.
