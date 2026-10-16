# Stage 32 Accounting Summary

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** Authoritative Multi-Level Accounting Summary  
**Stage:** Stage 32 — Sinhala Child-Vocabulary Lexicon Construction  
**Status:** Authoritative Accounting Deliverable  

---

## 1. Exact Multi-Level Accounting Reconciliation

```text
Level 1: Corpus Input Accounting
  Expected Canonical Records:           150
  Processed Canonical Records:          150
  Provenance Corpus Records:            180
  Unaccounted Corpus Records:           0

Level 2: Token Occurrence Accounting
  Total Token Occurrences Observed:     4,072
  Included Candidate Occurrences:       3,668
  Excluded Token Class Occurrences:       400
  Manual Review Occurrences:                4
  Rejected Occurrences:                     0
  Unaccounted Token Occurrences:            0

Level 3: Candidate Entry Accounting
  Total Extracted Candidates:           1,010
  Accepted Draft Entries:               1,002
  Manual Review Required Entries:           8
  Excluded Non-Lexical Entries:             0
  Excluded Non-Sinhala Entries:             0
  Rejected Entries:                         0
  Unaccounted Candidate Entries:            0

Level 4: Provisional Band Accounting
  Foundational Candidates:                 12
  Early Candidates:                        14
  Developing Candidates:                  151
  Advanced Candidates:                    678
  Review Required:                        155
  Excluded Non-Lexical:                     0
  Sum of Provisional Bands:             1,010
  Unaccounted Banded Entries:               0

Level 5: Duplicate Weight Parity
  Canonical Primary Denominator:        150
  Provenance Records:                   180
  Sum of Cluster Duplicate Weights:     149.999995
  Delta vs Canonical Denominator:       0.000005 (within 1e-4 tolerance)
  Maximum Per-Term Parity Delta:        0.000000

Level 6: Contributing Source Membership & Rights Profile Accounting
  Distinct Lexicon Entries:             1,010
  Entry-Source Memberships:             1,194
  Entries Occurring in Multiple Sources:  138 (derived from membership ledger)
  Entries Occurring in Single Source:     872
  Included Token Occurrences:           3,668
  Missing Rights-Profile References:        0
  Unregistered Contributing Sources:        0
  Membership Ledger Invariant:          sum_{e=1}^{1010} |sources_e| = 1,194 (PASSED)
```

---

## 2. Contributing Source Membership and Version-Pinned Rights Inheritance

> **Authoritative Rights Notice:**  
> Licence labels shown in Stage 32 are descriptive only. The authoritative rights decision is the exact `rights_profile_id` and `rights_profile_version` inherited from `stage-31-complete-v8`.

| Source ID | Source Name | Descriptive Licence Label | Contributing Entries (Memberships) | Included Token Occurrences | Pinned Stage 31 Rights Profile ID | Inherited Profile Version | Field Export Posture |
|---|---|---|---:|---:|---|---:|---|
| `SRC-SI-001` | Sinhala Wikipedia Official Dump | CC BY-SA 4.0 (Wikimedia pinned) | 448 | 1,450 | `RP-SRC-SI-001` | 1 | `PUBLIC_PERMITTED_STANDALONE` |
| `SRC-SI-002` | AI4Bharat IndicCorp Sinhala | CC BY-NC-SA 4.0 | 207 | 594 | `RP-SRC-SI-002` | 2 | `SUPPRESSED_BY_PROJECT_POLICY` |
| `SRC-SI-003` | FLORES-200 Sinhala Benchmark | CC BY-SA 4.0 | 179 | 448 | `RP-SRC-SI-003` | 1 | `PUBLIC_PERMITTED_STANDALONE` |
| `SRC-SI-004` | UCSC LTRL Sinhala News / POS | Academic Research Agreement | 215 | 946 | `RP-SRC-SI-004` | 1 | `PROTECTED_INTERNAL_ONLY` |
| `SRC-SI-008` | StoryWeaver Sinhala Children | CC BY 4.0 | 145 | 230 | `RP-SRC-SI-008` | 1 | `PUBLIC_PERMITTED_STANDALONE` |
| **Total** | **All 5 Contributing Sources** | **Inherited from Stage 31 v8** | **1,194** | **3,668** | **All 5 Validated** | **Exact Equality** | **Zero Field Leaks** |

> **Note on SRC-SI-002:**  
> - Effective Stage 32 export policy: `SUPPRESSED_BY_PROJECT_POLICY`  
> - Underlying licence observation: CC BY-NC-SA 4.0 may permit qualifying standalone noncommercial redistribution, subject to attribution and share-alike obligations; Stage 32 does not enable that export.

### Multi-Level Membership Reconciliation
- Distinct lexicon entries: 1,010
- Entry-source memberships: 1,194
- Entries occurring in multiple sources: 138 (124 in 2 sources, 14 in 3 sources)
- Entries occurring in a single source: 872
- Included token occurrences: 3,668
- Missing rights-profile references: 0
- Unregistered contributing sources: 0

$$\sum_{e=1}^{1010}|\text{contributing sources}_e|=1,194$$

Do not sum the five source-specific entry counts directly into "1,010 distinct entries." The sum represents 1,194 entry-source memberships across 1,010 distinct lexicon entries.

---

## 3. Reconciliation of Review Units (4 Token Occurrences vs. 8 Candidate Entries)

The 4 manual-review token occurrences and 8 review-required candidate entries operate at two completely distinct, sequential screening boundaries:

1. **Level 2 (Token Occurrence Bridge):** Exactly **4 token occurrences** (`SI-OCC-00000006`, `SI-OCC-00000103`, `SI-OCC-00000694`, `SI-OCC-00000815`) were flagged at the Stage 30/31 ingestion bridge with exclusion reason `MIXED_SCRIPT_TOKEN` (`MANUAL_REVIEW_OCCURRENCE`). Because they failed the lexical token class filter, they were decoupled to protected storage, contractually preserved with `entry_id: null`, `candidate_extraction_status: "NOT_EXTRACTED"`, `reason_codes: ["MIXED_SCRIPT_TOKEN"]`, and abstract `protected_context_ref` without dummy foreign keys. They did **not** generate candidate lexicon entries.
2. **Level 3 (Candidate Lexicon Entries):** The **3,668 included candidate occurrences** were grouped into **1,010 distinct candidate entries**. The automated quality screener (`LexiconQualityRouter`) screened all 1,010 entries, passing 1,002 clean entries as `ACCEPTED_DRAFT_LEXICON_ENTRY` and routing exactly **8 candidate entries** to `MANUAL_REVIEW_REQUIRED`:
   - 6 sensitive / clinical vocabulary items (`SENSITIVE_VOCABULARY_FLAG` e.g. danger, illness terms) routed to the P1 review queue for expert child-safety evaluation.
   - 2 suspected character repetition / OCR artifact items (`OCR_OR_REPETITION_FLAG` / `SUSPECTED_OCR_OR_REPETITION_ARTIFACT`) routed for manual inspection.
3. **Morphology Referrals:** Low-confidence morphology referrals are strictly **0** (`LOW_CONFIDENCE_MORPHOLOGY = 0`; all 1,010 candidate entries retained identity canonical form with confidence 1.0). Exactly 8 candidate entries require manual review: 6 under `SENSITIVE_VOCABULARY_FLAG` and 2 under `OCR_OR_REPETITION_FLAG`. The 8 review entries are NOT competing morphology hypotheses derived from the 4 review occurrences; the two metrics represent independent anomalies at two separate screening gates.
