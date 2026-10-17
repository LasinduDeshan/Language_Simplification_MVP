# Stage 36 — Error Analysis and Failure Mode Classification

**Component:** Component 3 — AI/NLP-Based Language Simplification  

---

## 1. Classification of Blocked Candidates

During the Stage 36 evaluation, 13 non-standard candidates were processed through the pipeline, triggering gate failures, review routing, or fallback ladders.

### 1.1 Category Breakdown

| Failure Mode | Triggering Validator | Severity | Primary Assigned Disposition | Resolution Trajectory |
|---|---|---|---|---|
| **Invalid Provenance Hash** | V0 | CRITICAL | `REJECTED_CONFIGURATION_OR_PROVENANCE` | Fallback to C0 Baseline |
| **Corrupt Unicode (Mojibake)** | V1 | CRITICAL | `REJECTED_INVALID_UNICODE` | Fallback to C0 / Abstention |
| **Control Characters** | V1 | CRITICAL | `REJECTED_INVALID_UNICODE` | Terminal Safe Abstention |
| **Consecutive Virama** | V7 | CRITICAL | `REJECTED_INVALID_UNICODE` | Fallback to C0 Baseline |
| **Declared Proper Name Dropped** | V3 | CRITICAL | `REJECTED_PROTECTED_SPAN_VIOLATION` | Fallback to C0 Baseline |
| **Deterministic Number Omitted** | V3 | CRITICAL | `REJECTED_PROTECTED_SPAN_VIOLATION` | Fallback to C0 Baseline |
| **Numeric Mutation in C0** | V3 | CRITICAL | `REJECTED_PROTECTED_SPAN_VIOLATION` | Fallback to Unchanged Source |
| **Polarity Inversion (Negation Flip)**| V4 | CRITICAL | `REJECTED_NUMERICAL_OR_POLARITY_DRIFT` | Fallback to C0 Baseline |
| **Novel Unsupported Tokens (>0.65)** | V5 | CRITICAL | `REJECTED_UNSUPPORTED_INSERTION` | Fallback to C0 Baseline |
| **Severe Truncation (<0.20 Length)** | V2 | CRITICAL | `REJECTED_CRITICAL_SEMANTIC_RISK` | Fallback to C0 Baseline |
| **Inferred Entity Mutated** | V3 | REVIEW | `MANUAL_REVIEW_REQUIRED` | Routed to Review Queue |
| **Unbalanced Delimiters** | V7 | REVIEW | `MANUAL_REVIEW_REQUIRED` | Routed to Review Queue |

---

## 2. Key Insights and Edge Case Resolutions

1. **Sinhala Number Suffixes:** Suffixes attached to digits (e.g. `100ක්`, `500ට`) required regex pattern boundary adjustments (`r"\d+(?:[\.,]\d+)?%?"`) to avoid word boundary boundary-masking artifacts in Python `re`.
2. **Colloquial Negation Markers:** Colloquial negative forms (`නෑ`, `නැතුව`) were incorporated into $V_4$'s negation lexicon to ensure colloquial simplifications do not trigger false-positive polarity inversion alarms.
3. **Fail-Closed Security:** In zero cases did an invalid candidate escape to an accepted state.
