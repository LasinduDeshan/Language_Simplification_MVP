# Stage 30 Error Analysis and Edge-Case Governance — Sinhala Preprocessing

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Sinhala (`si`, `si-LK`, script `Sinh`), children aged 4–8  
**Report Version:** 1.0.0  
**Status:** Complete & Sealed  

---

## 1. Executive Summary

This error analysis examines the edge cases, potential failure modes, and fail-closed routing decisions in the Stage 30 Sinhala Unicode normalization and preprocessing pipeline.

Across the 32 governed test fixtures, 0 unaccounted records, 0 offset failures, and 0 pipeline-introduced replacement characters occurred.

---

## 2. Detailed Edge-Case Analysis

### 2.1 Security Controls and Invalid Unicode
- **Prohibited Controls:** Inputs containing null bytes (`\0`), C0 controls (`\x07`), or bidirectional overrides (`U+202E`) are immediately routed to `REJECTED_INVALID_UNICODE` with reason `PROHIBITED_CONTROL_CHARACTER`.
- **Pre-Existing Replacement Characters:** When an input text already contains `U+FFFD`, it is rejected under `REJECTED_INVALID_UNICODE` with reason code `PREEXISTING_REPLACEMENT_CHARACTER`.
  > *Governance Distinction:* The record is rejected because source-text fidelity cannot be established, not because `U+FFFD` itself is an invalid Unicode scalar.
- **Pipeline Replacement Character Invariant:** In no case did the pipeline introduce `U+FFFD` into valid text. The count of `REPLACEMENT_CHARACTER_INTRODUCED_BY_PIPELINE` was verified to be strictly `0`.

### 2.2 Combining Marks and Lith Digits Distinction
- **Initial Risk:** In early draft specifications, combining mark ranges were broadly specified as `U+0DCA <= cp <= 0x0DF3`, which inadvertently encompassed Sinhala Lith Digits `U+0DE6` to `U+0DEF`.
- **Resolution:** The validator was refined to strictly use standard Unicode general categories: combining marks must belong to category `M` (`Mn` or `Mc`). Lith digits belong to category `Nd` (Number, decimal digit) and are correctly treated as base numeric characters, eliminating false combining-mark rejections.
- **Unattached Marks:** A combining mark appearing at index 0 or preceded by a non-attaching character (such as whitespace) is routed to `MANUAL_REVIEW_REQUIRED` with reason `COMBINING_SEQUENCE_REVIEW`.
- **Excessive Runs:** Combining mark runs exceeding 3 consecutive marks are flagged and routed to `MANUAL_REVIEW_REQUIRED`.

### 2.3 Joiner (ZWJ / ZWNJ) Orthographic Contexts
- **Allowlisted Contexts:** ZWJ (`U+200D`) appearing in valid Yansaya (`[C, Virama, ZWJ, Ya]`), Rakaransaya (`[C, Virama, ZWJ, Ra]`), Bandi-akuru conjuncts, or Repaya (`[Ra, Virama, ZWJ, C]`) is preserved without modification.
- **Unexpected Contexts:** Isolated ZWJ at string boundaries (e.g. `පාසල\u200D`) is preserved in raw text, flagged with `UNEXPECTED_JOINER_CONTEXT`, and routed to `MANUAL_REVIEW_REQUIRED`. Joiners are never silently stripped.

### 2.4 Mixed-Script Educational Text vs Non-Sinhala Exclusion
- **Mixed-Script Invariant:** Sentences containing English words alongside Sinhala (e.g., `Grade 2 සිසුන්.`, `Maths පාඩම`) are explicitly supported. The flag `MIXED_SCRIPT_PRESENT` is assigned, tokens are categorized accurately (`LATIN_WORD`, `SINHALA_WORD`), and the text is **not** excluded.
- **Governed Exclusion Rule:** `EXCLUDED_NON_SINHALA` applies exclusively when trusted input provenance does not declare Sinhala AND zero Sinhala script characters are present in the text.

### 2.5 Sentence Boundary False Positives
- **Decimals:** Periods flanked by digits (`12.5`) are protected from sentence splitting.
- **Abbreviations:** Governed abbreviations (`වෛ.`, `මහා.`, `පෙ.ව.`, `ප.ව.`, `Dr.`, `No.`) are protected from false terminal splits.
- **Repeated Runs:** Runs of multiple punctuation marks (`...`, `?!`) are treated as a single composite boundary, ensuring trailing periods are not emitted as empty sentences.

---

## 3. Summary of Failure Metrics

| Metric | Target | Observed | Status |
|---|---|---|---|
| Unaccounted records | 0 | 0 | PASSED |
| Pipeline-introduced `U+FFFD` | 0 | 0 | PASSED |
| Offset mapping failures | 0 | 0 | PASSED |
| Token reconstruction failures | 0 | 0 | PASSED |
| Raw-text mutations | 0 | 0 | PASSED |
| Disposition mismatch rate | 0.0% | 0.0% | PASSED |
