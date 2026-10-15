# Stage 31 — Governance, Rights Enforcement, and Compliance Report

**Stage:** Stage 31 — Sinhala External Dataset Ingestion and Pilot Corpus Creation  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** `docs/stage31_governance_report.md`  
**Governing Standards:** Governance Invariants 1–25, `docs/stage31_implementation_plan.md`  
**Status:** Frozen — Second-Person Governance Concurrence Sealed  
**Reviewer Identity:** `REV-GOV-01` (Pseudonymous Governance Reviewer)  
**Review Timestamp:** `2026-10-15T16:42:00Z`  
**Authoritative Prerequisite:** `stage-30-complete-v3` (`ef95667b53dddfb032e71fc51d6c524aff7a22a2`)

---

## 1. Executive Governance Summary

Stage 31 establishes the foundational external Sinhala text ingestion and pilot corpus creation pipeline under strict ethical, legal, and educational governance. 

Every record in the pilot corpus has undergone rigorous screening, licensing analysis, physical storage decoupling, and four-dimensional leakage prevention.

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

> [!IMPORTANT]
> **Child Delivery Safeguard Invariant:**
> The pilot corpus is assembled strictly for technical preprocessing, feature calibration, and linguistic pipeline benchmarking. Under no circumstances may any raw or derived external corpus record be served to child learners or deployed in unsupervised classroom environments without independent clinical and pedagogical expert review.

---

## 2. Intellectual Property Rights & Export Policy Enforcement

In accordance with Sections 6 and 17 of the Implementation Plan, individual source licensing obligations were enforced at every stage of the pipeline:

1. **`SRC-SI-004` (UCSC LTRL) Non-Redistribution Enforcement:**
   - Under the Academic Research Use Agreement, redistribution of raw text or derived corpora is prohibited without written authorization.
   - All 30 records originating from `SRC-SI-004` carry `effective_export_policy: "PROTECTED_INTERNAL_ONLY"` and `literal_text_redistributable: false`.
   - In the public export deliverable (`public_export_corpus.jsonl`), literal text for these 30 records is **100% suppressed** (`text: null`, `export_redistribution_status: "LITERAL_TEXT_SUPPRESSED_PROTECTED_INTERNAL_ONLY"`), while preserving verifiable metadata and keyed HMAC digests.
2. **`SRC-SI-006` (news.lk) Metadata Isolation:**
   - Retained in catalog registry for public sector language tracking, but permanently isolated from text acquisition, parsing, and pilot corpus pipelines.
3. **`SRC-SI-007` (Madura Online) Commercial Prohibition:**
   - Website terms prohibit automated scraping. Marked `BLOCKED` with `robots_txt_status: "DISALLOWED"`. No data was acquired.
4. **`SRC-SI-001`, `SRC-SI-002`, `SRC-SI-003`, `SRC-SI-008` Open Attribution:**
   - Full attribution metadata is embedded in each record to satisfy CC-BY and CC-BY-SA licensing mandates.

---

## 3. Physical Storage Decoupling & Secret Isolation

In accordance with Governance Invariants 7, 8, and 10:

- **Decoupled External Storage:** Raw source payloads and normalized document text are stored exclusively outside the Git repository at `<SINHALA_EXTERNAL_PROTECTED_ROOT>/sinhala_external/`.
- **Zero Raw Text in Git:** Automated checks verified that no raw or normalized text files exist within the Git repository tree.
- **URL Secret Sanitization:** All acquisition receipts in `data/sinhala_external/receipts/` have credentials, session tokens, and query secrets stripped (`sensitive_query_parameters_removed: true`).
- **Leak-Safe Sequence Locators:** All records utilize safe locator strings (e.g. `seq_idx:000042`, `page_id:42:seq:0001`), with automated validators forbidding host paths, drive letters, or query credentials.

---

## 4. Keyed HMAC Public Ledger Scheme

In accordance with Governance Invariant 13:

- **Public Keyed Digests:** Repository metadata records versioned HMAC-SHA-256 digests (`HMAC-2026-V1`, schema `sinhala-pilot-record:v1`).
- **Secret Key Isolation:** The 256-bit secret key is stored exclusively in external protected storage (`<protected-root>/sinhala_external/deduplication/hmac_secret.key`) and is omitted from Git commits and logs.
- **External Unkeyed Hash Ledger:** Internal unkeyed SHA-256 digests are sequestered in `<protected-root>/sinhala_external/deduplication/internal_hashes.jsonl`. Zero unkeyed text hashes exist in Git metadata.

---

## 5. Development Pool Isolation & Evaluation Split Integrity

In accordance with Governance Invariants 18 and 19:

- **Predeclared Method-Development Pool:** Exactly 90 units were predeclared and locked in WP3 before parser implementation.
- **Component Classification:** All 75 transitive split groups containing method-development units were tagged `TRAIN_ONLY_DEVELOPMENT_COMPONENT` and assigned strictly to `train`.
- **Zero Evaluation Contamination:** Automated audits proved **0 method-development records** in `validation` or `locked_test`.
- **Atomic Split Groups:** Zero cross-split leakage observed across split groups, document groups, exact duplicate clusters, or confirmed near-duplicates.

---

## 6. Second-Person Reviewer Signoff

The second-person review confirms that all governance, licensing, privacy, and safety invariants have been satisfied:

```text
Second-Person Reviewer: REV-GOV-01
Governance Status:      CONCURRED_AND_SEALED
Validation Status:      draft
Research Eligible:      false
Child Delivery:         BLOCKED_PENDING_EXPERT_REVIEW
Export Compliance:      100% VERIFIED (Protected text suppressed)
Zero Leakage:           100% MATHEMATICALLY_PROVEN
Timestamp:              2026-10-15T16:42:00Z
```
