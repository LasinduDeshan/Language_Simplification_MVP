# Stage 33 Implementation Plan — Sinhala Linguistic Simplification Rules and Controlled Rewrite Engine (Governance-Restored Pre-Execution Baseline Specification)

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Deterministic Sinhala linguistic simplification rules, guarded rewrite execution, qualified traceability, and multi-partition zero-loss accounting  
**Status:** Approved Pre-Execution Implementation Baseline  
**Document Nature:** Governance-Restored Pre-Execution Baseline Specification (Reconstructed Execution Contract)  
**Authoritative prerequisite:** `stage-32-complete-v5` at commit `7c6bb81a744305c3a59100a2c2af8fc06deb01c8`  
**Implementation branch:** `feature/stage33-sinhala-simplification-rules`  
**Historical start tag:** `stage-33-start`  
**Historical completion tag:** `stage-33-complete`  
**Reconciled authoritative tag:** `stage-33-complete-v2`  
**Historical implementation status:** EXECUTED  
**Current document purpose:** GOVERNANCE RESTORATION ONLY  
**Ready to create stage-33-start:** NOT APPLICABLE — TAG ALREADY EXISTS  
**Ready to begin WP1:** NOT APPLICABLE — EXECUTION ALREADY COMPLETED  

> [!NOTE]
> **Historical Accuracy Notice:** This document reconstructs the approved pre-execution specification baseline and execution contract without embedding observed Stage 33 results, actual execution counts, locked-test timestamps, final commit hashes, or test execution outcomes. All retrospective empirical observations, locked-test execution logs, test outputs, and Git sealing evidence are strictly maintained in `docs/stage33_completion_record.md` and `docs/stage33_reconciliation_report.md`.

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
7. **Partition-Isolated Evaluation & Dynamic Manifest Enforcement:** Partition counts and memberships are dynamically loaded from the sealed Stage 31 authoritative partition metadata artifact (`data/sinhala_external/corpus/corpus_metadata.json`) and verified against `canonical_analytical_corpus.jsonl`. Rule authoring and calibration are strictly restricted to canonical train records, defect detection to canonical validation records, and final evaluation to a single execution on canonical locked-test records.
8. **Multi-Partition Zero-Loss Conservation Accounting:** Authoritative accounting across all four evaluation scopes (Train-partition development, Validation, Locked-Test, and Consolidated Canonical Evaluation over the 150 inputs) across all six levels with strictly zero unaccounted units.

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
10. **Transformation trace qualification:** Traces provide complete raw/normalized-to-output span mappings with explicit status (`one_to_one`, `many_to_one`, `one_to_many`, `inserted`, `deleted`, `non_local`, `unmapped`) and `mapping_exact: bool`. Exact one-to-one mapping is not claimed for insertions, deletions, or non-local splits. Candidates containing unmapped elements may only be routed to manual review. They are prohibited from selection as draft rewrites. Selected rewrites must contain zero unmapped elements.
11. **Analytical corpus view freeze:** Rule development and evaluation denominator is the **150-record canonical analytical corpus** (`canonical_analytical_150`). The 180-record pilot corpus and rational duplicate weights are used solely for provenance and rights diagnostics.
12. **Method-development sample isolation:** Any Stage 31 predeclared exploratory development units remain excluded or isolated exactly as specified by sealed Stage 31 v8 manifests; Stage 33 must not silently reinterpret them as ordinary training records.
13. **Rule payload rights separation:** Rule registry definitions derived from restricted sources are partitioned: public registries contain opaque IDs, types, and versioned keyed HMACs; literal source/target expressions, concordances, and evidence reside in protected storage.
14. **Mandatory protected storage boundary:** All restricted text, candidate rewrites, and protected rule payloads reside in external storage specified by `SINHALA_SIMPLIFICATION_PROTECTED_ROOT`, failing closed if unset, nonexistent, unwritable, or resolving inside the repository worktree.
15. **Expanded request provenance:** Every rewrite request cryptographically binds `stage30_configuration_hash`, `stage31_split_manifest_hash`, `stage31_corpus_view`, `stage32_configuration_hash`, `stage32_lexicon_manifest_hash`, `stage33_configuration_hash`, and structured `rights_profile_ids_and_versions`.
16. **Partition isolation & dynamic manifest enforcement:** Partition counts and record memberships are dynamically loaded from the sealed Stage 31 authoritative partition metadata artifact (`data/sinhala_external/corpus/corpus_metadata.json`) and verified against `canonical_analytical_corpus.jsonl`. Stage 33 fails closed if observed counts or memberships differ from the sealed manifest. Rule discovery and calibration use canonical training records only; validation records serve defect detection only; locked-test records are evaluated exactly once.
17. **Configuration freeze sequence:** Provisional configuration is frozen before validation; final immutable configuration is frozen and sealed before locked-test execution. In-memory loaded configuration bytes are verified against disk hash prior to execution.
18. **Public export safety:** Public exports expose opaque IDs or versioned, domain-separated keyed HMACs; raw SHA-256 hashes of restricted literal text are never exposed in public artifacts.
19. **No fabricated review:** Reviewer IDs, decisions, timestamps, and approval fields remain null.
20. **Historical tag immutability:** Existing Stage 26–32 tags must not be moved. Prerequisite `stage-32-complete-v5` and start `stage-33-start` must resolve to `7c6bb81a744305c3a59100a2c2af8fc06deb01c8`.
21. **Multi-partition zero-loss accounting:** All six accounting equations use mutually exclusive terminal categories with strictly zero unaccounted units across Train, Validation, Locked-Test, and Consolidated partitions.

