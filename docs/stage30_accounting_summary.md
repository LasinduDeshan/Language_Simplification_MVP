# Stage 30 Accounting Summary — Sinhala Preprocessing

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Sinhala (`si`, `si-LK`, script `Sinh`), children aged 4–8  
**Document Version:** 1.0.0  
**Status:** Reconciled & Audited  

---

## 1. Input Record Accounting

Every input record across all governed fixtures is accounted for in exactly one mutually exclusive terminal disposition:

$$
32 = 20 + 2 + 5 + 4 + 1 + 0
$$

\[
\text{Total Inputs} = \text{Passed} + \text{PassedWithNormalization} + \text{ManualReviewRequired} + \text{RejectedInvalidUnicode} + \text{ExcludedNonSinhala} + \text{Unaccounted}
\]

| Disposition Category | Count | Percentage |
|---|---|---|
| `PASSED` | 20 | 62.50% |
| `PASSED_WITH_NORMALIZATION` | 2 | 6.25% |
| `MANUAL_REVIEW_REQUIRED` | 5 | 15.62% |
| `REJECTED_INVALID_UNICODE` | 4 | 12.50% |
| `EXCLUDED_NON_SINHALA` | 1 | 3.12% |
| **Total Inputs** | **32** | **100.0%** |
| **Unaccounted Records** | **0** | **0.0%** |

---

## 2. Transformation Operations Accounting

| Operation Type | Rule Version | Operations Count | Status |
|---|---|---|---|
| `UNICODE_NFC` | 1.0.0 | 1 | All spans mapped [start, end) |
| `WHITESPACE_NORMALIZATION` | 1.0.0 | 2 | Leading/trailing & CRLF normalized |
| **Total Operations** | — | **3** | **Zero unaccounted transformations** |

---

## 3. Structural & Lexical Units Accounting

| Element | Count | Notes |
|---|---|---|
| Sentences Segmented | 32 | Protected decimals & abbreviations intact |
| Total Tokens Produced | 111 | Grapheme-safe tokenization |
| `SINHALA_WORD` Tokens | 73 | Precomposed base + vowel signs |
| `PUNCTUATION` Tokens | 23 | Western periods, Kunddaliya, delimiters |
| `LATIN_WORD` Tokens | 9 | English words in mixed fixtures |
| `ARABIC_NUMBER` Tokens | 3 | Digits 0–9 |
| `SINHALA_NUMBER` Tokens | 1 | Sinhala Lith digit `෧` |
| `UNKNOWN` Tokens | 2 | Special isolated test probes |
| Records with Joiners (`U+200D`/`U+200C`) | 7 | Preserved in allowlist |
| Records with Mixed Scripts | 3 | Preserved without exclusion |
| Records Routed to Review | 5 | Fail-closed routing |

---

## 4. Invariant Verification

- **Offset Boundary Violations:** `0`
- **Exact Normalized-Text Reconstruction Failures:** `0` (exact normalized-text reconstruction verified using ordered token spans and preserved inter-token gaps; token-text concatenation alone is not claimed unless separators are represented explicitly)
- **Pipeline-Introduced Replacement Characters (`U+FFFD`):** `0`
- **Raw-Text Mutation Incidents:** `0` (auditable operation traces and explicit raw-to-normalized span mappings; original text remains recoverable from the immutable `raw_text` field)
- **Accounting Invariant:** `PASSED (Unaccounted = 0)`

---

## 5. Governance Scope and Contract Clarifications

1. **Character Inventory:** The 138-entry inventory is a **governed selected inventory** for early-grade educational preprocessing; it is not an exhaustive enumeration of all assigned and unassigned code points across all referenced Unicode blocks.
2. **Security Controls vs Whitespace:** Null bytes, prohibited C0/C1 controls, bidi overrides, and other denylisted security controls are rejected. Explicitly allowlisted structural whitespace characters (TAB `U+0009`, LF `U+000A`, CR `U+000D`, NBSP `U+00A0`) are preserved or normalized according to policy. Prohibited C1 controls like `U+0085` (NEXT LINE / NEL) are rejected with `REJECTED_INVALID_UNICODE` / `PROHIBITED_CONTROL_CHARACTER`.
3. **Grapheme Conformance Boundary:** `regex` `\X` fixture testing establishes 32-fixture/defined-fixture correctness, not general Sinhala linguistic validity or complete UAX #29 conformance.
4. **Test Suite Scope:** Stage 30 verification comprises **16 test modules / files** containing **43 individual test cases/functions** (43/43 passed).
5. **Git Tag Immutability:** Historical tag `stage-30-complete` remains immutable at checkpoint `155008bbe460386bcaa7042aa7694718fccc08d8`. Reconciled authoritative tag `stage-30-complete-v2` seals this reconciled release.
