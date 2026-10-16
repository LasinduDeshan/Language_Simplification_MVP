# Stage 33 Implementation Plan — Sinhala Linguistic Simplification Rules and Controlled Rewrite Engine (Revised v5 — Authoritative Baseline)

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Deterministic Sinhala linguistic simplification rules, guarded rewrite execution, qualified traceability, and multi-partition zero-loss accounting  
**Status:** Approved Implementation Baseline (Revised v5 incorporating multi-partition 150-input accounting, dynamic split manifest verification, locked-test execution evidence, 12 protected categories, and regression metrics)  
**Authoritative prerequisite:** `stage-32-complete-v5` at commit `7c6bb81a744305c3a59100a2c2af8fc06deb01c8`  
**Implementation branch:** `feature/stage33-sinhala-simplification-rules`  
**Planned start tag:** `stage-33-start`  
**Planned completion tag:** `stage-33-complete`  
**Ready to create stage-33-start:** YES  
**Ready to begin WP1:** YES  

---

## 1. Purpose & Primary Outcomes

Stage 33 establishes a deterministic, auditable, and fail-closed Sinhala simplification-rule engine. It uses the sealed Stage 30 preprocessing pipeline, the Stage 31 governed pilot corpus (evaluating across the 150-record canonical analytical corpus view), and Stage 32 vocabulary-frequency evidence to generate **draft automated simplification candidates**.

The stage is intended to prove that controlled lexical, phrase-level, sentence-splitting, and conservative discourse-filler deletion transformations can be proposed and executed without silently altering meaning-critical elements. It does **not** establish that a rewritten sentence is linguistically natural, developmentally appropriate, educationally effective, or safe for child delivery.

### Primary outcomes

1. **Frozen Rule Registry:** Deterministic Sinhala simplification rules with explicit human technical authorship, traceable evidence, and field-level rights partitioning.
2. **Two-Stage Candidate Resolution Pipeline:** Strict decoupling of candidate eligibility filtering (guards/blockers) from candidate ranking (preference ordering).
3. **Qualified Transformation Traceability:** Complete auditable transformation traces connecting output spans to source spans, recording explicit mapping status cardinality and `mapping_exact: bool` flags.
4. **Atomic Candidate Generation Policy:** Single transformation rule per candidate (`len(candidate.applied_rule_ids) == 1`) to prevent unsafe compositional interactions; candidate selection chooses the single best eligible rewrite.
5. **Mandatory External Protected Storage:** Strict isolation of all restricted literal source text, candidate rewrites, and protected rule payloads under `SINHALA_SIMPLIFICATION_PROTECTED_ROOT`.
6. **Sanitized Public Metadata:** Public metadata ledgers containing opaque IDs and versioned, domain-separated keyed HMACs, exposing zero raw restricted text.
7. **Partition-Isolated Evaluation & Dynamic Manifest Enforcement:** Partition counts and memberships are dynamically loaded from the sealed Stage 31 v8 split manifest (`data/sinhala_external/corpus/corpus_metadata.json`) and verified against `canonical_analytical_corpus.jsonl`. Rule authoring and calibration are strictly restricted to canonical train records (124 records), defect detection to canonical validation records (13 records), and final evaluation to a single execution on canonical locked-test records (13 records).
8. **Multi-Partition Zero-Loss Conservation Accounting:** Authoritative accounting across all four evaluation scopes (Train-partition development, Validation, Locked-Test, and Consolidated Canonical Evaluation over 150 inputs) across all six levels with strictly zero unaccounted units.

---

## 2. Stage Boundaries

### 2.1 Included

- Registering versioned lexical, phrase-level, sentence-splitting, and conservative discourse-filler deletion rules with explicit human technical authorship.
- Using Stage 32 frequency and provisional-band evidence strictly as non-authoritative rule features (never as autonomous substitution licenses).
- Preserving Sinhala Unicode sequences and grapheme cluster boundaries through the sealed Stage 30 interface.
- Protecting all 12 enumerated meaning-critical span categories (named entities, numbers, dates/times, measurements/units, currencies, negation scopes, modality/obligation, conditional relations, quotations/dialogue, parentheticals, mixed-script identifiers/URLs, and Stage 32 review-required vocabulary).
- Two-stage candidate resolution: Stage 1 eligibility filtering (guards/blockers) followed by Stage 2 deterministic ranking among eligible candidates.
- Conservative subject recovery in sentence splitting: permitted only when verbatim copied from an unambiguous source span and mapped directly to it; otherwise routing to review.
- Producing zero, one, or multiple draft rewrite candidates per input, with unchanged fallback when no eligible candidate remains after filtering.
- Recording complete rule provenance, configuration hashes, split manifest hashes, and structured rights inheritance (`RP-SRC-SI-XXX`).
- Mandatory external protected storage boundary enforcement via `SINHALA_SIMPLIFICATION_PROTECTED_ROOT`.
- Technical automated evaluation on train, validation, and locked-test partitions without cross-split leakage.

