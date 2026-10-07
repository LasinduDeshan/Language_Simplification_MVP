# Stage 26 Dataset Eligibility & Group-Safe Audit Report

**Stage:** Stage 26 — Pretrained Model / LLM-Based English Simplification  
**Corpus Release:** 0.2.0 (Stage 20 Internal Benchmark)  
**Issue Register Source:** `data/simplification_corpus/releases/0.2.0/dataset_issue_register.json`  
**Manifest Version:** 2.1.0  
**Corpus Immutability Guarantee:** `source_records_modified: false` (Original records preserved unchanged)  

---

## 1. Executive Summary

Stage 25 registered **326 task reformulations** across the 900-pair Stage 20 draft corpus. In Stage 26-v2, pair-level exclusion was upgraded to **group-safe whole-source-group exclusion**. Every source group containing even a single task reformulation has all 3 of its companion pairs excluded to eliminate partial-group leakage and structural distortion.

### Key Audit Metrics
- **Total Audited Pairs:** 900 (300 source groups)
- **Directly Flagged Reformulation Pairs:** 326
- **Dynamically Recalculated Contaminated Groups:** 203
- **Total Group-Excluded Pairs ($3N$):** 609
- **Eligible Internal Training Groups (Clean, Complete 3-Tier):** 70 groups
- **Eligible Internal Training Pairs:** 210 pairs (70 groups $\times$ 3 tiers)

---

## 2. Mutually Exclusive Pair Dispositions (Precedence Hierarchy)

Every pair is assigned exactly one disposition following the strict precedence hierarchy:

| Priority | Pair Disposition Category | Count | Percentage | Description |
| :---: | :--- | :---: | :---: | :--- |
| **1** | `direct_task_reformulation_excluded` | 326 | 36.22% | Directly flagged in Stage 25 issue register |
| **2** | `source_group_reformulation_excluded` | 283 | 31.44% | Unflagged companion in a contaminated group |
| **3** | `non_development_split_excluded` | 81 | 9.00% | Clean groups residing in Validation or Test splits |
| **4** | `incomplete_group_excluded` | 0 | 0.00% | Groups lacking all 3 tiers (Mild, Moderate, Strong) |
| **5** | `rights_or_governance_excluded` | 0 | 0.00% | Missing rights / authoring permissions |
| **6** | `quality_failed` | 0 | 0.00% | Failed automated quality checks |
| **7** | `manual_review_unresolved` | 0 | 0.00% | Unresolved human review flags |
| **8** | `eligible_internal_training` | 210 | 23.33% | **Approved for Derived Pilot Training Manifest** |
| **Total** | **Reconciled Sum** | **900** | **100.00%** | **Mutually Exclusive Reconciliation** |

---

## 3. Split-Level Group Accounting

| Split Name | Total Source Groups | Contaminated Groups | Clean Source Groups | Eligible Training Pairs |
| :--- | :---: | :---: | :---: | :---: |
| **Train (Development Candidate)** | 210 | 140 | 70 | **210** (70 groups $\times$ 3 tiers) |
| **Validation (Evaluation Candidate)** | 45 | 31 | 14 | 0 (Reserved for Validation) |
| **Locked Test (Benchmark)** | 45 | 32 | 13 | 0 (Locked Benchmark Holdout) |
| **Total** | **300** | **203** | **97** | **210** |

---

## 4. Governance & Corpus Preservation

1. **Byte-for-Byte Corpus Preservation:** Original files in `data/simplification_corpus/releases/0.2.0/` remain strictly unmodified.
2. **Derived Training Approval:** Internal training approval applies strictly to derived pilot experiments.
3. **Draft Boundary Invariant:** Training eligibility does **not** imply public research release approval or unsupervised child-facing delivery permission. All generated models and candidate outputs remain `validation_status: "draft"` and `requires_expert_review: true`.