---

## 4. Evidence Hierarchy

1. **Sealed Stage 31 v8 analytical corpus (`data/sinhala_external/corpus/canonical_analytical_corpus.jsonl`):** Authoritative source for the 150 canonical inputs (record identity and `"split"` field).
2. **Sealed Stage 31 partition metadata artifact (`data/sinhala_external/corpus/corpus_metadata.json`):** Authoritative Stage 31 split definition, hash-verified under Stage 31 implementation manifest (`39ee316a...`).
3. **Governed Stage 32 frequency evidence (`data/sinhala_lexicon/lexicon/draft_lexicon.jsonl` & `data/sinhala_lexicon/ledgers/candidate_entry_ledger.jsonl`):** Governed lexicon ledgers controlled by Stage 32 v5 implementation manifest; used strictly as non-authoritative rule features.
4. **Stage 33 rule registry (`data/sinhala_simplification/registry/stage33_configuration.json`):** Governed, authored rules with priority, preconditions, and postconditions.
5. **Partition-specific ledgers:** Partition-isolated ledgers (`train_*`, `validation_*`, `locked_test_*`) ensuring strict traceability without cross-contamination.
6. **Consolidated public ledgers (`final_disposition_ledger.jsonl`, etc.):** Audit trails recording all canonical evaluations.
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
- **Invariant:** Candidates containing `unmapped` elements may only be routed to manual review. They are prohibited from selection as draft rewrites. Selected rewrites must contain strictly zero `unmapped` elements.

---

## 11. Explicit Automated Evaluation Metrics Framework

The pipeline specifies 17 technical diagnostic metrics reported separately for each canonical analytical split (`train`, `validation`, and `locked_test`, with partition counts loaded dynamically from the sealed Stage 31 partition metadata artifact `data/sinhala_external/corpus/corpus_metadata.json`):