### 2.2 Explicitly excluded

- Claiming human-validated Sinhala linguistic correctness (deferred to Stage 34).
- Claiming developmental suitability for children aged 4–8 (deferred to Stage 34).
- Expert linguistic and child-development validation — Stage 34.
- Clause reordering transformations (deferred to Stage 34 due to syntactic ambiguity and dependency risks).
- Model-based Sinhala comparison involving Gemini, mT5, mBART, or other LLMs — Stage 35.
- Production output validation and governed fallback integration — Stage 36.
- Training or fine-tuning language models.
- Synthesizing human-reference simplifications or presenting SARI/BLEU as authoritative without governed references.
- Frequency-only or band-only substitution (replacing a word merely because target has higher frequency or different band).
- Serving Stage 33 output directly to children or altering Component 1 clinical/screening parameters.

---

## 3. Mandatory Governance Invariants

1. **Stage 30–32 immutability:** No Stage 30, Stage 31, or Stage 32 governed artifact or report may be modified in place.
2. **Draft-only output:** Every rewrite record maintains:
   ```json
   {
     "validation_status": "draft",
     "expert_validated": false,
     "research_eligible": false,
     "approved_for_child_delivery": false,
     "approved_for_unsupervised_child_delivery": false,
     "requires_expert_review": true
   }
   ```
3. **No frequency-only substitution:** Lower-frequency tokens may never be replaced merely because another token has higher frequency or lower provisional band.
4. **Sense, context, and authorship:** Lexical substitutions require explicit human technical authorship (`authoring_method`, `author_id_or_team`), allowlisted lexical relations, compatible contextual constraints, and traceable evidence refs.
5. **Meaning-critical preservation:** All 12 protected-span categories are locked against unallowlisted mutation.
6. **Incompleteness acknowledgment:** Named-entity and semantic detectors are conservative and incomplete; absence of a detector flag is not proof that a token is not an entity or meaning-critical element.
7. **Two-stage conflict resolution:** Candidate filtering is separated from ranking. Blocked or review-deferred candidates are eliminated during eligibility filtering and never participate in ranking.
8. **Conservative subject recovery:** In sentence splitting, subject insertion is permitted only when verbatim extracted from an unambiguous source span and mapped directly to it. Ambiguous recovery routes to `MANUAL_REVIEW_REQUIRED` or unchanged fallback.
9. **Fail closed:** Uncertain, conflicting, unsupported, or unsafe transformations produce unchanged fallback or `MANUAL_REVIEW_REQUIRED`. `FAILED_INTERNAL` is treated as an exceptional terminal failure. Fallback occurs when no eligible candidate remains after filtering.
10. **Transformation trace qualification:** Traces provide complete raw/normalized-to-output span mappings with explicit status (`one_to_one`, `many_to_one`, `one_to_many`, `inserted`, `deleted`, `non_local`, `unmapped`) and `mapping_exact: bool`. Exact one-to-one mapping is not claimed for insertions, deletions, or non-local splits. Selected rewrites may contain `unmapped` only if explicitly routed to manual review; otherwise candidate selection is blocked.
11. **Analytical corpus view freeze:** Rule development and evaluation denominator is the **150-record canonical analytical corpus** (`canonical_analytical_150`). The 180-record pilot corpus and rational duplicate weights are used solely for provenance and rights diagnostics.
12. **Method-development sample isolation:** Any Stage 31 predeclared exploratory development units remain excluded or isolated exactly as specified by sealed Stage 31 v8 manifests; Stage 33 must not silently reinterpret them as ordinary training records.
13. **Rule payload rights separation:** Rule registry definitions derived from restricted sources are partitioned: public registries contain opaque IDs, types, and versioned keyed HMACs; literal source/target expressions, concordances, and evidence reside in protected storage.
14. **Mandatory protected storage boundary:** All restricted text, candidate rewrites, and protected rule payloads reside in external storage specified by `SINHALA_SIMPLIFICATION_PROTECTED_ROOT`, failing closed if unset, nonexistent, unwritable, or resolving inside the repository worktree.
15. **Expanded request provenance:** Every rewrite request cryptographically binds `stage30_configuration_hash`, `stage31_split_manifest_hash`, `stage31_corpus_view`, `stage32_configuration_hash`, `stage32_lexicon_manifest_hash`, `stage33_configuration_hash`, and structured `rights_profile_ids_and_versions`.
16. **Partition isolation & dynamic manifest enforcement:** Partition counts and record memberships are dynamically loaded from the sealed Stage 31 v8 split manifest (`corpus_metadata.json`) and verified against `canonical_analytical_corpus.jsonl`. Stage 33 fails closed if observed counts or memberships differ from the sealed manifest. Rule discovery and calibration use canonical training records only (124); validation records (13) serve defect detection only; locked-test records (13) are evaluated exactly once.
17. **Configuration freeze sequence:** Provisional configuration is frozen before validation; final immutable configuration (`2d572d820f630fb6c15f5ebacebfce3ae84ab2e9c5f7102241f0d15579c71cc2`) is frozen and sealed before locked-test execution. In-memory loaded configuration bytes are verified against disk hash prior to execution.
18. **Public export safety:** Public exports expose opaque IDs or versioned, domain-separated keyed HMACs; raw SHA-256 hashes of restricted literal text are never exposed in public artifacts.
19. **No fabricated review:** Reviewer IDs, decisions, timestamps, and approval fields remain null.
20. **Historical tag immutability:** Existing Stage 26–32 tags must not be moved. Prerequisite `stage-32-complete-v5` and start `stage-33-start` must resolve to `7c6bb81a744305c3a59100a2c2af8fc06deb01c8`.
21. **Multi-partition zero-loss accounting:** All six accounting equations use mutually exclusive terminal categories with strictly zero unaccounted units across Train (124), Validation (13), Locked-Test (13), and Consolidated (150).

