# Stage 36 — Fixture Evaluation Report

**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Modules:** `backend/app/sinhala_output_validation/evaluation_fixtures.py`, `backend/tests/sinhala_output_validation/test_stage36_evaluation.py`  
**Configuration Freeze:** `7175125fbb32459a8f41100007c13c37994a1063ffb04b745414bd58a22aaaf6`  

---

## 1. Governed Final Fixtures Evaluation Results

All 16 declared fixtures were evaluated under the prospective frozen configuration bundle. Every fixture attained its exact pre-declared terminal outcome:

| Fixture ID | Category | Primary Outcome | Selected Output / Abstention | Fallback Depth | Reconciled Terminal State |
|---|---|---|---|---|---|
| `EVAL_01_VALID_PRIMARY` | Valid Simplification | `ACCEPTED` | Primary Candidate | 0 | `PRIMARY_CANDIDATE_SELECTED` |
| `EVAL_02_VALID_UNCHANGED` | Unchanged Valid | `VALID_UNCHANGED` | Primary Candidate | 0 | `UNCHANGED_SOURCE_SELECTED_FOR_RESEARCH_ONLY` |
| `EVAL_03_NUMERIC_VIOLATION_FALLBACK_C0` | Numeric Violation | `REJECTED_PROTECTED_SPAN` | C0 Rule Baseline | 1 | `RULE_FALLBACK_SELECTED` |
| `EVAL_04_DECLARED_SPAN_FALLBACK_C0` | Declared Span Omission | `REJECTED_PROTECTED_SPAN` | C0 Rule Baseline | 1 | `RULE_FALLBACK_SELECTED` |
| `EVAL_05_POLARITY_INVERSION_FALLBACK_C0` | Polarity Inversion | `REJECTED_NUMERICAL_OR_POLARITY` | C0 Rule Baseline | 1 | `RULE_FALLBACK_SELECTED` |
| `EVAL_06_HALLUCINATION_FALLBACK_C0` | High Novel Token Ratio | `REJECTED_UNSUPPORTED_INSERTION` | C0 Rule Baseline | 1 | `RULE_FALLBACK_SELECTED` |
| `EVAL_07_INFERRED_SPAN_MANUAL_REVIEW` | Inferred Entity Altered | `MANUAL_REVIEW_REQUIRED` | Safe Abstention (Review) | 1 | `MANUAL_REVIEW_NO_OUTPUT` |
| `EVAL_08_UNBALANCED_BRACKETS_MANUAL_REVIEW` | Delimiter Imbalance | `MANUAL_REVIEW_REQUIRED` | Safe Abstention (Review) | 1 | `MANUAL_REVIEW_NO_OUTPUT` |
| `EVAL_09_CORRUPT_UNICODE_TERMINAL_REJECT` | Source Mojibake | `REJECTED_INVALID_UNICODE` | Safe Abstention (Terminal) | 3 | `REJECTED_NO_OUTPUT` |
| `EVAL_10_DOUBLE_VIRAMA_FALLBACK_C0` | Orthographic Virama Error | `REJECTED_INVALID_UNICODE` | C0 Rule Baseline | 1 | `RULE_FALLBACK_SELECTED` |
| `EVAL_11_TRUNCATION_FALLBACK_C0` | Length Truncation (<0.20) | `REJECTED_CRITICAL_SEMANTIC` | C0 Rule Baseline | 1 | `RULE_FALLBACK_SELECTED` |
| `EVAL_12_C0_ALSO_FAILS_FALLBACK_UNCHANGED` | C0 Numeric Mutation | `REJECTED_PROTECTED_SPAN` | Unchanged Source | 2 | `UNCHANGED_SOURCE_SELECTED_FOR_RESEARCH_ONLY` |
| `EVAL_13_COMPLEX_HISTORICAL_PRIMARY` | Complex Historical | `ACCEPTED` | Primary Candidate | 0 | `PRIMARY_CANDIDATE_SELECTED` |
| `EVAL_14_SCIENCE_TEXT_NUMBERS_PRESERVED` | Science / Numbers | `ACCEPTED` | Primary Candidate | 0 | `PRIMARY_CANDIDATE_SELECTED` |
| `EVAL_15_PROVENANCE_FAIL_FALLBACK_C0` | Hash Mismatch | `REJECTED_CONFIGURATION` | C0 Rule Baseline | 1 | `RULE_FALLBACK_SELECTED` |
| `EVAL_16_TOTAL_SOURCE_CORRUPTION_ABSTAIN` | Control Characters | `REJECTED_INVALID_UNICODE` | Safe Abstention (Terminal) | 3 | `REJECTED_NO_OUTPUT` |

---

## 2. Fixture Segregation and Zero Overlap Verification

- **Development Calibration Fixtures ($N=14$):** Defined in `calibration_fixtures.py` (`DEV_FIX_01` through `DEV_FIX_14`).
- **Governed Final Evaluation Fixtures ($N=16$):** Defined in `evaluation_fixtures.py` (`EVAL_01` through `EVAL_16`).
- **Overlap Audit:** Zero overlap in IDs, text hashes, or provenance references between calibration and evaluation sets.
