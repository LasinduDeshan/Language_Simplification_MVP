# Stage 31 — Governance, Rights Enforcement, and Compliance Report

**Stage:** Stage 31 — Sinhala External Dataset Ingestion and Pilot Corpus Creation  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** `docs/stage31_governance_report.md`  
**Governing Standards:** Governance Invariants 1–25, `docs/stage31_implementation_plan.md`  
**Status:** Frozen — Reconciled Technical Governance Concurrence Sealed (v2)  
**Technical Governance Reviewer:** `REV-GOV-01` (Internal technical reviewer; identity verified: false)  
**Review Timestamp:** `2026-10-15T17:15:00Z`  
**Authoritative Prerequisite:** `stage-30-complete-v3` (`ef95667b53dddfb032e71fc51d6c524aff7a22a2`)

---

## 1. Executive Governance Summary & Scope Clarifications

Stage 31 establishes the foundational external Sinhala text ingestion and pilot corpus creation pipeline under strict ethical, legal, and educational governance.

### Core Governance Declarations

```json
{
  "validation_status": "draft",
  "research_eligible": false,
  "approved_for_child_delivery": false,
  "approved_for_unsupervised_child_delivery": false,
  "requires_expert_review": true
}
```

```text
Technical governance reviewer: REV-GOV-01
Reviewer identity verified:    false (pseudonymous internal technical reviewer)
Independent legal review:      NOT ESTABLISHED
Sinhala linguistic review:     NOT ESTABLISHED
Child-development review:      NOT ESTABLISHED
```

> [!IMPORTANT]
> **Governance Scope Clarification:**
> Technical governance concurrence represents internal technical verification only. It does not imply legal, linguistic, clinical, or pedagogical approval. Under no circumstances may any raw or derived external corpus record be served to child learners or deployed in unsupervised classroom environments without independent clinical and pedagogical expert review.

---

## 2. Intellectual Property Rights & Export Policy Enforcement

In accordance with Sections 6 and 17 of the Implementation Plan, individual source licensing obligations were enforced at every stage of the pipeline:

1. **`SRC-SI-004` (UCSC LTRL) Non-Redistribution Enforcement:**
   - Under the Academic Research Use Agreement, redistribution of raw text or derived corpora is prohibited without written authorization.
   - All 30 records originating from `SRC-SI-004` carry `effective_export_policy: "PROTECTED_INTERNAL_ONLY"` and `literal_text_redistributable: false`.
   - **Confirmed Scope:** All 30 `SRC-SI-004` records are **completely excluded from every literal-text public artifact** (including `public_export_corpus.jsonl` where `text: null`, `export_redistribution_status: "LITERAL_TEXT_SUPPRESSED_PROTECTED_INTERNAL_ONLY"`).
2. **Attribution & Permitted Redistribution:**
   - Literal text from the other four approved sources (`SRC-SI-001`, `SRC-SI-002`, `SRC-SI-003`, `SRC-SI-008`) is exported only because their pinned rights profiles (`PUBLIC_PERMITTED_CC_BY_SA` and `PUBLIC_PERMITTED_CC_BY`) explicitly permit redistribution with attribution.
3. **`SRC-SI-006` (news.lk) Metadata Isolation:**
   - Retained in catalog registry for public sector language tracking, but permanently isolated from text acquisition, parsing, and pilot corpus pipelines.
4. **`SRC-SI-007` (Madura Online) Commercial Prohibition:**
   - Website terms prohibit automated scraping. Marked `BLOCKED` with `robots_txt_status: "DISALLOWED"`. No data was acquired.

---

## 3. Privacy and Sensitive Information Findings

```text
Automated privacy flags detected: 0
Manual protected-sample review: NOT PERFORMED
Absence of all personal information: NOT ESTABLISHED
```

- **Automated Screening:** Regular expression scanning for emails, telephone numbers, national identifiers (NIC), and API credentials detected **zero flags**.
- **Important Qualification:** Automated screening rules cannot establish the absolute absence of personal information or private disclosures; manual expert review has not been performed.
- **Quarantine Isolation:** The quarantine mechanism is active and operational in external storage; zero private records were required to be routed to quarantine during pilot acquisition.

---

## 4. Physical Storage Decoupling & Secret Isolation

In accordance with Governance Invariants 7, 8, 10, and 13:

- **Decoupled External Storage:** Raw source payloads and normalized document text are stored exclusively outside the Git repository at `<SINHALA_EXTERNAL_PROTECTED_ROOT>/sinhala_external/`.
- **Zero Raw Text in Git:** Automated checks confirmed that zero raw or normalized text files exist within the Git repository tree.
- **Zero Unkeyed Hashes in Git:** Automated checks confirmed that unkeyed text hashes are absent from Git history, commit messages, logs, CI artifacts, exception traces, and test snapshots.
- **Keyed HMAC Public Ledger:** Repository records expose only versioned keyed HMAC-SHA-256 digests (`HMAC-2026-V1`, schema `sinhala-pilot-record:v1`). The 256-bit secret key is sequestered in `<protected-root>/sinhala_external/deduplication/hmac_secret.key`.
- **URL Secret Sanitization:** All acquisition receipts in `data/sinhala_external/receipts/` have credentials, session tokens, and query secrets stripped (`sensitive_query_parameters_removed: true`).

---

## 5. Development Pool Isolation & Evaluation Split Integrity

In accordance with Governance Invariants 18 and 19:

- **Predeclared Method-Development Pool:** Exactly 90 units were predeclared and locked in WP3 before parser implementation.
- **Component Classification:** All transitive split groups containing method-development units were tagged `TRAIN_ONLY_DEVELOPMENT_COMPONENT` and assigned strictly to `train`.
- **Split Ratio Reconciliation:**
  - Untouched evaluation-eligible records (90 units): 64 train (71.1%) / 13 validation (14.4%) / 13 locked test (14.4%) $\approx 70/15/15$.
  - Combined corpus (180 units): 154 train (85.6%) / 13 validation (7.2%) / 13 locked test (7.2%).
- **Zero Evaluation Contamination:** Automated audits proved **0 method-development records** in `validation` or `locked_test`.
- **Four-Dimensional Zero Leakage:** Zero cross-split leakage verified across split groups, document groups, exact duplicate clusters, or confirmed near-duplicates.

---

## 6. Technical Reviewer Signoff

```text
Technical Governance Reviewer: REV-GOV-01
Reviewer Identity Verified:    false (pseudonymous internal technical reviewer)
Governance Status:             CONCURRED_AND_SEALED_TECHNICAL_V2
Validation Status:             draft
Research Eligible:             false (retained across all 180 accepted records)
Child Delivery:                BLOCKED_PENDING_EXPERT_REVIEW
Independent Legal Review:      NOT ESTABLISHED
Sinhala Linguistic Review:     NOT ESTABLISHED
Child-Development Review:      NOT ESTABLISHED
Timestamp:                     2026-10-15T17:15:00Z
```
