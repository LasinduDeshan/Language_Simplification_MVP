# Stage 31 — Deduplication and Contamination Prevention Report

**Stage:** Stage 31 — Sinhala External Dataset Ingestion and Pilot Corpus Creation  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** `docs/stage31_deduplication_and_contamination_report.md`  
**Status:** Frozen — Reconciled Transitive Clustering and Exact-Duplicate Model C Sealed (v3)  
**Stage 31 Configuration Hash:** `53aa0a8aa7ccc226f17107a18ee024dd85e71ad5776388650ee973a60bc1ef40`  
**Authoritative Prerequisite:** `stage-30-complete-v3` (`ef95667b53dddfb032e71fc51d6c524aff7a22a2`)  
**Sealed Timestamp:** `2026-10-15T19:50:00+05:30` (UTC: `2026-10-15T14:20:00Z`)  
**Technical Governance Reviewer:** `REV-GOV-01` (Internal technical reviewer; identity verified: false)  
**Internal Technical Governance Concurrence:** RECORDED  
**Independent Governance Signoff:** NOT ESTABLISHED  
**Independent Legal / Linguistic / Child-Development Reviews:** NOT ESTABLISHED

---

## 1. Executive Summary

In Work Package 8 (WP8), full-corpus deduplication, multi-source provenance aggregation, and transitive connected component clustering were executed across all 180 accepted pilot candidate records.

- **Zero-Leakage Finding:** Zero cross-split leakage detected under the frozen document, exact-duplicate, and near-duplicate relations.
- **Development Pool Isolation:** Exactly 90 method-development records were isolated in `TRAIN_ONLY_DEVELOPMENT_COMPONENT` groups and assigned strictly to `train`.
- **Evaluation Split Integrity:** Exactly 0 method-development records exist in `validation` or `locked_test`.
- **Multi-Source Rights Resolution:** Multi-source duplicates aggregate all contributing source IDs and inherit the most restrictive export policy.

---

## 2. Exact-Duplicate Accounting & Model C Protocol Deviation

In Stage 31, **Model C (Duplicates Intentionally Retained)** was adopted and formally documented:
- **Total Candidate Records:** 180
- **Total Exact Duplicate Clusters Formed:** 150
- **Single-Member Clusters:** 145 (145 records)
- **Multi-Member Clusters:** 5 clusters (`DUP-SI-000146` through `DUP-SI-000150`, 7 records each = 35 records)
- **Canonical Representative Records:** 150
- **Retained Exact-Duplicate Records:** **30** (surplus across 5 clusters)
- **`EXCLUDED_DUPLICATE` Count:** 0
- **Protocol Deviation Justification:** In early-grade educational reader series (StoryWeaver), natural narrative refrains, recurring character dialogues, and story progressions repeat intentionally across difficulty tiers. All 30 duplicate records were intentionally retained to evaluate simplification model behavior on repetitive early-grade text.
- **Leakage Prevention Verification:** All duplicate members across all 5 multi-member clusters were bound into the exact same `split_group_id` (`SPLIT-GRP-SI-000146` to `SPLIT-GRP-SI-000150`) and assigned exclusively to `train`.
- **All Duplicate Members Share One `split_group_id`:** **PASSED (Zero Leakage)**

---

## 3. Near-Duplicate Candidate Accounting & Reconciliation

Across all 180 evaluated records, all candidate pairs with token/char Jaccard similarity $\ge 0.80$ were reconciled prior to split assignment:

$$
\text{NearDuplicateCandidates (108)} = \text{ConfirmedDuplicateRelation (105)} + \text{ConservativelyUnioned (3)} + \text{RejectedAsDistinct (0)} + \text{UnresolvedAtSealing (0)}
$$

- **Near-Duplicate Candidates Detected ($\ge 0.80$):** 108 pairs
- **Confirmed as Duplicate Relation ($\ge 0.90$):** 105 pairs (automatically unified into transitive closure)
- **Conservatively Unioned into Split Groups ($0.80 \le \text{sim} < 0.90$):** 3 pairs (unioned into split groups to eliminate any cross-split leakage risk)
- **Rejected as Distinct:** 0 pairs
- **Unresolved at Split Sealing:** **0 pairs (100% resolved)**

---

## 4. Production Corpus Split Accounting

