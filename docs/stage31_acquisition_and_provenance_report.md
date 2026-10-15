# Stage 31 — Acquisition and Provenance Report

**Stage:** Stage 31 — Sinhala External Dataset Ingestion and Pilot Corpus Creation  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** `docs/stage31_acquisition_and_provenance_report.md`  
**Status:** Frozen — Raw Snapshots and Receipts Sealed  
**Protected Storage Location:** Outside Git repository (`SINHALA_EXTERNAL_PROTECTED_ROOT`)  
**Authoritative Prerequisite:** `stage-30-complete-v3` (`ef95667b53dddfb032e71fc51d6c524aff7a22a2`)

---

## 1. Executive Summary

In Work Package 3 (WP3), rate-limited acquisition was executed for all five legally approved candidate sources. In accordance with Governance Invariants 7, 8, 9, and 15:
- All raw payloads were stored **exclusively outside the Git repository** in external protected storage.
- Every retrieval receipt was sanitized to strip API tokens, session IDs, and signed query parameters (`sensitive_query_parameters_removed: true`).
- Raw whole-file SHA-256 digests were computed prior to parsing and recorded in `data/sinhala_external/manifests/raw_source_manifest.sha256`.
- Method-development document units were predeclared and locked in `data/sinhala_external/registry/method_development_predeclaration.json` before any format parsing begins.

### Retrieved Files Accounting Summary

$$
\text{ExpectedFiles (5)} = \text{DownloadedVerified (5)} + \text{Failed (0)} + \text{NotAttempted (0)} + \text{Quarantined (0)} + \text{Unaccounted (0)}
$$

$$\text{Accounting Status: 0 Unaccounted (RECONCILED)}$$

---

## 2. Acquired Source Registry & Sanitized Receipts

| Retrieval ID | Source ID | Source Name | Content Type | Byte Size | SHA-256 Digest | Raw Storage Reference |
|---|---|---|---|---|---|---|
| `RET-SI-001-001` | `SRC-SI-001` | Sinhala Wikipedia Official Dump | `application/xml` | 33,229 | `e8a12315aec2d0b4...` | `protected://sinhala_external/raw/SRC-SI-001/RET-SI-001-001/siwiki_sample.xml` |
| `RET-SI-002-001` | `SRC-SI-002` | AI4Bharat IndicCorp Sinhala Monolingual Corpus | `application/jsonlines` | 12,365 | `712baa1f226626a9...` | `protected://sinhala_external/raw/SRC-SI-002/RET-SI-002-001/indiccorp_si_sample.jsonl` |
| `RET-SI-003-001` | `SRC-SI-003` | FLORES-200 Sinhala Benchmark Evaluation Dataset | `text/tab-separated-values` | 8,646 | `22c8324b8473a9b2...` | `protected://sinhala_external/raw/SRC-SI-003/RET-SI-003-001/flores200_si_sample.tsv` |
| `RET-SI-004-001` | `SRC-SI-004` | UCSC LTRL Sinhala News / POS Corpus | `text/plain` | 17,912 | `a8b15d5f428bda30...` | `protected://sinhala_external/raw/SRC-SI-004/RET-SI-004-001/ltrl_news_sample.txt` |
| `RET-SI-008-001` | `SRC-SI-008` | StoryWeaver Open Educational Sinhala Children's Stories | `application/json` | 34,240 | `8cbaf0bb46a11643...` | `protected://sinhala_external/raw/SRC-SI-008/RET-SI-008-001/storyweaver_si_sample.json` |

---

## 3. URL Sanitization Evidence

To prevent credentials or signed query secrets from leaking into the Git repository, the URL sanitizer processed all raw resolved URLs and redirect hops:

| Retrieval ID | Sanitized Resolved Endpoint (`resolved_url_sanitized`) | Query Secrets Removed |
|---|---|---|
| `RET-SI-001-001` | `https://dumps.wikimedia.org/siwiki/latest/siwiki-latest-pages-articles.xml.bz2` | Yes (`sensitive_query_parameters_removed: true`) |
| `RET-SI-002-001` | `https://ai4bharat.iitm.ac.in/indiccorp/downloads/si.jsonl` | Yes (`sensitive_query_parameters_removed: true`) |
| `RET-SI-003-001` | `https://raw.githubusercontent.com/facebookresearch/flores/main/flores200/dev/sin_Sinh.dev` | Yes (`sensitive_query_parameters_removed: true`) |
| `RET-SI-004-001` | `https://ucsc.cmb.ac.lk/ltrl/downloads/sinhala_news_corpus.zip` | Yes (`sensitive_query_parameters_removed: true`) |
| `RET-SI-008-001` | `https://storyweaver.org.in/api/v1/stories/sinhala.json` | Yes (`sensitive_query_parameters_removed: true`) |

---

## 4. Method-Development Pool Predeclaration

In accordance with Invariant 18, the method-development pool was predeclared in WP3 before parser implementation in WP4:

| Source ID | Source Name | Predeclared Unit Range | Predeclared Units | Reserved Purpose |
|---|---|---|---|---|
| `SRC-SI-001` | Sinhala Wikipedia Official Dump | `[0, 19]` | 20 | Parser validation for MediaWiki XML structures |
| `SRC-SI-002` | AI4Bharat IndicCorp Sinhala Corpus | `[0, 19]` | 20 | Parser validation for JSONL lines and general web crawl |
| `SRC-SI-003` | FLORES-200 Sinhala Benchmark Split | `[0, 14]` | 15 | Parser validation for TSV and clean reference sentences |
| `SRC-SI-004` | UCSC LTRL Sinhala News / POS Corpus | `[0, 14]` | 15 | Parser validation for raw text paragraph offsets |
| `SRC-SI-008` | StoryWeaver Sinhala Children's Stories | `[0, 19]` | 20 | Graded story JSON and early-childhood vocabulary screening |

$$\text{Total Predeclared Method-Development Units} = 20 + 20 + 15 + 15 + 20 = 90\text{ units}$$

> [!IMPORTANT]
> **Immutability Invariant:**
> Method-development designation is immutable after first use. Records cannot be retroactively marked as development records after results have been inspected.

---

## 5. Verification Signoff

```text
Retrieved Files:         5 / 5 verified
Failed Downloads:        0
Raw Bytes Stored:        External protected root only
URL Query Secrets in Git:0 (Sanitized across all receipts)
Raw Source Manifest:     Sealed (data/sinhala_external/manifests/raw_source_manifest.sha256)
Predeclared Dev Units:   90 units locked
Timestamp:               2026-10-15T15:35:00Z
Verifier:                REV-GOV-01
```

