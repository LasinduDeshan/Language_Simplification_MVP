# Stage 36 Implementation Plan — Sinhala Output Validation and Fallback Pipeline

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Sinhala (`si`, `si-LK`, script `Sinh`) output validation, risk routing, abstention, and governed fallback  
**Status:** Planned — prerequisite sealing required before execution  
**Required prerequisite:** `stage-35-complete-v7` at commit `cd86a6b0aff2d07d7d0c4f8079f10e9833b5b3d0`  
**Historical Stage 35 dry-run:** `stage-35-complete-v6` at `f222efc5919627effd62fa2b31c14f5913b6ec9e`  
**Implementation branch:** `feature/stage36-sinhala-output-validation`  
**Planned start tag:** `stage-36-start`  
**Planned completion tag:** `stage-36-complete`

---

## 1. Purpose

Stage 36 establishes a deterministic, fail-closed Sinhala output-validation and fallback pipeline. It evaluates draft simplification candidates produced by governed providers, rejects or quarantines unsafe or unverifiable outputs, and selects a traceable fallback when a candidate fails validation.

Stage 36 does not establish that Gemini, mT5, or mBART is superior. Stage 35 completed only a controlled offline dry-run; empirical cross-family comparison remains **not established**. Until a separately authorized empirical evaluation is completed, the Stage 33 controlled rule engine (`C0_RULE_BASELINE`) remains the operational fallback.

The pipeline is infrastructure for research and supervised evaluation. It does not approve content for direct or unsupervised child delivery.

### Primary outcomes

1. A provider-neutral candidate envelope for rule-engine and experimental model outputs.
2. Deterministic Unicode, language, structural, protected-span, semantic-risk, and simplification validation.
3. Explicit separation between hard rejection gates, review gates, and non-critical diagnostics.
4. A fail-closed disposition router with two-tier execution outcome and candidate disposition.
5. A deterministic fallback ladder with loop prevention and bounded attempts.
6. Complete provenance and transformation traces for every selected, rejected, reviewed, or fallback output.
7. Privacy-safe protected storage with atomic writes and post-write hash verification, public metadata boundaries, accounting across 9 levels, tests, and immutable release evidence.

---

## 2. Prerequisite Gate

Stage 36 execution must not begin until all of the following are true:

```text
stage-35-complete-v7^{commit}
= cd86a6b0aff2d07d7d0c4f8079f10e9833b5b3d0

stage-35-complete-v6^{commit}
= f222efc5919627effd62fa2b31c14f5913b6ec9e
```

Required commands:

```powershell
# 1. Fetch tags from remote origin
git fetch --tags origin

# 2. Check local tag dereference
git rev-parse "stage-35-complete-v7^{commit}"

# 3. Check remote tag dereference on origin
git ls-remote --tags origin "stage-35-complete-v7*"

# 4. Verify tag object annotation and ancestor relationship
git cat-file -t stage-35-complete-v7
git merge-base --is-ancestor "stage-35-complete-v7^{commit}" HEAD

# 5. Confirm clean working tree
git status --short
```

The start tag must be created at the unchanged prerequisite commit:

```text
stage-36-start^{commit}
= stage-35-complete-v7^{commit}
```

If `stage-35-complete-v7` does not exist, points elsewhere, lacks matching remote evidence from `git ls-remote`, is not annotated, or the working tree is not clean, WP0 must stop.

---

## 3. Stage Boundaries

### 3.1 Included

- Provider-neutral validation of Sinhala simplification candidates.
- Exact byte and decoded-Unicode round-trip integrity checks for the source and candidate independently; semantic rewriting may change candidate content only through the governed generation process.
- NFC and Stage 30 preprocessing compatibility checks without silently rewriting provider output.
- Sinhala-script, mixed-script, grapheme, token, sentence, and length diagnostics.
- Protected-span preservation across three distinct evidence categories:
  - `DECLARED_PROTECTED_SPAN`: exact source metadata or frozen rule (hard gate);
  - `DETERMINISTIC_PROTECTED_SPAN`: numbers, dates, times, quantities, units, currencies, quotations, URLs, and identifiers (hard gate);
  - `INFERRED_PROTECTED_SPAN`: named entities and domain terminology detected heuristically (conservative review gate).
- Detection of omissions, unsupported insertions, suspicious named entities, numerical drift, polarity changes, and possible hallucination.
- Technical simplification checks using the Stage 32 lexicon and Stage 33 structural features.
- Explicit no-op detection.
- Output provenance, validator versions, evidence, hashes, and trace mappings.
- Fail-closed candidate dispositions.
- Deterministic fallback to the Stage 33 rule baseline, unchanged source, or manual-review queue.
- Bounded retry and fallback-loop prevention.
- Public/protected artifact separation with full 256-bit keyed HMAC digests (`stage36-public-provenance-v1`), atomic writes, and post-write verification.
- Automated testing, accounting across 9 levels, error analysis, documentation, and immutable sealing.

### 3.2 Explicitly excluded

- Claiming a winning Gemini, mT5, or mBART model.
- Treating Stage 35 simulated outputs as empirical model evidence.
- Running a new live model comparison without a separate prospective freeze and authorization.
- Fine-tuning or training language models.
- Changing the Stage 30 normalizer, Stage 31 corpus, Stage 32 lexicon, Stage 33 rules, or Stage 34 annotations in place.
- Creating synthetic Sinhala simplification reference pairs.
- Synthetic adversarial and contract-testing fixtures are permitted exclusively for software verification. They must be labelled `technical_fixture`, excluded from linguistic-reference datasets, excluded from training, and never treated as human simplification references.
- Clinical validation, DLD diagnosis, severity classification, or screening-risk modification.
- Claiming complete semantic equivalence from automated metrics.
- Direct or unsupervised child delivery.
- Sinhala TTS/STT integration.

