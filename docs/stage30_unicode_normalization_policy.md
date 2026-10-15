# Stage 30 Unicode Normalization Policy — Sinhala

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Sinhala (`si`, `si-LK`, script `Sinh`), children aged 4–8  
**Policy Version:** 1.0.0  
**Status:** Frozen & Governed  

---

## 1. Purpose and Foundational Principles

This policy defines the deterministic, fail-closed, and auditable Unicode normalization standards for Sinhala text preprocessing in Stage 30.

### Core Principles
1. **Raw Text Immutability:** Raw input is captured exactly as received and hashed via SHA-256. Normalization writes exclusively to a separate derived representation `normalized_text`.
2. **Auditable Operation Traces:** Every transformation (NFC composition, whitespace collapse, control handling) is captured in auditable operation traces and explicit raw-to-normalized span mappings; original text remains recoverable from the immutable raw_text field.
3. **No Silent Corrections:** Unknown, ambiguous, or suspicious orthographic sequences are flagged and routed to manual review rather than silently rewritten or stripped.
4. **Non-Authoritative Scope:** Technical normalization correctness does not imply linguistic correctness, child suitability, or clinical approval (`approved_for_child_delivery: false`).

---

## 2. Unicode Forms and Idempotence

### 2.1 Primary Derived Canonical Form: NFC

All derived text is normalized using Unicode Normalization Form C (NFC):
\[
\text{normalized\_text} = NFC(\text{raw\_text})
\]

- NFC is the standard canonical form across web and mobile platforms and ensures precomposed base consonants and dependent vowel signs form consistent grapheme clusters.
- NFD (Decomposition) is calculated only for diagnostic comparisons and test assertions; it is never stored as the production canonical text.

### 2.2 Normalization Idempotence

Every normalized output must satisfy the idempotence property:
\[
NFC(NFC(x)) = NFC(x)
\]
A second pass through the normalizer must produce zero changes (`operations: []` empty, `changed: false`).

---

## 3. Character Inventory and Number Systems

The 138-entry character inventory is a **governed selected inventory** selected for technical preprocessing of anticipated early-grade content; it is not an exhaustive enumeration of all assigned and unassigned code points across all referenced Unicode blocks. The selected inventory covers:

### 3.1 Sinhala Block (`U+0D80–U+0DFF`)
- **Independent Vowels:** `U+0D85` (අ) through `U+0D96` (ඖ)
- **Consonants:** `U+0D9A` (ක) through `U+0DC6` (ෆ)
- **Dependent Vowel Signs:** `U+0DCF` (ා) through `U+0DF3` (ෲ)
- **Al-lakuna / Virama:** `U+0DCA` (්)
- **Anusvara & Visarga:** `U+0D82` (ං) and `U+0D83` (ඃ)
- **Sinhala Punctuation:** Kunddaliya `U+0DF4` (෴)
- **Sinhala Lith Digits:** `U+0DE6` (෦) through `U+0DEF` (෯)

### 3.2 Sinhala Archaic Numbers Block (`U+111E1–U+111F4`)
- Historical Sinhala numbers (e.g., Sinhala Archaic Digit One `U+111E1` to Number One Thousand `U+111F4`).
- Classified under script block `Sinhala Archaic Numbers` and distinguished from modern digits.

### 3.3 Arabic / ASCII Digits (`U+0030–U+0039`)
- Standard digits `0` to `9` commonly used in modern contemporary Sinhala educational materials. Classified as `ARABIC_NUMBER`.

### 3.4 Format and Joiner Controls
- Zero Width Joiner: `U+200D` (ZWJ)
- Zero Width Non-Joiner: `U+200C` (ZWNJ)

---

## 4. Joiner (ZWJ / ZWNJ) Governance

Stage 30 does not possess authoritative linguistic knowledge to determine general orthographic validity. Therefore, joiner behavior is strictly governed by allowlisted test contexts:

1. **Allowlisted Joiner Contexts (Preserved in NFC):**
   - **Yansaya:** Consonant + Virama (`U+0DCA`) + ZWJ (`U+200D`) + Ya (`U+0DBF`) $\rightarrow$ e.g., `ක්‍ය`
   - **Rakaransaya:** Consonant + Virama (`U+0DCA`) + ZWJ (`U+200D`) + Ra (`U+0DBB`) $\rightarrow$ e.g., `ක්‍ර`
   - **Bandi-akuru (Conjuncts):** Consonant + Virama (`U+0DCA`) + ZWJ (`U+200D`) + Consonant $\rightarrow$ e.g., `ක්ව`
   - **Repaya:** Ra (`U+0DBB`) + Virama (`U+0DCA`) + ZWJ (`U+200D`) + Consonant $\rightarrow$ e.g., `ර්‍ක`
