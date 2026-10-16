# Stage 33 — Meaning Preservation Policy Specification

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Meaning-critical element detection, preservation guards, and failure handling  
**Governance Checkpoint:** Stage 33 Technical Draft  

---

## 1. Protected Meaning Categories

Automated simplification must not alter, drop, or reposition meaning-critical elements without explicit allowlist authorization. The detector identifies 12 categories:

1. **`NAMED_ENTITY`:** Proper names, person names, geographical locations, organizations.
2. **`NUMBER_NUMERIC`:** Digits, decimal numbers, percentages, fractions, and spelled-out numerals.
3. **`DATE_TIME`:** Years, calendar months, days, dates, timestamps.
4. **`UNIT_MEASUREMENT`:** Metric and standard physical units (`කිලෝග්‍රෑම්`, `මීටර්`, `ලීටර්`).
5. **`CURRENCY`:** Financial currencies (`රුපියල්`, `ඩොලර්`, `$`, `Rs.`).
6. **`NEGATION_MARKER`:** Negation particles (`නැත`, `නො`, `නෙවෙයි`, `නොවේ`, `නැතැයි`, `නැහැ`).
7. **`MODALITY_CONDITION`:** Modal and conditional operators (`හැකිය`, `යුතුය`, `නම්`, `බැවින්`, `හෙයින්`).
8. **`QUOTATION_DIRECT_SPEECH`:** Quoted speech within `“...”`, `"..."`, or ‘...’.
9. **`IDENTIFIER_CODE_URL`:** Web links, email addresses, filenames, system codes.
10. **`PARENTHETICAL_REFERENCE`:** Content enclosed in round brackets `(...)`.
11. **`MIXED_SCRIPT_TERM`:** Latin script tokens embedded in Sinhala text.
12. **`STAGE32_REVIEW_REQUIRED_VOCABULARY`:** Sensitive, clinical, or complex vocabulary identified in Stage 32.

---

## 2. Incompleteness Acknowledgment

> [!WARNING]
> Automated Sinhala named-entity and semantic scope detection is conservative and rule-assisted. The absence of a detector flag does not prove that a token is not a proper noun or meaning-critical element.

---

## 3. Mandatory Preservation Guards

Before any rewrite candidate can be considered for ranking, it must satisfy all mandatory guards in Stage 1 eligibility filtering:

- **Entity Preservation Guard:** All protected text identified in the source must be present verbatim in the candidate.
- **Number Preservation Guard:** Extracted numbers in candidate must match source numbers exactly.
- **Negation Preservation Guard:** Negation markers must match source negation markers exactly.
- **Modality Preservation Guard:** Modality and conditional markers must match source markers exactly.
- **Quotation Preservation Guard:** Direct quotations must be preserved verbatim.
- **Unicode Replacement Guard:** Introduced `U+FFFD` characters equal strictly 0.

Failure of any required guard terminates the candidate as `BLOCKED_MEANING_GUARD` or `BLOCKED_PROTECTED_SPAN` and eliminates it from ranking.
