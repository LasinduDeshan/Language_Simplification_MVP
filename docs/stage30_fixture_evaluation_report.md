# Stage 30 Fixture Evaluation Report — Sinhala Preprocessing

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Sinhala (`si`, `si-LK`, script `Sinh`), children aged 4–8  
**Evaluation Suite:** Governed Preprocessing Fixture Evaluation v1.0.0  
**Status:** Complete & Reconciled  

---

## 1. Executive Summary

This report documents the empirical evaluation of the Stage 30 Sinhala Unicode normalization and preprocessing pipeline against all 32 governed fixtures across 6 technical categories.

### Key Evaluation Invariants
- **Raw-Text Preservation Rate:** `100.0%` (Zero raw texts mutated).
- **NFC Normalization Idempotence:** `100.0%` ($NFC(NFC(x)) = NFC(x)$ across all inputs).
- **Fixture Disposition Accuracy:** `32/32 (100.0%)`.
- **Pipeline-Introduced Replacement Characters (`U+FFFD`):** `0` (Zero tolerance confirmed).
- **Exact Normalized-Text Reconstruction Failures:** `0` (Exact normalized-text reconstruction verified using ordered token spans and preserved inter-token gaps; token-text concatenation alone is not claimed unless separators are represented explicitly).
- **Unaccounted Records:** `0` (Exact mathematical reconciliation achieved).

---

## 2. Fixture Category Distribution & Results

| Fixture File | Category Tested | Records | Matched | Pass Rate |
|---|---|---|---|---|
| `normalization_cases.json` | NFC preservation & whitespace operations | 5 | 5 | 100.0% |
| `grapheme_cases.json` | Extended grapheme clusters, Yansaya, Rakaransaya, Repaya | 5 | 5 | 100.0% |
| `sentence_cases.json` | Full stops, question/exclamation marks, kunddaliya, decimals, abbreviations | 5 | 5 | 100.0% |
| `tokenization_cases.json` | Sinhala words, Latin words, mixed tokens, Arabic & Lith digits | 5 | 5 | 100.0% |
| `mixed_script_cases.json` | Educational mixed Sinhala–English text & non-Sinhala exclusion | 3 | 3 | 100.0% |
| `invalid_unicode_cases.json` | U+FFFD, prohibited controls (C0, nulls, bidi), unattached & excessive marks, isolated ZWJ, empty text | 9 | 9 | 100.0% |
| **Total** | **All Categories** | **32** | **32** | **100.0%** |

---

## 3. Terminal Disposition Reconciliation

Every input record is reconciled to exactly one mutually exclusive terminal disposition following the frozen left-to-right precedence rule:

$$\text{REJECTED\_INVALID\_UNICODE} \longrightarrow \text{MANUAL\_REVIEW\_REQUIRED} \longrightarrow \text{EXCLUDED\_NON\_SINHALA} \longrightarrow \text{PASSED\_WITH\_NORMALIZATION} \longrightarrow \text{PASSED}$$

### Disposition Breakdown
- `PASSED`: 20
- `PASSED_WITH_NORMALIZATION`: 2
- `MANUAL_REVIEW_REQUIRED`: 5
- `REJECTED_INVALID_UNICODE`: 4
- `EXCLUDED_NON_SINHALA`: 1
- **Unaccounted Records:** `0`

### Accounting Formula Verification

$$
32 = 20 + 2 + 5 + 4 + 1 + 0
$$

\[
\text{Total Inputs (32)} = 20 (\text{PASSED}) + 2 (\text{PASSED\_WITH\_NORMALIZATION}) + 5 (\text{MANUAL\_REVIEW}) + 4 (\text{REJECTED}) + 1 (\text{EXCLUDED}) + 0 (\text{UNACCOUNTED})
\]

---

## 4. Linguistic and Structural Elements Breakdown

- **Total Recorded Operations:** 3
  - NFC operations: 1
  - Whitespace normalization operations: 2
- **Total Sentences Segmented:** 32
- **Total Tokens Produced:** 111
  - `SINHALA_WORD`: 73
  - `PUNCTUATION`: 23
  - `LATIN_WORD`: 9
  - `ARABIC_NUMBER`: 3
  - `SINHALA_NUMBER`: 1
  - `UNKNOWN`: 2
- **Records with Joiners (`U+200D`/`U+200C`):** 7
- **Records with Mixed Scripts (Sinhala + Latin):** 3
- **Records Routed to Review:** 5

---

## 5. Non-Clinical and Governance Invariant Statement

All evaluated fixtures and derived records retain the governance metadata:
```json
{
  "validation_status": "draft",
  "research_eligible": false,
  "approved_for_child_delivery": false,
  "requires_expert_review": true
}
```

### Governing Boundaries
1. **Governed Selected Inventory:** The 138-entry inventory is a governed selected inventory selected for technical preprocessing of anticipated early-grade content; it is not an exhaustive enumeration of all code points.
2. **Defined-Fixture Grapheme Scope:** `regex` `\X` fixture testing establishes 32-fixture/defined-fixture correctness, not general Sinhala linguistic validity or complete UAX #29 conformance.
3. **Test Scope Distinction:** Stage 30 verification comprises **16 test modules / files** with **44 individual test cases/functions** (44/44 passed).
4. **Selected Stage 29 Immutability Scope (13 Items):** The 13 checked items represent a selected Stage 29 immutability scope comprising the 11 manifest-controlled documentation deliverables plus 2 runtime registry artifacts (`font_registry.json`, `control_character_policy.json`). It does not include `docs/stage29_manifest.sha256` or every Stage 29 runtime artifact.
5. **Non-Authoritative Delivery:** Technical fixture evaluation results do not constitute population-level linguistic accuracy or approval for unsupervised child delivery.
6. **Git Tag Immutability:** Historical tag `stage-30-complete` (`c395bfe3f9059f756640118635e31fd26bfc9341`) and reconciled checkpoint tag `stage-30-complete-v2` (`2441c4f73d8c5b62732943a21307428a0034801a`) remain strictly immutable. Authoritative completion tag `stage-30-complete-v3` seals this final reconciliation with full CRLF governance, indexed reconstruction formulation, and selected Stage 29 immutability scope clarification.
