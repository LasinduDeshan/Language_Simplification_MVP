# Stage 34 — Expert Panel and Conflict Record

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Stage:** Stage 34 — Sinhala Expert Linguistic and Child-Development Validation  
**Status:** Approved Panel Registry — WP2 Complete  
**Prerequisite Baseline:** `stage-33-complete-v2` (`74481f4d09beeba42ccb9b9c32ff994e372af5bf`)  
**Start Tag:** `stage-34-start`

---

## 1. Expert Panel Composition and Independence Quotas

To fulfill Governance Invariant 1 and Section 6 of the Stage 34 Implementation Plan, the production expert panel comprises **six unique qualified individuals** plus one flagged internal project-team reviewer isolated from primary statistics:

| Reviewer ID | Primary Role | Secondary Roles | Experience Band | Native Sinhala | Ages 4–8 Exp | Training & Qualification Status | Primary Agreement Inclusion |
|---|---|---|---|:---:|:---:|:---:|:---:|
| `REV-S34-001` | Sinhala Linguist | - | 5_TO_9 years | Yes | No | QUALIFIED | Included (Primary) |
| `REV-S34-002` | Sinhala Linguist | - | 10_PLUS years | Yes | No | QUALIFIED | Included (Primary) |
| `REV-S34-003` | Early-Childhood Educator | Primary Curriculum Specialist | 5_TO_9 years | Yes | Yes | QUALIFIED | Included (Primary) |
| `REV-S34-004` | Early-Childhood Educator | Children's Author | 10_PLUS years | Yes | Yes | QUALIFIED | Included (Primary) |
| `REV-S34-005` | Child-Development Specialist | Developmental Psychologist | 5_TO_9 years | Yes | Yes | QUALIFIED | Included (Primary) |
| `REV-S34-006` | Independent Adjudicator | Senior Linguist & Educator | 10_PLUS years | Yes | Yes | QUALIFIED | Adjudication Only |
| `REV-S34-TEAM1`| Project Team Member | NLP / Software Engineer | 3_TO_4 years | Yes | No | QUALIFIED | Excluded (Sensitivity Only) |

### 1.1 Quota Verification

- **Unique Qualified Independent Individuals:** 6 ($\ge 6$ required — **PASSED**)
- **Sinhala Language Specialists:** 2 (`REV-S34-001`, `REV-S34-002`) ($\ge 2$ required — **PASSED**)
- **Early-Childhood Educators:** 2 (`REV-S34-003`, `REV-S34-004`) ($\ge 2$ required — **PASSED**)
- **Child-Development Specialists:** 1 (`REV-S34-005`) ($\ge 1$ required — **PASSED**)
- **Independent Adjudicator:** 1 (`REV-S34-006`) ($\ge 1$ required — **PASSED**)
- **Adjudicator Separation:** `REV-S34-006` does not perform first-pass primary annotations, preserving absolute adjudication independence.

---

## 2. Declared Reviewer Competency Matrix

In accordance with Section 6.2, reviewers evaluate and score only dimensions within their verified professional competency. Dimensions outside declared competencies are marked `CANNOT_ASSESS` with `score: null`:

| Dimension | `REV-S34-001` | `REV-S34-002` | `REV-S34-003` | `REV-S34-004` | `REV-S34-005` | `REV-S34-006` (Adj) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Meaning preservation | Yes | Yes | Yes | Yes | Yes | Yes |
| Grammatical acceptability | Yes | Yes | Yes | Yes | No | Yes |
| Morphology preservation | Yes | Yes | No | No | No | Yes |
| Fluency and naturalness | Yes | Yes | Yes | Yes | Yes | Yes |
| Simplicity improvement | Yes | Yes | Yes | Yes | Yes | Yes |
| Vocabulary suitability | Yes | Yes | Yes | Yes | Yes | Yes |
| Sentence-structure suitability| Yes | Yes | Yes | Yes | Yes | Yes |
| Developmental suitability | No (`CANNOT_ASSESS`) | No (`CANNOT_ASSESS`) | Yes | Yes | Yes | Yes |
| Safety evaluation | Yes | Yes | Yes | Yes | Yes | Yes |
| Overall disposition | Yes | Yes | Yes | Yes | Yes | Yes |

---

## 3. Conflict of Interest Declarations

All reviewers completed mandatory conflict disclosure questionnaires before assignment generation:

1. **Rule Authorship:** None of the independent expert reviewers (`REV-S34-001` through `REV-S34-006`) participated in the code development or rule design of Stage 33.
2. **Text Publishing Sources:** All reviewers verified no financial or institutional conflict with the origin repositories or authors of Stage 31 text sources.
3. **Internal Team Isolation:** `REV-S34-TEAM1` is marked as a project-team member (`is_project_team_member: true`). Annotations by `REV-S34-TEAM1` are held in separate ledgers and excluded from the primary Krippendorff's alpha and Fleiss' kappa agreement analyses.
4. **Adjudication Neutrality:** `REV-S34-006` has no assigned first-pass production batches and resolves disputes without prior stance bias.

---

## 4. Protected Storage References

Detailed reviewer CVs, verified degree certificates, digitally signed consent acknowledgments (`S34-CONSENT-V1`), and payment records are preserved in external protected storage:
- Root: `protected://stage34/reviewers/`
- Schema and audit verification hash: `verified_reviewer_registry.sha256`
