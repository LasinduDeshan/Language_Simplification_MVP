# Stage 31 — Pilot Corpus Accounting and Evaluation Split Report

**Stage:** Stage 31 — Sinhala External Dataset Ingestion and Pilot Corpus Creation  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** `docs/stage31_pilot_corpus_report.md`  
**Status:** Frozen — Dual-View Corpus Population, Exact Ledger, and Zero Leakage Reconciled (v8)  
**Configuration SHA-256:** `53aa0a8aa7ccc226f17107a18ee024dd85e71ad5776388650ee973a60bc1ef40`  
**Authoritative Prerequisite:** `stage-30-complete-v3` (`ef95667b53dddfb032e71fc51d6c524aff7a22a2`)  
**Historical Sealed Checkpoint:** `stage-31-complete-v7` (`724be7005542989dc2de65cabf157bb49ce53925`)  

---

## 1. Executive Summary & Dual Analytical Views

In Work Package 8 (WP8), the Stage 31 Sinhala Pilot Corpus was synthesized from 5 approved external sources, preprocessed under Stage 30 Unicode normalization standards, deduplicated via exact and near-duplicate transitive graph clustering, and partitioned into deterministic splits.

The corpus provides two mathematically reconciled views:
1. **Provenance-Preserving View (`pilot_corpus.jsonl`):** 180 total records retaining all source tiers and narrative repetitions for early-grade reading level analysis.
2. **Canonical Analytical View (`canonical_analytical_corpus.jsonl`):** 150 unique-text records where multi-member duplicate clusters are collapsed to primary canonical exemplars.

---

## 2. Reconciled Split Population Accounting

The pilot corpus strictly enforces **Invariants 18 and 19**: all 90 predeclared method-development records (`is_method_development_record == True`) are locked into `train`. The 70/15/15 ratio is applied exclusively to the 90 untouched evaluation-eligible records.

### Provenance-Preserving Population (`pilot_corpus.jsonl`, 180 records)
| Population Partition | Train | Validation | Test (`locked_test`) | Total | Train % | Val % | Test % |
|---|---|---|---|---|---|---|---|
| **Method-development** | **90** | 0 | 0 | **90** | 100.0% | 0.0% | 0.0% |
| **Untouched population** | **64** | **13** | **13** | **90** | 71.1% | 14.4% | 14.4% |
| **Combined corpus** | **154** | **13** | **13** | **180** | 85.6% | 7.2% | 7.2% |

### Canonical Analytical Population (`canonical_analytical_corpus.jsonl`, 150 records)
| Population Partition | Train | Validation | Test (`locked_test`) | Total | Train % | Val % | Test % |
|---|---|---|---|---|---|---|---|
| **Method-development** | **75** | 0 | 0 | **75** | 100.0% | 0.0% | 0.0% |
| **Untouched population** | **49** | **13** | **13** | **75** | 65.3% | 17.3% | 17.3% |
| **Combined corpus** | **124** | **13** | **13** | **150** | 82.7% | 8.7% | 8.7% |

$$\text{CombinedProvenance (180)} - \text{SurplusRetainedDuplicates (30)} = \text{CanonicalAnalyticalCorpus (150)}$$
All 30 surplus duplicates reside exclusively in `train` (15 method-dev + 15 untouched), so validation (13) and locked test (13) populations remain identical across both views.

---

## 3. Source Distribution & Duplicate Provenance

All 30 surplus retained duplicates in Stage 31 originate strictly from repeated story refrains in `SRC-SI-008` (StoryWeaver). No other source contains exact duplicates.

| Source ID | Source Name | Provenance Records | Canonical Records | Surplus Duplicates | Retention Justification |
|---|---|---|---|---|---|
| `SRC-SI-001` | Sinhala Wikipedia Official Dump | 40 | 40 | 0 | Informational & encyclopedic reference text |
| `SRC-SI-002` | AI4Bharat IndicCorp Sinhala | 40 | 40 | 0 | Diverse contemporary monolingual web corpus |
| `SRC-SI-003` | FLORES-200 Sinhala Benchmark | 35 | 35 | 0 | High-quality professionally translated sentences |
| `SRC-SI-004` | UCSC LTRL News Corpus | 30 | 30 | 0 | Standard formal news journalism discourse |
| `SRC-SI-008` | StoryWeaver Open Educational Stories | 35 | 5 | 30 | Graded early-grade readers (Model C retention) |
| **Total** | | **180** | **150** | **30** | |

---

## 4. Exact-Duplicate Cluster Ledger

Exact duplicate detection was executed using normalized UTF-8 string matching (SHA-256 hash identity).

- **Total Clusters Formed:** 150
- **Singleton Clusters:** 145 (1 record each = 145 records)
- **Multi-Member Clusters:** 5 (7 records each = 35 records)
- **Cross-Source Duplicate Clusters:** 0 (all multi-member clusters are strictly intra-source `SRC-SI-008`)
- **Total Canonical Records:** 150
- **Total Surplus Retained Duplicates:** 30

