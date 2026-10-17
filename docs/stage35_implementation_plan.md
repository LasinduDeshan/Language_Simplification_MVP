# Stage 35 Implementation Plan — Comparative Evaluation of Gemini, mT5, and mBART for Sinhala Simplification

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Controlled technical comparison of Gemini, mT5, and mBART for Sinhala (`si`, `si-LK`, script `Sinh`) text simplification  
**Status:** Planned — governance and model-registry review required before execution  
**Technical prerequisite:** `stage-34-complete-v2` at commit `79c0f2619096869090615090b662e9ce9c8e2a7e`  
**Stage 34 institutional governance status:** `NOT ESTABLISHED` unless authentic institutional determination from the legally identified committee is verified  
**Implementation branch:** `feature/stage35-sinhala-model-comparison`  
**Planned start tag:** `stage-35-start`  
**Planned completion tag:** `stage-35-complete`

---

## 1. Purpose

Stage 35 establishes a reproducible, contamination-controlled technical comparison of three multilingual model families for Sinhala text simplification:

1. A version-pinned Gemini text-generation endpoint.
2. A revision-pinned mT5 checkpoint.
3. A revision-pinned mBART checkpoint with explicit Sinhala support (`si_LK`).

The comparison measures technical simplification characteristics, automated meaning-preservation proxies, automated grammatical-integrity proxies, safety, reliability, latency, resource consumption, and cost under frozen conditions against the Stage 33 rule baseline. It does not approve any model for child delivery and does not establish clinical, pedagogical, or universal Sinhala linguistic validity.

### Primary Outcome

Produce an evidence-based recommendation of one of the following four governed outcomes:

```text
SELECTED_FOR_STAGE36_VALIDATION
CONDITIONALLY_SELECTED_WITH_FALLBACK
NO_MODEL_SELECTED_FROM_DRY_RUN
NO_MODEL_MEETS_MINIMUM_GATE
INSUFFICIENT_COMPARABLE_EVIDENCE
```

Selection remains an internal technical research decision. Production deployment and child delivery remain strictly prohibited.

---

## 2. Stage Boundaries

### 2.1 Included

- Verification of model cards, provisional licences, terms, Sinhala coverage, access, and revision identity.
- Explicit model-identity classification (including hosted-service volatility and reproducibility limits).
- Verification of per-source external-provider disclosure permissions and partition into primary common vs local-only denominators ($N_{\text{common}} \le 13$ on locked test).
- Frozen comparison registry for Gemini, mT5, and mBART.
- Identical governed evaluation inputs across all eligible models within the primary common denominator.
- Primary operational zero-shot evaluation across model families.
- Secondary, separately reported within-family adaptation experiments (mT5, mBART) where feasible.
- Training-only prompt, decoding, and calibration development; template hashes in Git, literal prompts in protected storage.
- One authorized locked-test run (including predetermined stability repetitions) after configuration sealing.
- Comprehensive pinning and applicability dispositioning of all evaluators, tokenizers, heuristic scripts, and reference datasets.
- Automated proxy evaluation for semantic preservation, simplification, grammaticality, lexical features, hallucination heuristics, script integrity, and safety.
- Latency, throughput, token, cost, local compute (RAM, VRAM, wall-clock), retry, and failure accounting.
- Output provenance, privacy-safe logging, protected storage, cryptographic hash sealing, and rights inheritance.
- Exploratory statistical uncertainty, paired comparisons, item-level outcomes, and bootstrap confidence intervals over $N_{\text{common}} \le 13$.
- Fail-closed recommendation and fallback decision for Stage 36.

### 2.2 Explicitly Excluded

- Child-facing deployment or unsupervised classroom delivery (`approved_for_child_delivery: false`).
- Clinical validation, diagnosis, DLD classification, or modification of Component 1 risk.
- Training on validation or locked-test records.
- Using locked-test observations to revise prompts, decoding parameters, checkpoints, thresholds, or metrics.
- Automatically copying Stage 34 human expert ratings onto newly generated Stage 35 model outputs.
- Treating BLEU, ROUGE, BERTScore, readability proxies, or LLM-as-judge scores as proof of semantic equivalence or child suitability.
- Presenting API cost and local compute resource consumption as directly equivalent monetary costs without a frozen conversion methodology.
- Fabricating human reviews, institutional ethics decisions, model versions, prices, or runtime measurements.
- Publishing licence-restricted input or output text.
- Production fallback orchestration, which belongs to Stage 36.