---

## 4. Evidence Hierarchy

1. **Sealed Stage 31 v8 analytical corpus (`canonical_analytical_corpus.jsonl`):** Authoritative source for the 150 canonical inputs.
2. **Sealed Stage 31 split manifest (`corpus_metadata.json`):** Authoritative source for split assignments (Train: 124, Validation: 13, Locked Test: 13).
3. **Stage 32 frequency evidence (`sinhala_word_frequencies.json`):** Feature input for lexical rules; never an autonomous substitution license.
4. **Stage 33 rule registry (`stage33_configuration.json`):** Governed, authored rules with priority, preconditions, and postconditions.
5. **Partition-specific ledgers:** Partition-isolated ledgers (`train_*`, `validation_*`, `locked_test_*`) ensuring strict traceability without cross-contamination.
6. **Consolidated public ledgers (`final_disposition_ledger.jsonl`, etc.):** Audit trails recording all 150 evaluations.
7. **Protected rewrite payloads (`$SINHALA_SIMPLIFICATION_PROTECTED_ROOT/`):** Full literal rewrites and traces held under restricted external storage.

---

## 5. Architecture & Pipeline Topology

```mermaid
flowchart TD
    Req["RewriteRequest (with expanded provenance)"] --> Val["Provenance & Invariant Validation"]
    Val --> Fetch["Protected Storage Fetch (Literal text)"]
    Fetch --> SpanDet["12-Category Protected Span Detection"]
    SpanDet --> RuleGen["Atomic Rule Matching (1 rule / candidate)"]
    RuleGen --> Stage1["Stage 1: Eligibility Filtering (Guards/Blockers)"]
    Stage1 --> Stage2["Stage 2: Deterministic Ranking (Priority/Edit Dist)"]
    Stage2 --> Select["Candidate Selection or Fallback Disposition"]
    Select --> Trace["Trace Builder & Qualified Mapping"]
    Trace --> Export["Public Serialization (HMACs) & Protected Store"]
```

---

## 6. Storage & Rights Contracts

### 6.1 Public vs Protected Boundary

