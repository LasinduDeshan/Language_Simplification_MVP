# Stage 22 Label Governance Policy & Stop Condition Specification

**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Target Scope:** English Complexity Analysis and Difficulty Classification  
**Status:** SEALED  

---

## 1. Intrinsic Difficulty Definitions

Difficulty classifications characterize the intrinsic linguistic properties of educational text without age or support-level confounding:

- **`easy`**: Low lexical and syntactic complexity, short structures, limited relational or instructional load.
- **`medium`**: Moderate vocabulary, sentence structure, clause complexity, and instructional load.
- **`hard`**: High lexical, syntactic, or semantic-processing complexity, such as advanced vocabulary, embedded clauses, multiple relations, or multi-step load.

---

## 2. Tiered Label Governance Tiers

| Label Status Tier | Primary Training | Secondary Sensitivity | Final Benchmark | Provenance / Qualification Rule |
|---|---|---|---|---|
| **`expert_verified`** | **Yes** | **Yes** | **Yes** | Verified by domain expert or linguist |
| **`reviewer_consensus`** | **Yes** | **Yes** | **Yes** | Agreed by $\ge 2$ independent reviewers |
| **`provisional`** | **No** | **Yes** | **No** | Unverified single author draft label |
| **`rule_seeded`** | **No** | **No** | **No** | Heuristically generated (circular leakage risk; audit only) |
| **`missing_or_conflicting`** | **No** | **No** | **No** | Excluded until adjudicated |

---

## 3. Label-Sufficiency Stop Condition (Mandatory Gate)

Primary supervised model training begins **only when all of the following conditions are met**:
1. All three classes (`easy`, `medium`, `hard`) are represented among Tier 1 labels;
2. Every class contains enough independent source groups for group-aware cross-validation;
3. No class is represented only by duplicated variants or single-source expansions;
4. The number of CV folds ($K$) does not exceed the smallest class-specific source-group count.

$$\text{maximum\_valid\_folds} = \min(\text{distinct\_easy\_groups}, \text{distinct\_medium\_groups}, \text{distinct\_hard\_groups}) \ge 3$$

If $\text{maximum\_valid\_folds} < 3$, Stage 22 **pauses for annotation** and strictly refuses to promote provisional labels to ground truth.

---

## 4. Current Stage 22 Governance Status

### 4.1 Gate Dispositions
- **Primary Tier-1 Training Gate:** **NOT PASSED**
  - **Reason:** 0 `expert_verified` or `reviewer_consensus` labels
- **Secondary Provisional-Label Pilot Gate:** **PASSED**
  - **Pilot Labels Available:** 1,440
  - **Pilot Labels Eligible After Higher-Precedence Exclusions:** 1,430

The trained B0–B5 models are secondary pilot models trained to reproduce provisional author labels—not validated difficulty classifiers.

### 4.2 Governance Attributes
Because the available Stage 20 educational corpus records hold draft authoring metadata (`validation_status: "draft"`, `requires_expert_review: true`), all labels are classified as **`provisional`**:

```json
{
  "model_status": "provisional_label_pilot",
  "ground_truth_status": "not_expert_validated",
  "approved_for_child_delivery": false,
  "research_eligible": false,
  "production_inference_enabled": false,
  "requires_expert_validation": true
}
```

- Characterization: **Stage 22 completed as an internal pilot complexity classifier.**