---

## 3. Mandatory Governance Invariants

1. **Frozen Prerequisite:** Stage 30–34 governed artifacts and historical tags remain immutable.
2. **Honest Stage 34 Status:** Stage 34 evidence remains labeled internal technical governance evidence with institutional ethics status `NOT ESTABLISHED` unless authentic institutional determination from the legally identified committee is verified.
3. **Stage 34 Label Non-Transferability:** Stage 34 expert ratings apply solely to Stage 33 rule outputs and source metadata. They must never be copied onto newly generated Stage 35 outputs.
4. **Denominator Separation & Disclosure Enclosure:** Only records legally permitted for external disclosure form the `PRIMARY_COMMON_DENOMINATOR`. Restricted local records form the `LOCAL_ONLY_SUPPLEMENTARY_DENOMINATOR` and are never sent to external APIs. In the locked test split, $N_{\text{common}} \le 13$.
5. **Operational Fairness & Asymmetry Qualification:** Cross-family comparison is strictly zero-shot (`C0`–`C3`). Adapted open-weight models (`C4`, `C5`) are secondary within-family analyses and must never be used to claim cross-family superiority without prominent qualification.
6. **Immutable Model Identity & Volatility Disclosure:** Open-weight models are pinned by repository, commit SHA, artifact hashes, tokenizer hashes, provisional licence verification, and library version. Gemini records exact model ID, timestamp, region, frozen safety threshold dictionary, and returned provider metadata. If immutable versioning is unavailable from the provider, reproducibility limits must be formally declared.
7. **Complete Evaluator Freezing & Applicability Dispositions:** Every evaluator component—including semantic encoder, perplexity/grammaticality model, tokenizers, vocabulary-band registries, heuristic detectors, morphology rules, and thresholds—must be frozen by commit SHA and content hash before evaluation, with formal applicability dispositions assigned per record.
8. **Partition Isolation:** Prompt design, fine-tuning, decoding calibration, threshold setting, and error-driven changes use training records only.
9. **Authorized Run Specification & Repetition Accounting:** The locked test is executed under a single authorized run specification. Predefined stability repetitions are multiplied explicitly into the Level 2 execution denominator; best-of-$n$ selection is strictly prohibited.
10. **Rights Inheritance & Cryptographic Storage Sealing:** Input and output artifacts inherit source restrictions. Restricted literal text, raw model outputs, and filled prompts reside strictly in external protected storage. Immutability is enforced via write-once storage and cryptographic hash verification (SHA-256) at ingest and validation, not merely OS-level read-only flags.
11. **Fail-Closed Output Handling:** Invalid Unicode, introduced `U+FFFD`, unexpected scripts, meaning-critical omissions, additions, negation changes, entity/number changes, or unsafe content route to review or rejection.
12. **Heuristic vs. Confirmed Disposition Separation:** Automated heuristics generate `REVIEW_REQUIRED_POTENTIAL_*` dispositions. Definitive `REJECTED_*` outcomes are reserved for deterministic checks (Unicode, script, protected spans) or human confirmation.
13. **No Silent Retries:** Every attempt, retry, timeout, refusal, truncation, parser failure, and empty output is retained in accounting.
14. **Exploratory Statistical Honesty:** Statistical significance tests are exploratory over $N_{\text{common}} \le 13$ units. Reporting prioritizes effect sizes, item-level tables, and bootstrap confidence intervals.
15. **Zero-Loss Accounting:** All accounting levels (Levels 1–9, plus conditional Level 10 if active) must reconcile to zero unaccounted units at sealing.
16. **No Child Approval:** Every output retains `approved_for_child_delivery: false`, `approved_for_unsupervised_child_delivery: false`, and `requires_expert_review: true`.
17. **Historical Tag Immutability:** Historical tags are never moved; corrections receive new versioned tags.

---

## 4. Human-Evaluation Pathway Governance

To prevent conflation between automated metrics and human validation, Stage 35 freezes both the execution mode and the resulting evidence status before execution:

### 4.1 Execution Mode

