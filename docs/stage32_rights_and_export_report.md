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

## 2. Field-Level Export Matrix

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

## 3. Cryptographic Protection & HMAC Domain Separation

For public occurrence tracking, Stage 32 uses keyed HMAC-SHA-256 digests with explicit domain separation:

$$\text{HMAC}(\text{key}, \text{"sinhala-lexicon-surface-form:v1:"} \parallel \text{occurrence\_id} \parallel \text{surface\_form})$$

- Secret key is stored strictly outside Git under `~/.sinhala_lexicon_protected_data/sinhala_lexicon/hmac_secret.key`.
- Keyed HMAC prevents offline dictionary guessing attacks on short Sinhala words.
- In Git schemas, `surface_form_hmac` defaults to `null` and is populated exclusively at runtime.

---

## 4. Empirical Export Safety Verification

A complete safety scan over `public_metadata_export.jsonl` confirmed:
- Restricted source sentences in public export: **0**
- Concordance snippets leaked: **0**
- Plain/unkeyed SHA-256 hashes in public export: **0**
- Unaccounted entries: **0**
