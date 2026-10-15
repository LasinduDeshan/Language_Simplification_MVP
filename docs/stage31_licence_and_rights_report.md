# Stage 31 — Licence and Rights Review Report

**Stage:** Stage 31 — Sinhala External Dataset Ingestion and Pilot Corpus Creation  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** `docs/stage31_licence_and_rights_report.md`  
**Governing Standard:** Section 6, `docs/stage31_implementation_plan.md`  
**Status:** Frozen — Second-Person Governance Review Completed  
**Reviewer Identity:** `REV-GOV-01` (Pseudonymous Governance Reviewer)  
**Review Timestamp:** `2026-10-15T15:20:00Z`  
**Authoritative Prerequisite:** `stage-30-complete-v3` (`ef95667b53dddfb032e71fc51d6c524aff7a22a2`)

---

## 1. Executive Summary

In accordance with Section 6 of the Stage 31 Implementation Plan, every candidate source discovered in WP1 was evaluated against independent intellectual property, contractual, crawling compliance, and redistribution constraints. 

No candidate source was approved without an immutable evidence snapshot and cryptographic hash verification. Web crawling signals (`robots.txt`) were assessed independently from intellectual property licences, and technical text normalization was recognized as not extinguishing underlying author rights or licence obligations.

### Primary Decision Accounting Summary

Every candidate source belongs to exactly one mutually exclusive primary decision status:

$$
\text{TotalCandidates (8)} = \text{Approved (5)} + \text{MetadataOnly (1)} + \text{ReviewRequired (1)} + \text{Blocked (1)} + \text{SourceUnavailable (0)} + \text{Unaccounted (0)}
$$

$$\text{Accounting Status: 0 Unaccounted (RECONCILED)}$$

---

## 2. Primary Decision Registry

| Source ID | Source Name | Source Class | Primary Decision | Licence Name & Version | Ingestion Action |
|---|---|---|---|---|---|
| `SRC-SI-001` | Sinhala Wikipedia Official Dump | `encyclopedic_reference` | **`APPROVED`** | CC BY-SA 3.0 / CC BY-SA 4.0 | Eligible for WP3 retrieval & WP5 parsing |
| `SRC-SI-002` | AI4Bharat IndicCorp Sinhala Corpus | `open_research_corpus` | **`APPROVED`** | CC-BY 4.0 Research Use | Eligible for WP3 retrieval & WP5 parsing |
| `SRC-SI-003` | FLORES-200 Sinhala Benchmark Split | `open_research_corpus` | **`APPROVED`** | CC-BY-SA 4.0 | Eligible for WP3 retrieval & WP5 parsing |
| `SRC-SI-004` | UCSC LTRL Sinhala News / POS Corpus | `open_research_corpus` | **`APPROVED`** | Academic Non-Commercial Agreement | Eligible for WP3 retrieval (Internal research only) |
| `SRC-SI-005` | CC-100 Sinhala Monolingual Web Corpus | `web_crawled_text` | **`REVIEW_REQUIRED`** | Common Crawl Terms of Use 2020 | **BLOCKED** pending domain provenance review |
| `SRC-SI-006` | Dept. of Govt. Information Public Notices | `government_institutional` | **`METADATA_ONLY`** | Crown Copyright / Public Record | **BARRED** from text preprocessing pipelines |
| `SRC-SI-007` | Madura English-Sinhala Online Dictionary | `news_or_commercial` | **`BLOCKED`** | Proprietary Commercial Terms | **BLOCKED** from all retrieval and ingestion |
| `SRC-SI-008` | StoryWeaver Sinhala Children's Stories | `open_educational_resource` | **`APPROVED`** | CC-BY 4.0 International | Eligible for WP3 retrieval & WP5 parsing |

---

## 3. Immutable Evidence Snapshots & SHA-256 Hashes

All legal evidence, terms summaries, and licence declarations were captured and saved into `data/sinhala_external/registry/licence_snapshots/`. Each file was verified with an immutable SHA-256 digest:

| Snapshot File Name | Associated Sources | SHA-256 Checksum |
|---|---|---|
| `CC-BY-SA-3.0.txt` | `SRC-SI-001` | `810f40629c89130cb3ad67bd92a50ba03b424c28dab33c4e31a36b08a1c12f57` |
| `CC-BY-4.0.txt` | `SRC-SI-002`, `SRC-SI-008` | `584de4c9f788c0f0f6b6c111b7eacfe17c5228d0b9a8cba8c9bfaf9fce11e8d0` |
| `CC-BY-SA-4.0.txt` | `SRC-SI-003` | `c17d8a3e91c875e1757860f562ac6be2fd2d5d11d4a44908b583d60897467007` |
| `UCSC-LTRL-Academic-Research-Terms.txt` | `SRC-SI-004` | `60283a488ec063b7f3fbcb6cd7d87a9db9a4dd5d364f24e90751670f5e6f062a` |
| `CommonCrawl-Terms-2020.txt` | `SRC-SI-005` | `4f442c85397e972066227f629c891d3ce775330f8d78d3aeacd82e4b3148402b` |
| `NewsLK-Government-Terms.txt` | `SRC-SI-006` | `04bc335211c502256c32d872ddc3bf8573685adf7bd12464969a89f4534f9a2b` |
| `Madura-Online-Terms.txt` | `SRC-SI-007` | `bf16b2a58a9bde2e31b7003732b68cfa15de887dd043f290a14b2004a0688ffc` |