```text
STAGE35_HUMAN_EVALUATION_MODE:
  - AUTOMATED_TECHNICAL_ONLY (Default baseline):
      No expert judgments collected for Stage 35 outputs. Selection is preliminary, technical,
      and must be formally validated by human experts in Stage 36 prior to any child delivery.
  - NEW_BLINDED_REVIEW:
      New model outputs reviewed under a verified institutional ethics/governance extension.
      Requires model-blinded, randomized presentation, independent multi-reviewer coverage,
      adjudicator separation, and activates Level 10 human accounting.
```

### 4.2 Human Evidence Status

Recorded explicitly in all run summaries and output schemas:

```text
HUMAN_EVIDENCE_STATUS:
  - NOT_COLLECTED (default under AUTOMATED_TECHNICAL_ONLY)
  - AVAILABLE_FOR_STAGE35_OUTPUTS (only under NEW_BLINDED_REVIEW)
  - INSUFFICIENT_OR_NONCOMPARABLE
```

Under `AUTOMATED_TECHNICAL_ONLY`, all automated endpoints must strictly use automated proxy terminology (e.g., *Automated semantic-similarity proxy*, *Automated-gate pass rate*).

---

## 5. Model Registry and Comparison Conditions

### 5.1 Model Identity Dispositions

Every candidate model in the registry is assigned one of the following identity dispositions:

```text
IMMUTABLY_PINNED
VERSION_METADATA_CAPTURED
TIMESTAMP_PINNED_MUTABLE_SERVICE
IDENTITY_INSUFFICIENT_FOR_AUTHORITATIVE_COMPARISON
```

### 5.2 Candidate Registry

| Family | Candidate | Sinhala Basis | Freeze Evidence & Identity Disposition |
|---|---|---|---|
| **Gemini** | `<exact stable Gemini text-model ID verified during WP1>` | Capability verification & non-evaluation technical smoke test | Snapshot of exact model ID (verified from live API during WP1), provider metadata, SDK version, terms SHA-256, pricing snapshot, region, explicit pinned safety settings dictionary. Disposition: `VERSION_METADATA_CAPTURED` or `TIMESTAMP_PINNED_MUTABLE_SERVICE` (with reproducibility limits documented). |
| **mT5** | `google/mt5-base` | 101-language pretraining coverage includes Sinhala (`si`) | Hugging Face commit SHA, model/tokenizer weights SHA-256, provisional licence label (Apache 2.0, subject to WP1 verification), Transformers version. Disposition: `IMMUTABLY_PINNED`. |
| **mBART** | `facebook/mbart-large-50-many-to-many-mmt` (or `facebook/mbart-large-cc25`) | Pretraining & fine-tuning includes explicit `si_LK` token | Hugging Face commit SHA, model/tokenizer weights SHA-256, provisional licence label (MIT, subject to WP1 verification), Transformers version, forced BOS token configuration. Disposition: `IMMUTABLY_PINNED`. |

*Coverage vs. Competence Notice:* Pretraining language coverage confirms vocabulary and tokenization presence only. It does not establish baseline simplification competence for mT5 or mBART.

*Licence Notice:* All licence assertions are provisional until verified against official repository terms during WP1.

### 5.3 Comparison Conditions and Fairness Protocol

```text
Primary Operational Comparison (Zero-Shot across families):
  C0_RULE_BASELINE       Frozen Stage 33 rule engine
  C1_GEMINI_ZERO_SHOT    Frozen Sinhala simplification prompt, deterministic decoding, explicit pinned safety settings
  C2_MT5_ZERO_SHOT       Frozen task prefix and constrained decoding configuration
  C3_MBART_ZERO_SHOT     Frozen si_LK target language configuration and decoding

Secondary Within-Family Adaptation Analysis (Reported separately; asymmetric):
  C4_MT5_ADAPTED         Fine-tuned/adapted strictly on training partition
  C5_MBART_ADAPTED       Fine-tuned/adapted strictly on training partition
```

**C1 Safety Setting Freezing:** `C1_GEMINI_ZERO_SHOT` must NOT rely on mutable provider defaults. It must specify an explicit, pinned dictionary of thresholds across all standard harm categories (e.g., `HARM_CATEGORY_HARASSMENT`, `HARM_CATEGORY_HATE_SPEECH`, `HARM_CATEGORY_SEXUALLY_EXPLICIT`, `HARM_CATEGORY_DANGEROUS_CONTENT`) set to block medium and above or strict project research settings, recorded in `stage35_model_registry.json`.

