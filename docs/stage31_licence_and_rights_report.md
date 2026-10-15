# Stage 31 — Licence and Rights Provenance Report

**Stage:** Stage 31 — Sinhala External Dataset Ingestion and Pilot Corpus Creation  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** `docs/stage31_licence_and_rights_report.md`  
**Status:** Frozen — Conclusive Non-Commercial Rights Verification Sealed (v5)  
**Authoritative Prerequisite:** `stage-30-complete-v3` (`ef95667b53dddfb032e71fc51d6c524aff7a22a2`)  
**Sealed Timestamp:** `2026-10-15T20:30:00+05:30` (UTC: `2026-10-15T15:00:00Z`)  
**Technical Governance Reviewer:** `REV-GOV-01` (Internal technical reviewer; identity verified: false)  
**Internal Technical Governance Concurrence:** RECORDED  
**Independent Governance Signoff:** NOT ESTABLISHED  
**Independent Legal / Linguistic / Child-Development Reviews:** NOT ESTABLISHED

---

## 1. Executive Summary

This report establishes the intellectual property, licensing, and usage rights framework governing all eight candidate datasets identified for Stage 31. Every source was audited against primary upstream licences, terms of service, and academic use agreements.

- **Candidate Sources Evaluated:** 8
- **Approved Sources:** 5 (`SRC-SI-001`, `SRC-SI-002`, `SRC-SI-003`, `SRC-SI-004`, `SRC-SI-008`)
- **Blocked / Excluded Sources:** 3 (`SRC-SI-005`, `SRC-SI-006`, `SRC-SI-007`)
- **Unaccounted:** 0 (Reconciled)
- **Zero Raw Text in Git:** Confirmed across all sources.

---

## 2. Granular Source Rights and Verified Licence Terms

### 2.1 `SRC-SI-001`: Sinhala Wikipedia
- **Retrieved Revision or Dump:** `siwiki-20261001-pages-articles-multistream.xml.bz2` (Sample Extraction sequence `0..39`)
- **Applicable Licence:** **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)** (governing modern Wikimedia text contributions pursuant to the June 2023 Wikimedia Terms of Use update).
- **Licence Evidence URL:** [Wikimedia Foundation Terms of Use](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use)
- **Licence Evidence SHA-256:** `c17d8a3e91c875e17740f98363717d23d887a0f7e65cb84ab1b3b2ae4c185bb8` (`CC-BY-SA-4.0.txt`)
- **Attribution Method:** Article URL and revision/history reference; credited to "Contributors to Sinhala Wikipedia".
- **Redistribution Status:** `PUBLIC_TEXT_PERMITTED_WITH_ATTRIBUTION`.

### 2.2 `SRC-SI-002`: AI4Bharat IndicCorp Sinhala (Conclusive Upstream Verification — Option A)
- **Source Identifier:** `SRC-SI-002`
- **Artifact:** IndicCorp v1 Sinhala / `si.txt.gz`
- **Applicable Licence:** **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**
- **Rights Evidence Source:** `https://raw.githubusercontent.com/AI4Bharat/indicnlp_corpus/master/LICENSE`
- **Rights Evidence SHA-256:** `dc95bad5386871bab6b5b62daa4d2ae2eb4aa5244e37dff11ff233514761cbef` (`CC-BY-NC-SA-4.0.txt`)
- **Internal Non-Commercial Research Allowed:** `true`
- **Commercial Use Allowed:** `false`
- **Public Literal Export Enabled:** `false`
- **Public Export Policy:** `SUPPRESSED_BY_PROJECT_POLICY`
- **Primary Decision:** `APPROVED_INTERNAL_NONCOMMERCIAL_ONLY`
- **Redistribution Status:** **`SUPPRESSED_BY_PROJECT_POLICY`** (Literal text is 100% suppressed: `text: null`).

