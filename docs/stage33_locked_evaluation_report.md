# Stage 33 — Validation & Locked-Test Evaluation Report

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** One-time evaluation on sealed validation (13 records) and locked-test (13 records) partitions  
**Sealed Configuration SHA256:** `2d572d820f630fb6c15f5ebacebfce3ae84ab2e9c5f7102241f0d15579c71cc2`  
**Status:** Executed Once & Sealed with Full Cryptographic Evidence  

---

## 1. Locked Evaluation Discipline & Execution Evidence

The Stage 33 configuration, rule registry, priorities, thresholds, and protected payloads were permanently frozen prior to locked execution. Neither validation nor locked-test records were inspected during rule design or threshold calibration.

Locked-test evaluation was executed **exactly once** using the sealed runner (`scripts/stage33/run_locked_evaluation.py`).

### Authoritative Locked-Test Execution Record

```text
Locked-test execution ID:               SI-LOCKED-EVAL-20261016-01
Execution started:                      2026-10-16T10:17:05.187313+00:00
Execution completed:                    2026-10-16T10:17:05.655829+00:00
Locked-test input-manifest SHA-256:     96a44d0c6aaf86382482e25bd41c4df653326a41e7098d991efd2e4c4c5de7de
Final Stage 33 configuration SHA-256:   2d572d820f630fb6c15f5ebacebfce3ae84ab2e9c5f7102241f0d15579c71cc2
Configuration loaded by execution:      2d572d820f630fb6c15f5ebacebfce3ae84ab2e9c5f7102241f0d15579c71cc2
In-memory byte hash verification:       PASSED (In-memory bytes identical bit-for-bit to disk file)
Locked-test output-ledger SHA-256:      6c04256bc43731b971e02ef2ef6041babd43898e02c7bca376fcf38927d1866c
Records expected:                       13
Records processed:                      13
Execution count:                        1
Execution status:                       LOCKED_TEST_COMPLETE
Post-execution configuration changes:   0
```

---

## 2. Partition Results Comparison Across Full Analytical Population

| Metric | Training Split (124) | Validation Split (13) | Locked-Test Split (13) | Total Canonical View (150) |
|---|---|---|---|---|
| **Submitted Inputs** | 124 | 13 | 13 | **150** |
| **Draft Rewrites Selected** | 54 (43.5%) | 8 (61.5%) | 9 (69.2%) | **71 (47.3%)** |
| **Unchanged No Applicable Rule** | 68 (54.8%) | 4 (30.8%) | 4 (30.8%) | **76 (50.7%)** |
| **Unchanged Blocked by Guard** | 2 (1.6%) | 1 (7.7%) | 0 (0.0%) | **3 (2.0%)** |
| **Manual Review Required** | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | **0 (0.0%)** |
| **Failed Internal Error** | 0 | 0 | 0 | **0** |
| **Rule Attempts** | 1,001 | 105 | 104 | **1,210** |
| **Generated Candidates** | 79 | 15 | 12 | **106** |
| **Guard Blocked Candidates** | 5 | 2 | 0 | **7** |
| **Protected-Span Violations** | 0 | 0 | 0 | **0** |
| **Introduced U+FFFD** | 0 | 0 | 0 | **0** |
| **Unaccounted Units (All 6 Levels)** | **0** | **0** | **0** | **0** |

---

## 3. Findings & Performance Consistency

1. **Consistent Rewrite Yield:**
   - Validation rewrite selection rate: 61.5% (8/13)
   - Locked-test rewrite selection rate: 69.2% (9/13)
   - Consolidated rewrite selection rate: 47.3% (71/150)
   - The selection rate in validation and test reflects the presence of formal coordination markers (`සහ`, `නමුත්`) in benchmark news sentences.
2. **Zero Invariant Violations:**
   - Both held-out partitions achieved 100% preservation across all 12 protected-span categories.
   - Zero Unicode replacement characters (`U+FFFD`) or grapheme cluster split violations were introduced.
3. **Fail-Closed Fallback Integrity:**
   - In all cases without applicable rules (4 validation records, 4 locked-test records), the pipeline returned the original normalized text deterministically with `UNCHANGED_NO_APPLICABLE_RULE`.
   - In the single validation record where all candidates were blocked by meaning guards, the pipeline returned `UNCHANGED_ALL_CANDIDATES_BLOCKED` with zero leakage.