**Asymmetry Qualification Rule:** Adapted conditions (`C4`, `C5`) represent within-family potential and must not be used to claim superiority over zero-shot Gemini (`C1`) unless equivalent adaptation is established for all families.

---

## 6. Evaluation Population and Denominator Protocol

### 6.1 Two-Tier Evaluation Population

To prevent privacy and rights violations when querying external hosted APIs, the sealed Stage 31 canonical dataset (150 records: 124 Train, 13 Validation, 13 Locked Test) is bifurcated:

1. **`PRIMARY_COMMON_DENOMINATOR`:** Records where source licences, consent terms, and data-protection policies explicitly allow third-party processor disclosure. Only this denominator is used for cross-model ranking (`C0`, `C1`, `C2`, `C3`). In the locked test split, $N_{\text{common}} \le 13$.
2. **`LOCAL_ONLY_SUPPLEMENTARY_DENOMINATOR`:** Records restricted to on-premise processing ($N_{\text{local}} = 13 - N_{\text{common}}$). Eligible for `C0`, `C2`, `C3`, `C4`, `C5`, but strictly excluded from external Gemini requests (`C1`).

### 6.2 Partition Isolation

- **Train (124 records):** Used exclusively for prompt engineering, prefix tuning, decoding search, adapter training, heuristic calibration, and failure analysis.
- **Validation (13 records):** One pre-freeze dry run for integration defect checks and gate sanity. No iterative tuning.
- **Locked Test (13 records):** One authorized execution under sealed configuration, evaluated on $N_{\text{common}} \le 13$ for cross-family comparisons.

---

## 7. Evaluator and Tooling Governance

To ensure evaluation behavior is as immutable as model checkpoints, all evaluation tooling must be frozen before locked-test execution:

### 7.1 Pinned Evaluator Inventory

| Evaluator Component | Pinned Version / Artifact | Frozen Content Hash | Purpose |
|---|---|---|---|
| Multilingual Semantic Encoder | Specific model ID & commit SHA (e.g. `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`) | Weights SHA-256 | Automated semantic-similarity proxy |
| Grammaticality / Perplexity Model | Pinned multilingual model & commit SHA | Weights SHA-256 | Automated grammaticality proxy |
| Tokenizer Libraries & Assets | Pinned library versions & sentencepiece models | File SHA-256 | Token counts, length ratios |
| Vocabulary-Band Registry | Stage 32 frozen vocabulary bands | Manifest SHA-256 | Vocabulary-band shift analysis |
| Protected-Span Extractor | Stage 31/32 deterministic rule engine | Code SHA-256 | Protected span preservation checking |
| Hallucination Heuristic Engine | Stage 35 heuristic script (v1.0) | Code SHA-256 | Flagging potential additions/hallucinations |
| Sinhala Morphology Rules | Stage 30/33 frozen morphological rule set | Rule set SHA-256 | Agreement and case checking |

### 7.2 Evaluator Applicability Dispositions

For every item and metric cell, the evaluation engine must formally assign one of the following applicability dispositions:

```text
EVALUATOR_APPLICABLE                   Metric successfully evaluated under standard conditions
EVALUATOR_FALLBACK                     Evaluated using declared secondary fallback model
EVALUATOR_INSUFFICIENT_RESOURCE        Skipped due to memory/hardware constraint (fails Level 6 if unexplained)
EVALUATOR_EXCLUDED_BY_FROZEN_RULE      Formally excluded (e.g. item length exceeds maximum context window)
```

### 7.3 Protected Prompts and Public Hashes

When filled prompts contain literal restricted corpus text:
- The filled prompt is stored exclusively in `<SINHALA_MODEL_COMPARISON_PROTECTED_ROOT>/stage35/inputs/`.
- Only the parameterized template and its SHA-256 hash are committed to Git.

---

## 8. Output Validation and Failure Taxonomy

Raw outputs pass through Stage 30 Unicode preprocessing and a Stage 35 validator without rewriting raw model responses.