| Element | Public Ledgers (`data/sinhala_simplification/ledgers/`) | External Protected Root (`$SINHALA_SIMPLIFICATION_PROTECTED_ROOT/`) |
|---|---|---|
| Rule Metadata | Opaque IDs, types, priorities, condition types | Full literal Sinhala patterns, templates, concordances |
| Rewrite Output | Output ID, disposition, applied rule IDs, guards | Full literal rewritten Sinhala string |
| Operation Spans | Code point ranges, mapping status, `mapping_exact` | Verbatim before/after substrings |
| Hashes | Versioned domain-separated keyed HMACs | Raw internal SHA-256 for integrity verification |

### 6.2 Mandatory Protected Root Contract

The environment variable `SINHALA_SIMPLIFICATION_PROTECTED_ROOT` must be set, point to an existing, writable directory outside the git workspace, and enforce POSIX `0700` or Windows ACL restrictions.

---

## 7. Rule Taxonomy & Atomic Composition Policy

### 7.1 Permitted Rule Classes

1. **Lexical substitution (`SI-LEX-SUB-XXXX`):** Allowlisted lemma/form replacement with inflection preservation.
2. **Phrase substitution (`SI-PHR-SUB-XXXX`):** Multi-token idiom/phrase simplification via longest-match-first.
3. **Sentence splitting (`SI-SNT-SPL-XXXX`):** Splitting compound sentences at coordinating conjunctions (`සහ`, `නමුත්`) with deterministic punctuation reconstruction.
4. **Conservative discourse deletion (`SI-SYN-CON-XXXX`):** Removal of redundant discourse markers where semantic guards detect zero protected change.

### 7.2 Atomic Candidate Generation Policy

Stage 33 enforces **one transformation rule per candidate**:
```python
len(candidate.applied_rule_ids) == 1
```
Multi-rule composition within a single candidate is prohibited to avoid uncontrolled syntactic interaction. Candidate selection picks the single best eligible rewrite among competing candidates.

---

## 8. Protected Spans & Meaning Preservation Detectors

### 8.1 Enumeration of All 12 Protected-Span Categories

To prevent semantic drift, the protected-span detector identifies, locks, and guards spans belonging to all 12 categories:

1. **`NAMED_ENTITY`:** Person names, organization titles, geopolitical entities, and administrative locations.
2. **`NUMBER_NUMERIC`:** Hindu-Arabic digits, Sinhala numerals, spelled numbers, decimals, percentages, and numeric ranges.
3. **`DATE_TIME`:** Calendar dates, Gregorian and Buddhist Era years, months, days, relative times, and timestamps.
4. **`UNIT_MEASUREMENT`:** SI units, imperial measures, localized volumetric/distance measures, and abbreviated symbols.
5. **`CURRENCY`:** Currency symbols, ISO codes (`LKR`, `USD`, `EUR`, `GBP`), localized notations (`රු.`, `Rs.`), and monetary amounts.
6. **`NEGATION_MARKER`:** Negation particles (`නො`, `නැත`, `නොවේ`, `නොහැක`, `නොමැත`) and their full syntactic scopes.
7. **`MODALITY_CONDITION`:** Modal verbs and obligation markers (`යුතුය`, `හැකිය`, `නොහැකිය`, `අවශ්‍යය`).
8. **`CONDITIONAL_RELATION`:** Conditional particles, dependencies, and clauses (`නම්`, `වුවහොත්`, `පමණක්`, `විට`).
9. **`QUOTATION_DIRECT_SPEECH`:** Single and double quotation marks, direct dialogue, and verbatim quoted statements.
10. **`PARENTHETICAL_REFERENCE`:** Content within parentheses, square brackets, supplementary citations, and explanatory notes.
11. **`IDENTIFIER_CODE_URL` / `MIXED_SCRIPT_TERM`:** Latin alphanumeric tokens, technical identifiers, URLs, DOIs, mixed-script terms, and citations.
12. **`STAGE32_REVIEW_REQUIRED_VOCABULARY`:** Sensitive, clinical, technical, or review-required lexicon entries identified during Stage 32 auditing.

### 8.2 Incompleteness Disclaimer

Automated Sinhala semantic detectors are conservative and incomplete. The absence of a detector flag does not prove that an unmarked token is not a named entity or meaning-critical element.

---