1. **Rule applicability rate:** Fraction of submitted inputs matching at least one rule.
2. **Candidate generation rate:** Mean count of candidates generated per input.
3. **Candidate eligibility rate:** Fraction of generated candidates passing Stage 1 guards.
4. **Draft rewrite selection rate:** Fraction of submitted inputs yielding a selected draft rewrite.
5. **Unchanged-no-rule rate:** Fraction of inputs with no applicable rule (`UNCHANGED_NO_APPLICABLE_RULE`).
6. **Unchanged-all-blocked rate:** Fraction of inputs where all generated candidates were blocked by guards (`UNCHANGED_ALL_CANDIDATES_BLOCKED`).
7. **Manual-review rate:** Fraction of inputs routed to `MANUAL_REVIEW_REQUIRED`.
8. **Protected-span block rate:** Fraction of candidates rejected due to protected-span overlap.
9. **Meaning-guard block rate:** Fraction of candidates rejected due to semantic guard violations.
10. **Trace classification coverage:** Fraction of trace elements classified with a mapping status and exactness flag (target 100%). Calculated over trace elements rather than output spans because deletion operations have no output span. Candidates containing unmapped elements may only be routed to manual review; they are prohibited from selection as draft rewrites. Selected rewrites must contain strictly zero `unmapped` elements.
11. **Exact vs qualified-non-exact mappings:** Proportion of operations with `mapping_exact == true` vs `false`.
12. **Mean operations per selected rewrite:** Average number of operations per selected draft.
13. **Token-count change:** Absolute and relative delta in Stage 30 tokens.
14. **Grapheme-count change:** Absolute and relative delta in Sinhala grapheme clusters.
15. **Sentence-count change:** Net change in sentence count (sentence-splitting diagnostic).
16. **Deterministic rerun equality:** Percentage of byte-identical outputs upon repeated runs (target 100%).
17. **Configured invariant violations:** Detected violations of protected spans, numbers, entities, negation, modality, Unicode, grapheme, or trace rules. Target: strictly 0 among selected candidates.

> [!IMPORTANT]
> - **Complete semantic-equivalence validation:** NOT ESTABLISHED
> - **Expert semantic-drift assessment:** DEFERRED TO STAGE 34
> These metrics are automated technical diagnostics of rule execution and guard enforcement. Automated Stage 33 checks can only detect violations of configured technical rules and explicit invariants; they cannot mathematically or linguistically establish propositional equivalence or developmental readability.

---

## 12. Multi-Partition Accounting Framework

Stage 33 specifies **authoritative multi-partition zero-loss conservation accounting** covering all 150 canonical inputs:
- **Train-partition development accounting:** Reconciled on canonical training inputs.
- **Validation partition accounting:** Reconciled on canonical validation inputs.
- **Locked-test partition accounting:** Reconciled on canonical locked-test inputs.
- **Consolidated canonical evaluation accounting:** Reconciled across the complete 150-input population.

### 12.1 The Six Conservation Equations

#### Level 1: Authoritative Input Disposition Accounting

$$\text{TotalInputs} = \text{DraftSelected} + \text{UnchangedNoRule} + \text{UnchangedBlocked} + \text{ManualReview} + \text{RejectedIneligible} + \text{RejectedInvalid} + \text{FailedInternal} + \text{Unaccounted}$$

Target `Unaccounted`: strictly **0**.

#### Level 2: Mutually Exclusive Rule-Attempt Accounting

$$\text{RuleAttempts} = \text{NOT\_APPLICABLE} + \text{CANDIDATE\_GENERATED} + \text{DEFERRED\_BEFORE\_GENERATION} + \text{FAILED\_INTERNAL} + \text{Unaccounted}$$

**Definition of Rule Attempt & Arithmetic Formulation:**
A rule attempt represents an evaluated rule applicability site. An evaluation is initiated for every input and every registered rule:
- When the rule pattern does not match the input text, exactly 1 attempt with terminal status `NOT_APPLICABLE` is recorded.
- When the rule pattern matches one or more non-overlapping source spans, an attempt with terminal status `CANDIDATE_GENERATED` is recorded for each discrete match site.

The exact mathematical relationship between base input-rule evaluations and total rule attempts is:
$$\text{AdditionalMatchSiteEvaluations} = \sum_{\text{input, rule}} \max(0, \text{MatchSiteCount} - 1)$$

Therefore:
$$\text{TotalRuleAttempts} = N_{\text{inputs}} \times N_{\text{rules}} + \text{AdditionalMatchSiteEvaluations}$$