### 8.1 Heuristic Findings vs. Deterministic Dispositions

Automated heuristic detectors produce `REVIEW_REQUIRED_POTENTIAL_*` dispositions. Only deterministic script/Unicode/span errors produce automatic `REJECTED_*` outcomes.

### 8.2 Terminal Dispositions

#### 8.2.1 Selected Responses (Level 5A)
```text
VALID_CHANGED_OUTPUT
VALID_UNCHANGED_OUTPUT
REVIEW_REQUIRED_SEMANTIC_RISK
REVIEW_REQUIRED_POTENTIAL_HALLUCINATION
REVIEW_REQUIRED_POTENTIAL_UNSAFE_OUTPUT
REJECTED_PROTECTED_SPAN_CHANGE
REJECTED_INVALID_UNICODE_OR_SCRIPT
REJECTED_TRUNCATION
REJECTED_EMPTY_OUTPUT
```

#### 8.2.2 Terminal Execution Failures (Level 5B)
```text
FAILED_REFUSAL
FAILED_TIMEOUT_EXHAUSTED
FAILED_RATE_LIMIT_EXHAUSTED
FAILED_PROVIDER_RUNTIME
FAILED_LOCAL_RUNTIME
FAILED_CANCELLED_OR_INTERRUPTED
```

---

## 9. Evaluation Metrics (Automated Technical Proxies)

Because Stage 34 ratings cannot be transferred, Stage 35 measures automated technical proxies:

### 9.1 Primary Automated Endpoints

1. **Critical semantic-drift proxy rate:** Unresolved negation flips, entity changes, or number mutations.
2. **Protected-span violation rate:** Mutation of sealed Stage 31/32 protected spans.
3. **Potential hallucination / addition rate:** Heuristic detection of novel named entities or predicates.
4. **Valid-output rate:** Fraction of outputs passing basic structural and script integrity.
5. **Automated semantic-similarity proxy:** Cosine similarity via the frozen multilingual encoder.
6. **Automated grammaticality proxy:** Perplexity / surface morphological agreement checks.
7. **Automated simplification proxy:** Reduction in grapheme/word length and vocabulary band shift.
8. **Automated-gate pass rate:** Fraction of outputs satisfying all minimum automated technical criteria.

### 9.2 Operational & Resource Metrics (Separately Reported)

- **API Operational Metrics:** Latency (p50, p90, p95), prompt/completion token usage, and invoiced/estimated API cost ($ USD).
- **Local Compute Metrics:** Wall-clock runtime, peak system RAM (MB), peak VRAM (MB), device/hardware specifications.
- **Rule of Non-Conflation:** API dollar cost and local compute resource consumption are reported separately and never summed without a verified, frozen cost-conversion model.

### 9.3 Statistical Posture

With $N_{\text{common}} \le 13$ locked-test items:
- All pairwise hypothesis tests (e.g., permutation, Wilcoxon, McNemar) are **exploratory**.
- Reporting prioritizes item-by-item results, effect sizes, and bootstrap 95% confidence intervals.
- Broad uncertainty intervals must be acknowledged in all conclusions.
- The actual realized sample size $N_{\text{common}}$ must be explicitly reported in all denominators.

---

## 10. Selection and Fallback Policy

### 10.1 Minimum Technical Exclusion Gates

A condition is disqualified from selection if:
- **Critical semantic-drift proxy rate $> 0$** on common denominator test set (project-defined technical exclusion threshold, not a clinically or linguistically validated safety limit);
- **Pipeline-introduced `U+FFFD` $> 0$**;
- **Unresolved protected-span violation rate $> 0$**;
- **Valid-output rate $< 90\%$**.

### 10.2 Decision Hierarchy

Eligible conditions are ranked by:
1. Meaning preservation & safety proxies.
2. Grammatical acceptability proxy.
3. Simplification benefit.
4. Operational reliability & fallback burden.
5. Latency and resource efficiency.

### 10.3 Final Stage-Level Decision

Exactly one outcome is selected from Section 1.

---

## 11. Security, Privacy, Rights, and Storage

```text
<SINHALA_MODEL_COMPARISON_PROTECTED_ROOT>/stage35/
├── inputs/
├── raw_outputs/<condition_id>/
├── traces/
├── logs/
└── quarantine/
```