In accordance with Section 18.5 of the Implementation Plan:

### Explanation of Split-Ratio Allocation
The planned 70/15/15 allocation was applied **only to the 90 untouched evaluation-eligible records**. The 90 method-development records were mandatorily assigned to `train` (in accordance with Invariants 18 & 19), producing an overall 85.6% / 7.2% / 7.2% corpus distribution:

$$
\text{Untouched Records (90)} = \text{Untouched Train (64, 71.1\%)} + \text{Validation (13, 14.4\%)} + \text{Locked-Test (13, 14.4\%)}
$$

$$
\text{TotalCorpus (180)} = \text{Train (154, 85.6\%)} + \text{Validation (13, 7.2\%)} + \text{Locked-Test (13, 7.2\%)} + \text{Unaccounted (0)}
$$

| Split Partition | Overall Count | Overall Ratio | Method-Dev Units | Untouched Units | Untouched Ratio | Governance Status |
|---|---|---|---|---|---|---|
| **`train`** | **154** | 85.6% | **90** (100% dev pool) | 64 | 71.1% | Training & tuning eligible |
| **`validation`** | **13** | 7.2% | **0** | 13 | 14.4% | Hyperparameter selection |
| **`locked_test`** | **13** | 7.2% | **0** | 13 | 14.4% | Sealed benchmark evaluation |
| **Total** | **180** | 100.0% | **90** | **90** | **100.0%** | **Zero Cross-Contamination** |

---

## 5. Four-Dimensional Leakage Proofs

Every potential channel of data leakage between splits was audited and mathematically proven to be zero:

| Leakage Dimension | Audited Edges / Entities | Observed Cross-Split Overlap | Result |
|---|---|---|---|
| **1. Split Group Boundaries** | 150 atomic components | **0 overlapping groups** | **PASSED** |
| **2. Document / Story Groups** | 180 document groups | **0 multi-split documents** | **PASSED** |
| **3. Exact Duplicate Clusters** | 150 exact clusters | **0 multi-split clusters** | **PASSED** |
| **4. Confirmed Near-Duplicates** | 105 confirmed pairs ($\ge 0.90$) | **0 cross-split pairs** | **PASSED** |
| **5. Dev Pool Evaluation Leakage** | 90 method-development records | **0 records in Val/Test** | **PASSED** |

---

## 6. Multi-Source Duplicate Provenance Aggregation

When duplicate records were identified, the contributing source list and export policy were resolved:
- `all_contributing_sources`: Populated with complete list of origin sources.
- `effective_export_policy`: Pinned to the most restrictive policy according to the sealed hierarchy (`PROTECTED_INTERNAL_ONLY` > `PUBLIC_PERMITTED_CC_BY_SA` > `PUBLIC_PERMITTED_CC_BY`).
- If any contributing source disallows public redistribution (e.g. `SRC-SI-004`), the unified record is marked `PROTECTED_INTERNAL_ONLY`.

---

## 7. Verification Signoff

```text
Total Pilot Corpus Records:                180 (Exceeds >= 150 requirement)
Zero-Leakage Finding:                      Zero cross-split leakage detected under the frozen document, exact-duplicate, and near-duplicate relations
Method-Development Isolation:              100% IN TRAIN (0 in Val/Test)
Split Allocations:                         Train 154 (85.6%), Val 13 (7.2%), Test 13 (7.2%)
Untouched Allocations:                     Train 64 (71.1%), Val 13 (14.4%), Test 13 (14.4%)
Unresolved Near-Duplicates:                0
Exact-Duplicate Accounting:                Model C (30 duplicates retained in 5 clusters in Train)
Configuration Sealed:                      53aa0a8aa7ccc226f17107a18ee024dd85e71ad5776388650ee973a60bc1ef40
Technical Governance Reviewer:             REV-GOV-01
Reviewer Identity Verified:                false (internal technical reviewer)
Internal Technical Governance Concurrence: RECORDED
Independent Governance Signoff:            NOT ESTABLISHED
Independent Legal Review:                  NOT ESTABLISHED
Sinhala Linguistic Review:                 NOT ESTABLISHED
Child-Development Review:                  NOT ESTABLISHED
Sealed Timestamp:                          2026-10-15T19:50:00+05:30 (UTC: 2026-10-15T14:20:00Z)
```