### Multi-Member Cluster Detail Ledger
| Duplicate Cluster ID | Member Count | Canonical Record ID | Member Record IDs | Source ID | Split Group ID | Assigned Split |
|---|---|---|---|---|---|---|
| `DUP-CLUST-SI-PILOT-000146` | 7 | `SI-PILOT-000146` | `SI-PILOT-000146`, `SI-PILOT-000151`, `SI-PILOT-000156`, `SI-PILOT-000161`, `SI-PILOT-000166`, `SI-PILOT-000171`, `SI-PILOT-000176` | `SRC-SI-008` | `SPLIT-GRP-SI-000146` | `train` |
| `DUP-CLUST-SI-PILOT-000147` | 7 | `SI-PILOT-000147` | `SI-PILOT-000147`, `SI-PILOT-000152`, `SI-PILOT-000157`, `SI-PILOT-000162`, `SI-PILOT-000167`, `SI-PILOT-000172`, `SI-PILOT-000177` | `SRC-SI-008` | `SPLIT-GRP-SI-000147` | `train` |
| `DUP-CLUST-SI-PILOT-000148` | 7 | `SI-PILOT-000148` | `SI-PILOT-000148`, `SI-PILOT-000153`, `SI-PILOT-000158`, `SI-PILOT-000163`, `SI-PILOT-000168`, `SI-PILOT-000173`, `SI-PILOT-000178` | `SRC-SI-008` | `SPLIT-GRP-SI-000148` | `train` |
| `DUP-CLUST-SI-PILOT-000149` | 7 | `SI-PILOT-000149` | `SI-PILOT-000149`, `SI-PILOT-000154`, `SI-PILOT-000159`, `SI-PILOT-000164`, `SI-PILOT-000169`, `SI-PILOT-000174`, `SI-PILOT-000179` | `SRC-SI-008` | `SPLIT-GRP-SI-000149` | `train` |
| `DUP-CLUST-SI-PILOT-000150` | 7 | `SI-PILOT-000150` | `SI-PILOT-000150`, `SI-PILOT-000155`, `SI-PILOT-000160`, `SI-PILOT-000165`, `SI-PILOT-000170`, `SI-PILOT-000175`, `SI-PILOT-000180` | `SRC-SI-008` | `SPLIT-GRP-SI-000150` | `train` |

All 5 multi-member clusters and their 35 constituent records are assigned strictly to `train` within dedicated atomic split groups.

---

## 5. Near-Duplicate Candidate Accounting & Parameters

Near-duplicate detection was executed under frozen Stage 31 protocol parameters:

| Parameter | Specification |
|---|---|
| **Candidate Threshold ($T_{cand}$):** | `0.80` |
| **Confirmation Threshold ($T_{conf}$):** | `0.90` |
| **Tokenizer:** | Character 5-gram shingle generator (`get_token_shingles(text, n=5, shingle_type='char')`, whitespace stripped) |
| **Shingle Size:** | `5` characters |
| **Input Population:** | 180 records (`pilot_corpus.jsonl`) |
| **Candidate Pairs Detected ($\ge 0.80$):** | **108** |
| **Confirmed Pairs ($\ge 0.90$):** | **105** |
| **Conservatively Unioned Pairs ($0.80 \le \text{sim} < 0.90$):** | **3** |
| **Rejected Pairs as Distinct:** | **0** |
| **Unresolved Pairs at Sealing:** | **0 (100% resolved)** |
| **Configuration SHA-256:** | `53aa0a8aa7ccc226f17107a18ee024dd85e71ad5776388650ee973a60bc1ef40` |

$$108 = 105\text{ confirmed} + 3\text{ conservatively unioned}$$

Both confirmed and conservatively unioned pairs were linked into transitive connected components. All connected pairs share the same `split_group_id` and are assigned to the same split.

---

## 6. Four-Dimensional Leakage Prevention Audit

Zero cross-split leakage was detected under the frozen document, exact-duplicate, and near-duplicate relations:

| Leakage Relation / Dimension | Audited Edges / Entities | Cross-Split Overlaps Detected | Audit Result |
|---|---|---|---|
| **1. Split Group Boundaries** | 150 atomic components | **0** | **PASSED** |
| **2. Document / Story Groups** | 180 document groups | **0** | **PASSED** |
| **3. Exact Duplicate Clusters** | 150 exact clusters (5 multi-member) | **0** | **PASSED** |
| **4. Confirmed / Unioned Near-Duplicates** | 108 candidate pairs | **0** | **PASSED** |
| **5. Dev Pool Evaluation Contamination** | 90 method-development records | **0 records in Val/Test** | **PASSED** |

**Zero-Leakage Finding:** Zero cross-split leakage detected under the frozen document, exact-duplicate, and near-duplicate relations.

---

## 7. Governance Limitations & Non-Clinical Declarations

In accordance with strict clinical, legal, and early-childhood governance contracts:
- `validation_status: "draft"`
- `research_eligible: false`
- `approved_for_child_delivery: false`
- `approved_for_unsupervised_child_delivery: false`
- `requires_expert_review: true`

Stage 31 constitutes technical preprocessing and data ingestion infrastructure only. No models were trained, evaluated, or deployed to human or child subjects.
