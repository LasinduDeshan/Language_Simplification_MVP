# Stage 30 Quality and Review Policy — Sinhala Preprocessing

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Sinhala (`si`, `si-LK`, script `Sinh`), children aged 4–8  
**Policy Version:** 1.0.0  
**Status:** Frozen & Governed  

---

## 1. Overview and Scope

The Quality and Review Policy governs the automated classification, review routing, and terminal disposition assignment of all Sinhala text entering Component 3. It guarantees that any technical ambiguity, encoding flaw, or non-conforming orthography is routed to manual review rather than silently altered or passed downstream.

---

## 2. Frozen Terminal Disposition Precedence

When multiple conditions or flags apply to an input record, the final disposition is resolved strictly from left to right; the **first matching condition wins**:

$$\text{REJECTED\_INVALID\_UNICODE} \longrightarrow \text{MANUAL\_REVIEW\_REQUIRED} \longrightarrow \text{EXCLUDED\_NON\_SINHALA} \longrightarrow \text{PASSED\_WITH\_NORMALIZATION} \longrightarrow \text{PASSED}$$

| Precedence | Terminal Disposition | Mandatory Condition |
|---|---|---|
| **1 (Highest)** | `REJECTED_INVALID_UNICODE` | Prohibited control character (null byte, C0/C1, bidi overrides) or pre-existing `U+FFFD` replacement character in raw text. |
| **2** | `MANUAL_REVIEW_REQUIRED` | Suspicious orthographic sequences, unattached combining marks, unexpected joiner contexts, unsupported foreign scripts, or empty text. |
| **3** | `EXCLUDED_NON_SINHALA` | Input lacking trusted Sinhala provenance AND showing zero Sinhala script content. |
| **4** | `PASSED_WITH_NORMALIZATION` | Valid Sinhala text requiring Unicode NFC composition or whitespace adjustments to attain canonical form. |
| **5 (Default)** | `PASSED` | Valid, clean Sinhala text already in canonical NFC representation requiring zero transformations. |

Every processed record receives **exactly one** terminal disposition.

---

## 3. Quality Flags Inventory

| Quality Flag | Trigger Condition | Disposition Impact |
|---|---|---|
| `PROHIBITED_CONTROL_PRESENT` | Null bytes, C0/C1 controls, bidi overrides | Forces `REJECTED_INVALID_UNICODE` |
| `REPLACEMENT_CHARACTER_PRESENT` | Raw text contains `U+FFFD` | Forces `REJECTED_INVALID_UNICODE` |
| `COMBINING_SEQUENCE_REVIEW` | Combining mark without base character or $> 3$ consecutive marks | Forces `MANUAL_REVIEW_REQUIRED` |
| `UNEXPECTED_JOINER_CONTEXT` | ZWJ/ZWNJ outside allowlisted Yansaya/Rakaransaya/Conjunct/Repaya contexts | Forces `MANUAL_REVIEW_REQUIRED` |
| `UNSUPPORTED_SCRIPT_PRESENT` | Non-allowlisted foreign scripts (Tamil, Cyrillic, Arabic, etc.) present | Forces `MANUAL_REVIEW_REQUIRED` |
| `EMPTY_AFTER_DERIVED_WHITESPACE` | Input text is empty or collapses to empty string after whitespace trimming | Forces `MANUAL_REVIEW_REQUIRED` |
| `NORMALIZATION_CHANGED` | NFC or whitespace transformations modified the text | Promotes clean text to `PASSED_WITH_NORMALIZATION` |
| `MIXED_SCRIPT_PRESENT` | English/Latin words present alongside Sinhala | Supported; processing continues |
| `JOINER_PRESENT` | Allowlisted ZWJ/ZWNJ present | Supported; processing continues |
| `TOKENIZATION_UNCERTAIN` | Tokenizer encounters unmapped orthographic sequence | Flags record; routes to review |
| `SENTENCE_BOUNDARY_UNCERTAIN` | Text exceeds 200 code points without terminal punctuation | Flags record; routes to review |

---

## 4. Reason Codes

Every terminal disposition is paired with an explicit reason code:
- `PROHIBITED_CONTROL_CHARACTER`: Source text contains forbidden control characters.
- `PREEXISTING_REPLACEMENT_CHARACTER`: Source text contains pre-existing `U+FFFD`.
- `COMBINING_SEQUENCE_REVIEW`: Combining mark sequence requires linguistic inspection.
- `UNEXPECTED_JOINER_CONTEXT`: Joiner context is not in governed allowlist.
- `UNSUPPORTED_SCRIPT_PRESENT`: Unsupported foreign script detected.
- `EMPTY_AFTER_DERIVED_WHITESPACE`: Input contains no analyzable characters.
- `NO_SINHALA_CONTENT`: Provenance and script evidence indicate non-Sinhala text.
- `NORMALIZATION_APPLIED`: Canonical NFC or whitespace changes recorded.
- `CANONICAL_NFC`: Input text matches canonical form with zero changes.

---

## 5. Non-Clinical and Governance Invariants

1. All records retain the immutable metadata:
   ```json
   {
     "validation_status": "draft",
     "research_eligible": false,
     "approved_for_child_delivery": false,
     "requires_expert_review": true
   }
   ```
2. **Privacy Logging:** Logs record only hashes, counts, rule codes, and dispositions. Raw learner text is never logged.
3. **Non-Clinical Guarantee:** Features extracted during preprocessing are structural counts; they do not represent reading levels, developmental milestones, or DLD diagnostic assessments.
