# Stage 31 — Completion Record (Reconciled v3)

**Stage:** Stage 31 — Sinhala External Dataset Ingestion and Pilot Corpus Creation  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** `docs/stage31_completion_record.md`  
**Status:** Complete — Final Authoritative Checkpoint Sealed (v3)  
**Authoritative Prerequisite:** `stage-30-complete-v3` (`ef95667b53dddfb032e71fc51d6c524aff7a22a2`)  
**Historical Initial Tag:** `stage-31-complete` (`975989e701561d8530781b57c9cd82f8db7ee72d`, preserved immutable)  
**Historical Reconciled Tag:** `stage-31-complete-v2` (`181e8608364649466ba8bf55fed52bf1a977a0f9`, preserved immutable)  
**Final Checkpoint Tag:** `stage-31-complete-v3`  
**Sealed Timestamp:** `2026-10-15T19:50:00+05:30` (UTC: `2026-10-15T14:20:00Z`)  
**Technical Governance Reviewer:** `REV-GOV-01` (Internal technical reviewer; identity verified: false)  
**Internal Technical Governance Concurrence:** RECORDED  
**Independent Governance Signoff:** NOT ESTABLISHED  
**Independent Legal / Linguistic / Child-Development Reviews:** NOT ESTABLISHED

---

## 1. Executive Summary & Critical Clarifications

Stage 31 establishes the external Sinhala dataset acquisition, normalization, deduplication, and pilot corpus construction pipeline for Component 3. 

The stage was executed across twelve discrete work packages (WP0 through WP10), establishing an immutable **180-record pilot corpus** partitioned into train, validation, and locked-test sets with mathematically proven zero leakage across four independent dimensions.

### Core Governance Declarations

```json
{
  "validation_status": "draft",
  "research_eligible": false,
  "approved_for_child_delivery": false,
  "approved_for_unsupervised_child_delivery": false,
  "requires_expert_review": true
}
```

```text
Technical governance reviewer:             REV-GOV-01
Reviewer identity verified:                false (pseudonymous internal technical reviewer)
Internal technical governance concurrence: RECORDED
Independent governance signoff:            NOT ESTABLISHED
Independent legal review:                  NOT ESTABLISHED
Sinhala linguistic review:                 NOT ESTABLISHED
Child-development review:                  NOT ESTABLISHED
```

> [!IMPORTANT]
> **Governance Scope Clarification:**
> Internal technical governance concurrence represents internal verification only. It does not imply legal, linguistic, clinical, or pedagogical approval. Under no circumstances may any raw or derived external corpus record be served to child learners or deployed in unsupervised classroom environments without independent clinical and pedagogical expert review.

---

## 2. Reconciled Conservation Equations

All balance equations from Section 18 of the Implementation Plan are fully reconciled with **zero unaccounted items**:

1. **Candidate-Source Accounting (Section 18.1):**
   $$\text{TotalCandidates (8)} = \text{Approved (5)} + \text{MetadataOnly (1)} + \text{Review (1)} + \text{Blocked (1)} + \text{SourceUnavailable (0)} + \text{Unaccounted (0)}$$
2. **Retrieved-File Accounting (Section 18.2):**
   $$\text{ExpectedFiles (5)} = \text{DownloadedVerified (5)} + \text{Failed (0)} + \text{NotAttempted (0)} + \text{Quarantined (0)} + \text{Unaccounted (0)}$$
3. **Parsed-Unit Accounting (Section 18.3):**
   $$\text{SourceUnits (180)} = \text{Parsed (180)} + \text{SkippedByPolicy (0)} + \text{ParseFailed (0)} + \text{Quarantined (0)} + \text{Unaccounted (0)}$$
4. **Terminal-Disposition Accounting & Model C Reconciliation (Section 18.4):**
   $$\text{CandidateRecords (180)} = \text{Accepted (180)} + \text{ManualReview (0)} + \text{Rejected (0)} + \text{Excluded (0)} + \text{Quarantined (0)} + \text{Unaccounted (0)}$$
   - `ACCEPTED_PILOT_CANDIDATE`: 180
   - `MANUAL_REVIEW_REQUIRED`: 0
   - `REJECTED_RIGHTS`: 0
   - `REJECTED_SECURITY`: 0
   - `REJECTED_PRIVACY`: 0
   - `REJECTED_INVALID_UNICODE`: 0
   - `REJECTED_QUALITY`: 0
   - `EXCLUDED_NON_SINHALA`: 0
   - `EXCLUDED_DUPLICATE`: 0 (Model C Retained)
   - `EXCLUDED_OUT_OF_SCOPE`: 0
   - `QUARANTINED_SOURCE_ERROR`: 0
5. **Near-Duplicate Candidate Accounting (Section 18.4):**
   $$\text{NearDuplicateCandidates (108)} = \text{ConfirmedDuplicateRelation (105)} + \text{ConservativelyUnioned (3)} + \text{RejectedAsDistinct (0)} + \text{UnresolvedAtSealing (0)}$$
   - Unresolved at split sealing: **0**
6. **Pilot Corpus Split Accounting (Section 18.5):**
   $$\text{TotalCorpus (180)} = \text{Train (154)} + \text{Validation (13)} + \text{Locked-Test (13)} + \text{Unaccounted (0)}$$