Every additional attempt must evaluate a distinct, non-overlapping `source_span`.
All observed partition-specific counts (registered rules, base evaluations, additional match sites, and observed total attempts) are empirical execution outcomes and are maintained strictly in `docs/stage33_accounting_summary.md` and `docs/stage33_completion_record.md`.

Target `Unaccounted`: strictly **0**.

#### Level 3: Mutually Exclusive Candidate Accounting

$$\text{GeneratedCandidates} = \text{SELECTED} + \text{NOT\_SELECTED\_LOWER\_RANK} + \text{BLOCKED\_PROTECTED\_SPAN} + \text{BLOCKED\_MEANING\_GUARD} + \text{DEFERRED\_MANUAL\_REVIEW} + \text{FAILED\_INTERNAL} + \text{Unaccounted}$$

Target `Unaccounted`: strictly **0**.

#### Level 4: Transformation Operation Accounting

$$\text{RecordedOperations} = \text{Replacements} + \text{Splits} + \text{Insertions} + \text{Deletions} + \text{Unaccounted}$$

Target `Unaccounted`: strictly **0**.

#### Level 5: Mutually Exclusive Trace Element Accounting

$$\text{TraceElements} = \text{ExactlyMapped} + \text{QualifiedNonExact} + \text{UnmappedReviewed} + \text{Unaccounted}$$

Target `Unaccounted`: strictly **0**.

#### Level 6: Rights and Export Decision Slots Accounting

$$\text{ExportDecisionSlots} = \text{PublicPermitted} + \text{ProtectedInternal} + \text{SuppressedByPolicy} + \text{ReviewRequired} + \text{Unaccounted}$$

**Frozen Inventory of the 4 Evaluated Decision Slots Per Input Record:**
Each canonical input evaluates exactly 4 structured export decision slots (grouping multiple fields per slot):
1. **Record Identifier Slot:** groups `request_id`, `record_id`, `output_id` (PublicPermitted)
2. **Rule and Guard Metadata Slot:** groups `final_disposition`, `applied_rule_ids`, `guard_results`, `validation_status` (PublicPermitted)
3. **Output Storage Locator Slot:** groups `output_storage_ref` (ProtectedInternal — opaque external pointer)
4. **Restricted Text Content Slot:** groups literal `source_text`, `candidate_text_internal`, `output_text` (SuppressedByPolicy — omitted from public export)

The baseline specifies the exact expected number of export decision slots across the evaluated input population:
$$\text{ExpectedExportDecisionSlots} = N_{\text{inputs}} \times 4$$

Observed partition-specific category breakdowns belong strictly in `docs/stage33_accounting_summary.md` and `docs/stage33_completion_record.md`.
Target `Unaccounted`: strictly **0**.

---

## 13. Dynamic Partition Contract & Isolation Requirements

Partition assignments are dynamically loaded from the sealed Stage 31 baseline:
- **Authoritative partition metadata artifact:** `data/sinhala_external/corpus/corpus_metadata.json`
- **Canonical analytical corpus:** `data/sinhala_external/corpus/canonical_analytical_corpus.jsonl`
- **Partition verification script:** `scripts/stage33/verify_partition_isolation.py`
- **Invariants:** Zero cross-split record overlaps, zero cross-split document-group overlaps, zero leakage of evaluation records into training.

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
    WP7 --> WP8["WP8: Train Development Evaluation"]
    WP8 --> WP9["WP9: Validation Defect Check & One-Time Locked-Test"]
    WP9 --> WP10["WP10: Accounting Reconciliation & Authoritative Sealing"]