---

## 4. Mandatory Governance Invariants

1. **Fail closed:** uncertainty, missing evidence, validator failure, configuration mismatch, or internal error must never silently produce an accepted output.
2. **Immutable input:** the exact source text and its SHA-256 remain unchanged and separately retained.
3. **Candidate immutability:** the originally received candidate is never overwritten. Any technical canonicalization is a separate derived representation.
4. **Execution vs disposition separation:** every candidate receives an explicit `execution_outcome` (`COMPLETED` or `FAILED_INTERNAL`) and, if completed, exactly one terminal `candidate_disposition`.
5. **Hard gates dominate:** a failed critical gate cannot be offset by a high aggregate metric score.
6. **No automatic semantic-equivalence claim:** automated similarity is a risk indicator, not proof of meaning preservation.
7. **Protected-span hierarchy:** `DECLARED` and `DETERMINISTIC` protected spans enforce hard rejection; `INFERRED` spans route to conservative expert review.
8. **Numerical fidelity:** changes to numbers, dates, percentages, units, currency values, ranges, or ordered identifiers fail closed unless an allowlisted rule proves equivalence.
9. **Polarity and modality fidelity:** negation, obligation, permission, uncertainty, tense, and modal-strength changes require rejection or expert review.
10. **No provider preference:** validation thresholds apply identically to every provider family unless a documented format-specific rule is necessary.
11. **No model selection inference:** Stage 36 validation outcomes cannot be used to claim model superiority unless a separate empirical protocol authorizes that analysis.
12. **Fallback is not approval:** selecting `C0_RULE_BASELINE` or unchanged source does not make the content child-approved.
13. **Bounded execution:** retries and fallback steps have frozen maximum counts; recursive fallback is prohibited.
14. **Comprehensive rights inheritance:** every candidate inherits source-content rights, transformation-rule rights, model/artifact rights, provider-processing constraints, and export restrictions applicable to its complete lineage.
15. **Privacy:** literal protected input, output, prompts, validator evidence, and reviewer notes remain outside Git.
16. **No raw identifiers:** learner, child, reviewer, or private source identifiers must not enter logs or public artifacts.
17. **Stage 34 evidence boundary:** expert ratings may inform frozen rules only where the approved protocol permits; they are not automatically transferred to unseen outputs.
18. **Upstream immutability:** declared Stage 30–35 artifacts and historical tags remain unchanged.
19. **Child safety flags:** all records retain `approved_for_child_delivery: false` and `approved_for_unsupervised_child_delivery: false`.
20. **Corrections use new tags:** existing tags must never be moved.

---

## 5. Governance Status Contract

Every Stage 36 result must include:

```json
{
  "language": "si",
  "locale": "si-LK",
  "script": "Sinh",
  "validation_status": "draft",
  "automated_validation_status": "NOT_STARTED",
  "completed_validator_count": 0,
  "expected_validator_count": 9,
  "expert_validated_for_this_output": false,
  "research_eligible": false,
  "approved_for_child_delivery": false,
  "approved_for_unsupervised_child_delivery": false,
  "requires_expert_review": true
}
```

### Automated Validation Status Enum
- `NOT_STARTED`: Pipeline not yet invoked.
- `PARTIALLY_COMPLETED`: Halted by an early terminal hard gate (by design).
- `COMPLETED`: All applicable validators evaluated.
- `FAILED_INTERNAL`: Internal execution failure or unhandled exception.

Automated success may transition an output to `TECHNICALLY_VALIDATED_RESEARCH_CANDIDATE`, but must not change either child-delivery flag.

---

## 6. Trust and Evidence Model

Stage 36 distinguishes four evidence classes:

| Evidence class | Meaning | Permitted use |
|---|---|---|
| `AUTHORITATIVE_DETERMINISTIC` | Exact comparison, declared span, or frozen rule | Hard pass/fail gate |
| `GOVERNED_HEURISTIC` | Frozen heuristic (e.g., NER detector) | Conservative risk routing / review gate |
| `AUTOMATED_PROXY` | Statistical or learned score (e.g., embedding similarity) | Supporting diagnostic evidence only |
| `HUMAN_EXPERT_DECISION` | Output-specific review by qualified reviewer | Final research disposition within approved scope |

No `AUTOMATED_PROXY` or `GOVERNED_HEURISTIC` may override a failed `AUTHORITATIVE_DETERMINISTIC` gate.

---

## 7. Candidate Sources and Provider Status

Supported candidate origins:

```text
C0_RULE_BASELINE
C1_GEMINI_EXPERIMENTAL
C2_MT5_EXPERIMENTAL
C3_MBART_EXPERIMENTAL
OTHER_GOVERNED_EXPERIMENTAL_PROVIDER
```

At the Stage 36 baseline:

| Condition | Status |
|---|---|
| C0 rule baseline | Operational fallback candidate |
| Gemini | Experimental; empirical Stage 35 evaluation not established |
| mT5 | Experimental; real Stage 35 inference not established |
| mBART | Experimental; real Stage 35 inference not established |

The pipeline must accept a candidate only when its execution receipt identifies whether it is `REAL_PROVIDER`, `REAL_LOCAL_MODEL`, `CACHED_EMPIRICAL`, `SIMULATED`, or `RULE_ENGINE`. Simulated candidates test infrastructure only and are ineligible for empirical claims.

---

## 8. Core Data Contracts

### 8.1 Candidate Envelope

