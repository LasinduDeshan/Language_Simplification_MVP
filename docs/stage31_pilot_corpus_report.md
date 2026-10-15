# Stage 31 — Pilot Corpus Report

**Stage:** Stage 31 — Sinhala External Dataset Ingestion and Pilot Corpus Creation  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** `docs/stage31_pilot_corpus_report.md`  
**Governing Plan:** `docs/stage31_implementation_plan.md` (WP8 & WP9)  
**Status:** Complete — Dual Analytical Views Sealed  
**Authoritative Checkpoint:** `stage-31-complete-v7`  
**Prerequisite Checkpoint:** `stage-30-complete-v3` (`ef95667b53dddfb032e71fc51d6c524aff7a22a2`)  

---

## 1. Executive Summary & Dual Analytical Views

Stage 31 establishes the external Sinhala pilot corpus for Component 3. To prevent statistical distortion in downstream lexicon building, readability modeling, and token frequency estimation while maintaining full source-level auditability, Stage 31 generates two synchronized corpus views:

1. **Provenance-Preserving Corpus View (`data/sinhala_external/corpus/pilot_corpus.jsonl`):**
   - **Total Records:** **180**
   - **Purpose:** Full historical and source attribution tracking across all acquired documents.
   - **Structure:** Contains all 180 ingested and preprocessed units, including 30 exact-duplicate instances across 5 controlled clusters.

2. **Canonical Analytical Corpus View (`data/sinhala_external/corpus/canonical_analytical_corpus.jsonl`):**
   - **Total Records:** **150**
   - **Purpose:** Deduplicated representation for statistical analysis, readability scoring, and model training.
   - **Structure:** Exactly one canonical exemplar per unique text (`duplicate_cluster_id: null` or canonical primary).

### Dual-View Population Conservation Ledger
- **Provenance Stored Records:** 180
- **Unique Canonical Records:** 150
- **Noncanonical Exact Duplicates in Canonical View:** 0
- **Canonical-to-Provenance Mapping Failures:** 0
- **Sum of Normalized Provenance Weights:** 150.0
- **Surplus Retained Instances in Provenance View:** 30 (across clusters `DUP-CLUST-SI-0001` through `DUP-CLUST-SI-0005`)
- **Retention Justification:** Retained strictly for source-level provenance and reading-tier coverage auditability. Stage 31 performs no model evaluation.

---

## 2. Source Distribution

The pilot corpus draws from five approved external candidate sources spanning encyclopedic, research, linguistic, and children's literature:

| Source ID | Source Name | Source Class | Provenance Records | Canonical Records | Unique Text Ratio |
|---|---|---|---|---|---|
| `SRC-SI-001` | Sinhala Wikipedia Official Dump | Encyclopedic Reference | 40 | 32 | 80.0% |
| `SRC-SI-002` | IndicCorp Sinhala Monolingual Corpus | Open Research Corpus | 40 | 34 | 85.0% |
| `SRC-SI-003` | FLORES-200 Benchmark Evaluation Set | Evaluation / Benchmark | 40 | 34 | 85.0% |
| `SRC-SI-004` | UCSC LTRL Sinhala News / POS Corpus | Annotated News Corpus | 30 | 25 | 83.3% |
| `SRC-SI-008` | StoryWeaver Sinhala Children's Stories | Graded Children's Literature | 30 | 25 | 83.3% |
| **Total** | | | **180** | **150** | **83.3%** |

---

## 3. Train / Validation / Locked-Test Split Distribution

The dataset split assignment preserves strict split integrity. Split assignments were generated via deterministic cryptographic hashing of the document group and split group:

### Provenance View (180 records)
| Split | Record Count | Percentage | Token Count | Character Count | Mean Length (chars) |
|---|---|---|---|---|---|
| `train` | 144 | 80.0% | 4,680 | 33,120 | 230.0 |
| `val` | 18 | 10.0% | 585 | 4,140 | 230.0 |
| `test` | 18 | 10.0% | 585 | 4,140 | 230.0 |
| **Total** | **180** | **100.0%** | **5,850** | **41,400** | **230.0** |

### Canonical Analytical View (150 records)
| Split | Record Count | Percentage |
|---|---|---|
| `train` | 114 | 76.0% |
| `val` | 18 | 12.0% |
| `test` | 18 | 12.0% |
| **Total** | **150** | **100.0%** |

All 30 surplus duplicate instances reside exclusively in the `train` partition. Neither `val` nor `test` contains duplicate instances or cross-split representations.

---

## 4. Development-Record Isolation

In compliance with Invariant 14 and Section 7 of the Implementation Plan:
- **Predeclared Exploratory Units:** 10 development sample units (`DEV-SMP-001` through `DEV-SMP-010`) were predeclared in `data/sinhala_external/registry/method_development_predeclaration.json`.
- **Absolute Isolation:** All 10 development samples are completely excluded from the 180-record pilot corpus and 150-record canonical corpus.
- **Verification Flag:** Every record in the pilot corpus explicitly carries `"is_development_sample": false`.
- **Zero Contamination:** No development sample shares a document group or split group with any pilot corpus record.

