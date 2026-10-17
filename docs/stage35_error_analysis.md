# Stage 35 Error Analysis and Diagnostic Breakdown

**Stage:** Stage 35 — Comparative Evaluation of Gemini, mT5, and mBART for Sinhala Simplification  
**Ledger Reference:** `data/model_comparison/stage35/evaluations/stage35_locked_evaluation_results.json`  

---

## 1. Diagnostic Outcome Categorization

Across the 47 executed attempts, responses were evaluated against Stage 35's critical safety gates:

| Diagnostic Outcome Category | Count | Associated Condition(s) | Methodological Nature |
|---|---|---|---|
| **Valid Unchanged Output** | 39 | C0 (13), C2 (13), C3 (13) | Pipeline fallback / identity rule baseline |
| **Rejected Protected-Span Change** | 8 | C1 (8) | Controlled synthetic test fixture |
| **Rejected Unicode / Script Violation** | 0 | None | Gate verified clean (zero U+FFFD) |
| **Rejected Truncation** | 0 | None | Gate verified clean |
| **Rejected Empty Output** | 0 | None | Gate verified clean |
| **Terminal Execution Failures** | 0 | None | Zero pipeline crashes or unhandled exceptions |
| **Total Evaluated** | **47** | — | $\text{Unaccounted} = 0$ |

---

## 2. In-Depth Error Evaluation

### 2.1 C1 Protected-Span Rejection
All 8 responses generated under C1 violated the protected span `ශ්‍රී ලංකාවේ`. The validator successfully detected the missing entity and classified each attempt as `REJECTED_PROTECTED_SPAN_CHANGE`. This validates the critical safety gate logic and proves the pipeline successfully halts non-conforming responses before downstream propagation.

### 2.2 Script and Unicode Cleanliness
No instances of corrupted byte sequences, invalid grapheme cluster boundaries, or Unicode replacement characters (`U+FFFD`) were detected across any of the 47 responses.
