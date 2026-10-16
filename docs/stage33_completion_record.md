# Stage 33 — Completion Record (Multi-Partition Reconciled)

```text
================================================================
STAGE 33 — SINHALA CONTROLLED SIMPLIFICATION RULE ENGINE
================================================================

Stage 33:                                   COMPLETE
Governance accounting:                      RECONCILED (Multi-Partition 150/150)
Locked-test execution:                      VERIFIED ONCE
Authoritative completion tag:               SEALED
Approved for child delivery:                FALSE

Prerequisite tag:                           stage-32-complete-v5
Prerequisite commit:                        7c6bb81a744305c3a59100a2c2af8fc06deb01c8
Start tag:                                  stage-33-start
Final commit:                               PENDING_FINAL_SEAL
Completion tag:                             stage-33-complete

Ancestry verification:                      PASSED (7 checkpoints)
Stage 30–32 immutability:                   PASSED (All declared manifest paths, 0 mismatches)
Corpus view evaluated:                      canonical_analytical_150
External protected root:                    PASSED (Verified outside worktree)
Rule registry:                              8 rules, PASSED
Protected rule payloads separated:          PASSED (Field-level rights isolation)
Protected-span policy:                      PASSED (12 categories explicitly enumerated)
Two-stage candidate resolution:             PASSED (Decoupled filtering & ranking)
Constrained subject recovery:               PASSED (Strict non-invention)
Trace classification coverage:              100% of trace elements classified
Selected rewrite unmapped traces:           0
Deterministic rerun equality:                PASSED (100% byte identical)
Training-only rule development:             PASSED
Configuration frozen before locked test:    PASSED (SHA256: 2d572d820f630fb6c15f5ebacebfce3ae84ab2e9c5f7102241f0d15579c71cc2)
Locked-test executions:                     1

----------------------------------------------------------------
1. Dynamic Partition Evidence (data/sinhala_external/corpus/corpus_metadata.json)
----------------------------------------------------------------
Stage 31 split manifest path:               data/sinhala_external/corpus/corpus_metadata.json
Stage 31 split manifest SHA-256:            39ee316a7b3df502f188712c89be5c4d87ca6e856835bde9ef4961c3d778909a
Canonical analytical corpus SHA-256:        f862bf30bedc92dcbff24076c289c7a757a3962c59096bc3a40c3d985d9a0f7d
Train record count:                         124
Validation record count:                    13
Locked-test record count:                   13
Total canonical records:                    150
Duplicate record IDs:                       0
Missing record IDs:                         0
Cross-split record overlaps:                0
Cross-split document-group overlaps:        0
Method-dev records in eval splits:          0
Partition verification script result:       PASSED

----------------------------------------------------------------
2. Locked-Test Execution Evidence (One-Time Governed Gate)
----------------------------------------------------------------
Locked-test execution ID:                   SI-LOCKED-EVAL-20261016-01
Execution started:                          2026-10-16T10:17:05.187313+00:00
Execution completed:                        2026-10-16T10:17:05.655829+00:00
Locked-test input-manifest SHA-256:         96a44d0c6aaf86382482e25bd41c4df653326a41e7098d991efd2e4c4c5de7de
Final Stage 33 configuration SHA-256:       2d572d820f630fb6c15f5ebacebfce3ae84ab2e9c5f7102241f0d15579c71cc2
Configuration loaded by execution:          2d572d820f630fb6c15f5ebacebfce3ae84ab2e9c5f7102241f0d15579c71cc2
In-memory byte hash verification:           PASSED (In-memory bytes identical bit-for-bit to disk file)
Locked-test output-ledger SHA-256:          6c04256bc43731b971e02ef2ef6041babd43898e02c7bca376fcf38927d1866c
Records expected:                           13
Records processed:                          13
Execution count:                            1
Execution status:                           LOCKED_TEST_COMPLETE
Post-execution configuration changes:       0

----------------------------------------------------------------
3. Multi-Partition Reconciled Accounting Table (All 6 Levels)
----------------------------------------------------------------
Partition       Inputs  Rule attempts   Candidates  Operations  Trace elements  Export fields
Train           124     1,001           79          79          79              496
Validation      13      105             15          15          15              52
Locked test     13      104             12          12          12              52
Total           150     1,210           106         106         106             600

----------------------------------------------------------------
4. Categorical Breakdown of Conservation Equations
----------------------------------------------------------------
Level 1: Final Input Dispositions (150 = 71 + 76 + 3 + 0 + 0 + 0 + 0)
- DRAFT_REWRITE_SELECTED:                   71 (Train: 54, Val: 8, Test: 9)
- UNCHANGED_NO_APPLICABLE_RULE:             76 (Train: 68, Val: 4, Test: 4)
- UNCHANGED_ALL_CANDIDATES_BLOCKED:         3  (Train: 2,  Val: 1, Test: 0)
- MANUAL_REVIEW_REQUIRED:                   0
- REJECTED_SOURCE_INELIGIBLE:               0
- REJECTED_INVALID_PREPROCESSING_STATE:     0
- FAILED_INTERNAL_ERROR:                    0
- Level 1 Unaccounted Inputs:               0

Level 2: Mutually Exclusive Rule Attempts (1,210 = 1,104 + 106 + 0 + 0)
- NOT_APPLICABLE:                           1,104 (Train: 922, Val: 90, Test: 92)
- CANDIDATE_GENERATED:                      106   (Train: 79,  Val: 15, Test: 12)
- DEFERRED_BEFORE_GENERATION:               0
- FAILED_INTERNAL:                          0
- Level 2 Unaccounted Attempts:             0

Level 3: Mutually Exclusive Candidates (106 = 71 + 28 + 0 + 7 + 0 + 0)
- SELECTED:                                 71 (Train: 54, Val: 8, Test: 9)
- NOT_SELECTED_LOWER_RANK:                  28 (Train: 20, Val: 5, Test: 3)
- BLOCKED_PROTECTED_SPAN:                   0
- BLOCKED_MEANING_GUARD:                    7  (Train: 5,  Val: 2, Test: 0)
- DEFERRED_MANUAL_REVIEW:                   0
- FAILED_INTERNAL:                          0
- Level 3 Unaccounted Candidates:           0

Level 4: Transformation Operations (106 = 50 + 56 + 0 + 0)
- REPLACE:                                  50 (Train: 33, Val: 8, Test: 9)
- SPLIT:                                    56 (Train: 46, Val: 7, Test: 3)
- INSERT:                                   0
- DELETE:                                   0
- Level 4 Unaccounted Operations:           0

Level 5: Mutually Exclusive Trace Elements (106 = 50 + 56 + 0)
- Exactly Mapped (mapping_exact: true):     50 (Train: 33, Val: 8, Test: 9)
- Qualified Non-Exact (mapping_exact: false): 56 (Train: 46, Val: 7, Test: 3)
- Unmapped Reviewed:                        0
- Level 5 Unaccounted Trace Elements:       0

Level 6: Rights and Export Fields (600 = 300 + 150 + 150 + 0)
- Public Permitted:                         300 (Train: 248, Val: 26, Test: 26)
- Protected Internal:                       150 (Train: 124, Val: 13, Test: 13)
- Suppressed By Policy:                     150 (Train: 124, Val: 13, Test: 13)
- Review Required:                          0
- Level 6 Unaccounted Export Fields:        0

----------------------------------------------------------------
5. The 12 Protected-Span Categories Explicitly Enumerated
----------------------------------------------------------------
1.  NAMED_ENTITY:                           Person, organization, geopolitical entity, location
2.  NUMBER_NUMERIC:                         Hindu-Arabic digits, Sinhala numerals, decimals, ranges
3.  DATE_TIME:                              Calendar dates, BE/CE years, months, timestamps
4.  UNIT_MEASUREMENT:                       SI units, imperial measures, localized symbols
5.  CURRENCY:                               LKR, USD, EUR, GBP, Rs., රු., currency symbols
6.  NEGATION_MARKER:                        නො, නැත, නොවේ, නොහැක, නොමැත and syntactic scope
7.  MODALITY_CONDITION:                     යුතුය, හැකිය, නොහැකිය, අවශ්‍යය (modality & obligation)
8.  CONDITIONAL_RELATION:                   නම්, වුවහොත්, පමණක්, විට (conditional dependencies)
9.  QUOTATION_DIRECT_SPEECH:                Single/double quotation marks, direct speech citations
10. PARENTHETICAL_REFERENCE:                Parentheses, square brackets, supplementary metadata
11. IDENTIFIER_CODE_URL:                    Alphanumeric IDs, URLs, DOIs, mixed-script terms
12. STAGE32_REVIEW_REQUIRED_VOCABULARY:     Technical, sensitive, or review-required lexicon terms

----------------------------------------------------------------
6. Test Verification & Regression Evidence
----------------------------------------------------------------
Stage 33 Tests:                             32/32 passed (32 test cases across 18 test files, 17 suites)
Full Backend Tests:                         643/643 passed
- Failures:                                 0
- Errors:                                   0
- Skipped:                                  0
- Warnings:                                 7 (FastAPI/Starlette/sklearn/SQLAlchemy deprecations)
- Duration:                                 172.55s (0:02:52)
Frontend Tests:                             17/17 passed
Frontend Production Build:                  PASSED
Documentation Manifest:                     13/13 verified (Tamper test PASSED)
Implementation Manifest:                    29/29 verified (Tamper test PASSED)

----------------------------------------------------------------
7. Governance Exclusions & Sealing Verdict
----------------------------------------------------------------
Complete semantic-equivalence validation:   NOT ESTABLISHED
Expert semantic-drift assessment:           DEFERRED TO STAGE 34
Sinhala expert linguistic validation:       DEFERRED TO STAGE 34
Child-development validation:               DEFERRED TO STAGE 34
Model comparison:                           DEFERRED TO STAGE 35
Production validation and fallback:         DEFERRED TO STAGE 36
Approved for child delivery:                FALSE
================================================================
```