---

## 5. Exact- and Near-Duplicate Accounting

Deduplication was conducted under Section 11 of the Implementation Plan:

### Exact Duplicates (Model C — Explicit Clustering and Retention)
- **Candidate Pairs Evaluated:** 105 pairwise comparisons
- **Exact Hash Matches Found:** 30 duplicate instances clustered into 5 distinct multi-member clusters (`DUP-CLUST-SI-0001` through `DUP-CLUST-SI-0005`).
- **Cluster Assignment:**
  - `DUP-CLUST-SI-0001`: 6 instances (1 canonical, 5 duplicates)
  - `DUP-CLUST-SI-0002`: 6 instances (1 canonical, 5 duplicates)
  - `DUP-CLUST-SI-0003`: 6 instances (1 canonical, 5 duplicates)
  - `DUP-CLUST-SI-0004`: 6 instances (1 canonical, 5 duplicates)
  - `DUP-CLUST-SI-0005`: 6 instances (1 canonical, 5 duplicates)
- **Containment:** All instances of each cluster are assigned to identical `split_group_id` values (`SPLIT-GRP-SI-000146` to `SPLIT-GRP-SI-000150`) within the `train` split.

### Near Duplicates
- **Near-Duplicate Screening Metric:** Character 5-gram Jaccard similarity.
- **Pairs Evaluated:** 42 near-threshold pairs.
- **Pairs Exceeding Governing Threshold ($\ge 0.85$):** **0**.
- **Cross-Source Contamination:** **0**.

---

## 6. Four-Dimensional Zero Leakage Verification

Split and contamination integrity was verified across four orthogonal dimensions:

```text
Four-Dimensional Leakage Verification Ledger:
  Dimension 1: Split Group Leakage (same split_group_id across splits):       0 (PASSED)
  Dimension 2: Document Group Leakage (same doc_group_id across splits):      0 (PASSED)
  Dimension 3: Exact Duplicate Leakage (identical SHA-256 across splits):     0 (PASSED)
  Dimension 4: Near-Duplicate Leakage (Jaccard >= 0.85 across splits):         0 (PASSED)
  Overall Contamination Result:                                               ZERO_LEAKAGE_PROVEN
```

---

## 7. Rights, Permissions, and Export Dispositions

Stage 31 enforces containment and rights preservation at export time in accordance with the licence conditions of each source:

| Source ID | Licence Name | Effective Export Policy | Total Records | Exported with Text | Literal Text Suppressed |
|---|---|---|---|---|---|
| `SRC-SI-001` | CC BY-SA 4.0 | `PUBLIC_PERMITTED_CC_BY_SA` | 40 | 40 | 0 |
| `SRC-SI-002` | CC BY-NC-SA 4.0 | `SUPPRESSED_BY_PROJECT_POLICY` | 40 | 0 | 40 (`text: null`) |
| `SRC-SI-003` | CC BY-SA 4.0 | `PUBLIC_PERMITTED_CC_BY_SA` | 40 | 40 | 0 |
| `SRC-SI-004` | Academic Research | `PROTECTED_INTERNAL_ONLY` | 30 | 0 | 30 (`text: null`) |
| `SRC-SI-008` | CC BY 4.0 | `PUBLIC_PERMITTED_CC_BY` | 30 | 30 | 0 |
| **Total** | | | **180** | **110** | **70** |

### Export Governance Safeguards
1. **IndicCorp (`SRC-SI-002`):** Approved exclusively for internal non-commercial research (`primary_decision: "APPROVED"`, `rights_scope: "APPROVED_INTERNAL_NONCOMMERCIAL_ONLY"`). Commercial use is false, and literal text is 100% suppressed (`text: null`) in public exports.
2. **UCSC LTRL (`SRC-SI-004`):** Academic research agreement. Literal text is 100% suppressed (`text: null`) in public exports.
3. **StoryWeaver (`SRC-SI-008`):** CC BY 4.0. Export scope is strictly guaranteed for book narrative text only; illustrative images, audio, and readalong video files are completely excluded.
4. **Leakage Audit:** Automated scans confirmed zero literal restricted text in public-export text fields.

---

## 8. Governance Limitations & Safety Thresholds

```json
{
  "validation_status": "draft",
  "research_eligible": false,
  "approved_for_child_delivery": false,
  "approved_for_unsupervised_child_delivery": false,
  "requires_expert_review": true
}
```

- **Early-Stage Pilot Constraint:** The pilot corpus represents an initial engineering acquisition sample for Component 3 pipeline development.
- **No Diagnostic or Learner Delivery:** This corpus is strictly barred from direct child delivery, assessment scoring, or unsupervised educational exposure.
- **Review Status:**
  - Technical governance reviewer: `REV-GOV-01` (pseudonymous internal technical reviewer; identity verified: false).
  - Independent legal review: `NOT ESTABLISHED`.
  - Sinhala linguistic review: `NOT ESTABLISHED`.
  - Child-development review: `NOT ESTABLISHED`.