2. **Unexpected Joiner Contexts:**
   - Any ZWJ or ZWNJ appearing in non-allowlisted contexts (e.g. adjacent to whitespace, isolated, or at boundary) is **preserved in raw text**, flagged with `UNEXPECTED_JOINER_CONTEXT`, and routed to `MANUAL_REVIEW_REQUIRED`.
   - Joiners are **never silently stripped or inserted**.

---

## 5. Security Controls, U+FFFD, and Validation Policy

Null bytes, prohibited C0/C1 controls, bidi overrides, and other denylisted security controls are rejected. Explicitly allowlisted structural whitespace characters are preserved or normalized according to the frozen field policy.

### 5.1 Control Characters vs. Allowlisted Whitespace Classification

| Code Point | Character Name | Category | Status | Disposition / Handling |
|---|---|---|---|---|
| `U+0000` | NULL | `Cc` (C0) | Prohibited Control | `REJECTED_INVALID_UNICODE` (`PROHIBITED_CONTROL_CHARACTER`) |
| `U+0001–U+0008` | C0 Controls (SOH, STX, ETX, EOT, ENQ, ACK, BEL, BS) | `Cc` (C0) | Prohibited Control | `REJECTED_INVALID_UNICODE` (`PROHIBITED_CONTROL_CHARACTER`) |
| `U+0009` | CHARACTER TABULATION (TAB) | `Cc` (C0) | Allowlisted Whitespace | Preserved in raw text; collapsed to ASCII space (`U+0020`) in normalized text |
| `U+000A` | LINE FEED (LF) | `Cc` (C0) | Allowlisted Whitespace | Preserved in raw text; preserved as structural line break in normalized text |
| `U+000B–U+000C` | LINE TABULATION (VT), FORM FEED (FF) | `Cc` (C0) | Prohibited Control | `REJECTED_INVALID_UNICODE` (`PROHIBITED_CONTROL_CHARACTER`) |
| `U+000D` | CARRIAGE RETURN (CR) | `Cc` (C0) | Allowlisted Whitespace | Preserved in raw text; converted to `U+000A` (LF) in normalized text |
| `U+000E–U+001F` | C0 Controls (SO, SI, DLE, DC1–DC4, NAK, SYN, ETB, CAN, EM, SUB, ESC, FS, GS, RS, US) | `Cc` (C0) | Prohibited Control | `REJECTED_INVALID_UNICODE` (`PROHIBITED_CONTROL_CHARACTER`) |
| `U+007F` | DELETE (DEL) | `Cc` (C0) | Prohibited Control | `REJECTED_INVALID_UNICODE` (`PROHIBITED_CONTROL_CHARACTER`) |
| `U+0085` | NEXT LINE (NEL) | `Cc` (C1) | Prohibited Control | `REJECTED_INVALID_UNICODE` (`PROHIBITED_CONTROL_CHARACTER`). If encountered, rejected under security control policy. |
| `U+0080–U+0084`, `U+0086–U+009F` | C1 Controls | `Cc` (C1) | Prohibited Control | `REJECTED_INVALID_UNICODE` (`PROHIBITED_CONTROL_CHARACTER`) |
| `U+0020` | SPACE | `Zs` | Allowlisted Whitespace | Standard inter-word whitespace |
| `U+00A0` | NO-BREAK SPACE (NBSP) | `Zs` | Allowlisted Whitespace | Preserved in raw text; collapsed to `U+0020` in normalized text |

### 5.2 Disposition and Validation Rules