```

### WP0 — Prerequisite Verification and Baseline Auditing
1. Verify prerequisite tag `stage-32-complete-v5` at `7c6bb81a744305c3a59100a2c2af8fc06deb01c8`.
2. Dynamically load split counts and record memberships from `data/sinhala_external/corpus/corpus_metadata.json`.
3. Verify Stage 30–32 immutability: zero differences relative to `stage-33-start`.
4. Verify `SINHALA_SIMPLIFICATION_PROTECTED_ROOT` resolves outside the git workspace.
5. Record baseline metrics and run baseline test suites.

### WP1–WP7 — Core Engine, Rules, Detectors, and Traces
1. Freeze rule taxonomy and register rules with human technical authorship (`authoring_method`, `author_id_or_team`).
2. Establish Pydantic v2 schemas and external protected storage boundary.
3. Implement 12-category protected-span detectors and semantic guards.
4. Implement lexical and phrase substitution engines.
5. Implement sentence splitting with constrained verbatim subject recovery.
6. Implement two-stage candidate resolution (Stage 1 eligibility filtering, Stage 2 deterministic ranking).
7. Implement qualified transformation trace builder and public serialization with keyed HMACs.

### WP8 — Development Evaluation on Canonical Training Partition
1. Execute rewrite pipeline exclusively on the canonical training records.
2. Emit partition-isolated development ledgers (`train_*_ledger.jsonl`).
3. Calibrate rule parameters on training partition only.

### WP9 — Validation Partition Defect Check, Sealing, and One-Time Locked-Test
WP9 explicitly delineates validation defect handling from configuration sealing and locked-test execution:

#### WP9.1: Validation Partition Execution & Defect Detection Protocol
- The validation evaluation runs already-declared behavior against canonical validation records (`validation_*_ledger.jsonl`).
- **Permitted scope:** Identifying implementation defects, unhandled exceptions, serialization errors, or Unicode combining sequence defects in already declared behavior.
- **Explicit prohibitions:**
  - Validation must **not** be used to add validation-specific lexical rules.
  - Validation must **not** change frequency thresholds or provisional bands.
  - Validation must **not** tailor protected-span patterns or regexes to validation records.
  - Validation must **not** select, prioritize, or disable rules based on validation performance.
- **Configuration change recording schema:** Any change between provisional and final configurations must be recorded in an audit entry with:
  - `change_id`
  - `change_type`
  - `reason`
  - `affected_files`
  - `rule_inventory_changed` (`false` required)
  - `threshold_changed` (`false` required)
  - `validation_specific_pattern_added` (`false` required)

#### WP9.2: Configuration Sealing & Hash Locking
- Following validation defect verification, the configuration status is sealed to `"FROZEN_FOR_LOCKED_EVALUATION"`.
- The final configuration SHA-256 is recorded and locked.

#### WP9.3: One-Time Governed Locked-Test Execution
- The locked-test runner reads in-memory configuration bytes and verifies that in-memory byte SHA-256 matches the on-disk file hash before accessing any locked-test record.
- Locked evaluation is executed **exactly once** on canonical locked-test records (`locked_test_*_ledger.jsonl`), appending to consolidated ledgers.
- Generates an immutable execution record with execution ID, timestamps, input manifest SHA-256, configuration SHA-256, and zero post-execution modification confirmation.

### WP10 — Multi-Partition Accounting Reconciliation and Authoritative Sealing
1. Reconcile all six conservation equations across Train, Validation, Locked Test, and Consolidated partitions with strictly 0 unaccounted items.
2. Generate and verify the self-excluding documentation checksum manifest (14 deliverables = 13 documents + manifest).
3. Generate and verify the implementation manifest (29 artifacts).
4. Run negative tamper tests on all manifests.
5. Create immutable annotated tag `stage-33-complete` and push branch and tag to remote origin.

---

## 15. Automated Test Plan

The Stage 33 test suite comprises **18 test modules (32 test cases)** in `backend/tests/sinhala_simplification/`:

1. `test_stage33_rule_registry.py`: Validates unique rule IDs, human authorship fields, evidence refs, and public/protected separation.
2. `test_stage33_lexical_rules.py`: Validates allowlisted lexical substitution, morphology preservation, and rejection of frequency-only swaps.
3. `test_stage33_phrase_rules.py`: Validates longest-match-first behavior and prevents overlapping partial substitutions.
4. `test_stage33_sentence_splitting.py`: Validates punctuation reconstruction, structural completeness, and boundary preservation.
5. `test_stage33_constrained_subject_recovery.py`: Validates that subject insertion occurs only from unambiguous source spans; ambiguous recovery routes to review.
6. `test_stage33_protected_spans.py`: Validates detection of entities, numbers, dates, units, currencies, parentheticals, and technical terms across all 12 categories.
7. `test_stage33_negation_and_modality.py`: Validates that negation markers and modal/conditional scopes are never altered or dropped.
8. `test_stage33_two_stage_candidate_resolution.py`: Validates that blocked candidates are filtered out before ranking and never participate in ranking.
9. `test_stage33_composed_rule_safety.py`: Validates atomic single-rule policy (`len(candidate.applied_rule_ids) == 1`) and verifies composite candidate rejection.
10. `test_stage33_transformation_traces.py`: Validates trace mappings, mapping status enums, and `mapping_exact` flags.
11. `test_stage33_determinism.py`: Validates byte-for-byte reproducibility across repeated pipeline runs.
12. `test_stage33_partition_isolation.py`: Validates dynamic loading from Stage 31 manifest, fail-closed handling of count mismatches, and zero cross-partition data leakage.
13. `test_stage33_corpus_view_and_denominators.py`: Validates that the 150-record canonical analytical view governs evaluation metrics.
14. `test_stage33_rights_and_protected_payloads.py`: Validates external protected storage boundary, source hash verification, and zero text leakage.
15. `test_stage33_public_export_safety.py`: Validates versioned domain-separated keyed HMACs and confirms absence of raw text hashes in git worktree.
16. `test_stage33_accounting.py`: Validates that all six conservation equations hold with exactly 0 unaccounted items.
17. `test_stage33_end_to_end.py`: Comprehensive pipeline tests from raw request to governed output and audit traces.
18. `test_stage33_entity_number_preservation.py`: Dedicated adversarial regression suite for numeric precision, unit binding, and entity boundary preservation.

---

## 16. Required Deliverables and Manifest Accounting

Stage 33 mandates a strict documentation and implementation delivery contract:

### 16.1 Documentation Deliverables Contract (15 Deliverables)

The documentation deliverable package consists of **15 deliverables = 14 manifest-controlled documents + 1 self-excluding checksum manifest**:

1. `docs/stage33_implementation_plan.md`: Reconstructed pre-execution baseline specification.
2. `docs/stage33_rule_governance_and_scope.md`: Rule governance, lifecycle, authoring standards, and authority boundaries.
3. `docs/stage33_schema_and_trace_contract.md`: Pydantic data schemas, terminal status enums, and trace mapping contracts.
4. `docs/stage33_meaning_preservation_policy.md`: Specifications for the 12 protected-span categories and semantic guards.
5. `docs/stage33_lexical_and_phrase_rules.md`: Allowlisted lexical substitutions, phrase patterns, and morphology constraints.
6. `docs/stage33_sentence_and_syntactic_rules.md`: Sentence-splitting grammar, punctuation reconstruction, and constrained subject recovery.
7. `docs/stage33_candidate_selection_and_fallback.md`: Two-stage candidate resolution (filtering then ranking) and fallback routing.
8. `docs/stage33_development_evaluation_report.md`: Empirical evaluation report on canonical training partition records.
9. `docs/stage33_locked_evaluation_report.md`: Execution report on canonical locked-test partition records.
10. `docs/stage33_error_analysis.md`: Analysis of guard-blocked candidates, fallback dispositions, and review triggers.
11. `docs/stage33_accounting_summary.md`: Multi-partition master reconciliation table across all 6 levels.
12. `docs/stage33_reproducibility_record.json`: Machine-readable execution parameters, environment state, and verification hashes.
13. `docs/stage33_completion_record.md`: Final completion record with unabridged Git, tag, and test execution evidence.
14. `docs/stage33_reconciliation_report.md`: Authoritative governance reconciliation report resolving review audit inquiries.
15. `docs/stage33_manifest.sha256`: Self-excluding SHA-256 checksum manifest over the 14 documentation deliverables above.

### 16.2 Governed Implementation Manifest

Controlled under `data/sinhala_simplification/manifests/stage33_implementation_manifest.sha256`, governing **29 implementation artifacts**:
- 16 core pipeline modules (`backend/app/sinhala_simplification/*.py`)
- 5 governed registry files (`data/sinhala_simplification/registry/*`)
- 4 evaluation and metadata outputs (`data/sinhala_simplification/evaluation/*`)
- 4 consolidated audit ledgers (`data/sinhala_simplification/ledgers/*`)

---

## 17. Formal Completion Criteria Checklist

Stage 33 completion requires satisfying every item in this pass/fail checklist:

- [ ] **Prerequisite and start-tag equality:** `stage-32-complete-v5` resolves to `7c6bb81a744305c3a59100a2c2af8fc06deb01c8`; `stage-33-start` is tagged on the identical commit.
- [ ] **Dynamic split membership verification:** Partition counts and memberships are dynamically loaded from `data/sinhala_external/corpus/corpus_metadata.json` and match `canonical_analytical_corpus.jsonl`.
- [ ] **Stage 30–32 immutability:** Zero modifications to Stage 30, Stage 31, or Stage 32 governed artifacts relative to `stage-33-start`.
- [ ] **Protected root isolation:** `SINHALA_SIMPLIFICATION_PROTECTED_ROOT` verified set, existing, writable, and strictly outside git workspace.
- [ ] **Rule authorship completeness:** All registered rules specify explicit human technical authorship (`authoring_method`, `author_id_or_team`), evidence references, and rights profile refs.
- [ ] **Atomic rule policy:** Exactly one rule per candidate (`len(candidate.applied_rule_ids) == 1`); multi-rule composition prohibited.
- [ ] **Two-stage filtering/ranking:** Candidate eligibility filtering (guards/blockers) strictly decoupled from deterministic candidate ranking.
- [ ] **Zero selected unmapped traces:** Candidates containing unmapped elements prohibited from selection; selected rewrites contain strictly zero unmapped elements.
- [ ] **Train-only rule development:** Rule discovery, pattern specification, and threshold calibration restricted to canonical training records.
- [ ] **Validation used only for defect detection:** Validation records evaluate already declared behavior; no rule addition, threshold tuning, or pattern tailoring permitted.
- [ ] **Final configuration frozen before locked test:** In-memory loaded configuration bytes verified against disk SHA-256 prior to accessing locked-test records.
- [ ] **Exactly one locked-test execution:** Locked-test evaluation executed exactly once with immutable audit record emitted.
- [ ] **Six-level accounting:** All six conservation equations hold with strictly zero unaccounted units across Train, Validation, Locked Test, and Consolidated partitions.
- [ ] **No public text leakage:** Public ledgers expose opaque IDs and keyed HMACs; zero restricted raw Sinhala text or raw SHA-256 hashes exposed in git worktree.
- [ ] **Test and build success:** 32/32 Stage 33 tests pass across 18 test modules; full backend test suite passes; frontend tests and production bundle pass.
- [ ] **Manifest and tamper verification:** Read-only manifest verifier confirms all 14 documentation and 29 implementation files with passing negative tamper tests.
- [ ] **Clean working tree:** `git status --short` returns exit code 0 and empty output.
- [ ] **Annotated tag and remote verification:** Historical tag `stage-33-complete` preserved; new immutable annotated tag `stage-33-complete-v2` created, pointing to final commit, and verified on remote origin.

---

## 18. Evidence Required for Authoritative Sealing

The completion record requires complete, unabridged terminal command outputs:

1. `git rev-parse HEAD`
2. `git rev-parse "stage-33-start^{commit}"`
3. `git rev-parse "stage-33-complete^{commit}"`
4. `git rev-parse "stage-33-complete-v2^{commit}"`
5. `git cat-file -t stage-33-complete-v2`
6. `git merge-base --is-ancestor "stage-32-complete-v5^{commit}" "stage-33-complete-v2^{commit}"`
7. `git status --short`
8. `git ls-remote --tags origin "stage-33-complete*"`
9. `python scripts/stage33/verify_partition_isolation.py`
10. `python scripts/stage33/verify_stage30_to_32_immutability.py`
11. `python scripts/stage33/verify_stage33_accounting.py`
12. `python scripts/stage33/verify_stage33_manifest.py`

---

## 19. Authoritative Completion Template (Pre-Execution Specification)

```text
================================================================
STAGE 33 — SINHALA CONTROLLED SIMPLIFICATION RULE ENGINE
================================================================

Stage 33:                                   <COMPLETE / REVISION_REQUIRED>
Governance accounting:                      <RECONCILED / UNRECONCILED>
Locked-test execution:                      <VERIFIED ONCE / PENDING>
Authoritative completion tag:               <SEALED / UNSEALED>
Approved for child delivery:                FALSE

Prerequisite tag:                           stage-32-complete-v5
Prerequisite commit:                        7c6bb81a744305c3a59100a2c2af8fc06deb01c8
Start tag:                                  stage-33-start
Final commit:                               <full 40-character SHA>
Historical completion tag:                  stage-33-complete
Reconciled authoritative tag:               stage-33-complete-v2

Ancestry verification:                      <PASSED / FAILED>
Stage 30–32 immutability:                   <PASSED / FAILED>
Corpus view evaluated:                      canonical_analytical_150
Verified canonical split counts:            Train: <dyn_train>, Validation: <dyn_val>, Locked Test: <dyn_test> (Total: 150)
External protected root:                    <verified outside worktree>
Rule registry:                              <count> rules, <PASSED / FAILED>
Protected rule payloads separated:          <PASSED / FAILED>
Protected-span policy:                      <PASSED (12 categories) / FAILED>
Two-stage candidate resolution:             <PASSED / FAILED>
Constrained subject recovery:               <PASSED / FAILED>
Trace classification coverage:              <percentage> (target: 100%)
Selected rewrite unmapped traces:           <count> (target: 0)
Deterministic rerun equality:                <PASSED / FAILED>
Training-only rule development:             <PASSED / FAILED>
Configuration frozen before locked test:    <PASSED / FAILED>
Locked-test executions:                     <count> (target: exactly 1)

Multi-Partition Reconciled Totals (150 inputs):
- Train-partition development accounting:   <count> / <count>
- Validation partition accounting:          <count> / <count>
- Locked-test partition accounting:         <count> / <count>
- Consolidated canonical accounting:        <count> / <count>

Terminal Dispositions:
- Draft rewrites selected:                  <count>
- Unchanged no applicable rule:             <count>
- Unchanged all candidates blocked:         <count>
- Manual review required:                   <count>
- Rejected source ineligible:               <count>
- Rejected invalid preprocessing:           <count>
- Failed internal error:                    <count> (target: 0)
- Total reconciled inputs:                  <actual>/<expected> (target: 150/150)

Conservation Equation Parity (Unaccounted across all levels):
- Level 1 (Inputs):                         <count> (target: 0)
- Level 2 (Rule attempts):                  <count> (target: 0)
- Level 3 (Candidates):                     <count> (target: 0)
- Level 4 (Operations):                     <count> (target: 0)
- Level 5 (Trace elements):                 <count> (target: 0)
- Level 6 (Export decision slots):          <count> (target: 0)

Automated Test Suites:
- Stage 33 test cases:                      <passed>/<collected> (18 test modules, 32 test cases)
- Full backend regression:                  <passed>/<collected>
- Frontend test suite:                      <passed>/<collected>
- Frontend production bundle:               <PASSED / FAILED>

Manifest Verification:
- Documentation manifest:                   <verified>/<expected>
- Implementation manifest:                  <verified>/<expected>

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