```json
{
  "candidate_id": "S36-CAND-000001",
  "request_id": "S36-REQ-000001",
  "parent_candidate_id": null,
  "fallback_depth": 0,
  "fallback_reason_code": null,
  "source_record_id": "<opaque governed id>",
  "source_text_ref": "protected://stage36/input/S36-REQ-000001.txt",
  "source_text_sha256_internal": "<64-char digest>",
  "candidate_text_ref": "protected://stage36/candidate/S36-CAND-000001.txt",
  "candidate_text_sha256_internal": "<64-char digest>",
  "provider_condition": "C0_RULE_BASELINE",
  "execution_mode": "RULE_ENGINE",
  "provider_model_id": null,
  "provider_version": null,
  "provider_terms_profile_id": "TERMS-INTERNAL-RULE-ENGINE-V1",
  "model_license_profile_id": "RIGHTS-RULE-ENGINE-S33-01",
  "rights_evidence_ref": "protected://stage36/rights/S33_RULE_ENGINE_RIGHTS.json",
  "external_processing_authorized": false,
  "execution_region": "LOCAL_WORKSPACE",
  "generation_configuration_hash": "<hash>",
  "rights_profile_refs": ["RIGHTS-CORPUS-S31-PUBLIC-01"],
  "received_at": "<ISO-8601 UTC>",
  "simulation_only": false
}
```

*Note on external processing:* `external_processing_authorized` is required to be `true` strictly for candidates that transmit data externally (e.g., C1 API). For local offline candidates (e.g., C0, local C2/C3), `false` is fully valid and expected. A missing field fails universally.

### 8.2 Protected-Span Record & Validator Finding

```json
{
  "finding_id": "S36-FIND-000001",
  "validator_id": "PROTECTED-SPAN-VALIDATOR",
  "validator_version": "1.0.0",
  "severity": "CRITICAL",
  "reason_code": "PROTECTED_NUMBER_CHANGED",
  "evidence_class": "AUTHORITATIVE_DETERMINISTIC",
  "span_category": "DETERMINISTIC_PROTECTED_SPAN",
  "source_representation": "NFC_CODEPOINTS",
  "source_spans": [{"start": 12, "end": 14}],
  "candidate_representation": "NFC_CODEPOINTS",
  "candidate_spans": [{"start": 10, "end": 12}],
  "mapping_exact": true,
  "protected_evidence_ref": "protected://stage36/evidence/S36-FIND-000001.json",
  "public_summary": "A protected numeric value changed."
}
```

Offsets are zero-based Unicode code-point half-open intervals `[start, end)` over the explicitly named text representation.

### 8.3 Validation Result

```json
{
  "validation_result_id": "S36-VAL-000001",
  "candidate_id": "S36-CAND-000001",
  "configuration_hash": "<frozen hash>",
  "execution_outcome": "COMPLETED",
  "candidate_disposition": "ACCEPTED_TECHNICAL_RESEARCH_CANDIDATE",
  "automated_validation_status": "COMPLETED",
  "completed_validator_count": 9,
  "expected_validator_count": 9,
  "critical_gate_passed": true,
  "fallback_required": false,
  "findings": [],
  "diagnostic_metrics": {},
  "selected_output_ref": "protected://stage36/selected/S36-REQ-000001.txt",
  "selected_output_origin": "C0_RULE_BASELINE",
  "approved_for_child_delivery": false,
  "requires_expert_review": true
}
```

---

## 9. Validation Pipeline Stages

The evaluation order is fixed. Hard failures ($V_0$–$V_5$) halt subsequent gate checks and designate the candidate as `PARTIALLY_COMPLETED`.

```text
V0  Schema, provenance, rights and configuration validation
 ↓
V1  Unicode serialization and round-trip integrity
 ↓
V2  Language, script and structural validation
 ↓
V3  Protected-span and numerical fidelity (Declared, Deterministic, Inferred)
 ↓
V4  Negation, modality and polarity preservation
 ↓
V5  Omission, insertion and hallucination-risk analysis
 ↓
V6  Semantic-risk proxy diagnostics
 ↓
V7  Grammaticality and fluency diagnostics
 ↓
V8  Simplification-effect and no-op analysis
 ↓
V9  Terminal disposition routing and fallback orchestration
```

### V0 — Schema, provenance, rights and configuration
- Reject missing or unknown provider identities or configuration-hash mismatch.
- Reject missing lineage rights or missing external-processing authorization where data crosses machine boundaries.
- Verify execution mode (`REAL_PROVIDER`, `REAL_LOCAL_MODEL`, `CACHED_EMPIRICAL`, `SIMULATED`, `RULE_ENGINE`).
- Flag simulated outputs as `simulation_only: true`.

### V1 — Unicode serialization and round-trip integrity
- Enforce strict UTF-8 decoding and round-trip verification without data loss.
- Reject introduced `U+FFFD`, lone surrogates, denylisted control characters, or invalid escapes.
- Preserve governed Sinhala ZWJ (`U+200D`) and ZWNJ (`U+200C`) sequences.
- Report bytes, code points, and grapheme clusters separately.
- Evaluate Stage 30 compatibility without mutating the original candidate text.

### V2 — Language, script and structure
- Confirm primary presence of Sinhala script (`\u0D80-\u0DFF`).
- Detect unsupported foreign scripts while permitting governed Sinhala–English mixed structures.
- Reject empty strings, whitespace-only content, severe truncation, or structural repetition loops.

### V3 — Protected spans and numerical fidelity
Evaluate across three distinct tiers:
1. `DECLARED_PROTECTED_SPAN`: Hard gate. Spans explicitly flagged in source annotations.
2. `DETERMINISTIC_PROTECTED_SPAN`: Hard gate. Numbers, dates, times, units, currencies, percentages, ranges, URLs, identifiers, and exact quotations.
3. `INFERRED_PROTECTED_SPAN`: Review gate. Heuristically extracted named entities; mutations trigger `MANUAL_REVIEW_REQUIRED`.

