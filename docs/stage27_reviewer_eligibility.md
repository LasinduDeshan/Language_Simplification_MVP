# Stage 27 Reviewer Eligibility, Authorization Matrix, and Calibration Standards

**Component:** Component 3 — AI and NLP Based Language Simplification  
**Scope:** English educational language support for children aged 4–8  
**Prerequisite:** `stage-26-complete-v5` (`1a67bd4`)  
**Protocol Status:** Authoritative Operating Standard  

---

## 1. Overview and Purpose

Stage 27 evaluation requires specialized linguistic, pedagogical, and developmental expertise to evaluate English simplification datasets for children aged 4–8. This document establishes:
1. Documented qualification criteria for candidate reviewers across multidisciplinary domains;
2. A formal **Dimension Authorization Matrix** mapping evaluation decisions to qualified professional roles;
3. Conflict of Interest (COI) declaration standards;
4. Rubric onboarding and calibration training benchmarks.

---

## 2. Reviewer Eligibility Criteria

To ensure rigorous linguistic and pedagogical evaluation without artificially excluding academic linguists or researchers whose disciplines do not use commercial licenses or statutory certifications, reviewers must satisfy at least one of the following documented qualification tracks:

### Track 1: English Language Teaching (ELT / Primary Literacy)
- **Qualifications:** University degree in Primary Education, TESOL, Applied Linguistics, or recognized teaching credential (e.g., PGCE, State Teaching License, CELTA/DELTA).
- **Experience:** $\ge 2$ years of direct classroom instruction or curriculum design for young English learners (ages 4–8).

### Track 2: Speech and Language Therapy / Pathology (SLT / SLP)
- **Qualifications:** Recognized professional degree in Speech-Language Pathology / Therapy or Communication Disorders.
- **Experience:** $\ge 2$ years clinical or educational support experience addressing developmental language delays, speech sound disorders, or language comprehension barriers.

### Track 3: Early Childhood Education & Child Development
- **Qualifications:** Degree in Early Childhood Studies, Child Development, or Educational Psychology.
- **Experience:** $\ge 2$ years designing, assessing, or implementing early-literacy materials for children aged 4–8.

### Track 4: Applied Linguistics & Child Language Acquisition
- **Qualifications:** Master’s or doctoral degree in Linguistics, Psycholinguistics, or Cognitive Science with specialization in child syntax, lexical semantics, or readability.
- **Experience:** Peer-reviewed publications, dissertations, or documented research projects in syntactic complexity or vocabulary acquisition.

### Track 5: NLP-Based Text Simplification & Computational Linguistics
- **Qualifications:** Postgraduate degree or demonstrable research record in NLP, Computational Linguistics, or Language Technologies.
- **Experience:** Authorship of models, benchmarks, or evaluation frameworks for lexical or syntactic text simplification.

---

## 3. Dimension Authorization Matrix

Not all reviewers possess the specialized credentials required for clinical accessibility or child delivery recommendations. The evaluation engine enforces role-based authorization:

| Evaluation Dimension / Decision | Permitted Reviewer Role | Authorization Requirement |
| :--- | :--- | :--- |
| **Grammar, Fluency, and Syntactic Simplicity** | English teacher, linguist, or qualified language expert | Tracks 1, 4, or 5 |
| **Meaning Preservation & Propositional Accuracy** | Linguist, teacher, or trained linguistic reviewer | Tracks 1, 2, 4, or 5 |
| **Vocabulary Simplicity & Word Sense** | Primary educator, linguist, or lexicographer | Tracks 1, 3, 4, or 5 |
| **Age Appropriateness (Ages 4–8)** | Early-childhood educator or developmental specialist | Tracks 1, 2, or 3 |
| **DLD-Related Accessibility & Language Scaffolding** | Speech-Language Pathologist or domain specialist | Track 2 (Mandatory SLT/SLP background) |
| **Supervised Child Delivery Review Recommendation** | Authorized educational or clinical specialist | Track 1, 2, or 3 under approved ethics protocol |
| **Unsupervised Child Delivery Authorization** | **PROHIBITED** | **Universally disabled across all roles in Stage 27** |

---

## 4. Conflict of Interest (COI) Policy and Declaration Schema

### 4.1 Independence and Impartiality Requirements
To prevent conflict of interest, reviewers must declare:
1. **Financial Independence:** No commercial interest in proprietary competing educational products;
2. **Authorship Independence:** Reviewers who authored Stage 20 candidate pairs cannot review their own submissions;
3. **Research Independence:** Independence from model tuning pipelines evaluated in Stage 26 or Stage 28.

### 4.2 Reviewer Registration Record Schema
The private administrative registry records reviewer onboarding data:

```json
{
  "reviewer_id": "REV-ENG-001",
  "name_redacted": "[RESTRICTED_ADMIN_STORAGE]",
  "email_redacted": "[RESTRICTED_ADMIN_STORAGE]",
  "professional_role": "Primary Literacy Specialist / Speech-Language Pathologist",
  "qualification_category": "Clinical & Pedagogical",
  "relevant_experience_years": 7,
  "language_expertise": ["en-US", "en-GB"],
  "child_age_expertise": ["4-6", "6-8"],
  "qualification_track": ["Track 1", "Track 2"],
  "conflict_of_interest_declared": false,
  "participation_agreement_signed": true,
  "confidentiality_undertaking_signed": true,
  "calibration_completed": true,
  "calibration_agreement_score": 0.86,
  "authorized_dimensions": [
    "grammar_and_fluency",
    "meaning_preservation",
    "vocabulary_simplicity",
    "age_appropriateness",
    "dld_accessibility",
    "supervised_delivery_review"
  ],
  "account_status": "active",
  "created_at": "2026-10-10T09:00:00Z"
}
```

*Note: Public research releases expose only `reviewer_id`, `qualification_category`, and review round.*

---

## 5. Reviewer Onboarding and Rubric Calibration

Before receiving live evaluation batches, all reviewers must complete the standardized Stage 27 Calibration Program.

### 5.1 Calibration Training Materials
Reviewers complete a self-paced training module containing:
1. Stage 27 Rating Rubric definitions, scoring anchors, and decision trees;
2. Taxonomy classification guidelines with counter-examples;
3. Benchmark gold calibration set of **20 pre-annotated simplification pairs**, **10 lexicon entries**, and **5 adaptation activities**.

### 5.2 Calibration Assessment Benchmark
- Candidate reviewers independently rate the calibration set.
- Their ratings are automatically compared against reference adjudicator benchmarks.
- **Certification Gate:** The reviewer must achieve:
  * **Critical Binary Check Agreement:** $\ge 90\%$ concordance on failure flags;
  * **Taxonomy Agreement:** Cohen's $\kappa \ge 0.80$ against reference classifications;
  * **Ordinal Rating Concordance:** Quadratic weighted $\kappa_w \ge 0.75$ on quality dimensions.

### 5.3 Recalibration and Adjudicator Guidance
If a reviewer falls below the calibration threshold:
1. The Lead Adjudicator conducts a 1-on-1 calibration review session explaining rating divergence;
2. The reviewer is assigned a secondary calibration set of 15 new benchmark items;
3. If the reviewer again fails to achieve calibration concordance, they are excused from the review panel without penalty.
