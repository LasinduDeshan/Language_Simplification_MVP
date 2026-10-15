# Stage 31 — Accounting Summary Report

**Stage:** Stage 31 — Sinhala External Dataset Ingestion and Pilot Corpus Creation  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** `docs/stage31_accounting_summary.md`  
**Governing Standard:** Section 18, `docs/stage31_implementation_plan.md`  
**Status:** Frozen — Complete Stage 31 Accounting Reconciliation  
**Authoritative Prerequisite:** `stage-30-complete-v3` (`ef95667b53dddfb032e71fc51d6c524aff7a22a2`)

---

## 1. Executive Reconciliation Summary

In accordance with Section 18 of the Implementation Plan, every entity in Stage 31—from candidate sources to retrieved raw payloads, staged document records, and corpus partitions—was tracked under strict zero-loss conservation accounting. 

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

## 5. Equation 4: Terminal-Disposition Accounting (Section 18.4)

Every preprocessed record was evaluated against privacy, quality, and scope criteria:

$$
\text{CandidateRecords (180)} = \text{Accepted (180)} + \text{ManualReview (0)} + \text{Rejected (0)} + \text{Excluded (0)} + \text{Quarantined (0)} + \text{Unaccounted (0)}
$$

| Disposition Code | Category | Record Count | Governance Action |
|---|---|---|---|
| `ACCEPTED_PILOT_CANDIDATE` | Accepted | **180** | Ingested into pilot corpus |
| `REJECTED_RIGHTS` | Rejected | 0 | None rejected |
| `REJECTED_SECURITY` | Rejected | 0 | None rejected |
| `REJECTED_PRIVACY` | Rejected | 0 | None rejected |
| `REJECTED_INVALID_UNICODE` | Rejected | 0 | None rejected |
| `MANUAL_REVIEW_REQUIRED` | ManualReview | 0 | None queued |
| `EXCLUDED_NON_SINHALA` | Excluded | 0 | None excluded |
| `REJECTED_QUALITY` | Rejected | 0 | None rejected |
| **Total** | | **180** | **180 Reconciled (0 Unaccounted)** |

---

## 6. Equation 5: Pilot Corpus Split Accounting (Section 18.5)

The final 180 pilot corpus records were partitioned into atomic transitive components:

$$
\text{TotalCorpus (180)} = \text{Train (154)} + \text{Validation (13)} + \text{Locked-Test (13)} + \text{Unaccounted (0)}
$$

| Split Partition | Record Count | Percentage | Method-Dev Records | Untouched Records | Cross-Split Leakage |
|---|---|---|---|---|---|
| **`train`** | **154** | 85.6% | **90** (100% of dev pool) | 64 | **0** |
| **`validation`** | **13** | 7.2% | **0** | 13 | **0** |
| **`locked_test`** | **13** | 7.2% | **0** | 13 | **0** |
| **Total** | **180** | 100.0% | **90** | **90** | **0 (Zero Leakage)** |

---

## 7. Signoff

```text
Accounting Ledger:        100% RECONCILED
Total Unaccounted Items:  0
Authoritative Status:     SEALED
Verifier:                 REV-GOV-01
Timestamp:                2026-10-15T16:40:00Z
```