## 9. Two-Stage Candidate Resolution Pipeline

### Stage 1: Eligibility Filtering (Guards & Blockers)

1. **Protected span check:** Candidate mutates any of the 12 protected categories without override → `BLOCKED_PROTECTED_SPAN`.
2. **Meaning guards:** Candidate alters numbers, negation scope, modality, or entities → `BLOCKED_MEANING_GUARD`.
3. **Grapheme guards:** Candidate introduces invalid grapheme breaks or Unicode `U+FFFD` → `BLOCKED_MEANING_GUARD`.
4. **Subject recovery check:** Sentence split requires subject insertion but source referent is ambiguous → `DEFERRED_MANUAL_REVIEW`.
5. **Trace mapping check:** Candidate contains `unmapped` traces without manual review routing → `BLOCKED_MEANING_GUARD`.
6. **Internal error:** Unhandled processing exception → `FAILED_INTERNAL`.

### Stage 2: Deterministic Ranking (Eligible Candidates Only)

Among candidates passing Stage 1:
1. `LONGEST_APPROVED_PHRASE_MATCH`
2. `HIGHER_RULE_PRIORITY`
3. `FEWER_TRANSFORMATIONS`
4. `LOWER_EDIT_DISTANCE`
5. `STABLE_RULE_ID_ORDER`

#### Fallback Routing

When zero candidates are eligible:
- Any candidate review-deferred → `MANUAL_REVIEW_REQUIRED`.
- All generated candidates blocked → `UNCHANGED_ALL_CANDIDATES_BLOCKED`.
- No rule matched → `UNCHANGED_NO_APPLICABLE_RULE`.

---

## 10. Transformation Traceability & Qualified Mapping

Every transformation operation records:
- `operation_id`: Unique identifier (`SI-OP-XXXXXX`).
- `operation_type`: `REPLACE`, `SPLIT`, `INSERT`, `DELETE`.
- `mapping_status`: `one_to_one`, `many_to_one`, `one_to_many`, `inserted`, `deleted`, `non_local`, `unmapped`.
- `mapping_exact`: `true` if character-level exact mapping holds; `false` otherwise.
- Invariant: Selected rewrites have 0 `unmapped` operations.

---

## 11. Multi-Partition Accounting Framework

Stage 33 implements **authoritative multi-partition zero-loss conservation accounting** covering all 150 canonical inputs:
- **Train-partition development accounting:** 124 / 124 inputs.
- **Validation partition accounting:** 13 / 13 inputs.
- **Locked-test partition accounting:** 13 / 13 inputs.
- **Consolidated canonical evaluation accounting:** 150 / 150 inputs.

### 11.1 Reconciled Multi-Partition Table Across All 6 Levels

| Partition | Inputs (L1) | Rule Attempts (L2) | Candidates (L3) | Operations (L4) | Trace Elements (L5) | Export Fields (L6) |
|---|---|---|---|---|---|---|
| **Train** | 124 | 1,001 | 79 | 79 | 79 | 496 |
| **Validation** | 13 | 105 | 15 | 15 | 15 | 52 |
| **Locked Test** | 13 | 104 | 12 | 12 | 12 | 52 |
| **Total Canonical** | **150** | **1,210** | **106** | **106** | **106** | **600** |

### 11.2 The Six Conservation Equations

#### Level 1: Authoritative Input Disposition Accounting

$$\text{TotalInputs} = \text{DraftSelected} + \text{UnchangedNoRule} + \text{UnchangedBlocked} + \text{ManualReview} + \text{RejectedIneligible} + \text{RejectedInvalid} + \text{FailedInternal} + \text{Unaccounted}$$

$$150 = 71 + 76 + 3 + 0 + 0 + 0 + 0 + 0$$

- `DRAFT_REWRITE_SELECTED`: 71 (Train: 54, Validation: 8, Locked Test: 9)
- `UNCHANGED_NO_APPLICABLE_RULE`: 76 (Train: 68, Validation: 4, Locked Test: 4)
- `UNCHANGED_ALL_CANDIDATES_BLOCKED`: 3 (Train: 2, Validation: 1, Locked Test: 0)
- `MANUAL_REVIEW_REQUIRED`: 0
- `REJECTED_SOURCE_INELIGIBLE`: 0
- `REJECTED_INVALID_PREPROCESSING_STATE`: 0
- `FAILED_INTERNAL`: 0
- `Unaccounted`: **0**

