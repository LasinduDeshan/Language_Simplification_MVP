# Stage 36 — Protected Span Integrity and Factual Fidelity Policy

**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Modules:** `backend/app/sinhala_output_validation/validators/v3_protected_spans.py`, `backend/app/sinhala_output_validation/validators/v4_v5_semantic_fidelity.py`  

---

## 1. Three-Tier Protected-Span Hierarchy (Validator V3)

Stage 36 divides all protected content elements into a deterministic three-tier hierarchy to balance child safety with linguistic flexibility:

| Tier | Category | Scope / Detection | Gate Level | Severity on Violation |
|---|---|---|---|---|
| **Tier 1** | `DECLARED_PROTECTED_SPAN` | Source metadata annotations, frozen proper names, key domain terms | Hard Gate | `CRITICAL` (`REJ_PROTECTED_SPAN_VIOLATION`) |
| **Tier 2** | `DETERMINISTIC_PROTECTED_SPAN` | Numbers, percentages, dates, years, currencies, units, URLs | Hard Gate | `CRITICAL` (`REJ_PROTECTED_SPAN_VIOLATION`) |
| **Tier 3** | `INFERRED_PROTECTED_SPAN` | Heuristically detected named entities (districts, historical figures) | Review Gate | `REVIEW` (`REV_INFERRED_SPAN_ALTERED`) |

### Sinhala Suffix Attachment Robustness
Sinhala numerals frequently attach inflectional suffixes (e.g., `250ක්`, `100කට`, `50න්`, `2000දී`). Numeric regex extraction `r"\d+(?:[\.,]\d+)?%?"` isolates the underlying numerical quantity regardless of suffix attachment.

---

## 2. Polarity and Numerical Drift Gate (Validator V4)

- **Negation & Polarity Inversion:**
  - Evaluates explicit Sinhala negation markers (`නැත`, `නැහැ`, `නැති`, `නොවේ`, `නොමැත`, `එපා`, `නොහැක`, `බැහැ`, `නොවෙයි`, `නොවන`, `නෑ`, `නැතුව`) and prefix `නො-`.
  - Detecting any flip between negative and positive propositions triggers hard rejection.
  - **Severity:** `CRITICAL`
  - **Reason Code:** `REJ_NUMERICAL_OR_POLARITY_DRIFT`
- **Unauthorized Quantity Injection:**
  - Novel numbers appearing in candidate text that were absent in source text are rejected.
  - **Severity:** `CRITICAL`
  - **Reason Code:** `REJ_NUMERICAL_OR_POLARITY_DRIFT`