- Path verified outside Git repository at startup.
- Logs contain opaque IDs and token counts only; no literal text or secrets.
- Public digests use versioned keyed HMACs.
- **Cryptographic Immutability Enforcement:** Raw outputs are saved to write-once storage and sealed with SHA-256 hashes immediately upon receipt. Any hash mismatch during evaluation triggers an immediate pipeline abort.

---

## 12. Work Packages (WP0 – WP10)

- **WP0: Prerequisite & Checkpoint Verification** — Confirm `stage-34-complete-v2` (`79c0f2619096869090615090b662e9ce9c8e2a7e`), establish honest governance status (`NOT ESTABLISHED`), verify clean tree, tag `stage-35-start`.
- **WP1: Model, Licence, Terms, and Capability Registry** — Pin exact Gemini model ID (verified from live API), pin explicit safety settings dictionary, pin mT5 and mBART commit SHAs, verify official licences, verify encoder weights and all evaluator hashes, run non-evaluation technical smoke test, freeze `stage35_model_registry.json`.
- **WP2: Dataset Bridge, Disclosure Gate, and Denominators** — Validate Stage 31 hashes, apply source rights disclosure gate, freeze `PRIMARY_COMMON_DENOMINATOR` ($N_{\text{common}} \le 13$) and `LOCAL_ONLY_SUPPLEMENTARY_DENOMINATOR`.
- **WP3: Schemas, Protected Storage, and Audit Infrastructure** — Implement Pydantic v2 schemas, initialize external protected storage, set up cryptographic hash sealing and privacy-safe audit logging.
- **WP4: Model Adapters** — Implement Gemini API adapter (metadata, usage, backoff), mT5 local inference adapter, mBART local inference adapter (`si_LK`).
- **WP5: Training-Only Prompt and Decoding Development** — Develop prompts and decoding parameters strictly on training split; commit template hashes, isolate literal filled prompts.
- **WP6: Validators, Automated Proxies, and Safety Gates** — Implement Unicode, script, protected-span, hallucination heuristic, and automated proxy metric evaluators with pinned weights and code.
- **WP7: Validation Run & Complete Configuration Freeze** — Execute single dry run on validation split, seal configuration SHA-256 and generate authorization token.
- **WP8: One Authorized Locked-Test Run** — Execute authorized locked-test run (including predetermined stability repetitions) across all eligible conditions.
- **WP9: Statistical Analysis & Governed Recommendation** — Compute automated endpoints, paired bootstrap intervals over $N_{\text{common}} \le 13$, evaluate gates, determine governed Stage 35 decision.
- **WP10: Regression, Accounting, Manifests, and Sealing** — Verify full regression suite (backend + frontend), reconcile Levels 1–9 (and Level 10 if active) with zero unaccounted units, generate and verify self-excluding documentation and implementation manifests with negative tamper tests, tag `stage-35-complete`.

---

## 13. Exact Accounting Conservation Equations

### Level 1 — Input Eligibility
$$\text{RegisteredInputs} = \text{PrimaryCommonEligible} + \text{LocalOnlyEligible} + \text{RightsBlocked} + \text{InvalidState} + \text{Unaccounted}$$

### Level 2 — Execution Initialization (Repetition-Aware)
$$\text{ExpectedExecutions} = \sum_{c \in C}\left(\text{EligibleInputs}_c \times \text{FrozenRepetitionCount}_c\right)$$
$$\text{ExpectedExecutions} = \text{ExecutionStarted} + \text{ExecutionBlockedBeforeStart} + \text{Unaccounted}$$

### Level 3 — Request Attempts
$$\text{Attempts} = \text{Succeeded} + \text{Timeout} + \text{RateLimited} + \text{Refused} + \text{InvalidRequest} + \text{CancelledOrInterrupted} + \text{ProviderFailed} + \text{LocalRuntimeFailed} + \text{Unaccounted}$$

### Level 4 — Selected Responses vs. Terminal Failures
$$\text{ExecutionStarted} = \text{ResponseSelected} + \text{TerminalExecutionFailure} + \text{Unaccounted}$$

