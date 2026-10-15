# Stage 31 — Accounting Summary Report

**Stage:** Stage 31 — Sinhala External Dataset Ingestion and Pilot Corpus Creation  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** `docs/stage31_accounting_summary.md`  
**Governing Standard:** Section 18, `docs/stage31_implementation_plan.md`  
**Status:** Frozen — Authoritative Conservation Ledger (Reconciled v3)  
**Authoritative Prerequisite:** `stage-30-complete-v3` (`ef95667b53dddfb032e71fc51d6c524aff7a22a2`)  
**Sealed Timestamp:** `2026-10-15T19:50:00+05:30` (UTC: `2026-10-15T14:20:00Z`)  
**Technical Governance Reviewer:** `REV-GOV-01` (Internal technical reviewer; identity verified: false)  
**Internal Technical Governance Concurrence:** RECORDED  
**Independent Governance Signoff:** NOT ESTABLISHED  
**Independent Legal / Linguistic / Child-Development Reviews:** NOT ESTABLISHED

---

## 1. Executive Reconciliation Summary

In accordance with Section 18 of the Implementation Plan, every entity in Stage 31—from candidate sources to retrieved raw payloads, staged document records, near-duplicate candidates, exact-duplicate clusters, and corpus partitions—was tracked under strict zero-loss conservation accounting. 

Every accounting balance equation has been reconciled with **zero unaccounted items**.

---

## 2. Equation 1: Candidate-Source Accounting (Section 18.1)

Every candidate source discovered in WP1 belongs to exactly one mutually exclusive status category:

$$
\text{TotalCandidates (8)} = \text{Approved (5)} + \text{MetadataOnly (1)} + \text{ReviewRequired (1)} + \text{Blocked (1)} + \text{SourceUnavailable (0)} + \text{Unaccounted (0)}
$$

| Source ID | Source Name | Primary Decision | Reconciliation Category |
|---|---|---|---|
| `SRC-SI-001` | Sinhala Wikipedia Official Dump | `APPROVED` | Approved |
| `SRC-SI-002` | AI4Bharat IndicCorp Sinhala Corpus | `APPROVED` | Approved |
| `SRC-SI-003` | FLORES-200 Sinhala Benchmark Split | `APPROVED` | Approved |
| `SRC-SI-004` | UCSC LTRL Sinhala News / POS Corpus | `APPROVED` | Approved |
| `SRC-SI-005` | CC-100 Sinhala Monolingual Web Corpus | `REVIEW_REQUIRED` | ReviewRequired |
| `SRC-SI-006` | Dept. of Govt. Information Public Notices | `METADATA_ONLY` | MetadataOnly |
| `SRC-SI-007` | Madura English-Sinhala Online Dictionary | `BLOCKED` | Blocked |
| `SRC-SI-008` | StoryWeaver Sinhala Children's Stories | `APPROVED` | Approved |
| **Total** | | | **8 Reconciled (0 Unaccounted)** |

---

## 3. Equation 2: Retrieved-File Accounting (Section 18.2)

Every approved candidate source planned for retrieval was tracked through acquisition:

$$
\text{ExpectedFiles (5)} = \text{DownloadedVerified (5)} + \text{Failed (0)} + \text{NotAttempted (0)} + \text{Quarantined (0)} + \text{Unaccounted (0)}
$$

| Retrieval ID | Source ID | File Name | Byte Size | SHA-256 Digest | Status |
|---|---|---|---|---|---|
| `RET-SI-001-001` | `SRC-SI-001` | `siwiki_sample.xml` | 33,229 | `e8a12315aec2d0b4...` | DownloadedVerified |
| `RET-SI-002-001` | `SRC-SI-002` | `indiccorp_si_sample.jsonl` | 12,365 | `712baa1f226626a9...` | DownloadedVerified |
| `RET-SI-003-001` | `SRC-SI-003` | `flores200_si_sample.tsv` | 8,646 | `22c8324b8473a9b2...` | DownloadedVerified |
| `RET-SI-004-001` | `SRC-SI-004` | `ltrl_news_sample.txt` | 17,912 | `a8b15d5f428bda30...` | DownloadedVerified |
| `RET-SI-008-001` | `SRC-SI-008` | `storyweaver_si_sample.json` | 34,240 | `8cbaf0bb46a11643...` | DownloadedVerified |
| **Total** | | | **106,392** | | **5 Reconciled (0 Unaccounted)** |

---

## 4. Equation 3: Parsed-Unit Accounting (Section 18.3)

Every parsed unit from acquired raw files was accounted for:

$$
\text{SourceUnits (180)} = \text{Parsed (180)} + \text{SkippedByPolicy (0)} + \text{ParseFailed (0)} + \text{Quarantined (0)} + \text{Unaccounted (0)}
$$

| Source ID | Format | Parsed Units | Method-Dev Units | Untouched Units | Safe Locator |
|---|---|---|---|---|---|
| `SRC-SI-001` | XML | 40 | 20 (`[0..19]`) | 20 (`[20..39]`) | `page_id:X:seq:YYYY` |
| `SRC-SI-002` | JSONL | 40 | 20 (`[0..19]`) | 20 (`[20..39]`) | `line_idx:YYYYY` |
| `SRC-SI-003` | TSV | 35 | 15 (`[0..14]`) | 20 (`[15..34]`) | `row_idx:YYYYY` |
| `SRC-SI-004` | TXT | 30 | 15 (`[0..14]`) | 15 (`[15..29]`) | `story_idx:YYYY` |
| `SRC-SI-008` | JSON | 35 | 20 (`[0..19]`) | 15 (`[20..34]`) | `story_idx:YYYY` |
| **Total** | | **180** | **90** | **90** | **180 Reconciled (0 Unaccounted)** |

---

## 5. Equation 4: Terminal-Disposition Accounting & Model C Reconciliation (Section 18.4)

Every preprocessed record was evaluated against privacy, quality, rights, and scope criteria:

$$
\text{CandidateRecords (180)} = \text{Accepted (180)} + \text{ManualReview (0)} + \text{Rejected (0)} + \text{Excluded (0)} + \text{Quarantined (0)} + \text{Unaccounted (0)}
$$

### Explicit Terminal Disposition Subtypes
- `ACCEPTED_PILOT_CANDIDATE`: **180**
- `MANUAL_REVIEW_REQUIRED`: **0**
- `REJECTED_RIGHTS`: **0**
- `REJECTED_SECURITY`: **0**
- `REJECTED_PRIVACY`: **0**
- `REJECTED_INVALID_UNICODE`: **0**
- `REJECTED_QUALITY`: **0**
- `EXCLUDED_NON_SINHALA`: **0**
- `EXCLUDED_DUPLICATE`: **0** (Model C Retained)
- `EXCLUDED_OUT_OF_SCOPE`: **0**
- `QUARANTINED_SOURCE_ERROR`: **0**
- **Unaccounted:** **0**

### Exact-Duplicate Accounting & Model C Formal Protocol Deviation
Under the approved baseline plan, exact duplicates were eligible for `EXCLUDED_DUPLICATE` with one canonical representative retained. In Stage 31, **Model C (Duplicates Intentionally Retained)** was applied:
- **Total Candidate Records:** 180
- **Total Exact Clusters Formed:** 150
- **Single-Member Clusters:** 145 (145 records)
- **Multi-Member Clusters:** 5 clusters (`DUP-SI-000146` through `DUP-SI-000150`, 7 records each = 35 records)
- **Canonical Representatives:** 150
- **Retained Exact-Duplicate Records:** **30** (surplus across 5 clusters)
- **`EXCLUDED_DUPLICATE` Count:** 0
- **Protocol Deviation Justification:** In early-grade educational reader series (StoryWeaver), natural narrative refrains, recurring character dialogues, and story progressions intentionally repeat across difficulty tiers. All 30 duplicate records were intentionally retained to evaluate simplification model behavior on repetitive early-grade text.
- **Leakage Prevention Enforcement:** Every duplicate member across all 5 multi-member clusters was bound into the exact same `split_group_id` (`SPLIT-GRP-SI-000146` to `SPLIT-GRP-SI-000150`) and assigned exclusively to `train`.
- **Duplicate Cross-Split Leakage:** **0 (PASSED)**

---

## 6. Equation 5: Near-Duplicate Candidate Reconciliation

Across all 180 records, all candidate pairs with token/char Jaccard similarity $\ge 0.80$ were reconciled prior to split assignment:

$$
\text{NearDuplicateCandidates (108)} = \text{ConfirmedDuplicateRelation (105)} + \text{ConservativelyUnioned (3)} + \text{RejectedAsDistinct (0)} + \text{UnresolvedAtSealing (0)}
$$

- **Confirmed as duplicate relation ($\ge 0.90$):** 105 pairs
- **Conservatively unioned into split groups ($0.80 \le \text{sim} < 0.90$):** 3 pairs
- **Rejected as distinct:** 0 pairs
- **Unresolved at split sealing:** **0 pairs (100% resolved)**