### V4 — Negation, modality and polarity
- Detect changes in Sinhala negation particles (e.g., නැත, නො, එපා).
- Detect modal shifts (obligation, possibility, permission, conditionality).
- Deterministic reversal triggers hard rejection; ambiguous shifts route to expert review.

### V5 — Omission, insertion and hallucination risk
- Align source and candidate propositions.
- Flag unsupported named entities, events, causal statements, or instructions.
- Flag substantive proposition omissions that alter core sentence semantics.

### V6 — Semantic-risk diagnostics
- Compute multilingual semantic similarity proxies (e.g., LaBSE/mDeBERTa) and phrase overlap.
- Scores serve purely as supporting diagnostic evidence and cannot override hard gates.

### V7 — Grammaticality and fluency diagnostics
- Compute morphological and structural diagnostics using Stage 30 tokenization and structural features combined with explicitly versioned Stage 36 grammar heuristics or proxy diagnostics.
- Automated scores remain non-authoritative pending output-specific expert review.

### V8 — Simplification effect and no-op analysis
- Cross-reference with Stage 32 lexicon tiers and Stage 33 structural metrics.
- Distinguish between genuine simplification, normalization-only edits, and exact no-ops (`VALID_UNCHANGED_NO_SIMPLIFICATION`).

### V9 — Terminal disposition routing and fallback
- Synthesize all findings and emit the two-tier outcome (`execution_outcome`, `candidate_disposition`).
- If rejected or review required, invoke the bounded fallback ladder.

---

## 10. Execution Outcomes, Terminal Dispositions, and Precedence

### 10.1 Execution Outcome
- `COMPLETED`: Validator pipeline executed to a determinable result.
- `FAILED_INTERNAL`: Pipeline crashed, encountered an unhandled exception, or I/O failed. Triggers fallback without a linguistic disposition.

### 10.2 Candidate Disposition Precedence (Left-to-Right)
When `execution_outcome == COMPLETED`, exactly one terminal disposition is assigned:

```text
REJECTED_CONFIGURATION_OR_PROVENANCE
→ REJECTED_INVALID_UNICODE
→ REJECTED_PROTECTED_SPAN_VIOLATION
→ REJECTED_NUMERICAL_OR_POLARITY_DRIFT
→ REJECTED_UNSUPPORTED_INSERTION
→ REJECTED_CRITICAL_SEMANTIC_RISK
→ MANUAL_REVIEW_REQUIRED
→ VALID_UNCHANGED_NO_SIMPLIFICATION
→ ACCEPTED_TECHNICAL_RESEARCH_CANDIDATE
```

---

## 11. Fallback Policy

### 11.1 Frozen Fallback Ladder

```text
Primary Candidate
  ↓ (Rejected, Review Required, or Failed Internal)
C0_RULE_BASELINE
  ↓ (Failed Validation or No Applicable Safe Rule)
UNCHANGED_SOURCE
  ↓ (Unchanged Source Unsuitable or Validation Uncertain)
MANUAL_REVIEW_QUEUE
```

### 11.2 Invariant Rules
1. A candidate receives at most one validation pass per frozen configuration.
2. Fallback candidates receive a new `candidate_id`, incremented `fallback_depth`, and explicit `parent_candidate_id` and `fallback_reason_code`.
3. `C0_RULE_BASELINE` is generated at most once per request; it cannot fall back to itself.
4. Unchanged source selection is recorded as `UNCHANGED_SOURCE_SELECTED_FOR_RESEARCH_ONLY` and is never claimed as simplified.
5. Maximum fallback depth is frozen at 3 transitions.
6. Maximum retry count is frozen at 0 (transient network retry policies excluded from deterministic pipeline).
7. Routing to manual review is a terminal queue outcome, not an automated fallback success.

### 11.3 Request-Level Final Selection Outcomes
Every registered request terminates in exactly one final outcome:
- `PRIMARY_CANDIDATE_SELECTED`
- `RULE_FALLBACK_SELECTED`
- `UNCHANGED_SOURCE_SELECTED_FOR_RESEARCH_ONLY`
- `MANUAL_REVIEW_NO_OUTPUT`
- `REJECTED_NO_OUTPUT`
- `FAILED_INTERNAL_NO_OUTPUT`

---

## 12. Protected Storage and Public Boundaries

### 12.1 Protected Storage Configuration
- Controlled via mandatory environment variable: `SINHALA_OUTPUT_VALIDATION_PROTECTED_ROOT`.
- Path must resolve outside the Git workspace; startup aborts if unset or repository-internal.
- Directory hierarchy:
  ```text
  <SINHALA_OUTPUT_VALIDATION_PROTECTED_ROOT>/stage36/
  ├── input/
  ├── candidate/
  ├── selected/
  ├── evidence/
  ├── review/
  ├── receipts/
  └── quarantine/
  ```

### 12.2 Atomic Writes, Post-Write Verification & TOCTOU Defense
- **Atomic Persistence:** Write payload to a sibling temporary file (`tempfile.NamedTemporaryFile`) on the same filesystem and execute `os.replace` to ensure atomicity.
- **Post-Write Hash Verification:** Immediately read back written bytes, compute SHA-256, and assert match against envelope hash.
- **TOCTOU & Symlink Defense:** Check for symlinks and path traversal before and after file operations. Reject operation if inode or real path changes.

### 12.3 Keyed HMAC Provenance for Public Artifacts
- Public linkage uses full 256-bit (64 hex characters) keyed HMAC digests:
  - Algorithm: HMAC-SHA-256
  - Domain: `stage36-public-provenance-v1`
  - Key ID: Defined via `STAGE36_HMAC_KEY_ID`
  - Key Rotation: Governed secret rotation policy; public logs expose only key ID and full 256-bit HMAC digest.