| Sequence / Condition | Technical Disposition | Reason Code | Explanation |
|---|---|---|---|
| Null bytes (`\0`), prohibited C0/C1 control characters | `REJECTED_INVALID_UNICODE` | `PROHIBITED_CONTROL_CHARACTER` | Security risk; prohibited in educational text |
| Bidirectional overrides / isolates (`U+202A–U+202E`, `U+2066–U+2069`) | `REJECTED_INVALID_UNICODE` | `PROHIBITED_BIDI_CONTROL` | Spoofing and formatting injection risk |
| Unpaired surrogates (`U+D800–U+DFFF`) | `REJECTED_INVALID_UNICODE` | `UNPAIRED_SURROGATE` | Malformed UTF sequence |
| Replacement character `U+FFFD` in raw input | `REJECTED_INVALID_UNICODE` | `PREEXISTING_REPLACEMENT_CHARACTER` | Source fidelity compromised prior to pipeline ingestion |
| Unattached combining mark (combining mark without preceding base) | `MANUAL_REVIEW_REQUIRED` | `COMBINING_SEQUENCE_REVIEW` | Malformed orthography; preserved and flagged |
| Excessive repeated combining marks ($> 3$) | `MANUAL_REVIEW_REQUIRED` | `COMBINING_SEQUENCE_REVIEW` | Potential Zalgo / malformed input |
| Unexpected ZWJ/ZWNJ context | `MANUAL_REVIEW_REQUIRED` | `UNEXPECTED_JOINER_CONTEXT` | Requires expert linguistic review |
| Unsupported foreign script present (non-Latin, non-Sinhala) | `MANUAL_REVIEW_REQUIRED` | `UNSUPPORTED_SCRIPT_PRESENT` | Preserved and routed to review |
| Empty or whitespace-only input | `MANUAL_REVIEW_REQUIRED` | `EMPTY_AFTER_DERIVED_WHITESPACE` | Fails minimum content requirement |
| No trusted Sinhala metadata AND zero Sinhala content | `EXCLUDED_NON_SINHALA` | `NO_SINHALA_CONTENT` | Non-Sinhala corpus input |
| Allowlisted Sinhala sequence with NFC changes | `PASSED_WITH_NORMALIZATION` | `NORMALIZATION_APPLIED` | Canonical form derived |
| Allowlisted Sinhala sequence already in NFC | `PASSED` | `CANONICAL_NFC` | Clean canonical text |

### Zero-Tolerance Pipeline Invariant
\[
\text{REPLACEMENT\_CHARACTER\_INTRODUCED\_BY\_PIPELINE} = 0
\]
Any replacement character introduced by normalization, tokenization, or segmentation is treated as a fatal pipeline defect.

---

## 6. Whitespace and Punctuation Policy

### 6.1 Governed Line Ending Sequences

| Raw Sequence | Normalized Sequence | Rule Explanation |
|---|---|---|
| CRLF (`U+000D U+000A`) | Single LF (`U+000A`) | Composite two-character Windows line ending collapses to a single canonical LF; never produces duplicate line feeds |
| Lone CR (`U+000D`) | Single LF (`U+000A`) | Legacy Mac/isolated carriage return normalizes to single canonical LF |
| Lone LF (`U+000A`) | Preserved as single LF (`U+000A`) | Unix line feed is canonical; preserved as single LF |
| Paragraph Breaks (`\n\n`, `\r\n\r\n`) | Dual LF (`\n\n`) | Preserved where multiline prose text role requires paragraph boundaries |

### 6.2 Horizontal Whitespace and Trimming

1. **Horizontal Whitespace Collapsing:** Consecutive horizontal whitespace characters (spaces, tabs, NBSP `U+00A0`) are collapsed to a single ASCII space (`U+0020`).
2. **Trimming:** Derived text is trimmed of leading and trailing whitespace.
3. **Paragraph Preservation:** Dual line breaks (`\n\n`) representing paragraph boundaries are preserved when the text role requires multiline prose.


---

## 7. Half-Open Offset Intervals and Operation Schema

Offsets are zero-based, code-point half-open intervals:
\[
[\text{start\_code\_point}, \text{end\_code\_point})
\]

Operation schema:
```json
{
  "operation_id": "OP-0001",
  "operation_type": "UNICODE_NFC",
  "raw_spans": [{"start_code_point": 0, "end_code_point": 2}],
  "normalized_spans": [{"start_code_point": 0, "end_code_point": 1}],
  "before_sha256": "...",
  "after_sha256": "...",
  "changed": true,
  "mapping_status": "many_to_one",
  "mapping_exact": true,
  "rule_version": "1.0.0"
}
```

Allowed mapping statuses: `one_to_one`, `many_to_one`, `one_to_many`, `reordered`, `non_local`, `unmapped`.
If an exact local mapping cannot be resolved, `mapping_status: "non_local"` with `mapping_exact: false` is used. Misleading offsets are prohibited.

---

## 8. Frozen Disposition Precedence

When multiple conditions match, evaluation proceeds strictly from left to right; the first matching terminal condition wins:

$$\text{REJECTED\_INVALID\_UNICODE} \longrightarrow \text{MANUAL\_REVIEW\_REQUIRED} \longrightarrow \text{EXCLUDED\_NON\_SINHALA} \longrightarrow \text{PASSED\_WITH\_NORMALIZATION} \longrightarrow \text{PASSED}$$