---

## 7. Equation 6: Pilot Corpus Split Accounting (Section 18.5)

### Explanation of Split-Ratio Allocation
The planned 70/15/15 allocation was applied **only to the 90 untouched evaluation-eligible records**. The 90 method-development records were mandatorily assigned to `train` (in accordance with Invariants 18 & 19), producing an overall 85.6% / 7.2% / 7.2% corpus distribution:

$$
\text{Untouched Records (90)} = \text{Untouched Train (64, 71.1\%)} + \text{Validation (13, 14.4\%)} + \text{Locked-Test (13, 14.4\%)}
$$

$$
\text{TotalCorpus (180)} = \text{Train (154, 85.6\%)} + \text{Validation (13, 7.2\%)} + \text{Locked-Test (13, 7.2\%)} + \text{Unaccounted (0)}
$$

| Split Partition | Overall Count | Overall Ratio | Method-Dev Units | Untouched Units | Untouched Ratio |
|---|---|---|---|---|---|
| **`train`** | **154** | 85.6% | **90** (100% dev pool) | 64 | 71.1% |
| **`validation`** | **13** | 7.2% | **0** | 13 | 14.4% |
| **`locked_test`** | **13** | 7.2% | **0** | 13 | 14.4% |
| **Total** | **180** | 100.0% | **90** | **90** | **100.0%** |

---

## 8. Redistribution and Licence Compatibility Framework

For the four sources whose literal text is exported in `public_export_corpus.jsonl`:

| Source ID | Source Name | Pinned Licence Version | Share-Alike Obligation | Attribution Mandate |
|---|---|---|---|---|
| `SRC-SI-001` | Sinhala Wikipedia | CC BY-SA 3.0 / 4.0 Dual | **YES (CC BY-SA)** | Credit "Contributors to Sinhala Wikipedia" + URL |
| `SRC-SI-002` | IndicCorp Sinhala | CC BY 4.0 | No (Permissive) | Cite AI4Bharat IndicCorp (Kakwani et al., 2020) |
| `SRC-SI-003` | FLORES-200 | CC BY-SA 4.0 | **YES (CC BY-SA)** | Cite NLLB Team, Meta AI (2022) |
| `SRC-SI-008` | StoryWeaver | CC BY 4.0 | No (Permissive) | Credit Pratham Books StoryWeaver + Authors/Illustrators |

### Corpus-Level Licence Compatibility Decision
1. **Per-Record Attribution:** In `public_export_corpus.jsonl`, each record retains its granular source ID, licence tag, and attribution metadata.
2. **Derivative Adaptation Licence Inheritance:** Any integrated derivative adaptation combining CC BY-SA records (`SRC-SI-001`, `SRC-SI-003`) with CC BY records inherits the **CC BY-SA 4.0** share-alike licence for the composite derivative.
3. **Protected Academic Corpus Isolation:** All 30 records originating from `SRC-SI-004` (UCSC LTRL) have literal text **100% suppressed** (`text: null`), completely preventing any public redistribution of restricted academic text.

---

## 9. Manifest Scope and Location Reconciliation

1. **Planned Documentation Manifest (`docs/stage31_manifest.sha256`):**
   - Required documentation deliverables: **12**
   - Manifest-controlled documentation files: **11**
   - Checksum manifest: **1** (excludes itself)
   - Balance formula:
     $$12 = 11 \text{ manifest-controlled documentation files} + 1 \text{ checksum manifest}$$
2. **Expanded Governed Implementation Manifest (`data/sinhala_external/manifests/stage31_manifest.sha256`):**
   - Controls **29 distinct implementation and documentation artifacts** across `docs/`, `data/sinhala_external/registry/`, `data/sinhala_external/receipts/`, and `data/sinhala_external/corpus/`.
   - The checksum manifest does not claim to hash itself.

---

## 10. Governance and Signoff

```text
Accounting Ledger:                         100% RECONCILED
Total Unaccounted Items:                   0
Technical Governance Reviewer:             REV-GOV-01
Reviewer Identity Verified:                false (internal technical reviewer)
Internal Technical Governance Concurrence: RECORDED
Independent Governance Signoff:            NOT ESTABLISHED
Independent Legal Review:                  NOT ESTABLISHED
Sinhala Linguistic Review:                 NOT ESTABLISHED
Child-Development Review:                  NOT ESTABLISHED
Sealed Timestamp:                          2026-10-15T19:50:00+05:30 (UTC: 2026-10-15T14:20:00Z)
Authoritative Status:                      SEALED_RECONCILED_V3
```