### 2.3 `SRC-SI-003`: FLORES-200 Sinhala Benchmark
- **Release Version:** FLORES-200 Dev/Devtest Split (`nllb-200`)
- **Repository / Release URL:** [facebookresearch/flores](https://github.com/facebookresearch/flores/blob/main/README.md)
- **Applicable Licence:** **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**
- **Licence File SHA-256:** `c17d8a3e91c875e17740f98363717d23d887a0f7e65cb84ab1b3b2ae4c185bb8` (`CC-BY-SA-4.0.txt`)
- **Attribution Method:** Citation of NLLB Team, Meta AI (2022).
- **Redistribution Status:** `PUBLIC_TEXT_PERMITTED_WITH_ATTRIBUTION`.

### 2.4 `SRC-SI-004`: UCSC LTRL Sinhala News / POS Corpus
- **Licence Framework:** Academic Research Use Agreement (LTRL-UCSC)
- **Licence Evidence:** `data/sinhala_external/registry/licence_snapshots/UCSC-LTRL-Academic-Research-Terms.txt`
- **Licence File SHA-256:** `60283a488ec063b7829285fb7ad213b28b7fe7ae2e8f172eaef289899f83f234`
- **Redistribution Status:** **`PROTECTED_INTERNAL_ONLY`** (Literal text strictly suppressed: `text: null`).

### 2.5 `SRC-SI-008`: StoryWeaver Sinhala Children's Stories
- **Platform / Source URL:** [StoryWeaver](https://storyweaver.org.in/en/attributions)
- **Applicable Licence:** **Creative Commons Attribution 4.0 International (CC BY 4.0)**
- **Asset Scope Guarantee:** Stage 31 exports **book narrative text only**. Separate audio, readalong, and video assets are completely excluded from ingestion and export.
- **Licence File SHA-256:** `584de4c9f788c0f06f5647a9ecf2f35d21469e7f8fbcfbb3231e33de3a738dfc` (`CC-BY-4.0.txt`)
- **Attribution Method:** Credit to Pratham Books StoryWeaver, original authors, and illustrators with source URL.
- **Redistribution Status:** `PUBLIC_TEXT_PERMITTED_WITH_ATTRIBUTION`.

---

## 3. Share-Alike Wording & Rights Assessment

> [!NOTE]
> **Internal Rights Assessment:**
> Records retain their individual source licences. If text is adapted or combined into a single derivative, the applicable compatibility and share-alike obligations must be assessed before redistribution. Mere aggregation into a corpus does not, by itself, establish that every independent record has been relicensed. This is an internal rights assessment, not legal advice.

---

## 4. Candidate-Source Accounting Conservation

In accordance with Section 18.1 of the Implementation Plan:

$$
\text{TotalCandidates (8)} = \text{Approved (5)} + \text{MetadataOnly (1)} + \text{ReviewRequired (1)} + \text{Blocked (1)} + \text{SourceUnavailable (0)} + \text{Unaccounted (0)}
$$

| Source ID | Source Name | Primary Licence | Decision | Export Policy |
|---|---|---|---|---|
| `SRC-SI-001` | Sinhala Wikipedia Dump | CC BY-SA 4.0 | `APPROVED` | `PUBLIC_PERMITTED_CC_BY_SA` |
| `SRC-SI-002` | IndicCorp Sinhala | CC BY-NC-SA 4.0 | `APPROVED_INTERNAL_NONCOMMERCIAL_ONLY` | `SUPPRESSED_BY_PROJECT_POLICY` |
| `SRC-SI-003` | FLORES-200 Benchmark | CC BY-SA 4.0 | `APPROVED` | `PUBLIC_PERMITTED_CC_BY_SA` |
| `SRC-SI-004` | UCSC LTRL Corpus | Academic Research | `APPROVED` | `PROTECTED_INTERNAL_ONLY` |
| `SRC-SI-005` | CC-100 Sinhala | Web Scraped Terms | `REVIEW_REQUIRED` | `BLOCKED_REVIEW_REQUIRED` |
| `SRC-SI-006` | news.lk Notices | Govt. Copyright | `METADATA_ONLY` | `METADATA_CATALOGUE_ONLY` |
| `SRC-SI-007` | Madura Online | Commercial Scraping Prohibited | `BLOCKED` | `BLOCKED_PROPRIETARY` |
| `SRC-SI-008` | StoryWeaver Stories | CC BY 4.0 | `APPROVED` | `PUBLIC_PERMITTED_CC_BY` |
| **Total** | | | **8 Reconciled** | **0 Unaccounted** |

---

## 5. Reviewer Signoff

```text
Technical Governance Reviewer:                         REV-GOV-01
Reviewer Identity Verified:                            false (pseudonymous internal technical reviewer)
Internal Technical Governance Concurrence:             RECORDED
Independent Governance Signoff:                        NOT ESTABLISHED
Independent Legal Review:                              NOT ESTABLISHED
Sinhala Linguistic Review:                             NOT ESTABLISHED
Child-Development Review:                              NOT ESTABLISHED
Sealed Timestamp:                                      2026-10-15T20:30:00+05:30 (UTC: 2026-10-15T15:00:00Z)
```