---

## 4. Independent Permission Profiles & Rights Attributes

For all candidate sources, independent permission attributes were determined and pinned to version 1 of their respective rights profiles:

| Source ID | Profile ID | Research Use | Download & Store | Modify & Process | Raw Redistribute | Derived Redistribute | Attribution Req. | Share-Alike Req. | Export Policy |
|---|---|---|---|---|---|---|---|---|---|
| `SRC-SI-001` | `RP-SRC-SI-001` | Yes | Yes | Yes | Yes | Yes | Yes | Yes | `PUBLIC_PERMITTED_CC_BY_SA` |
| `SRC-SI-002` | `RP-SRC-SI-002` | Yes | Yes | Yes | Yes | Yes | Yes | No | `PUBLIC_PERMITTED_CC_BY` |
| `SRC-SI-003` | `RP-SRC-SI-003` | Yes | Yes | Yes | Yes | Yes | Yes | Yes | `PUBLIC_PERMITTED_CC_BY_SA` |
| `SRC-SI-004` | `RP-SRC-SI-004` | Yes | Yes | Yes | **No** | **No** | Yes | No | **`PROTECTED_INTERNAL_ONLY`** |
| `SRC-SI-005` | `RP-SRC-SI-005` | No | No | No | No | No | Yes | No | `BLOCKED_REVIEW_REQUIRED` |
| `SRC-SI-006` | `RP-SRC-SI-006` | No | No | No | No | No | Yes | No | `METADATA_CATALOGUE_ONLY` |
| `SRC-SI-007` | `RP-SRC-SI-007` | No | No | No | No | No | Yes | No | `BLOCKED_PROPRIETARY` |
| `SRC-SI-008` | `RP-SRC-SI-008` | Yes | Yes | Yes | Yes | Yes | Yes | No | `PUBLIC_PERMITTED_CC_BY` |

### Specific Rights Enforcements

1. **`SRC-SI-004` (UCSC LTRL) Restricted Export:**  
   The UCSC LTRL Academic Research agreement permits internal computational simplification research and feature extraction but strictly forbids redistribution of raw text or derived corpora without written permission. Consequently, records derived from `SRC-SI-004` are marked `effective_export_policy: "PROTECTED_INTERNAL_ONLY"` and will not have literal text exposed in any public export artifact.
2. **`SRC-SI-006` (news.lk) Metadata Isolation:**  
   Under Governance Invariant 22, `SRC-SI-006` is catalogued solely for tracking public sector language registers. It is barred from entering text parsing, tokenization, or pilot corpus inclusion.
3. **`SRC-SI-007` (Madura Online) Commercial Prohibition:**  
   The website terms explicitly state "all rights reserved" and disallow automated extraction. The source is marked `BLOCKED` with `robots_txt_status: "DISALLOWED"`. No data will be retrieved.
4. **`SRC-SI-005` (CC-100) Common Crawl Provenance Barrier:**  
   Because Common Crawl terms disclaim copyright ownership of crawled articles, mass ingestion without domain-level copyright clearance carries substantial intellectual property infringement risks. Routed to `REVIEW_REQUIRED`.
5. **Rights Profile Validity Dates:**  
   All approved profiles establish `rights_profile_effective_at: "2026-10-15T12:00:00Z"` and `rights_profile_review_due_at: "2027-10-15T12:00:00Z"`. Any attempt to ingest text past this expiration date will trigger an automated ingestion gate error.

---

## 5. Ingestion Gate Rules & Implementation Directives

1. **Only Primary `APPROVED` Sources May Enter WP3:**
   The acquisition pipeline must reject any source whose primary decision is not `APPROVED`.
2. **Multi-Source Duplicate Attribution Rule:**
   When duplicates are detected across sources (e.g. text appearing in both Wikipedia and CC-100), the retained pilot candidate must aggregate all contributing source IDs and adopt the **most restrictive** export policy (Section 15.1).
3. **URL Sanitization Invariant:**
   All acquisition calls in WP3 must reference `canonical_url_sanitized` and strip any ephemeral authentication tokens or signed query parameters prior to creating receipts.
4. **Physical Storage Decoupling:**
   Downloaded raw bytes and derived normalized text for the 5 approved sources must be written exclusively to `<SINHALA_EXTERNAL_PROTECTED_ROOT>/sinhala_external/` and never inside the Git repository tree.

---

## 6. Reviewer Signoff

The technical governance review confirms that all 8 candidate sources have been evaluated against verified licence terms and legal disclaimers. Accounting is verified with 0 unaccounted candidates. The approved sources registry is sealed for technical execution.

```text
Technical Reviewer:         REV-GOV-01
Reviewer Identity Verified: false (internal technical reviewer)
Decision:                   CONCURRED_AND_SEALED_TECHNICAL
Independent Legal Review:   NOT ESTABLISHED
Approved Sources:           5 (SRC-SI-001, SRC-SI-002, SRC-SI-003, SRC-SI-004, SRC-SI-008)
Blocked/Excluded:           3 (SRC-SI-005 Review, SRC-SI-006 Metadata Only, SRC-SI-007 Blocked)
Timestamp:                  2026-10-15T17:15:00Z
```
