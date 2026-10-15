# Stage 31 — Accounting Summary Report

**Stage:** Stage 31 — Sinhala External Dataset Ingestion and Pilot Corpus Creation  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** `docs/stage31_accounting_summary.md`  
**Governing Standard:** Section 18, `docs/stage31_implementation_plan.md`  
**Status:** Frozen — Authoritative Conservation Ledger (Reconciled v5)  
**Authoritative Prerequisite:** `stage-30-complete-v3` (`ef95667b53dddfb032e71fc51d6c524aff7a22a2`)  
**Historical Initial Tag:** `stage-31-complete` (`975989e701561d8530781b57c9cd82f8db7ee72d`, preserved)  
**Historical Reconciled Tag v2:** `stage-31-complete-v2` (`181e8608364649466ba8bf55fed52bf1a977a0f9`, preserved)  
**Historical Reconciled Tag v3:** `stage-31-complete-v3` (`060be30fd6bddc6bc62495d6425cbb9215da5292`, preserved)  
**Historical Reconciled Tag v4:** `stage-31-complete-v4` (`c07a520438941fb047720176c4ef153131dc4716`, preserved)  
**Final Checkpoint Tag:** `stage-31-complete-v5`  
**Sealed Timestamp:** `2026-10-15T20:30:00+05:30` (UTC: `2026-10-15T15:00:00Z`)  
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

Every candidate source belongs to exactly one mutually exclusive status category:

$$
\text{TotalCandidates (8)} = \text{Approved (5)} + \text{MetadataOnly (1)} + \text{ReviewRequired (1)} + \text{Blocked (1)} + \text{SourceUnavailable (0)} + \text{Unaccounted (0)}
$$

| Source ID | Source Name | Primary Decision | Reconciliation Category |
|---|---|---|---|
| `SRC-SI-001` | Sinhala Wikipedia Official Dump | `APPROVED` | Approved |
| `SRC-SI-002` | AI4Bharat IndicCorp Sinhala Corpus | `APPROVED_INTERNAL_NONCOMMERCIAL_ONLY` | Approved |
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

## 5. Equation 4: Terminal-Disposition Accounting & Model C Dual-View Reconciliation (Section 18.4)

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
- `EXCLUDED_DUPLICATE`: **0** (Model C Retained with provenance view)
- `EXCLUDED_OUT_OF_SCOPE`: **0**
- `QUARANTINED_SOURCE_ERROR`: **0**
- **Unaccounted:** **0**

### Dual Corpus Views & Analytical Population Ledger
- **Stored Record Instances:** **180** (Provenance-preserving corpus: `pilot_corpus.jsonl`)
- **Unique Exact-Text Canonical Records:** **150** (Canonical analytical corpus: `canonical_analytical_corpus.jsonl`)
- **Surplus Retained Duplicate Instances:** **30** (across 5 multi-member clusters)
- **Effective Unweighted Analytical Population:** **150**
- **Sum of Provenance Weights:** **150.0** ($145 \times 1.0 + 5 \times [7 \times \frac{1}{7}] = 150.0$)
- **Canonical-to-Provenance Mapping Failures:** **0**
- **Noncanonical Exact Duplicates in Canonical View:** **0**
- **Retention Justification:** Retained to preserve source-level and reading-tier provenance for future governed analysis. Stage 31 performs no simplification-model evaluation.
- **Zero Leakage Invariant:** All duplicate members share the exact same `split_group_id` (`SPLIT-GRP-SI-000146` to `SPLIT-GRP-SI-000150`) in `train`.

---

## 6. Public Export Policy Enforcement Ledger

In accordance with strict rights-containment governance:

| Source ID | Primary Source Name | Pinned Licence | Literal Export Policy | Public Export Count |
|---|---|---|---|---|
| `SRC-SI-001` | Sinhala Wikipedia | CC BY-SA 4.0 | Permitted with Attribution | **40** (text included) |
| `SRC-SI-002` | IndicCorp Sinhala | CC BY-NC-SA 4.0 | `SUPPRESSED_BY_PROJECT_POLICY` | **40** (`text: null`) |
| `SRC-SI-003` | FLORES-200 | CC BY-SA 4.0 | Permitted with Attribution | **35** (text included) |
| `SRC-SI-004` | UCSC LTRL Corpus | Academic Research | `PROTECTED_INTERNAL_ONLY` | **30** (`text: null`) |
| `SRC-SI-008` | StoryWeaver (Books only) | CC BY 4.0 | Permitted with Attribution | **35** (text included) |
| **Total** | | | | **180 Records** |

- **Public Permitted Records (with text):** **110**
- **Literal Text Suppressed Records (`text: null`):** **70** (`SRC-SI-002` 40 + `SRC-SI-004` 30)
- **Literal restricted text detected in configured public-export fields:** **0 (PASSED)**

---

## 7. Manifest Scope and Verification Framework

1. **Planned Documentation Manifest (`docs/stage31_manifest.sha256`):**
   - Manifest-controlled documentation files: **11**
   - Checksum manifest: **1** (excludes itself)
   - Balance formula: $12 = 11 + 1$
2. **Expanded Governed Implementation Manifest (`data/sinhala_external/manifests/stage31_manifest.sha256`):**
   - Controls **31 distinct artifacts**:
     - 11 Documentation files
     - 8 Licence snapshots (including `CC-BY-NC-SA-4.0.txt`)
     - 4 Registry JSON files (candidate_sources, approved_sources, method_dev, config)
     - 5 Receipts (`RET-SI-001-001` through `RET-SI-008-001`)
     - 1 Raw source manifest (`raw_source_manifest.sha256`)
     - 1 Corpus metadata (`corpus_metadata.json`)
     - 1 Canonical analytical corpus view (`canonical_analytical_corpus.jsonl`)
   - The checksum manifest does not claim to hash itself.

---

## 8. Governance and Signoff

```text
Accounting Ledger:                                     100% RECONCILED
Total Unaccounted Items:                               0
Canonical Analytical Corpus Present in Manifest:       true
Canonical Records:                                     150
Noncanonical Exact Duplicates:                         0
Canonical-to-Provenance Mapping Failures:              0
Sum of Provenance Weights:                             150.0
Literal Restricted Text in Public-Export Fields:       0
Technical Governance Reviewer:                         REV-GOV-01
Reviewer Identity Verified:                            false (internal technical reviewer)
Internal Technical Governance Concurrence:             RECORDED
Independent Governance Signoff:                        NOT ESTABLISHED
Independent Legal Review:                              NOT ESTABLISHED
Sinhala Linguistic Review:                             NOT ESTABLISHED
Child-Development Review:                              NOT ESTABLISHED
Sealed Timestamp:                                      2026-10-15T20:30:00+05:30 (UTC: 2026-10-15T15:00:00Z)
Authoritative Status:                                  SEALED_RECONCILED_V5
```