---

## 3. Exact-Duplicate Accounting & Model C Formal Protocol Deviation

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

## 4. Explanation of Split-Ratio Allocation

The planned 70/15/15 allocation was applied **only to the 90 untouched evaluation-eligible records**. The 90 method-development records were mandatorily assigned to `train` (in accordance with Invariants 18 & 19), producing an overall 85.6% / 7.2% / 7.2% corpus distribution:

- **Untouched Records Population:** $180 - 90 = 90\text{ records}$
  - Untouched Train: $154 - 90 = 64\text{ records}$ ($64 / 90 = 71.1\%$)
  - Validation: $13\text{ records}$ ($13 / 90 = 14.4\%$)
  - Locked-Test: $13\text{ records}$ ($13 / 90 = 14.4\%$)
  - Total Untouched Partition: $71.1\% \text{ Train} + 14.4\% \text{ Val} + 14.4\% \text{ Test} \approx 70 / 15 / 15$
- **Total Combined Corpus Distribution:**
  - `train`: $154 / 180 = 85.6\%$ (contains 100% of method-development units)
  - `validation`: $13 / 180 = 7.2\%$ (zero method-development units)
  - `locked_test`: $13 / 180 = 7.2\%$ (zero method-development units)

---

## 5. Redistribution and Licence Compatibility Framework

For the four sources whose literal text is exported in `public_export_corpus.jsonl`:

1. **`SRC-SI-001` (Sinhala Wikipedia):** CC BY-SA 3.0 / 4.0 Dual. Attribution required ("Contributors to Sinhala Wikipedia"). Imposes Share-Alike.
2. **`SRC-SI-002` (AI4Bharat IndicCorp):** CC BY 4.0. Attribution required (Kakwani et al., 2020). Permissive.
3. **`SRC-SI-003` (FLORES-200):** CC BY-SA 4.0. Attribution required (NLLB Team, Meta AI). Imposes Share-Alike.
4. **`SRC-SI-008` (StoryWeaver):** CC BY 4.0. Attribution required (Pratham Books StoryWeaver + Authors/Illustrators). Permissive.
5. **Corpus Compatibility:** In `public_export_corpus.jsonl`, per-record licences are tagged individually. Any composite adaptation combining CC BY-SA records (`SRC-SI-001`, `SRC-SI-003`) inherits the **CC BY-SA 4.0** compatible share-alike licence.
6. **Restricted Source Isolation:** All 30 records originating from `SRC-SI-004` (UCSC LTRL) have literal text **100% suppressed** (`text: null`), isolating it completely from open redistribution.

---

## 6. Manifest Scope and Negative Tamper Test Results

### Manifest Scope
1. **Planned Documentation Manifest (`docs/stage31_manifest.sha256`):**
   - Controls **11 documentation deliverables** (excludes itself; $12 = 11 + 1$).
2. **Expanded Governed Implementation Manifest (`data/sinhala_external/manifests/stage31_manifest.sha256`):**
   - Controls **29 distinct implementation and documentation artifacts** (excludes itself).

### Rigorous Negative Tamper Test Mechanism
Both manifests were verified using a temporary on-disk artifact copy injected with corruption bytes:
```text
Original manifest modified:                 false
Temporary artifact copy modified:           true
Hash mismatch detected:                     true
Verifier returned failure for tampered copy: true
Negative Tamper Test:                       PASSED
```

---

## 7. Prerequisite Immutability & Full Test Suite Verification

- **Selected Stage 29 Immutability:** All 13 checked items verified bitwise identical (`verify_stage29_immutability.py`).
- **Stage 30 Immutability:** All 11 Stage 30 documentation items and configuration hash (`1a18da3a...`) verified bitwise identical (`verify_stage30_manifest.py`).
- **Stage 31 Manifests:** Both `docs/stage31_manifest.sha256` and `data/sinhala_external/manifests/stage31_manifest.sha256` verified OK with 0 mismatches.
- **Backend Test Suite:** 568/568 passed (545 baseline + 23 Stage 31 tests).
- **Frontend Test Suite & Build:** 17/17 passed; `vite build` completed cleanly in 1.01s.

---

## 8. Authoritative Final Signoff

```text
Historical Initial Checkpoint:             stage-31-complete    (975989e701561d8530781b57c9cd82f8db7ee72d, preserved)
Historical Reconciled Checkpoint:          stage-31-complete-v2 (181e8608364649466ba8bf55fed52bf1a977a0f9, preserved)
Final Reconciled Checkpoint:               stage-31-complete-v3
Prerequisite Checkpoint:                   stage-30-complete-v3 (ef95667b53dddfb032e71fc51d6c524aff7a22a2)
Technical Governance Reviewer:             REV-GOV-01
Reviewer Identity Verified:                false (pseudonymous internal technical reviewer)
Internal Technical Governance Concurrence: RECORDED
Independent Governance Signoff:            NOT ESTABLISHED
Independent Legal Review:                  NOT ESTABLISHED
Sinhala Linguistic Review:                 NOT ESTABLISHED
Child-Development Review:                  NOT ESTABLISHED
Sealed Timestamp:                          2026-10-15T19:50:00+05:30 (UTC: 2026-10-15T14:20:00Z)
Status:                                    SEALED_RECONCILED_V3
```
