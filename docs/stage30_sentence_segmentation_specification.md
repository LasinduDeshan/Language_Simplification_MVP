# Stage 30 Sentence Segmentation Specification — Sinhala

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Sinhala (`si`, `si-LK`, script `Sinh`), children aged 4–8  
**Specification Version:** 1.0.0  
**Status:** Frozen & Governed  

---

## 1. Overview and Scope

Sentence segmentation in Stage 30 is deterministic, non-semantic, and configuration-driven. It segments normalized Sinhala text into discrete, auditable sentences while protecting against false splits caused by abbreviations, decimals, and repeated punctuation runs.

---

## 2. Sentence Boundary Triggers

The segmenter identifies sentence boundaries upon encountering any of the following terminal delimiters:

| Delimiter | Code Point | Rule ID | Description |
|---|---|---|---|
| Full Stop `.` | `U+002E` | `FULL_STOP` | Western period commonly used in Sinhala |
| Question Mark `?` | `U+003F` | `QUESTION_MARK` | Interrogative boundary |
| Exclamation Mark `!` | `U+0021` | `EXCLAMATION_MARK` | Exclamatory boundary |
| Kunddaliya `෴` | `U+0DF4` | `KUNDDALIYA` | Traditional Sinhala punctuation mark |
| Dual Newline `\n\n` | `U+000A U+000A` | `PARAGRAPH_BREAK` | Explicit paragraph transition |
| End of Input | N/A | `END_OF_TEXT` | Final unpunctuated segment (if non-empty) |

---

## 3. False Boundary Protection Rules

A trigger character does **not** cause a sentence split under any of the following protected conditions:

### 3.1 Decimal Numbers
- Pattern: `\d\.\d`
- A period flanked on both sides by numeric digits (e.g., `12.5`, `3.1415`) is protected as part of a numeric token.

### 3.2 Governed Abbreviations
When a period is preceded by an allowlisted abbreviation, it is treated as an orthographic abbreviation marker, not a terminal sentence boundary:
- Sinhala educational titles: `වෛ.` (Doctor), `මහා.` (Professor), `ඩො.` (Doctor), `පිටු.` (Pages), `රු.` (Rupees).
- Time indicators: `පෙ.ව.` (a.m.), `ප.ව.` (p.m.).
- Latin educational abbreviations: `e.g.`, `i.e.`, `etc.`, `Dr.`, `Mr.`, `Mrs.`, `Prof.`, `No.`.

### 3.3 Repeated Punctuation Runs
- Sequences of multiple terminal punctuation marks (e.g., `...`, `??`, `?!`, `!!!`) are kept intact. The split occurs after the final character of the run.

---

## 4. Sentence Record Contract

Every segmented sentence produces an immutable `SentenceRecord`:

```json
{
  "sentence_index": 0,
  "text": "<trimmed sentence string>",
  "start_code_point": 0,
  "end_code_point": 24,
  "boundary_rule": "FULL_STOP",
  "sha256": "<64-character SHA-256>"
}
```

### Invariant Offset Guarantees
1. Offsets are zero-based, half-open intervals: `[start_code_point, end_code_point)`.
2. Offsets strictly refer to the derived `normalized_text`.
3. Offsets are strictly monotonic: `sentence[i].start_code_point <= sentence[i].end_code_point <= sentence[i+1].start_code_point`.

---

## 5. Quality Routing & Ambiguity

- If text contains no recognized terminal punctuation and exceeds 200 code points without a boundary, `SENTENCE_BOUNDARY_UNCERTAIN` is flagged.
- Flagged records proceed through tokenization but are routed to `MANUAL_REVIEW_REQUIRED` before downstream simplification.
