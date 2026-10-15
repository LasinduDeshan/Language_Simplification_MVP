# Stage 31 — Completion Record (Reconciled v7)

**Stage:** Stage 31 — Sinhala External Dataset Ingestion and Pilot Corpus Creation  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** `docs/stage31_completion_record.md`  
**Status:** Complete — Final Authoritative Checkpoint Sealed (v7)  
**Authoritative Prerequisite:** `stage-30-complete-v3` (`ef95667b53dddfb032e71fc51d6c524aff7a22a2`)  
**Historical Initial Tag:** `stage-31-complete` (`975989e701561d8530781b57c9cd82f8db7ee72d`, preserved immutable)  
**Historical Reconciled Tag v2:** `stage-31-complete-v2` (`181e8608364649466ba8bf55fed52bf1a977a0f9`, preserved immutable)  
**Historical Reconciled Tag v3:** `stage-31-complete-v3` (`060be30fd6bddc6bc62495d6425cbb9215da5292`, preserved immutable)  
**Historical Reconciled Tag v4:** `stage-31-complete-v4` (`c07a520438941fb047720176c4ef153131dc4716`, preserved immutable)  
**Historical Reconciled Tag v5:** `stage-31-complete-v5` (`7c224f12c4b303aa0178fb488810f4134a7f0eae`, preserved immutable)  
**Historical Reconciled Tag v6:** `stage-31-complete-v6` (`abfda0a7d66fa2a6c4f88d6853af55ed188eb224`, preserved immutable)  
**Final Checkpoint Tag:** `stage-31-complete-v7`  
**Documentation Finalized:** `2026-10-15T21:40:00+05:30` (UTC: `2026-10-15T16:10:00Z`)  
**Authoritative Tag Sealed:** `2026-10-15T21:42:00+05:30`  
**Technical Governance Reviewer:** `REV-GOV-01` (Internal technical reviewer; identity verified: false)  
**Internal Technical Governance Concurrence:** RECORDED  
**Independent Governance Signoff:** NOT ESTABLISHED  
**Independent Legal / Linguistic / Child-Development Reviews:** NOT ESTABLISHED

---

## 1. Executive Summary & Critical Governance Framework

Stage 31 establishes the external Sinhala dataset acquisition, normalization, deduplication, dual-view pilot corpus construction, and rights-containment export pipeline for Component 3.

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

---

## 2. IndicCorp Conclusive Rights Resolution (Option A)

Following conclusive verification against the upstream `AI4Bharat/indicnlp_corpus` repository, `SRC-SI-002` has been verified and approved exclusively for internal non-commercial research:

- **Source Identifier:** `SRC-SI-002`
- **Artifact:** IndicCorp v1 Sinhala / `si.txt.gz`
- **Applicable Licence:** **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**
- **Primary Decision:** `APPROVED`
- **Rights Scope:** `APPROVED_INTERNAL_NONCOMMERCIAL_ONLY` (descriptive rights scope; primary decision enum is strictly `APPROVED`)
- **Rights Profile ID:** `RP-SRC-SI-002` (version 2)
- **Permissions:**
  - `internal_research_use_allowed`: `true`
  - `commercial_use_allowed`: `false`
  - `public_literal_export_enabled`: `false`
- **Effective Export Policy:** `SUPPRESSED_BY_PROJECT_POLICY`
- **Rights Evidence Repository:** `AI4Bharat/indicnlp_corpus`
- **Rights Evidence Commit:** `7afab312dea591eca37abfa329999b1da3675b5b`
- **Rights Evidence Path:** `README.md` (Upstream CC BY-NC-SA 4.0 grant defined in `README.md#license`)
- **Rights Evidence URL:** `https://raw.githubusercontent.com/AI4Bharat/indicnlp_corpus/7afab312dea591eca37abfa329999b1da3675b5b/README.md`
- **Source Rights Evidence SHA-256:** `1ee3150c67dfc4e793c9e510c06305f093fc5678f63e45bcdc3ed912b340fd3a` (hash of pinned upstream `README.md` containing licence declaration)
- **Canonical Licence Text Path:** `data/sinhala_external/registry/licence_snapshots/CC-BY-NC-SA-4.0.txt`
- **Canonical Licence Text SHA-256:** `dc95bad5386871bab6b5b62daa4d2ae2eb4aa5244e37dff11ff233514761cbef` (hash of local canonical CC BY-NC-SA 4.0 legal code)
- **Public Export Status:** Literal text is **100% suppressed** (`text: null`) with `export_redistribution_status: "SUPPRESSED_BY_PROJECT_POLICY"`.

---