### Level 5A — Selected Responses Dispositions
$$\begin{aligned}
\text{ResponseSelected} ={}& \text{ValidChanged} + \text{ValidUnchanged} \\
& + \text{ReviewSemanticRisk} + \text{ReviewPotentialHallucination} \\
& + \text{ReviewPotentialUnsafe} + \text{RejectedProtectedSpan} \\
& + \text{RejectedInvalidScript} + \text{RejectedTruncation} \\
& + \text{RejectedEmpty} + \text{Unaccounted}
\end{aligned}$$

### Level 5B — Terminal Failures Dispositions
$$\begin{aligned}
\text{TerminalExecutionFailure} ={}& \text{Refused} + \text{TimeoutExhausted} + \text{RateLimitExhausted} \\
& + \text{ProviderFailure} + \text{LocalRuntimeFailure} + \text{Cancelled} + \text{Unaccounted}
\end{aligned}$$

### Level 6 — Metric Cells
$$\text{ExpectedMetricCells} = \text{ResponseSelected} \times \text{FrozenMetricCount}$$
$$\text{ExpectedMetricCells} = \text{Computed} + \text{NotApplicable} + \text{CannotCompute} + \text{Missing} + \text{Unaccounted}$$
*(At sealing: unexplained $\text{Missing} = 0$.)*

### Level 7 — Operational & Resource Accounting
$$\text{Attempts} = \text{ResourceUsageRecorded} + \text{UsageUnavailableWithReason} + \text{Unaccounted}$$

### Level 8 — Statistical Comparisons
$$\text{PlannedPairwiseComparisons} = \text{Completed} + \text{NotEstimable} + \text{ExcludedByFrozenRule} + \text{Unaccounted}$$

### Level 9 — Condition Decisions & Stage Decision
$$\text{RegisteredConditions} = \text{Selected} + \text{EligibleNotSelected} + \text{IneligibleCriticalGate} + \text{InsufficientEvidence} + \text{NotExecuted} + \text{Unaccounted}$$
$$\text{Stage35FinalDecisions} = 1 \quad (\text{exactly one governed outcome selected})$$

### Conditional Level 10 — Human Review Accounting (Active Only Under `NEW_BLINDED_REVIEW`)
$$\text{ExpectedHumanAssignments} = \text{Submitted} + \text{Missing} + \text{Withdrawn} + \text{Invalidated} + \text{Unaccounted}$$
$$\text{ExpectedHumanRatings} = \text{ValidSubmittedAssignments} \times \text{FrozenHumanDimensionCount}$$
$$\text{ExpectedHumanRatings} = \text{Rated} + \text{CannotAssess} + \text{NotApplicable} + \text{Missing} + \text{Unaccounted}$$
*(If `STAGE35_HUMAN_EVALUATION_MODE == AUTOMATED_TECHNICAL_ONLY`, Level 10 is formally declared `NOT_APPLICABLE` with expected count 0.)*

**Universal Conservation Target:** $\text{Unaccounted} = 0$ across all applicable levels.

---

## 14. Comprehensive Automated Test Plan

Minimum automated tests required in backend regression suite:

1. **Prerequisite and Tag Verification:** Verify start tag points to `79c0f2619096869090615090b662e9ce9c8e2a7e` and historical tags remain immutable.
2. **Upstream Immutability:** Verify Stage 30–34 checksums and protected paths are unmodified.
3. **Provider-Disclosure Gate:** Negative test confirming disclosure-blocked items abort if routed to Gemini.
4. **Model Identity and Freeze:** Confirm open-weight commit SHAs and tokenizer hashes match registry; verify Gemini model ID is resolved and non-empty.
5. **Evaluator Tooling Immutability:** Confirm semantic encoder, perplexity model, tokenizers, vocabulary bands, and heuristic scripts match frozen hashes.
6. **Protected Prompt Isolation:** Verify literal restricted prompts never appear in repo; verify Git only contains parameterized templates and hashes.
7. **Split Contamination Prevention:** Assert zero overlap between training, validation, and locked-test IDs.
8. **Locked-Run Authorization:** Negative test confirming locked-test execution fails without sealed configuration SHA-256 and valid authorization token.
9. **Repetition Accounting Multiplier:** Verify that predetermined stability repetitions multiply properly into Level 2 expected executions.
10. **Retry and Failure Preservation:** Ensure simulated network drop retains both failed attempts and subsequent retries.
11. **Raw Output Cryptographic Sealing:** Verify raw model outputs are saved externally with matching SHA-256 digests; assert tampering fails validation.
12. **Disposition Separation (Level 4, 5A, 5B):** Verify terminal failures (timeouts, refusals) are routed to Level 5B and never counted as selected responses in Level 5A.
13. **Heuristic vs Deterministic Dispositions:** Confirm automated heuristics only output `REVIEW_REQUIRED_POTENTIAL_*` while deterministic errors output `REJECTED_*`.
14. **Metric Cell Accounting:** Verify Level 6 contains zero unexplained missing cells.
15. **Child Safety Invariants:** Assert `approved_for_child_delivery == False` on 100% of generated and evaluated records.
16. **Manifest & Negative Tamper Verification:** Self-excluding documentation and implementation manifests pass read-only verification; synthetic byte perturbation fails negative tamper test.