- Literal text, prompt text, and unkeyed hashes of short sentences are prohibited from public artifacts.

---

## 13. Logging and Audit Requirements

- **Permitted in Logs:** Opaque request/candidate IDs, provider condition, execution mode, validator IDs, reason codes, execution durations, terminal dispositions, configuration hashes, and protected storage URI references.
- **Strictly Prohibited:** Raw child/learner text, full Sinhala source/candidate sentences, API keys/credentials, and personal/reviewer names.

---

## 14. Implementation Work Packages (Resequenced)

```text
WP0    Prerequisite verification, remote evidence check, and clean start tag
WP1    Draft schemas, enums, rights contracts, and storage interfaces
WP2    Protected storage implementation, atomic writes, and audit logger
WP3    Unicode, serialization, language, and structural validators (V0–V2)
WP4    Protected-span (Declared, Deterministic, Inferred) and numerical validators (V3)
WP5    Polarity, omission, and hallucination-risk validators (V4–V5)
WP6    Semantic proxy, grammaticality, and simplification diagnostics (V6–V8)
WP7    Disposition router and bounded fallback orchestrator (V9)
WP7A   Development-fixture calibration and threshold tuning
WP7B   Prospective configuration, code, threshold, and manifest freeze
WP8    Governed final fixture evaluation using frozen configuration bundle
WP9    Integration, database-isolation, and immutability verification
WP10   Regression, accounting reconciliation, manifests, and release sealing
```

### Detailed WP Specifications

#### WP0 — Prerequisite & Clean Checkpoint
1. Verify remote evidence of `stage-35-complete-v7` at commit `cd86a6b0aff2d07d7d0c4f8079f10e9833b5b3d0` via `git ls-remote --tags origin`.
2. Ensure working tree is clean (`git status --short` is empty).
3. Create annotated tag `stage-36-start` at `stage-35-complete-v7`.
4. Create branch `feature/stage36-sinhala-output-validation`.

#### WP1 — Schemas, Enums & Configuration Contracts
1. Implement Pydantic v2 schemas for Candidate Envelope, Validator Finding, Validation Result, and Fallback Traces.
2. Define enums for `AutomatedValidationStatus`, `ExecutionOutcome`, `CandidateDisposition`, `SpanCategory`, and `EvidenceClass`.
3. Model lineage rights and terms inheritance fields.
4. Forbid extra fields (`extra="forbid"`) on all security-critical schemas.

#### WP2 — Protected Storage & Audit Layer
1. Implement external root resolution and repository-rejection checks.
2. Implement atomic file writing and post-write SHA-256 verification.
3. Implement symlink and traversal protections.
4. Implement privacy-safe audit logger and full 256-bit HMAC digest generator.

#### WP3 — Unicode, Language & Structure (V0–V2)
1. Implement V0 provenance, rights, and configuration validation.
2. Implement V1 strict UTF-8 decoding, `U+FFFD` rejection, and ZWJ/ZWNJ preservation.
3. Implement V2 Sinhala script detection, mixed-script rules, and empty/truncation guards.

#### WP4 — Protected-Span & Numerical Fidelity (V3)
1. Implement extraction for Declared, Deterministic, and Inferred spans.
2. Implement exact number, date, time, quantity, unit, currency, and URL preservation.
3. Enforce code-point half-open interval indexing `[start, end)`.

#### WP5 — Polarity, Omission & Hallucination Risk (V4–V5)
1. Implement Sinhala negation particle and modality transition detectors.
2. Implement proposition coverage and unsupported entity insertion checks.
3. Enforce hard rejection for polarity flips; route ambiguity to review.

#### WP6 — Semantic, Grammar & Simplification Diagnostics (V6–V8)
1. Implement multilingual semantic similarity proxy computing.
2. Implement Stage 30 tokenization and structural features combined with explicitly versioned Stage 36 grammar heuristics or proxy diagnostics.
3. Implement Stage 32 lexicon coverage and Stage 33 structural simplification checks.
4. Implement exact no-op detection (`VALID_UNCHANGED_NO_SIMPLIFICATION`).

#### WP7 — Disposition Router & Bounded Fallback (V9)
1. Implement two-tier outcome generator (`execution_outcome`, `candidate_disposition`).
2. Enforce frozen precedence order.
3. Implement fallback ladder with maximum depth of 3 transitions and cycle detection.
4. Link fallback candidates to parent failures with lineage reasons.

#### WP7A — Development Calibration
1. Calibrate diagnostic thresholds and span regexes against a **predeclared, versioned development-only fixture set, excluded from final governed evaluation**.
2. Assert **zero unexpected rejections on deterministic contract fixtures; linguistic validity is not established by these fixtures**.

#### WP7B — Prospective Configuration & Code Freeze
1. Seal all validator code, registry entries, thresholds, reason codes, fallback rules, and evaluator versions into `stage36_configuration.json`.
2. Compute cryptographic SHA-256 manifest of the configuration bundle.
3. Commit the freeze to Git. Record the freeze commit SHA and timestamp.
4. Verify freeze timestamp strictly predates WP8 execution.

#### WP8 — Governed Fixture Evaluation
1. Execute validation pipeline against frozen final evaluation fixtures.
2. Verify all gates fire correctly across edge cases.
3. Reconcile validator execution cells and candidate dispositions.
4. Generate `docs/stage36_fixture_evaluation_report.md` and `docs/stage36_error_analysis.md`.

#### WP9 — Integration & Database Isolation
1. Verify Stage 33 C0 rule engine outputs pass validation as expected.
2. Verify simulated provider envelopes without claiming empirical model quality.
3. Assert `backend/adaptive_learning.db` remains 100% byte-identical before and after test execution.
4. Verify declared Stage 30–35 immutability.

