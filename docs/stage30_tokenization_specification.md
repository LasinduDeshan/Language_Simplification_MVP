# Stage 30 Tokenization Specification — Sinhala

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Sinhala (`si`, `si-LK`, script `Sinh`), children aged 4–8  
**Specification Version:** 1.0.0  
**Status:** Frozen & Governed  

---

## 1. Overview and Scope

Tokenization in Stage 30 is deterministic, non-semantic, and strictly grapheme-safe. It divides normalized Sinhala sentences into discrete lexical, numeric, and orthographic tokens suitable for structural analysis, vocabulary matching, and simplification pipeline ingestion.

---

## 2. Token Categories

Every token is assigned exactly one primary `TokenType`:

| Category | Description | Examples |
|---|---|---|
| `SINHALA_WORD` | Token consisting predominantly of Sinhala script letters and joiners | `අම්මා`, `ශ්‍රී`, `පාසල` |
| `LATIN_WORD` | Token consisting of Latin script letters | `Grade`, `English`, `school` |
| `MIXED_SCRIPT_TOKEN` | Token combining Sinhala and Latin scripts within a single unit | `COVID-19`, `1වන` |
| `ARABIC_NUMBER` | Standard Arabic numerals 0–9, including decimal notation | `1`, `25`, `3.14` |
| `SINHALA_NUMBER` | Sinhala Lith digits or Archaic numbers | `෧`, `෨`, `෩` |
| `PUNCTUATION` | Standard sentence and phrase punctuation delimiters | `.`, `,`, `?`, `!`, `෴` |
| `SYMBOL` | Mathematical, currency, and typographic symbols | `+`, `=`, `%`, `$` |
| `UNKNOWN` | Characters not categorized in the above classes | Unmapped code points |

---

## 3. Grapheme Integrity Invariant

> **Critical Invariant:** A token boundary must **never** split an extended grapheme cluster.

- Combining vowel signs (`ා`, `ි`, `ී`, `ු`, `ූ`, etc.), viramas (`්`), and ZWJ conjunct sequences remain permanently bonded to their base consonant.
- Token segmentation operates on whole extended grapheme clusters produced by the pinned `regex` `\X` engine.
- Byte-level or code-point-level slicing that would orphan a combining mark is strictly forbidden.

---

## 4. Token Record Contract

Each token produces an immutable `TokenRecord`:

```json
{
  "token_index": 0,
  "surface": "<surface text>",
  "normalized": "<normalized text>",
  "token_type": "SINHALA_WORD",
  "start_code_point": 0,
  "end_code_point": 5,
  "grapheme_count": 3,
  "script_profile": {
    "Sinh": 1.0,
    "Latn": 0.0,
    "Digit": 0.0
  }
}
```

### Invariant Offset Guarantees
1. Offsets are zero-based, half-open intervals: `[start_code_point, end_code_point)`.
2. Offsets strictly refer to the derived `normalized_text`.
3. Token offsets are non-overlapping and monotonically increasing.

---

## 5. Normalized-Text Reconstruction Contract

Exact normalized-text reconstruction is verified using ordered token spans and preserved inter-token gaps; token-text concatenation alone is not claimed unless separators are represented explicitly.

$$
\text{NormalizedText} = \sum_{i=0}^{n} \left( \text{Gap}_i + \text{Token}_i \right) + \text{Gap}_{n+1}
$$

where:
- $\text{Token}_i$ is the exact slice $\text{normalized\_text}[\text{start}_i:\text{end}_i]$.
- $\text{Gap}_i$ is the untouched intervening substring $\text{normalized\_text}[\text{end}_{i-1}:\text{start}_i]$ (covering spaces, tabs, and unparsed separators).
- Reconstruction equivalence is verified in unit and property test suites (`test_tokenization.py`).
