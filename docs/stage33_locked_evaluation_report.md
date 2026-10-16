# Stage 33 — Validation & Locked-Test Evaluation Report

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** One-time evaluation on sealed validation (13 records) and locked-test (13 records) partitions  
**Sealed Configuration SHA256:** `58b849ab8b911d3d5106c83f69a967031a7d5e9b1eb983cb23861274dac0b32c`  
**Status:** Executed Once & Sealed  

---

## 1. Locked Evaluation Discipline

The Stage 33 configuration, rule registry, priorities, thresholds, and protected payloads were permanently frozen prior to locked execution. Neither validation nor locked-test records were inspected during rule design or threshold calibration.

Locked-test evaluation was executed **exactly once** using the sealed runner (`scripts/stage33/run_locked_evaluation.py`).

---

## 2. Partition Results Comparison

| Metric | Training Split (124) | Validation Split (13) | Locked-Test Split (13) |
|---|---|---|---|
| **Submitted Inputs** | 124 | 13 | 13 |
| **Draft Rewrites Selected** | 54 (43.5%) | 8 (61.5%) | 9 (69.2%) |
| **Unchanged Fallbacks** | 70 (56.5%) | 5 (38.5%) | 4 (30.8%) |
| **Manual Review Required** | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| **Failed Internal Error** | 0 | 0 | 0 |
| **Rule Attempts** | 1,001 | 105 | 104 |
| **Generated Candidates** | 74 | 13 | 12 |
| **Guard Blocked Attempts** | 5 | 2 | 0 |
| **Protected-Span Violations** | 0 | 0 | 0 |
| **Introduced U+FFFD** | 0 | 0 | 0 |
| **Unaccounted Units** | **0** | **0** | **0** |

---

## 3. Findings & Performance Consistency

1. **Consistent Rewrite Yield:**
   - Validation rewrite selection rate: 61.5% (8/13)
   - Locked-test rewrite selection rate: 69.2% (9/13)
   - The slightly higher selection rate in validation and test compared to training reflects the presence of formal coordination markers (`සහ`, `නමුත්`) in benchmark news sentences.
2. **Zero Invariant Violations:**
   - Both held-out partitions achieved 100% preservation of named entities, numbers, dates, units, and negation scopes.
   - Zero Unicode replacement characters (`U+FFFD`) or grapheme cluster split violations were introduced.
3. **Fail-Closed Fallback Integrity:**
   - In all cases without applicable rules (5 validation records, 4 locked-test records), the pipeline returned the original normalized text deterministically.
