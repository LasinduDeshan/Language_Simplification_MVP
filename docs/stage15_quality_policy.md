# Stage 15 Quality Validation Policy

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Target Group:** Children aged 4–8 (English MVP)  
**Document Version:** 1.0.0  
**Effective Date:** 2026-09-24  

---

## 1. Purpose & Scope

This policy defines the automated quality control and validation standards for all governed dataset layers within Component 3:
1. **Adaptation Test Set** (`data/adaptation_test_set/`)
2. **Simplification Corpus** (`data/simplification_corpus/`)
3. **Age-Tiered Lexicons** (`data/lexicons/`)
4. **De-identified Interaction Exports** (`data/interaction_dataset/deidentified_exports/`)

Stage 15 evaluates whether the linguistic content inside schema-valid records is child-appropriate, grammatically sound, meaning-preserving, and safe for human review.

---

## 2. Core Governance Invariants

1. **Advisory Nature of Automatic Validation**:
   - Automated checks assign quality statuses (`automatic_check_passed`, `automatic_check_failed`, `manual_review_required`, `quarantined`).
   - Automated checks **never** grant `approved_for_child_delivery=true` or `research_eligible=true`.
   - Final approval is strictly reserved for authorized human experts in Stage 16.

2. **Draft Record Invariance**:
   - All 210 Simplification Corpus pairs remain strictly in `validation_status="draft"`.
   - Passing an automatic check does not alter draft status or licensing provenance.

3. **No Silent Data Dropping**:
   - Failed, rejected, or flagged records are never deleted.
   - All records are accounted for in an immutable, reproducible audit ledger:
     $$\text{Total Records} = \text{Passed} + \text{Failed} + \text{Manual Review Required} + \text{Quarantined}$$

4. **Protected Answer & Child-Safe Boundaries**:
   - Serialization for child delivery must never expose answer keys (`protected_answer`, `acceptable_answers`), rubrics, or evaluation notes.
   - Any answer key leakage in child serializers triggers an immediate `critical` rule failure.

5. **Privacy & Interaction Data Isolation**:
   - Raw interaction text and direct learner identifiers must never be published or included in public reports.
   - Any un-allowlisted field or PII in interaction exports triggers an immediate `quarantined` state.

6. **Component Boundaries & DLD Screening Invariance**:
   - Component 1 owns DLD risk screening (read-only snapshot).
   - Component 3 educational activities and quality validation cannot alter screening risk indicators.
   - Component 2 owns AR spatial anchors and action sequence contracts.
   - Component 4 receives only `local_preliminary_trend`.

---

## 3. Controlled Quality Status Model

| Quality Status | Definition | Next Required Action |
| :--- | :--- | :--- |
| `not_checked` | Record has not been evaluated by Stage 15 quality validators. | Run quality validation pipeline. |
| `automatic_check_passed` | Record passed all mandatory deterministic and NLP checks. | Awaits Stage 16 expert review. |
| `automatic_check_failed` | Record violated one or more blocking `error` quality rules. | Route to triage / correction service. |
| `manual_review_required` | Warning threshold exceeded or linguistic signals are inconclusive. | Route to manual review queue. |
| `quarantined` | Record triggered a `critical` safety, privacy, or answer-leak rule. | Isolate immediately; block export. |
| `expert_reviewed` | *(Stage 16)* An authorized expert completed evaluation. | Governed in Stage 16. |
| `approved` | *(Stage 16)* An authorized workflow approved child delivery. | Governed in Stage 16. |
| `rejected` | *(Stage 16)* An authorized reviewer permanently rejected record. | Governed in Stage 16. |

---

## 4. Evidence vs. Proof Caveats

- Automated metrics (e.g. Average Sentence Length, syllable counts, token ratios, embedding similarity) serve as **automatic quality indicators requiring expert calibration**.
- Statistical similarity is not proof of pedagogical validity or clinical safety.
- Protected meaning-unit preservation is strictly prioritized over vector embedding similarity.
