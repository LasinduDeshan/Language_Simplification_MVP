# Stage 13 Classification & Governance Rules

This document outlines the strict classification, ownership boundaries, and privacy governance rules for separating the English MVP data into three governed layers.

---

## 1. Governance & Ownership Matrix

| Data Layer / Subsystem | Owning Component | Component 3 Responsibility Boundary | Sensitivity Classification |
|---|---|---|---|
| **Screening Activities & Tasks** | **Component 1** | Adapts permitted instruction language only; never modifies target skill or reveals answers | Protected Benchmark Data |
| **DLD Screening Risk Level** | **Component 1** | Stored strictly as a read-only screening snapshot (`screening_risk_level`); never modified by interaction outcomes | Sensitive Clinical Screening Data |
| **AR Tasks & 3D Spatial Cues** | **Component 2** | Supplies simplified instructions & vocabulary; strictly preserves action sequence and 3D object IDs | Protected Spatial Learning Data |
| **Adaptation Test Set** | **Component 3** | Local development and integration test activities (simulated samples) | Non-Clinical Benchmark Data |
| **Simplification Corpus** | **Component 3** | Team-authored original–simplified sentence pairs and operations | Public/Research Eligible Text Pairs |
| **Interaction Dataset** | **Component 3** | Private educational interaction evidence produced during sessions (Database is source of truth) | Private & De-Identified Learner Evidence |
| **Longitudinal Progression & Trends** | **Component 4** | Receives exported interaction evidence (`local_preliminary_trend` only) | Educational Progression Analytics |

---

## 2. Classification Criteria for Existing MVP Records

### 1. Adaptation Test Set (`data/adaptation_test_set/`)
* **Inclusion:**
  - Tasks authored for testing language simplification across the 4 educational domains (vocabulary, grammar, comprehension, sentence & instruction).
  - Draft simulation fixtures for external Component 1 screening profiles and Component 2 AR payloads.
  - Development scenarios used to exercise multi-attempt scaffolding workflows.
* **Exclusion:**
  - Runtime learner attempts or responses.
  - Real learner profiles or identifiable data.

### 2. Simplification Corpus (`data/simplification_corpus/`)
* **Inclusion:**
  - Original instructions paired with simplified versions across support tiers (mild, moderate, strong).
  - Explicit linguistic simplification operations (e.g., `lexical_substitution`, `sentence_splitting`, `clause_restructuring`).
  - Protected meaning units and grammatical error annotations.
* **Exclusion:**
  - Automatic promotion of unreviewed learner transcripts or interaction outputs.
  - Sensitive learner metadata or clinical classifications.

### 3. Interaction Dataset (`data/interaction_dataset/`)
* **Inclusion:**
  - Pseudonymous session records, attempt histories, response times, and domain score deltas.
  - Relational database (`adaptive_learning.db`) remains the **operational source of truth**.
  - Local snapshots are stored strictly in `data/interaction_dataset/private/` (Git-ignored) for authorized review.
* **Exclusion:**
  - Raw identifiable child information or unverified consent data.
  - Must never appear in public git commits or uncurated releases.

---

## 3. Migration Dispositions & Accounting Rules

Every existing source record must be accounted for according to the formula:
$$\text{Source Records} = \text{Migrated Records} + \text{Excluded Records} + \text{Rejected Records} + \text{Manual-Review Records}$$

1. **`migrated`**: Successfully transformed into the target layer schema and published.
2. **`excluded`**: Intentionally kept outside reusable datasets (e.g. learner profiles kept in DB only).
3. **`rejected`**: Invalid records violating schema or safety constraints.
4. **`manual_review`**: Ambiguous records requiring human review before publication.
