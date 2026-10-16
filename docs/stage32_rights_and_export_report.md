# Stage 32 Rights and Export Report

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** Rights Inheritance and Public Export Report  
**Stage:** Stage 32 — Sinhala Child-Vocabulary Lexicon Construction  
**Status:** Authoritative Report Deliverable  

---

## 1. Executive Summary & Rights Governance

Stage 32 enforces rigorous IP and privacy boundaries when deriving lexical evidence from external Sinhala datasets. 

Key governance invariants verified:
1. **Rights Inheritance:** Every lexicon entry inherits obligations from all contributing sources using version-pinned references (`source_id`, `rights_profile_id`, `rights_profile_version`).
2. **Most Restrictive Rule:** When terms occur across multiple sources with conflicting rights, the most restrictive export policy is applied.
3. **Field-Level Exposure:** Granular permissions separate abstract lexical items from full sentences and definitions.
4. **Physical Decoupling:** Context sentences and raw concordances remain strictly in external protected storage (`protected://sinhala_lexicon/...`).
5. **Privacy by Design:** Public files contain zero personal data, zero reconstructable text passages, and zero guessable unkeyed SHA-256 hashes of short phrases.

---

## 2. Inherited Rights Profiles & Source-Entry Accounting

> **Authoritative Rights Notice:**  
> Licence labels shown in Stage 32 are descriptive only. The authoritative rights decision is the exact `rights_profile_id` and `rights_profile_version` inherited from `stage-31-complete-v8`.

| Source ID | Source Name | Descriptive Licence Label | Contributing Entries (Memberships) | Included Token Occurrences | Pinned Stage 31 Rights Profile ID | Inherited Profile Version | Field Export Posture |
|---|---|---|---:|---:|---|---:|---|
| `SRC-SI-001` | Sinhala Wikipedia Official Dump | CC BY-SA 4.0 (Wikimedia pinned) | 448 | 1,450 | `RP-SRC-SI-001` | 1 | `PUBLIC_PERMITTED_STANDALONE` |
| `SRC-SI-002` | AI4Bharat IndicCorp Sinhala | CC BY-NC-SA 4.0 | 207 | 594 | `RP-SRC-SI-002` | 2 | `SUPPRESSED_BY_PROJECT_POLICY` |
| `SRC-SI-003` | FLORES-200 Sinhala Benchmark | CC BY-SA 4.0 | 179 | 448 | `RP-SRC-SI-003` | 1 | `PUBLIC_PERMITTED_STANDALONE` |
| `SRC-SI-004` | UCSC LTRL Sinhala News / POS | Academic Research Agreement | 215 | 946 | `RP-SRC-SI-004` | 1 | `PROTECTED_INTERNAL_ONLY` |
| `SRC-SI-008` | StoryWeaver Sinhala Children | CC BY 4.0 | 145 | 230 | `RP-SRC-SI-008` | 1 | `PUBLIC_PERMITTED_STANDALONE` |
| **Total** | **All 5 Contributing Sources** | **Inherited from Stage 31 v8** | **1,194** | **3,668** | **All 5 Validated** | **Exact Equality** | **Zero Field Leaks** |

> **Note on SRC-SI-002:**  
> - Effective Stage 32 export policy: `SUPPRESSED_BY_PROJECT_POLICY`  
> - Underlying licence observation: CC BY-NC-SA 4.0 may permit qualifying standalone noncommercial redistribution, subject to attribution and share-alike obligations; Stage 32 does not enable that export.

### Accounting Breakdown
- Distinct lexicon entries: 1,010
- Entry-source memberships: 1,194
- Entries occurring in multiple sources: 138 (124 in 2 sources, 14 in 3 sources)
- Entries occurring in a single source: 872
- Included token occurrences: 3,668
- Missing rights-profile references: 0
- Unregistered contributing sources: 0

$$\sum_{e=1}^{1010}|\text{contributing sources}_e|=1,194$$

Do not sum the five source-specific entry counts directly into "1,010 distinct entries." The sum represents 1,194 entry-source memberships across 1,010 distinct lexicon entries.

### Reconciliation of Review Units (4 Token Occurrences vs. 8 Candidate Entries)
- **Token Occurrence Bridge (Level 2):** 4 token occurrences (`MIXED_SCRIPT_TOKEN`) were isolated at ingestion and excluded from candidate entry generation.
- **Candidate Quality Router (Level 3):** 8 candidate entries were routed to `MANUAL_REVIEW_REQUIRED` (6 sensitive/clinical items under `SENSITIVE_VOCABULARY_FLAG` + 2 suspected character repetition/OCR edge cases).
- Low-confidence morphology referrals: 0 (all 1,010 candidate entries retained identity canonical form with confidence 1.0). The two metrics represent independent quality filters across distinct architectural levels.

---

## 3. Field-Level Export Matrix

| Field Name | Resolved Public Export Policy | Exposure Rationale |
|---|---|---|
| `entry_id` | `PUBLIC_PERMITTED_AGGREGATE` | Synthetic opaque ID; zero IP risk. |
| `canonical_form` | `PUBLIC_PERMITTED_STANDALONE` | Standalone lexical word; permitted where source terms allow derived processing. |
| `frequencies` ($f_c, df_c, f_w$) | `PUBLIC_PERMITTED_AGGREGATE` | Statistical aggregate metrics. |
| `source_dispersion` ($D_s$) | `PUBLIC_PERMITTED_AGGREGATE` | Mathematical dispersion metric. |
| `grapheme_count`, `code_point_count` | `PUBLIC_PERMITTED_AGGREGATE` | Unicode structural metrics. |
| `concordance_contexts` | `RESTRICTED_PROTECTED_INTERNAL` | Contains full sentences; restricted to external protected storage. |
| `definitions` / `senses` | `RESTRICTED_PROTECTED_INTERNAL` | Unreviewed semantic descriptions; protected. |

---

## 4. Cryptographic Protection & HMAC Domain Separation

For public occurrence tracking, Stage 32 uses keyed HMAC-SHA-256 digests with explicit domain separation:

$$\text{HMAC}(\text{key}, \text{"sinhala-lexicon-surface-form:v1:"} \parallel \text{occurrence\_id} \parallel \text{surface\_form})$$

- Secret key is stored strictly outside Git under `~/.sinhala_lexicon_protected_data/sinhala_lexicon/hmac_secret.key`.
- Keyed HMAC prevents offline dictionary guessing attacks on short Sinhala words.
- In Git schemas, `surface_form_hmac` defaults to `null` and is populated exclusively at runtime.

---

## 5. Empirical Export Safety Verification

A complete safety scan over `public_metadata_export.jsonl` confirmed:
- Restricted source sentences in public export: **0**
- Concordance snippets leaked: **0**
- Plain/unkeyed SHA-256 hashes in public export: **0**
- Unaccounted entries: **0**