#### WP10 — Regression, Accounting & Sealing
1. Run full backend test suite, frontend tests, and production build.
2. Reconcile all 9 accounting levels with zero unaccounted units.
3. Generate self-excluding documentation and implementation checksum manifests:
   - Documentation manifest: `docs/stage36_manifest.sha256`
   - Implementation manifest: `data/sinhala_output_validation/manifests/stage36_implementation_manifest.sha256`
4. Run negative tamper tests on temporary copies.
5. Create annotated tag `stage-36-complete` and verify branch and tag remotely on origin.

---

## 15. Accounting Requirements (Fully Reconciled)

### Level 1 — Registered Requests
Every incoming simplification request must be accounted for in exactly one terminal outcome:
$$
\begin{aligned}
\text{RegisteredRequests} ={}& \text{PrimarySelected} \\
& + \text{RuleFallbackSelected} \\
& + \text{UnchangedResearchOnly} \\
& + \text{ManualReviewNoOutput} \\
& + \text{RejectedNoOutput} \\
& + \text{FailedInternalNoOutput} \\
& + \text{Unaccounted}
\end{aligned}
$$
*Constraint:* $\text{Unaccounted} = 0$.

### Level 2 — Candidate Origins
Total candidate envelopes evaluated across initial and fallback attempts:
$$
\begin{aligned}
\text{CandidatesReceived} ={}& \text{RuleEngine} \\
& + \text{RealProvider} \\
& + \text{RealLocalModel} \\
& + \text{CachedEmpirical} \\
& + \text{Simulated} \\
& + \text{Unaccounted}
\end{aligned}
$$
*Constraint:* $\text{Unaccounted} = 0$.

### Level 3 — Validator Execution Cells
$$
\text{ExpectedValidatorCells} = \sum_{c \in \text{Candidates}} \text{ApplicableValidators}(c)
$$
Reconciled across mutually exclusive states:
$$
\begin{aligned}
\text{ExpectedValidatorCells} ={}& \text{Completed} \\
& + \text{SkippedEarlierTerminalGate} \\
& + \text{NotApplicable} \\
& + \text{FailedInternal} \\
& + \text{Unaccounted}
\end{aligned}
$$
*Constraint:* $\text{Unaccounted} = 0$.

### Level 4 — Validator Findings
$$
\begin{aligned}
\text{TotalFindings} ={}& \text{Critical} \\
& + \text{Review} \\
& + \text{Warning} \\
& + \text{Diagnostic} \\
& + \text{Unaccounted}
\end{aligned}
$$
*Constraint:* $\text{Unaccounted} = 0$.

### Level 5 — Candidate Dispositions
Every evaluated candidate envelope with `execution_outcome == COMPLETED` receives exactly one disposition:
$$
\begin{aligned}
\text{CompletedCandidates} ={}& \text{RejectedConfigurationOrProvenance} \\
& + \text{RejectedInvalidUnicode} \\
& + \text{RejectedProtectedSpanViolation} \\
& + \text{RejectedNumericalOrPolarityDrift} \\
& + \text{RejectedUnsupportedInsertion} \\
& + \text{RejectedCriticalSemanticRisk} \\
& + \text{ManualReviewRequired} \\
& + \text{ValidUnchangedNoSimplification} \\
& + \text{AcceptedTechnicalResearchCandidate} \\
& + \text{Unaccounted}
\end{aligned}
$$
*Constraint:* $\text{Unaccounted} = 0$.

### Level 6 — Fallback Transitions
Mutually exclusive fallback transition events:
$$
\begin{aligned}
\text{FallbackTransitions} ={}& \text{ToRuleBaseline} \\
& + \text{ToUnchangedSource} \\
& + \text{ToManualReviewNoOutput} \\
& + \text{ToRejectedNoOutput} \\
& + \text{ToFailedInternalNoOutput} \\
& + \text{Unaccounted}
\end{aligned}
$$
*Constraint:* $\text{Unaccounted} = 0$.

### Level 7 — Selection vs. Abstention Reconciliation
Reconciles registered requests against delivery selections and safe abstentions:
$$
\text{RegisteredRequests} = \text{SelectedOutputs} + \text{AbstentionsNoOutput} + \text{Unaccounted}
$$
where:
$$
\text{SelectedOutputs} = \text{PrimarySelected} + \text{RuleFallbackSelected} + \text{UnchangedResearchOnly}
$$
$$
\text{AbstentionsNoOutput} = \text{ManualReviewNoOutput} + \text{RejectedNoOutput} + \text{FailedInternalNoOutput}
$$
*Constraints:* $\text{Unaccounted} = 0, \quad \text{ChildDeliveryApproved} = 0$.

### Level 8 — Span & Trace Mappings
$$
\begin{aligned}
\text{TraceElements} ={}& \text{ExactDeclaredMappings} \\
& + \text{ExactDeterministicMappings} \\
& + \text{InferredReviewMappings} \\
& + \text{UnmappedRoutedToReview} \\
& + \text{Unaccounted}
\end{aligned}
$$
*Constraint:* $\text{Unaccounted} = 0$.

### Level 9 — Export & Boundary Decisions
$$
\begin{aligned}
\text{ExportFields} ={}& \text{PublicPermitted} \\
& + \text{ProtectedInternal} \\
& + \text{SuppressedByPolicy} \\
& + \text{ReviewRequired} \\
& + \text{Unaccounted}
\end{aligned}
$$
*Constraint:* $\text{Unaccounted} = 0$.

---

## 16. Automated Test Plan

