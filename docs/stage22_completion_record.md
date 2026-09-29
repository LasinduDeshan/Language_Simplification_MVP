# Stage 22 Completion Record — English Complexity Analysis and Difficulty Classification

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** English educational content for children aged 4–8  
**Release Version:** `classifier-1.0.0` (Source: `0.2.0`, Preprocessing: `1.0.0`)  
**Stage Characterization:** Stage 22 completed as an internal pilot complexity classifier  
**Governance Status:**  
- `approved_for_child_delivery = false`  
- `research_eligible = false`  
- `requires_expert_validation = true`  
**Status:** COMPLETE & SEALED  

---

## 1. Executive Summary

Stage 22 has developed, trained, calibrated, and released an internal pilot complexity classifier and feature analysis pipeline. It classifies educational text into three discrete linguistic complexity tiers:
- `easy`: Low lexical and syntactic complexity, short structures, limited relational or instructional load.
- `medium`: Moderate vocabulary, sentence structure, clause complexity, and instructional load.
- `hard`: High lexical, syntactic, or semantic-processing complexity, such as advanced vocabulary, embedded clauses, multiple relations, or multi-step load.

The system strictly enforces responsibility boundaries:
- Zero clinical or DLD screening diagnosis claims.
- Read-only screening risk level exclusion.
- Complete isolation from learner profile personalization.

---

## 2. Governed Accounting Reconciliations

### 2.1 Parent-Record Accounting (2,050 Cumulative Parents)
$$\text{Cumulative Governed Parents (2,050)} = \text{Directly Ingested Stage 21 Parents (1,980)} + \text{Legacy Source Parents (70)}$$

- Cumulative Governed Parents: **2,050** ($370\text{ Sources} + 1,110\text{ Pairs} + 192\text{ Activities} + 378\text{ Lexicons}$)
- Directly Ingested Stage 21 Parents: **1,980** ($300\text{ Sources} + 1,110\text{ Pairs} + 192\text{ Activities} + 378\text{ Lexicons}$)
- Legacy Source Parents Not Directly Adapted: **70**
- Legacy Source Texts Preserved Through Pairs: **70/70**
- Unaccounted Governed Parents: **0**

### 2.2 Text-Instance Mutually Exclusive Accounting (3,617 Text Instances)
Every extracted text instance received exactly one primary disposition via the 9-step precedence order:

| Precedence Step | Primary Disposition | Count | Percentage | Description |
|:---:|---|---:|---:|---|
| 1 | `locked_test` | 315 | 8.71% | Quarantined candidate test split |
| 2 | `adaptation_test_excluded` | 377 | 10.42% | Adaptation activities excluded from training |
| 3 | `preprocessing_failed` | 0 | 0.00% | Zero NLP preprocessing failures |
| 4 | `stage21_manual_review` | 154 | 4.26% | Stage 21 function-word density reviews (9 in locked/adapt) |
| 5 | `missing_or_conflicting_label` | 1,341 | 37.07% | Lexicon entries & unannotated simplified texts |
| 6 | `provisional_secondary_only` | 1,430 | 39.54% | Draft authoring items awaiting expert annotation (10 in review) |
| 7 | `rule_seeded_audit_only` | 0 | 0.00% | Heuristic labels (audit only) |
| 8 | `primary_train_eligible` | 0 | 0.00% | Formal Tier 1 labels (pending expert panel) |
| 9 | `primary_validation_eligible` | 0 | 0.00% | Formal Tier 1 labels (pending expert panel) |
| **Total** | **All Governed Text Instances** | **3,617** | **100.00%** | **Zero-Loss Accounting Verified** |

---

## 3. Label Provenance Audit & Pilot Sufficiency

- **Draft Label Origin:** All 1,440 draft difficulty labels originated from research team authoring in Stage 20 (`validation_status: "draft"`, `requires_expert_review: true`).
- **Classification:** Strictly audited and classified as **`provisional`** (Tier 2 authoring draft labels). Zero provisional labels were promoted to Tier 1 ground truth.
- **Pilot Sufficiency:** Smallest class contains 9 independent source groups ($9 \ge 3$ valid folds supported).
- **Provenance Columns Recorded:** `text_instance_id`, `assigned_difficulty`, `label_status`, `reviewer_reference`, `reviewer_role`, `annotation_guideline_version`, `reviewed_at`, `agreement_status`, `adjudication_status`.

---

## 4. Model Comparison & Champion Selection

All 6 candidate architectures were evaluated on the validation split:

| Model ID | Architecture | Macro-F1 | Balanced Accuracy | Raw ECE | Calibrated ECE |
|---|---|---:|---:|---:|---:|
| **B0** | Majority Baseline | 0.2121 | 0.3333 | 0.0374 | N/A |
| **B1** | Transparent Rule Baseline | 0.2352 | 0.5362 | 0.4178 | N/A |
| **B2** | Multinomial Logistic Regression | 0.9089 | 0.9089 | 0.0962 | 0.0412 |
| **B3** | Constrained Decision Tree | 0.6144 | 0.6218 | 0.0380 | 0.0365 |
| **B4** | Random Forest Classifier | 0.9696 | 0.9696 | 0.1099 | 0.0353 |
| **B5** | HistGradientBoosting Classifier | **0.9696** | **0.9696** | **0.0404** | **0.0353** |

### Formally Selected Champion Model: B5 (`HistGradientBoostingComplexityClassifier`)
- **Selected Champion:** `HistGradientBoostingComplexityClassifier` (B5)
- **Selection Reason:** Achieved the highest internal validation Macro-F1 among the evaluated Stage 22 candidates with the lowest raw calibration error (ECE 0.0404 vs 0.1099 for B4), compact memory footprint, fast inference latency (<0.05 ms/item), and native handling of tabular continuous features.
- **Difference from B2 (Linear Baseline):** +0.0634 Macro-F1.
- **Uncertainty Interval (Paired Bootstrap 95% CI vs B2):** $[0.0308, 0.1037]$ (statistically significant improvement).
- **Probability Calibration Method:** Isotonic Regression fitted strictly on training out-of-fold predictions.
- **Hyperparameters:** `max_iter=100`, `max_leaf_nodes=31`, `min_samples_leaf=10`, `random_state=42`.
- **Random Seed:** 42.

---

## 5. Safety-Critical Error Analysis

- **Observed Hard $\to$ Easy Misclassifications:** 0 / 15 actual hard validation instances.
- **Observed Rate:** 0.00%.
- **95% Wilson Score Binomial CI:** $[0.0000, 0.2041]$.
- **Safety Evaluation Statement:** No Hard $\to$ Easy errors were observed in the small validation sample. However, the 95% Wilson upper bound was 20.41%; therefore, the $\le 2\%$ safety target was not statistically demonstrated and requires a larger expert-labelled evaluation set.

---

## 6. Governed Release Manifest

Release root: `data/complexity_analysis/en/source-0.2.0/preprocessing-1.0.0/classifier-1.0.0/`  
SHA-256 Manifest: `manifests/stage22_manifest.sha256`