## 3. Dual Corpus Views & Analytical Population Ledger

To prevent distortion of linguistic statistics and lexicon construction while preserving source provenance, Stage 31 exports two distinct views:

- **Provenance-Preserving Corpus (180 records):** Located at `data/sinhala_external/corpus/pilot_corpus.jsonl`.
- **Canonical Analytical Corpus (150 records):** Located at `data/sinhala_external/corpus/canonical_analytical_corpus.jsonl`.

### Analytical Ledger Verification
- **Canonical Analytical Corpus Present in Manifest:** `true`
- **Stored Record Instances:** **180**
- **Unique Exact-Text Canonical Records:** **150**
- **Noncanonical Exact Duplicates in Canonical View:** **0**
- **Canonical-to-Provenance Mapping Failures:** **0**
- **Sum of Provenance Weights:** **150.0**
- **Surplus Retained Duplicate Instances:** **30** (across 5 multi-member clusters)
- **Retention Reason:** Retained to preserve source-level and reading-tier provenance for future governed analysis. Stage 31 performs no simplification-model evaluation.
- **Zero Split Leakage:** All duplicate members share the exact same `split_group_id` (`SPLIT-GRP-SI-000146` to `SPLIT-GRP-SI-000150`) and reside exclusively in `train`.

---

## 4. Public Export Policy Enforcement Ledger

```text
Public Export Policy Enforcement Ledger:
  Total Records Evaluated:                                 180
  Public Permitted Records (with text):                    110
  Protected Academic Records (SRC-SI-004 text null):       30
  Project Policy Suppressed (SRC-SI-002 text null):        40
  Total Literal Text Suppressed Records:                   70
  Literal restricted text detected in configured fields:   0 (PASSED)
```

> [!NOTE]
> **Internal Rights Assessment:**
> Records retain their individual source licences. If text is adapted or combined into a single derivative, the applicable compatibility and share-alike obligations must be assessed before redistribution. Mere aggregation into a corpus does not, by itself, establish that every independent record has been relicensed. This is an internal rights assessment, not legal advice.

---

## 5. Manifest Scope and Verification

1. **Planned Documentation Manifest (`docs/stage31_manifest.sha256`):**
   - Controls **12 documentation deliverables** (excludes itself; $13 = 12 + 1$), restoring `docs/stage31_pilot_corpus_report.md` alongside `docs/stage31_governance_report.md`.
2. **Expanded Governed Implementation Manifest (`data/sinhala_external/manifests/stage31_manifest.sha256`):**
   - Controls **32 distinct implementation and documentation artifacts** (12 docs + 20 data/registry/corpus artifacts, including `CC-BY-NC-SA-4.0.txt` and `canonical_analytical_corpus.jsonl`).
   - The checksum manifest does not claim to hash itself.

---

## 6. Authoritative Final Signoff

```text
Historical Initial Checkpoint:             stage-31-complete    (975989e701561d8530781b57c9cd82f8db7ee72d, preserved)
Historical Reconciled Checkpoint v2:       stage-31-complete-v2 (181e8608364649466ba8bf55fed52bf1a977a0f9, preserved)
Historical Reconciled Checkpoint v3:       stage-31-complete-v3 (060be30fd6bddc6bc62495d6425cbb9215da5292, preserved)
Historical Reconciled Checkpoint v4:       stage-31-complete-v4 (c07a520438941fb047720176c4ef153131dc4716, preserved)
Historical Reconciled Checkpoint v5:       stage-31-complete-v5 (7c224f12c4b303aa0178fb488810f4134a7f0eae, preserved)
Historical Reconciled Checkpoint v6:       stage-31-complete-v6 (abfda0a7d66fa2a6c4f88d6853af55ed188eb224, preserved)
Final Reconciled Checkpoint:               stage-31-complete-v7
Prerequisite Checkpoint:                   stage-30-complete-v3 (ef95667b53dddfb032e71fc51d6c524aff7a22a2)
Technical Governance Reviewer:             REV-GOV-01
Reviewer Identity Verified:                false (pseudonymous internal technical reviewer)
Internal Technical Governance Concurrence: RECORDED
Independent Governance Signoff:            NOT ESTABLISHED
Independent Legal Review:                  NOT ESTABLISHED
Sinhala Linguistic Review:                 NOT ESTABLISHED
Child-Development Review:                  NOT ESTABLISHED
Documentation Finalized:                   2026-10-15T21:40:00+05:30 (UTC: 2026-10-15T16:10:00Z)
Authoritative Tag Sealed:                  2026-10-15T21:42:00+05:30
Status:                                    SEALED_RECONCILED_V7
```