Minimum required tests:
- **Storage & Security:**
  - Protected root rejects repository-internal paths, symlink redirections, and traversal (`../`).
  - Atomic write and post-write SHA-256 verification tests.
  - Symlink replacement after path check (TOCTOU) fails closed.
  - Literal text and unkeyed short-text hashes absent from public logs and outputs.
- **Envelope & Provenance:**
  - Raw source and candidate text remain immutable.
  - Hash mismatch between envelope and payload fails closed.
  - Missing provider terms, license evidence, or processing authorization fails closed.
  - Simulated outputs cannot produce empirical quality claims.
- **Unicode & Structural Integrity:**
  - Invalid UTF-8, lone surrogates, `U+FFFD`, and prohibited control codes are rejected.
  - Governed Sinhala ZWJ/ZWNJ sequences are strictly preserved.
  - Grapheme clusters are never split across span boundaries.
  - Governed Sinhala–English mixed script text evaluated according to frozen policy.
  - Empty, truncated, or repetitive strings rejected.
- **Factual & Protected-Span Fidelity:**
  - `DECLARED` and `DETERMINISTIC` span modifications trigger hard critical failure.
  - `INFERRED` span alterations route to `MANUAL_REVIEW_REQUIRED`.
  - Numerical substitution, date shifts, and unit/currency drift trigger critical gate failures.
  - Negation reversal and modality alterations fail or route to review.
  - Unsupported entity insertions fail validation.
- **Diagnostics & Simplification:**
  - Semantic proxy scores cannot override a hard-gate failure.
  - Exact no-op receives `VALID_UNCHANGED_NO_SIMPLIFICATION`.
  - Simplification diagnostics reference Stage 32 lexicon tiers.
- **Routing & Fallback:**
  - Exactly one terminal disposition emitted per completed candidate.
  - Execution outcome `FAILED_INTERNAL` properly handles unexpected errors and routes to fallback.
  - C0 fallback invoked at most once per request; cycle detection prevents infinite loops.
  - Bounded fallback depth ($\le 3$) strictly enforced.
  - Failed candidates never appear in selected-output storage.
  - Unchanged source never labeled as simplified.
- **Governance & Regression:**
  - All 9 accounting levels report zero unaccounted units.
  - Full test execution leaves `backend/adaptive_learning.db` byte-identical (`Baseline DB touched? False`).
  - Immutability of Stage 30–35 declared artifacts holds.
  - Self-excluding documentation and implementation manifests verify read-only.
  - Negative tamper tests pass on temporary copies.

Exact commands for execution:

```powershell
Push-Location backend
python -m pytest tests/sinhala_output_validation/ -v
python -m pytest tests/ -q
Pop-Location

Push-Location frontend
npm run test -- --run
npm run build
Pop-Location

python scripts/stage36/verify_stage36_accounting.py
python scripts/stage36/verify_stage36_manifest.py
python scripts/stage36/verify_stage30_to_35_immutability.py
```

---

## 17. Evaluation Protocol & Synthetic Fixture Safeguards

- Stage 36 evaluation is a validator pipeline test, not a model benchmark.
- **Synthetic Fixture Safeguard:** Synthetic adversarial and contract-testing fixtures are permitted exclusively for software verification. They must be labelled `technical_fixture`, excluded from linguistic-reference datasets, excluded from training, and never treated as human simplification references.
- Evaluation fixture categories:
  1. Clean unchanged Sinhala.
  2. Safe governed simplification.
  3. NFC-equivalent variation.
  4. Malformed Unicode / lone surrogates / `U+FFFD`.
  5. Illegal joiners and control characters.
  6. Declared protected-name deletion.
  7. Deterministic number/date/unit/currency mutation.
  8. Inferred named-entity substitution.
  9. Negation particle deletion/insertion.
  10. Modality-strength modification.
  11. Unsupported entity insertion / hallucination.
  12. Substantive proposition omission.
  13. Mixed-script preservation vs corruption.
  14. Empty / truncated / repetitive loop output.
  15. Unsalvageable input (no valid C0 fallback).
  16. Simulated provider envelope.
- Thresholds frozen in WP7B must not be altered during WP8 governed evaluation.

---

## 18. Manual Review Requirements

Manual review remains mandatory when:
- An `INFERRED_PROTECTED_SPAN` is modified or unmapped.
- Negation or modality shifts cannot be deterministically classified.
- Semantic proxies diverge significantly from structural metrics.
- A sensitive cultural, developmental, or clinical term is introduced or altered.
- Fallback to unchanged source involves uncertain suitability.

The pipeline outputs structured review cases with rubric definitions, but must never fabricate reviewer identities, scores, timestamps, or consensus.

---

## 19. Required Documentation Deliverables

```text
14 documentation deliverables
= 13 manifest-controlled documents
+ 1 self-excluding checksum manifest
```

1. `docs/stage36_implementation_plan.md`
2. `docs/stage36_governance_and_scope.md`
3. `docs/stage36_schema_and_candidate_contract.md`
4. `docs/stage36_unicode_language_and_structure_validation.md`
5. `docs/stage36_protected_span_and_factual_fidelity_policy.md`
6. `docs/stage36_semantic_risk_and_simplification_metrics.md`
7. `docs/stage36_fallback_and_abstention_policy.md`
8. `docs/stage36_protected_storage_and_privacy_report.md`
9. `docs/stage36_fixture_evaluation_report.md`
10. `docs/stage36_error_analysis.md`
11. `docs/stage36_accounting_summary.md`
12. `docs/stage36_reproducibility_record.json`
13. `docs/stage36_completion_record.md`
14. `docs/stage36_manifest.sha256`

An independent implementation manifest (`data/sinhala_output_validation/manifests/stage36_implementation_manifest.sha256`) will govern code, schemas, validators, registries, ledgers, and scripts.

