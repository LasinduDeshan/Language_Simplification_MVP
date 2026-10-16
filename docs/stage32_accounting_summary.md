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
  Accepted Draft Entries:               1,001
  Manual Review Required Entries:           9
  Excluded Non-Lexical Entries:             0
  Excluded Non-Sinhala Entries:             0
  Rejected Entries:                         0
  Unaccounted Candidate Entries:            0

Level 4: Provisional Band Accounting
  Foundational Candidates:                 12
  Early Candidates:                        14
  Developing Candidates:                  151
  Advanced Candidates:                    677
  Review Required:                        156
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

## 3. Reconciliation of Review Units (4 Token Occurrences vs. 9 Candidate Entries)

The 4 manual-review token occurrences and 9 review-required candidate entries operate at two completely distinct, sequential screening boundaries:

1. **Level 2 (Token Occurrence Bridge):** Exactly **4 token occurrences** (`SI-OCC-00000006`, `SI-OCC-00000103`, `SI-OCC-00000694`, `SI-OCC-00000815`) were flagged at the Stage 30/31 ingestion bridge with exclusion reason `MIXED_SCRIPT_TOKEN` (`MANUAL_REVIEW_OCCURRENCE`). Because they failed the lexical token class filter, they were decoupled to protected storage, contractually preserved with `entry_id: null`, `candidate_extraction_status: "NOT_EXTRACTED"`, `reason_codes: ["MIXED_SCRIPT_TOKEN"]`, and abstract `protected_context_ref` without dummy foreign keys. They did **not** generate candidate lexicon entries.
2. **Level 3 (Candidate Lexicon Entries):** The **3,668 included candidate occurrences** were grouped into **1,010 distinct candidate entries**. The automated quality screener (`LexiconQualityRouter`) screened all 1,010 entries, passing 1,001 clean entries as `ACCEPTED_DRAFT_LEXICON_ENTRY` and routing exactly **9 candidate entries** to `MANUAL_REVIEW_REQUIRED`:
   - 3 sensitive / clinical semantic heuristic items (`POTENTIALLY_SENSITIVE_SEMANTIC_REVIEW`: `SI-LEX-000020` අනතුරු, `SI-LEX-000428` නිරෝගී, `SI-LEX-000723` රෝග) routed to the P1 review queue for expert child-safety evaluation.
   - 6 structural complexity / rare form items (`COMPLEX_OR_RARE_FORM_REVIEW`: `SI-LEX-000193` ක්‍රියාකාරිත්වය, `SI-LEX-000199` කාබන්ඩයොක්සයිඩ්, `SI-LEX-000482` ප්‍රජාතන්ත්‍රවාදී, `SI-LEX-000487` ප්‍රතිශක්තිකරණයටද, `SI-LEX-000497` ප්‍රභාසංස්ලේෂණය, `SI-LEX-000905` සරච්චන්ද්‍රයන්ගේ) routed for morphological and developmental adjudication.
   - 0 OCR anomalies (`OCR_OR_REPETITION_FLAG = 0`; legitimate words like `ගොඩනැගිල්ලේ` and `ප්‍රභාසංස්ලේෂණය` are verified free of code-point repetition).
3. **Morphology Referrals:** Low-confidence morphology referrals are strictly **0** (`LOW_CONFIDENCE_MORPHOLOGY = 0`; all 1,010 candidate entries retained identity canonical form with confidence 1.0). Exactly 9 candidate entries require manual review: 3 under `POTENTIALLY_SENSITIVE_SEMANTIC_REVIEW` and 6 under `COMPLEX_OR_RARE_FORM_REVIEW`.
4. **Provisional Band vs. Entry Disposition Reconciliation:**
   - Assigned proficiency bands: 12 (Foundational) + 14 (Early) + 151 (Developing) + 677 (Advanced) = **854 entries**
   - Provisional band `REVIEW_REQUIRED`: **156 entries**
     = 147 accepted-draft entries with unresolved threshold boundaries/ties
     + 9 empirical review entries
   - Total: 854 + 156 = **1,010 distinct entries**
