# Stage 26 — Dataset Eligibility and Defect Handling Report

**Document ID:** STAGE26-DATASET-ELIG-001  
**Source Corpus Release:** Release 0.2.0 (Internal MVP Dataset)  
**Total Pairs Audited:** 900 Pairs  
**Total Source Groups Audited:** 300 Source Groups  
**Created At:** 2026-10-05 13:18:02Z  
**Governance Invariant:** Original Stage 20 corpus records remain **100% byte-for-byte immutable**. Internal model development approvals are recorded strictly within derived manifests.

---

## 1. Pair-Level Mutually Exclusive Precedence Accounting

Each of the 900 pairs is assigned **exactly one** primary eligibility disposition using the strict precedence hierarchy:

$$900 = \sum_{i=1}^{7} \text{Count}(\text{PairDisposition}_i)$$

| Priority | Precedence Classification | Dev Split | Val Split | Test Split | Total Pairs | Percentage | Disposition Action |
|---|---|---|---|---|---|---|---|
| **1** | `task_reformulation_excluded` | 225 | 49 | 52 | **326** | 36.22% | Excluded from training & pure simplification evaluation |
| **2** | `non_development_split_excluded` | 0 | 86 | 83 | **169** | 18.78% | Excluded from training (Validation/Test split boundaries) |
| **3** | `incomplete_source_group_excluded` | 0 | 0 | 0 | **0** | 0.00% | Excluded from training (Incomplete Mild/Mod/Str triplet) |
| **4** | `rights_or_governance_excluded` | 0 | 0 | 0 | **0** | 0.00% | Excluded from training (Restricted rights/governance) |
| **5** | `quality_failed` | 0 | 0 | 0 | **0** | 0.00% | Excluded from training (Schema/Quality failure) |
| **6** | `manual_review_unresolved` | 0 | 0 | 0 | **0** | 0.00% | Excluded from training (Pending expert resolution) |
| **7** | `eligible_for_internal_model_development` | 405 | 0 | 0 | **405** | 45.00% | **Eligible for internal model development / fine-tuning** |
| **Total** | **All Dispositions Reconciled** | **630** | **135** | **135** | **900** | **100.0%** | **Zero-loss exact balance** |

---

## 2. Source-Group-Level Mutually Exclusive Precedence Accounting

A source group containing even one ineligible tier is disqualified from training. The group inherits the highest-priority exclusion among its constituent pairs:

$$300 = \sum_{j=1}^{7} \text{Count}(\text{GroupDisposition}_j)$$

| Priority | Precedence Classification | Dev Split | Val Split | Test Split | Total Groups | Percentage | Disposition Action |
|---|---|---|---|---|---|---|---|
| **1** | `task_reformulation_group_excluded` | 140 | 32 | 31 | **203** | 67.67% | Group contains at least one task reformulation |
| **2** | `non_development_group_excluded` | 0 | 13 | 14 | **27** | 9.00% | Clean Validation and Locked Test split groups |
| **3** | `incomplete_tier_group_excluded` | 0 | 0 | 0 | **0** | 0.00% | Group missing required Mild/Moderate/Strong triplet |
| **4** | `rights_or_governance_group_excluded` | 0 | 0 | 0 | **0** | 0.00% | Group disqualified by rights/licence constraints |
| **5** | `quality_failed_group` | 0 | 0 | 0 | **0** | 0.00% | At least one pair failed quality/schema checks |
| **6** | `manual_review_group` | 0 | 0 | 0 | **0** | 0.00% | At least one pair pending manual review |
| **7** | `eligible_internal_training_group` | 70 | 0 | 0 | **70** | 23.33% | **Eligible complete 3-tier training groups (210 pairs)** |
| **Total** | **All Dispositions Reconciled** | **210** | **45** | **45** | **300** | **100.0%** | **Zero-loss exact balance** |

---

## 3. Group vs. Pair Training Eligibility Reconciliation
- **Pair-Level Unflagged Count in Development Split:** **405 clean pairs** ($630 - 225 = 405$).
- **Complete 3-Tier Training Groups:** **70 source groups** ($70 \times 3 = \mathbf210$ pairs) where **all three tiers** (Mild, Moderate, Strong) are completely clean text simplifications with zero task reformulations.
- **Incomplete Candidate Triplet Exclusion:** 195 clean pairs in development split belong to source groups where 1 or 2 companion tiers were flagged as task reformulations; under the complete-group governance invariant, these 195 pairs are excluded from multi-tier fine-tuning to preserve paired structural symmetry.

---

## 4. Locked-Test Dual-Benchmark Structure

The locked test set ($N=45$ source groups / 135 pairs) is structured into two predeclared evaluation sets:

1. **Full Reused Locked Benchmark:**
   - **45 Source Groups (135 Pairs)**
   - Reused from Stages 24 and 25 for historical continuity and full accounting reconciliation.
2. **Predeclared Text-Simplification Subset:**
   - **14 Clean Source Groups (42 Pairs)**
   - Clean source groups containing zero task reformulations across all 3 tiers, evaluated strictly for pure controlled text simplification without QA conversion artifacts.

---

## 5. Derived Manifest Verification
- **Training Eligibility Manifest:** `data/model_simplification/manifests/stage26_training_eligibility_manifest.json`
- **Locked Benchmark Manifest:** `data/model_simplification/manifests/stage26_locked_benchmark_manifest.json`
- **Integrity Statement:** All original Stage 20 corpus files remain **100% byte-for-byte unchanged**.