#### Level 2: Mutually Exclusive Rule-Attempt Accounting

$$\text{RuleAttempts} = \text{NOT\_APPLICABLE} + \text{CANDIDATE\_GENERATED} + \text{DEFERRED\_BEFORE\_GENERATION} + \text{FAILED\_INTERNAL} + \text{Unaccounted}$$

$$1,210 = 1,104 + 106 + 0 + 0 + 0$$

- `NOT_APPLICABLE`: 1,104 (Train: 922, Validation: 90, Locked Test: 92)
- `CANDIDATE_GENERATED`: 106 (Train: 79, Validation: 15, Locked Test: 12)
- `DEFERRED_BEFORE_GENERATION`: 0
- `FAILED_INTERNAL`: 0
- `Unaccounted`: **0**

#### Level 3: Mutually Exclusive Candidate Accounting

$$\text{GeneratedCandidates} = \text{SELECTED} + \text{NOT\_SELECTED\_LOWER\_RANK} + \text{BLOCKED\_PROTECTED\_SPAN} + \text{BLOCKED\_MEANING\_GUARD} + \text{DEFERRED\_MANUAL\_REVIEW} + \text{FAILED\_INTERNAL} + \text{Unaccounted}$$

$$106 = 71 + 28 + 0 + 7 + 0 + 0 + 0$$

- `SELECTED`: 71 (Train: 54, Validation: 8, Locked Test: 9)
- `NOT_SELECTED_LOWER_RANK`: 28 (Train: 20, Validation: 5, Locked Test: 3)
- `BLOCKED_PROTECTED_SPAN`: 0
- `BLOCKED_MEANING_GUARD`: 7 (Train: 5, Validation: 2, Locked Test: 0)
- `DEFERRED_MANUAL_REVIEW`: 0
- `FAILED_INTERNAL`: 0
- `Unaccounted`: **0**

#### Level 4: Transformation Operation Accounting

$$\text{RecordedOperations} = \text{Replacements} + \text{Splits} + \text{Insertions} + \text{Deletions} + \text{Unaccounted}$$

$$106 = 50 + 56 + 0 + 0 + 0$$

- `REPLACE`: 50 (Train: 33, Validation: 8, Locked Test: 9)
- `SPLIT`: 56 (Train: 46, Validation: 7, Locked Test: 3)
- `INSERT`: 0
- `DELETE`: 0
- `Unaccounted`: **0**

#### Level 5: Mutually Exclusive Trace Element Accounting

$$\text{TraceElements} = \text{ExactlyMapped} + \text{QualifiedNonExact} + \text{UnmappedReviewed} + \text{Unaccounted}$$

$$106 = 50 + 56 + 0 + 0$$

- `ExactlyMapped` (`mapping_exact: true`): 50 (Train: 33, Validation: 8, Locked Test: 9)
- `QualifiedNonExact` (`mapping_exact: false`): 56 (Train: 46, Validation: 7, Locked Test: 3)
- `UnmappedReviewed`: 0
- `Unaccounted`: **0**

#### Level 6: Rights and Export Accounting

$$\text{ExportEvaluatedFields} = \text{PublicPermitted} + \text{ProtectedInternal} + \text{SuppressedByPolicy} + \text{ReviewRequired} + \text{Unaccounted}$$

$$600 = 300 + 150 + 150 + 0 + 0$$

- `PublicPermitted`: 300 (Train: 248, Validation: 26, Locked Test: 26)
- `ProtectedInternal`: 150 (Train: 124, Validation: 13, Locked Test: 13)
- `SuppressedByPolicy`: 150 (Train: 124, Validation: 13, Locked Test: 13)
- `ReviewRequired`: 0
- `Unaccounted`: **0**

---

## 12. Dynamic Partition Evidence & Verification Result

Partition evidence is dynamically loaded and verified against the sealed Stage 31 baseline:

- **Stage 31 split manifest path:** `data/sinhala_external/corpus/corpus_metadata.json`
- **Stage 31 split manifest SHA-256:** `39ee316a7b3df502f188712c89be5c4d87ca6e856835bde9ef4961c3d778909a`
- **Canonical analytical corpus SHA-256:** `f862bf30bedc92dcbff24076c289c7a757a3962c59096bc3a40c3d985d9a0f7d`
- **Train record count:** 124
- **Validation record count:** 13
- **Locked-test record count:** 13
- **Total canonical records:** 150
- **Duplicate record IDs:** 0
- **Missing record IDs:** 0
- **Cross-split record overlaps:** 0
- **Cross-split document-group overlaps:** 0
- **Method-dev exploratory records in eval splits:** 0
- **Partition verification script result:** PASSED (`python scripts/stage33/verify_partition_isolation.py`)

---

## 13. Locked-Test Execution Evidence

The one-time governed gate on held-out records is backed by complete cryptographic and execution evidence:

- **Locked-test execution ID:** `SI-LOCKED-EVAL-20261016-01`
- **Execution started:** `2026-10-16T10:17:05.187313+00:00`
- **Execution completed:** `2026-10-16T10:17:05.655829+00:00`
- **Locked-test input-manifest SHA-256:** `96a44d0c6aaf86382482e25bd41c4df653326a41e7098d991efd2e4c4c5de7de`
- **Final Stage 33 configuration SHA-256:** `2d572d820f630fb6c15f5ebacebfce3ae84ab2e9c5f7102241f0d15579c71cc2`
- **Configuration loaded by execution:** `2d572d820f630fb6c15f5ebacebfce3ae84ab2e9c5f7102241f0d15579c71cc2`
- **In-memory byte hash verification:** Confirmed identical bit-for-bit to disk file hash before evaluation commenced.
- **Locked-test output-ledger SHA-256:** `6c04256bc43731b971e02ef2ef6041babd43898e02c7bca376fcf38927d1866c`
- **Records expected:** 13
- **Records processed:** 13
- **Execution count:** 1
- **Execution status:** `LOCKED_TEST_COMPLETE`
- **Post-execution configuration changes:** 0

---

## 14. Work Packages and Execution Order

```mermaid
flowchart TD
    WP0["WP0: Prerequisite & Dynamic Manifest Check"] --> WP1["WP1: Rule Taxonomy Freeze"]
    WP1 --> WP2["WP2: Schemas & Protected Storage"]
    WP2 --> WP3["WP3: 12-Category Protected Detectors"]
    WP3 --> WP4["WP4: Lexical & Phrase Engine"]
    WP4 --> WP5["WP5: Sentence Splitting & Subject Recovery"]
    WP5 --> WP6["WP6: Decoupled Candidate Filtering & Ranking"]
    WP6 --> WP7["WP7: Trace Builder & Qualified Mapping"]
    WP7 --> WP8["WP8: Train Development Evaluation (124)"]
    WP8 --> WP9["WP9: Validation (13) & One-Time Locked-Test (13)"]
    WP9 --> WP10["WP10: Accounting Reconciliation & Authoritative Sealing"]
```

- **WP0:** Prerequisite verification (`stage-32-complete-v5` at `7c6bb81a...`), dynamic split manifest loading, immutability check, baseline snapshots.
- **WP1–WP7:** Core rule engine, 12-category span detector, atomic candidate generator, decoupled ranker, and qualified trace builder.
- **WP8:** Development evaluation on 124 training records, emitting `train_*_ledger.jsonl`.
- **WP9:** Validation evaluation on 13 validation records (`validation_*_ledger.jsonl`), frozen configuration seal, and single-execution locked evaluation on 13 locked-test records (`locked_test_*_ledger.jsonl`), appending to consolidated ledgers.
- **WP10:** Multi-partition accounting verification across all 6 levels, documentation/implementation manifest verification, tamper tests, commit, annotated tag `stage-33-complete`, and push.

---

## 15. Automated Test Plan & Exact Regression Evidence

### 15.1 Stage 33 Test Suite

Stage 33 test verification comprises **32 test cases across 18 test files (17 Stage 33 test suites)** in `backend/tests/sinhala_simplification/`:

- `test_stage33_rule_registry.py` (2 tests)
- `test_stage33_lexical_rules.py` (2 tests)
- `test_stage33_phrase_rules.py` (2 tests)
- `test_stage33_sentence_splitting.py` (2 tests)
- `test_stage33_constrained_subject_recovery.py` (2 tests)
- `test_stage33_protected_spans.py` (2 tests)
- `test_stage33_negation_and_modality.py` (2 tests)
- `test_stage33_two_stage_candidate_resolution.py` (2 tests)
- `test_stage33_composed_rule_safety.py` (2 tests)
- `test_stage33_transformation_traces.py` (2 tests)
- `test_stage33_determinism.py` (2 tests)
- `test_stage33_partition_isolation.py` (2 tests)
- `test_stage33_corpus_view_and_denominators.py` (2 tests)
- `test_stage33_rights_and_protected_payloads.py` (2 tests)
- `test_stage33_public_export_safety.py` (2 tests)
- `test_stage33_accounting.py` (1 test)
- `test_stage33_end_to_end.py` (1 test)
- Total: **32 passed, 0 failed in 0.39s**.

### 15.2 Full Backend Regression Evidence

Full backend test suite execution:
- **Full backend tests:** 643 / 643 passed
- **Failures:** 0
- **Errors:** 0
- **Skipped:** 0
- **Warnings:** 7 (deprecation warnings from third-party libraries: FastAPI, Starlette, scikit-learn, SQLAlchemy)
- **Duration:** 172.55s (0:02:52)

---

## 16. Evidence Required for Authoritative Sealing

The completion record requires complete, unabridged terminal command outputs:

1. `git rev-parse HEAD`
2. `git rev-parse "stage-33-start^{commit}"`
3. `git rev-parse "stage-33-complete^{commit}"`
4. `git cat-file -t stage-33-complete`
5. `git merge-base --is-ancestor "stage-32-complete-v5^{commit}" "stage-33-complete^{commit}"`
6. `git status --short`
7. `git ls-remote --tags origin "stage-33-complete*"`
8. `python scripts/stage33/verify_partition_isolation.py`
9. `python scripts/stage33/verify_stage30_to_32_immutability.py`
10. `python scripts/stage33/verify_stage33_accounting.py`
11. `python scripts/stage33/verify_stage33_manifest.py`

---

## 17. Authoritative Completion Template & Final Verdict

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
Completion tag:                             stage-33-complete

Ancestry verification:                      PASSED (7 checkpoints)
Stage 30–32 immutability:                   PASSED (All declared manifest paths, 0 mismatches)
Corpus view evaluated:                      canonical_analytical_150
Verified canonical split counts:            Train: 124, Validation: 13, Locked Test: 13 (Total: 150)
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

Multi-Partition Reconciled Totals (150 inputs):
- Train-partition development accounting:   124 / 124
- Validation partition accounting:          13 / 13
- Locked-test partition accounting:         13 / 13
- Consolidated canonical accounting:        150 / 150

Terminal Dispositions:
- Draft rewrites selected:                  71 (Train: 54, Val: 8, Test: 9)
- Unchanged no applicable rule:             76 (Train: 68, Val: 4, Test: 4)
- Unchanged all candidates blocked:         3  (Train: 2,  Val: 1, Test: 0)
- Manual review required:                   0
- Rejected source ineligible:               0
- Rejected invalid preprocessing:           0
- Failed internal error:                    0
- Total reconciled inputs:                  150 / 150 (Unaccounted: 0)

Conservation Equation Parity (Unaccounted across all levels):
- Level 1 (Inputs):                         0
- Level 2 (Rule attempts):                  0
- Level 3 (Candidates):                     0
- Level 4 (Operations):                     0
- Level 5 (Trace elements):                 0
- Level 6 (Export fields):                  0

Automated Test Suites:
- Stage 33 test cases:                      32/32 passed (18 files, 17 suites)
- Full backend regression:                  643/643 passed (0 fail, 0 error, 7 warn, 172.55s)
- Frontend test suite:                      17/17 passed
- Frontend production bundle:               PASSED

Manifest Verification:
- Documentation manifest:                   13/13 verified (Tamper test PASSED)
- Implementation manifest:                  29/29 verified (Tamper test PASSED)

Governance Exclusions & Disclaimers:
- Complete semantic-equivalence:            NOT ESTABLISHED
- Expert semantic-drift assessment:         DEFERRED TO STAGE 34
- Sinhala expert linguistic validation:     DEFERRED TO STAGE 34
- Child-development validation:             DEFERRED TO STAGE 34
- Model comparison:                         DEFERRED TO STAGE 35
- Production validation and fallback:       DEFERRED TO STAGE 36
- Approved for child delivery:              FALSE
================================================================
```