---

## 20. Completion Criteria

Stage 36 is complete only when:
- [ ] Remote evidence of `stage-35-complete-v7` verified on `origin` at `cd86a6b0aff2d07d7d0c4f8079f10e9833b5b3d0`.
- [ ] `stage-36-start` created at unchanged prerequisite commit.
- [ ] WP7B prospective freeze committed before WP8 governed evaluation begins.
- [ ] Protected storage operates outside the repository with atomic writes and post-write verification.
- [ ] Two-tier outcome schema (`execution_outcome`, `candidate_disposition`) strictly enforced.
- [ ] Three-tier protected-span policy (Declared, Deterministic, Inferred) operational.
- [ ] Bounded fallback ladder ($\le 3$ depth, no cycles) functioning.
- [ ] Failed candidates never stored as selected outputs.
- [ ] Unchanged source never claimed as simplified.
- [ ] Zero restricted text in public artifacts; HMAC provenance implemented.
- [ ] All child-delivery flags remain `false`.
- [ ] All 9 accounting levels report zero unaccounted units.
- [ ] `backend/adaptive_learning.db` verified byte-identical before and after tests.
- [ ] All Stage 36 unit/integration tests and full backend regressions pass.
- [ ] Frontend tests and production build pass.
- [ ] Declared Stage 30–35 immutability verified.
- [ ] Self-excluding documentation and implementation manifests verify read-only.
- [ ] Negative tamper tests pass on temporary copies.
- [ ] Working tree is clean.
- [ ] Annotated tag `stage-36-complete` created and verified remotely on `origin`.

---

## 21. Completion Record Template (Placeholder)

```text
================================================================
STAGE 36 — SINHALA OUTPUT VALIDATION AND FALLBACK PIPELINE
================================================================

Prerequisite tag:                           stage-35-complete-v7
Prerequisite commit:                        cd86a6b0aff2d07d7d0c4f8079f10e9833b5b3d0
Start tag:                                  stage-36-start
Freeze commit (WP7B):                       <full SHA>
Freeze timestamp:                           <ISO-8601 UTC>
Final commit (WP10):                        <full SHA>
Completion tag:                             stage-36-complete

Ancestry verification:                      PASSED / FAILED
Remote evidence verification:               PASSED / FAILED
Protected storage isolation:                PASSED / FAILED
Atomic write & post-write verification:     PASSED / FAILED
Prospective configuration freeze:           PASSED / FAILED (WP7B pre-WP8)
Candidate provenance & rights completeness: <count>/<count>
Unicode and serialization gate:             PASSED / FAILED
Language and structural gate:               PASSED / FAILED
Declared & deterministic span fidelity:     PASSED / FAILED
Inferred span review routing:               PASSED / FAILED
Numerical & unit fidelity:                  PASSED / FAILED
Negation and modality fidelity:             PASSED / FAILED
Unsupported-insertion detection:            PASSED / FAILED
Semantic-risk diagnostics:                  PASSED / FAILED
Simplification/no-op diagnostics:           PASSED / FAILED
Two-tier outcome exclusivity:               PASSED / FAILED
Fallback loop & depth prevention:           PASSED / FAILED
Primary candidate selections:               <count>
Rule fallback selections:                   <count>
Unchanged-source research selections:       <count>
Manual-review no-output outcomes:           <count>
Rejected no-output outcomes:                <count>
Failed internal no-output outcomes:         <count>
Restricted text in public artifacts:        <count>
Pipeline-introduced U+FFFD:                 <count>
Unaccounted units across Levels 1–9:        <count>
Tracked database modified by tests:         TRUE / FALSE
Stage 36 tests:                             <passed>/<collected>
Full backend tests:                         <passed>/<collected>
Frontend tests:                             <passed>/<collected>
Frontend production build:                 PASSED / FAILED
Documentation manifest:                     <verified>/<controlled>
Implementation manifest:                    <verified>/<controlled>
Read-only manifest verification:            PASSED / FAILED
Negative tamper tests:                      PASSED / FAILED
Stage 30–35 immutability:                   PASSED / FAILED

Real Gemini evaluation:                     NOT ESTABLISHED / <authorized result>
Real mT5 evaluation:                        NOT ESTABLISHED / <authorized result>
Real mBART evaluation:                      NOT ESTABLISHED / <authorized result>
Cross-family model superiority:             NOT ESTABLISHED
Complete semantic equivalence:              NOT ESTABLISHED
Approved for child delivery:                FALSE

================================================================
```

---

## 22. Recommended Execution Order

```text
WP0   Prerequisite, remote evidence, clean start tag and branch
 ↓
WP1   Draft schemas, enums, rights contracts, and storage interfaces
 ↓
WP2   Protected storage, atomic writes, and audit logger
 ↓
WP3   Unicode, serialization, language, and structural validators
 ↓
WP4   Declared, deterministic, and inferred protected-span validators
 ↓
WP5   Polarity, omission, and hallucination-risk validators
 ↓
WP6   Semantic proxy, grammaticality, and simplification diagnostics
 ↓
WP7   Disposition router and bounded fallback orchestrator
 ↓
WP7A  Development calibration with predeclared versioned development fixtures
 ↓
WP7B  Prospective configuration, code, threshold, and manifest freeze
 ↓
WP8   Governed fixture evaluation using frozen bundle
 ↓
WP9   Integration, database-isolation, and immutability verification
 ↓
WP10  Regression, accounting reconciliation, manifests, and release sealing
```

Stage 37 or any production child-delivery integration must not begin until Stage 36 is sealed and its limitations remain explicit. A technically validated output remains a research candidate until the required output-specific expert and delivery approvals are independently established.