---

## 15. Required Documentation Deliverables

1. `docs/stage35_implementation_plan.md`
2. `docs/stage35_model_registry_and_rights_report.md`
3. `docs/stage35_dataset_partition_and_disclosure_report.md`
4. `docs/stage35_prompt_and_decoding_protocol.md`
5. `docs/stage35_output_validation_and_safety_policy.md`
6. `docs/stage35_metrics_and_statistical_analysis_plan.md`
7. `docs/stage35_development_and_validation_report.md`
8. `docs/stage35_locked_test_comparison_report.md`
9. `docs/stage35_cost_latency_and_resource_report.md`
10. `docs/stage35_error_analysis.md`
11. `docs/stage35_model_selection_and_fallback_record.md`
12. `docs/stage35_accounting_summary.md`
13. `docs/stage35_reproducibility_record.json`
14. `docs/stage35_completion_record.md`
15. `docs/stage35_manifest.sha256`

*(15 documentation deliverables = 14 manifest-controlled documents + 1 self-excluding checksum manifest)*

---

## 16. Completion Criteria

- [ ] `stage-34-complete-v2` resolves to `79c0f2619096869090615090b662e9ce9c8e2a7e`.
- [ ] Stage 34 institutional ethics status recorded honestly as `NOT ESTABLISHED`.
- [ ] Stage 34 human ratings explicitly separated from Stage 35 automated output evaluations.
- [ ] `STAGE35_HUMAN_EVALUATION_MODE` and `HUMAN_EVIDENCE_STATUS` formally recorded.
- [ ] `stage-35-start` points to the unchanged prerequisite commit.
- [ ] Primary common denominator separated from local-only denominator ($N_{\text{common}} \le 13$ on locked test); no disclosure-restricted data sent to Gemini.
- [ ] Model identities, commit SHAs, weights hashes, provisional licences, and reproducibility limits frozen in `stage35_model_registry.json`.
- [ ] Gemini safety settings explicitly pinned via frozen dictionary rather than mutable defaults.
- [ ] All evaluators (semantic encoder, perplexity model, tokenizers, vocabulary bands, heuristics) frozen by commit SHA and content hash, with applicability dispositions assigned.
- [ ] Cross-family evaluation restricted to zero-shot conditions (`C0`–`C3`); open-weight adaptations (`C4`, `C5`) qualified as secondary within-family analyses.
- [ ] Filled prompts with restricted text stored in external protected storage; template hashes in Git.
- [ ] Raw outputs sealed cryptographically with SHA-256 hashes at ingest; tampering triggers immediate failure.
- [ ] Configuration sealed prior to authorized locked-test run.
- [ ] All accounting conservation equations (Levels 1–9, plus conditional Level 10 if active) reconcile with zero unaccounted units.
- [ ] API costs and local hardware compute metrics reported in separate accounting channels.
- [ ] Statistical comparisons labeled exploratory over $N_{\text{common}} \le 13$ with bootstrap confidence intervals and effect sizes.
- [ ] Full backend regression test suite passes cleanly (`pytest backend/tests`).
- [ ] Frontend build and lint/regression checks pass cleanly (`npm run build` or equivalent).
- [ ] Dual self-excluding manifests verified read-only with passing negative tamper tests.
- [ ] Clean git working tree; new annotated tag `stage-35-complete` created.
