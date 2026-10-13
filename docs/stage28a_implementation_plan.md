# Stage 28A Implementation Plan — Preliminary English Model and Simplification Comparison

**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Language:** English  
**Target Users:** Children aged 4–8  
**Prerequisite Checkpoint:** `stage-26-complete-v5` and `stage-27-infrastructure-complete-v3` (annotated tag resolving to commit `22eb001eaed9a3dd8bcf09a1a14e4d99a840221f`)  
**Stage 27 Human-Validation Status:** Pending ethics clearance  
**Stage 28A Status:** Planned  
**Recommended Branch:** `feature/stage28-model-comparison`  
**Start Tag:** `stage-28a-start`  
**Completion Tag:** `stage-28a-complete`  
**Future Supplementary Phase:** Stage 28B — Expert-Aligned English Model Comparison  

---

## 1. Purpose & Executive Summary

Stage 28A performs a controlled, reproducible comparison of the English text simplification methods developed during Stages 24–26. It benchmarks deterministic baselines, the Stage 25 controlled engine, Gemini native generation, and the Stage 26 governed hybrid pipeline using frozen automated benchmarks.

Because Stage 27 human expert review is deferred pending institutional ethics clearance, Stage 28A operates strictly as a **preliminary automated research comparison**, not an expert-validated or child-suitability evaluation.

### Primary Objectives:
1. **Identical Input Protocol:** Compare all eligible English simplification approaches using identical evaluation inputs across both internal locked and external benchmarks.
2. **Multi-Dimensional Measurement:** Measure simplification quality, readability reduction, meaning preservation, operational reliability, latency, fallback behaviour, and estimated provider cost.
3. **Strict Generator Attribution:** Preserve strict generator attribution so fallback output is never presented as native model output.
4. **Historical Benchmark Immutability:** Maintain the immutability of Release `0.2.0`, locked test benchmarks, configurations, and previous stage results.
5. **Separation from Expert Evaluation:** Produce a frozen Stage 28A comparison package that can later be supplemented—but never overwritten—by the Stage 28B expert-aligned evaluation once genuine human review is conducted.

---

## 2. Mandatory Governance Boundary

All Stage 28A reports, code exports, and machine-readable ledgers must include the following governance metadata:

```json
{
  "evaluation_phase": "stage_28a_preliminary_automated_comparison",
  "expert_validated": false,
  "approved_for_child_delivery": false,
  "requires_expert_review": true,
  "stage27_human_validation_status": "pending",
  "release_0_3_0_used": false
}
```

### Mandatory Governance Statement:
> Stage 28A compares English simplification methods using automated metrics, frozen historical references, safety-oriented validation gates, and an external benchmark. Human expert suitability and child-delivery appropriateness have not yet been established.

### Strict Governance Prohibitions:
Stage 28A must **not**:
* Claim that automated metrics (SARI, BLEU, FKGL) establish educational or developmental child suitability for learners aged 4–8.
* Claim clinical, diagnostic, therapeutic, or DLD-treatment effectiveness.
* Use simulated Stage 27 ratings or operational mock reviews as human evidence.
* Modify Release `0.2.0`, historical locked-test references, or Stage 24–27 result artifacts.
* Generate, publish, or consume expert-reviewed Release `0.3.0` prior to genuine qualified expert sign-off.
* Tune prompts, thresholds, rules, or model parameters using locked-test results.
* Present fallback outputs as native Gemini, mT5, or mBART outputs.

---

## 3. Stage 28A and Stage 28B Separation

| Evaluation Phase | Execution Timing | Evidence Source | Permitted Conclusion |
| :--- | :--- | :--- | :--- |
| **Stage 28A** | **Current** | Release `0.2.0` historical benchmark, ASSET external benchmark, automated metrics, deterministic safety gates | Preliminary automated model comparison |
| **Stage 28B** | **Future (Post-Stage 27)** | Expert-reviewed Release `0.3.0` reference subset and genuine human ratings | Expert-aligned comparative evaluation |

> [!IMPORTANT]
> **Immutability Invariant:** Stage 28B will be executed as a separately versioned supplementary study upon completion of human expert reviews. It must never overwrite Stage 28A outputs, commits, tags, manifests, ledgers, or conclusions.

---

## 4. Systems Included in the Comparison: Registered vs. Evaluated Systems

The framework distinguishes between **registered systems** and **actively evaluated systems**:

| System ID | System Name | Execution Category | Registration & Evaluation Status |
| :---: | :--- | :--- | :--- |
| **B0** | Identity Baseline | Deterministic Reference | Registered & Evaluated (unmodified source text) |
| **B1** | Lexical Substitution | Deterministic Baseline | Registered & Evaluated (frozen Stage 24 implementation) |
| **B2** | Sentence Splitting | Deterministic Baseline | Registered & Evaluated (frozen Stage 24 implementation) |
| **B3** | Syntactic Rules | Deterministic Baseline | Registered & Evaluated (frozen Stage 24 implementation) |
| **B4** | Combined Deterministic | Deterministic Baseline | Registered & Evaluated (frozen Stage 24 implementation) |
| **B5** | Offline Deterministic Fallback | Deterministic Fallback Baseline | Registered & Evaluated under its own attribution |
| **C1** | Stage 25 Controlled Simplification | Controlled Rules Engine | Registered & Evaluated (`stage-25-complete-v2` engine) |
| **G1** | Gemini Native Simplification | Live External LLM | Registered & Evaluated (native outputs only; no fallback contamination) |
| **H1** | Stage 26 Gemini + Stage 25 Hybrid | Governed Hybrid Pipeline | Registered & Evaluated (disaggregated native/repair/fallback) |
| **T1** | mT5 Native Simplification | Local Transformer | Registered; Status: `NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS` (evaluated only if native checkpoint produces valid inference) |
| **T2** | mBART Native Simplification | Local Transformer | Registered; Status: `NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS` (evaluated only if native checkpoint produces valid inference) |

### Transformer Attribution & Status Invariant:
If local checkpoints for mT5 (`T1`) or mBART (`T2`) are unavailable or fail to produce valid native inference:
```text
native_inference_status: NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS
metrics: N/A
```
T1 and T2 remain registered in the registry for complete cataloguing, but their evaluation status is explicitly marked as `NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS`. Any fallback output invoked due to a transformer execution error must appear in a separate row with `generator_attribution: controlled_stage25`.

---

## 5. Evaluation Datasets

### 5.1 Internal Historical Locked Benchmark
* **Governing Source:** Release `0.2.0` (`data/simplification_corpus/releases/0.2.0/splits/locked_test_manifest.json`).
* **Full Historical Set:** 45 source groups $\times$ 3 support tiers = **135 evaluation items**.
* **Clean Text-Simplification Subset:** 13 source groups $\times$ 3 support tiers = **39 evaluation items** (derived from the frozen Stage 26 clean subset manifest).
* **Integrity Guarantee:** Historical item IDs, source text, references, split assignments, and cryptographic hashes remain strictly immutable.
* **Benchmark Reuse Clarification:** The Release 0.2.0 locked benchmark is a frozen historical project benchmark reused for longitudinal comparison across Stages 24–28. It is not claimed to be a previously unseen final test set in Stage 28A.
* **Reporting Protocol:** The full historical set (135 items) and clean subset (39 items) must be reported separately. The clean subset must not displace or replace full-set results.

### 5.2 ASSET External Benchmark
* **Source:** Official ASSET test split (Alva-Manchego et al., 2020) via the authorized local non-commercial research copy.
* **Volume:** **359 source groups** with 10 multi-reference simplifications per source (total 3,590 reference strings).
* **Frozen Operating Mode:** ASSET does not provide Mild/Moderate/Strong references. Stage 28A predeclares and freezes **one single operating mode for ASSET**: a fixed generic configuration (or fixed Moderate-support configuration). Tier outputs must never be mixed as though ASSET contains tier-matched references.
* **Redistribution & Rights Gate:** Raw ASSET sentences remain strictly stored locally and are Git-ignored outside public version control. Only rights-compliant aggregate statistics, evaluation metrics, non-reconstructable metadata, and hashes are published.
* **Automated Data-Protection Gate:** A dedicated unit test (`test_asset_rights_gate.py`) verifies that public release exports and committed files contain zero raw ASSET source or reference text.
* **Training Restriction:** ASSET data is strictly reserved for evaluation; no model fine-tuning may utilize ASSET content without formal rights registry updates.

### 5.3 Prohibited Evaluation Sources
* Simulated Stage 27 review submissions or synthetic consensus records.
* Unapproved web-scraped corpora (e.g. TurkCorpus, WikiLarge, Newsela, OasisSimp without license tracking).
* Stage 27 Release `0.3.0` draft records prior to authorized human execution.
* Component 3 local adaptation-test activities and fixtures as training data.

---

## 6. Fair-Comparison Protocol & Locked-Run Execution Rules

Every evaluated system must receive the identical source text and declared support-tier request (`Mild`, `Moderate`, `Strong`, or `Generic` for ASSET).

### Configuration Freeze Invariants:
The evaluation framework must record and freeze:
1. Input manifest path and SHA-256 hash.
2. Reference manifest path and SHA-256 hash.
3. Model identifiers, revisions, and dynamically discovered provider metadata (do not assume `gemini-3.5-flash-lite-preview-02-05` is the exact provider version; record actual model name returned by live discovery and actual provider metadata).
4. Prompt templates and prompt SHA-256 hashes.
5. Generation parameters (temperature, top_p, max_tokens, stop sequences).
6. Rule catalogue, vocabulary tier dictionaries, and configuration hashes.
7. Metric implementation versions (tokenizers, SacreBLEU signatures, pinned EASSE version).
8. Deterministic random seeds (`seed=42`).
9. Runtime environment (Python version, PyTorch/Numpy/Scipy versions, OS platform).
10. Operational policies (retry limits, timeouts, quota buffers, repair gates).
11. Frozen pricing snapshot: treat pricing values in the plan strictly as examples until retrieved and frozen with:
    - Exact billing surface
    - Source URL or snapshot
    - Retrieval timestamp
    - Currency and units
    - Pricing snapshot hash

### Locked-Test Execution Rules:
1. **Verification Before Run:** Complete all dry-run tests and pipeline validations on validation data prior to executing on locked sets.
2. **One-Time Frozen Run:** Execute each newly frozen Stage 28A configuration once across the benchmarks. (This reflects one controlled run of the new configuration, not the first historical project use of the reused Release 0.2.0 benchmark.)
3. **No Post-Hoc Tuning:** Never modify model weights, prompt templates, rule tables, or thresholds after inspecting locked results.
4. **No Hidden Fallbacks:** If native generation fails or is incomplete, record the run as partial or invalid. Never substitute fallback outputs into native result columns.
5. **Ledger Preservation:** Preserve every execution attempt and failure reason in the append-only ledger without deletion or overwriting.

---

## 7. Output Attribution Schema & Storage Boundaries

### 7.1 Protected vs. Public Storage Boundaries
State explicitly and enforce across all components:
* `output_text` exists only in the protected internal evaluation ledger (`data/model_comparison/stage28a/ledgers/internal_locked/` and local scratch).
* Public reports and release artifacts contain IDs, hashes, metrics, dispositions, and aggregate examples only when redistribution permits.
* ASSET public artifacts contain no source text, references, or reconstructable derived text.

### 7.2 Ledger Schema (Protected Internal Execution)
Every generation and evaluation item must be recorded in an append-only ledger conforming to the following schema:

```json
{
  "evaluation_item_id": "LOCKED-SIMP-001-MILD",
  "source_group_id": "SG-001",
  "support_level": "mild",
  "requested_system": "H1",
  "requested_model": "gemini-3.5-flash-lite",
  "resolved_model": "<dynamically_discovered_model_name>",
  "provider_model_version": "<dynamically_discovered_version_string>",
  "discovery_timestamp": "<iso_8601_discovery_timestamp>",
  "generator_attribution": "native_gemini_repaired",
  "native_output_received": true,
  "repair_used": true,
  "fallback_used": false,
  "fallback_reason": null,
  "http_status": 200,
  "attempt_count": 1,
  "latency_ms": 482.5,
  "input_tokens": 124,
  "output_tokens": 32,
  "currency": "USD",
  "pricing_source": "Google Cloud / Gemini Developer API Public Pricing",
  "pricing_snapshot_date": "2026-10-10",
  "pricing_snapshot_sha256": "<pricing_snapshot_hash>",
  "input_price_per_million_tokens": 0.075,
  "output_price_per_million_tokens": 0.30,
  "free_tier_usage": true,
  "estimated_billable_cost": 0.000019,
  "output_sha256": "<64-character-sha256-of-normalized-output>",
  "validation_status": "passed"
}
```

> [!NOTE]
> Pricing values (e.g. `$0.075` / `$0.30`) are illustrative examples until retrieved and frozen at configuration freeze with exact billing surface, snapshot URL, retrieval timestamp, and snapshot hash.

### Strict Non-Empty Invariant:
When `native_output_received = true`:
* `output_text` must be strictly non-empty.
* `output_sha256` must match the canonical 64-character SHA-256 hash of the normalized output text (never the empty string hash `e3b0c44...`).

> [!CAUTION]
> **Data Protection:** API tokens, raw Authorization headers, child identifiers, distractor answer keys, and protected hashes must never appear in output ledgers or public reports.

---

## 8. Metric Framework

### 8.1 Simplification Metrics
* **SARI Overall:** Multi-reference score against benchmark references (use "EASSE-style SARI" until numerical parity is tested and verified).
* **SARI Add:** Precision, recall, and F1-score on added n-grams.
* **SARI Keep:** Precision, recall, and F1-score on retained n-grams.
* **SARI Delete:** Deletion precision under the pinned Stage 28A EASSE-style formulation.
* **Mean Sentence BLEU-4:** Sentence-level smoothed BLEU-4 averaged across items.
* **Corpus SacreBLEU:** Benchmark corpus-level BLEU with explicit SacreBLEU signature string.
* **Readability Metrics:** Flesch-Kincaid Grade Level (FKGL) pre- and post-simplification, and FKGL grade reduction ($\Delta \text{FKGL}$).
* **Surface Metrics:** Compression ratio ($\text{length}_{\text{output}} / \text{length}_{\text{input}}$), character count, word count, and sentence count delta.

> [!NOTE]
> `Mean Sentence BLEU-4` and `Corpus SacreBLEU` must be reported in distinct columns with distinct labels. Their mathematical properties and magnitudes differ.

### 8.2 Meaning & Safety Metrics
* **Protected-Entity Preservation Rate:** Percentage of proper nouns, named entities, and subject nouns preserved.
* **Quantity & Number Preservation Rate:** Integrity of numerical values, quantities, and numerical words.
* **Negation Preservation Rate:** Integrity of logical polarity (`not`, `never`, `no`, `without`).
* **Temporal & Action Order Preservation Rate:** Preservation of temporal sequencing (`before`, `after`, `first`, `then`).
* **Spatial Relation Preservation Rate:** Preservation of spatial relations (`under`, `above`, `next to`, `inside`).
* **Answer Leakage Rate:** Zero-tolerance verification that activity distractor clues or solutions are not leaked.
* **Unsupported Information Rate:** Empirical detection of ungrounded or hallucinated factual propositions (reported as lowest observed unsupported-information rate; automated evaluation cannot prove zero hallucination).
* **Gate Dispositions:** Meaning-validation pass rate, manual-review-required rate, failed rate, and quarantined rate.

### 8.3 Operational & Efficiency Metrics (with Estimated Cost Reporting)
* **Native Delivery Rate:** Percentage of requests fulfilled by native model without fallback.
* **Controlled-Repair Rate:** Percentage of outputs adjusted by Stage 25 deterministic repair filters.
* **Safety-Gate Fallback Rate:** Percentage diverted to Stage 25 offline rules due to meaning/safety failure.
* **Provider/Quota Fallback Rate:** Percentage diverted due to HTTP timeouts, 429 quota exhaustion, or connectivity drops.
* **Latency Profile:** Mean latency, median latency, and 95th percentile (p95) latency in milliseconds.
* **Provider Cost Modeling:**
  * Treat pricing values in the plan as examples until retrieved and frozen with:
    - Exact billing surface
    - Source URL or snapshot
    - Retrieval timestamp
    - Currency and units
    - Pricing snapshot hash
  * Free tier usage accounting: tracked
  * All cost figures clearly labelled as **estimated costs** rather than exact billed charges.

### 8.4 Statistical Treatment of Metrics & Decision Protocol

* **Item-level SARI, FKGL, sentence BLEU and validation outcomes:** paired Wilcoxon signed-rank tests with matched rank-biserial correlation ($r_{\text{rb}}$) as effect size.
* **Corpus SacreBLEU:** corpus estimate plus paired bootstrap difference and 95% confidence interval across resampled complete evaluation items.
* **No paired significance test over one corpus-level scalar:** Wilcoxon signed-rank cannot operate directly on a single corpus-level SacreBLEU value.
* **Secondary Sensitivity Analysis:** Paired t-tests and Cohen's $d_z$ are reported as sensitivity checks for continuous score distributions.
* **Predefined Hypothesis Families:** Hypothesis families (e.g. SARI improvements over B0, SARI differences vs C1, FKGL grade reductions) are predefined prior to examining locked results, and Benjamini–Hochberg False Discovery Rate (FDR) adjustments are applied separately per family.
* **Accounting Transparency:** Report exact item denominators ($N$) and count of excluded zero-difference pairs ($N_{\text{zero\_diff}}$).
* **Bootstrap Confidence Intervals:** Paired stratified bootstrap 95% confidence intervals (2,000 requested iterations, minimum 1,000 valid iterations, seed 42) using complete evaluation records as sampling units. Exclude undefined replicates and track `undefined_reason_counts` rather than coercing to 0 or 1.

---

## 9. Multi-Dimensional Decision Framework

Stage 28A does not declare a single global "winner." Systems are evaluated across distinct operational and linguistic dimensions:

| Decision Dimension | Primary Evaluated Metrics |
| :--- | :--- |
| **Simplification Power** | SARI Overall, SARI Add, SARI Keep, SARI Delete |
| **Reference Proximity** | Mean Sentence BLEU-4, Corpus SacreBLEU |
| **Readability Reduction** | $\Delta \text{FKGL}$, compression ratio, syllable-count change |
| **Meaning Preservation** | Deterministic safety gates, entity/negation/number preservation rates, lowest unsupported-information rate |
| **Operational Reliability** | Native delivery rate, repair rate, fallback rate, failure rate |
| **Computational Efficiency** | p95 latency, token efficiency, estimated cost per 1,000 items |
| **Governance & Safety** | Privacy compliance, attribution accuracy, zero-leakage enforcement |

### Candidate Profile Designations:
The Stage 28A final synthesis will identify:
* **Best Automated Simplification Profile:** Highest multi-reference SARI with acceptable meaning preservation.
* **Best Automated Meaning-Preservation Profile:** Highest meaning preservation and lowest observed unsupported-information rate across deterministic safety gates.
* **Best Offline Deterministic Baseline:** Highest performing non-LLM system for resource-constrained edge environments.
* **Best Cost-Latency Profile:** Lowest estimated operational cost and sub-second p95 latency.
* **Best Governed Hybrid Candidate:** Optimal trade-off between expressive simplification and deterministic fallback safety for Stage 28B human validation.

---

## 10. Mutually Exclusive Accounting Conservation

To prevent double-counting (e.g. counting an output as both native and repaired), every evaluation item must be resolved into **exactly one mutually exclusive delivery category**:

$$\text{ExpectedItems} = \text{NativeUnmodifiedDelivered} + \text{NativeRepairedDelivered} + \text{SafetyFallbackDelivered} + \text{ProviderFallbackDelivered} + \text{Failed} + \text{NotAttempted} + \text{Unaccounted}$$

### Strict Conservation Invariant:
$$\text{Duplicates} = 0, \quad \text{MissingItems} = 0, \quad \text{Unaccounted} = 0$$

Every logical benchmark item receives exactly one final disposition in the execution ledger.

---

## 11. Proposed Backend Architecture

```text
backend/app/model_comparison/
├── __init__.py                 # Module exports and version metadata
├── schemas.py                  # Comparison configs, ledgers, metrics, schemas
├── registry.py                 # Frozen system registry (B0-H1, T1-T2) and status
├── input_repository.py         # Internal locked (135/39) and ASSET (359) benchmark loaders
├── execution_runner.py         # Uniform model execution orchestrator with retry/fallback
├── attribution.py              # Mutually exclusive delivery attribution engine
├── metric_adapter.py           # SARI (EASSE parity), BLEU, SacreBLEU, FKGL, compression
├── safety_evaluator.py         # Protected-element and deterministic validation evaluator
├── statistics.py               # Wilcoxon, rank-biserial, paired bootstrap CIs, FDR correction
├── accounting.py               # Zero-loss mutually exclusive execution reconciliation ledger
├── report_builder.py           # Markdown reports, CSV tables, reproducibility records
└── release_builder.py          # Frozen Stage 28A release bundle packager

backend/tests/model_comparison/
├── __init__.py
├── test_registry.py                    # Verify system definitions, models, statuses
├── test_input_hashes.py                # Verify locked test (135/39) and ASSET hashes
├── test_equal_input_protocol.py        # Verify identical source/tier across models
├── test_generator_attribution.py       # Verify mutually exclusive attribution categories
├── test_transformer_native_status.py   # Verify T1/T2 NOT_EVALUATED attribution
├── test_metric_protocols.py            # Verify SARI EASSE parity, FKGL, compression
├── test_bleu_separation.py             # Verify Sentence BLEU vs Corpus SacreBLEU
├── test_safety_accounting.py           # Verify entity, number, negation checks
├── test_latency_and_cost_accounting.py # Verify timing, token count, cost estimation
├── test_bootstrap_statistics.py        # Verify Wilcoxon, rank-biserial, and bootstrap CIs
├── test_locked_run_freeze.py           # Verify configuration freeze enforcement
├── test_asset_rights_gate.py           # Verify zero raw ASSET strings in public export
├── test_zero_loss_accounting.py        # Verify conservation: expected == completed
└── test_stage28a_end_to_end.py         # End-to-end comparison execution pipeline test
```

---

## 12. Implementation Work Packages

```mermaid
flowchart TD
    WP0[WP0: Safety Checkpoint & Verification] --> WP1[WP1: System Registry & Attribution Framework]
    WP1 --> WP2[WP2: Evaluation Input Ingestion & Manifest Hashing]
    WP2 --> WP3[WP3: Metric Parity, Test Harness & Dry-Run Verification]
    WP3 --> WP4[WP4: Development Evaluation & Configuration Freeze]
    WP4 --> WP5[WP5: Internal Locked Evaluation 135 full & 39 clean]
    WP4 --> WP6[WP6: ASSET External Benchmark Evaluation 359 items]
    WP5 --> WP7[WP7: Statistical Analysis & Error Analysis]
    WP6 --> WP7
    WP7 --> WP8[WP8: Zero-Loss Accounting & Documentation]
    WP8 --> WP9[WP9: Verification, Sealing & Checkpoint Tagging]
```

### WP0 — Safety Checkpoint & Environment Setup
1. Verify git working tree is clean and uncommitted work is resolved.
2. Confirm prerequisite checkpoint tags: `stage-26-complete-v5` and `stage-27-infrastructure-complete-v3` (annotated tag resolving to commit `22eb001eaed9a3dd8bcf09a1a14e4d99a840221f`).
3. Create branch `feature/stage28-model-comparison` from the verified prerequisite commit, then create annotated tag `stage-28a-start` at that clean baseline commit.
4. Verify SHA-256 integrity of Release `0.2.0`, Stage 24–27 results, and local ASSET copy.
5. Verify baseline test execution: confirm all collected backend tests pass (baseline before Stage 28A: 426/426 passed) and frontend production builds cleanly.

### WP1 — Comparison Protocol & System Registry
1. Implement `backend/app/model_comparison/registry.py` and `schemas.py`.
2. Define systems B0 through B5, C1, G1 (live Gemini), H1, T1, T2 with frozen identities.
3. Implement attribution schema with mutually exclusive delivery categories and dynamic provider discovery fields (`requested_model`, `resolved_model`, `provider_model_version`, `discovery_timestamp`).
4. Register T1 (mT5) and T2 (mBART) with status `NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS` and `metrics: N/A` without fallback substitution.
5. Unit test registry schemas and attribution invariants in `test_registry.py` and `test_generator_attribution.py`.

### WP2 — Evaluation Input Ingestion & Manifest Hashing
1. Implement `input_repository.py` to ingest:
   * Internal locked full set: 135 items (45 source groups $\times$ 3 tiers).
   * Internal locked clean subset: 39 items (13 source groups $\times$ 3 tiers).
   * ASSET test split: 359 source groups with 10 references each in fixed `generic` mode.
2. Verify zero overlap between internal training items and locked benchmarks.
3. Enforce Stage 23 rights gate: verify raw ASSET sentences are loaded locally and protected from public git indexing (Git-ignored).
4. Generate `stage28a_input_manifest.json` with item IDs and cryptographic hashes.

### WP3 — Metric Parity, Test Harness & Dry-Run Verification
1. Implement `metric_adapter.py`:
   * Use "EASSE-style SARI" until parity is tested. Verify EASSE parity requiring:
     - Pinned EASSE version
     - Identical inputs and tokenization
     - Allowed numerical tolerance ($\le 1\text{e}-4$)
     - Test fixture and recorded delta
     - Implementation and configuration hashes
   * Mean Sentence BLEU-4 and Corpus SacreBLEU (strictly separated; no paired significance tests on corpus scalars).
   * Pre- and post-simplification FKGL, grade reduction, compression ratio.
2. Implement `safety_evaluator.py`:
   * Protected entity, number, negation, temporal, spatial checks.
   * Answer leakage prevention and unsupported content detection (reporting lowest observed unsupported-information rate; no zero-hallucination claim).
3. Execute non-locked dry runs on validation samples for all available systems.
4. Verify attribution tags and ensure zero leakage of confidential answer tokens.

### WP4 — Development Evaluation & Configuration Freeze
1. Evaluate candidate systems exclusively on non-locked development/validation sets.
2. Resolve any timeout, quota, or JSON parse exceptions in `execution_runner.py`.
3. Freeze all prompts, decoding parameters, validation thresholds, model revisions (resolved via live discovery), random seeds (`seed=42`), and pricing snapshot metadata.
4. Generate `stage28a_configuration_freeze.json` and compute its canonical SHA-256 hash.

### WP5 — Official Internal Locked Evaluation
1. Execute the frozen configurations once across the 135-item locked set:
   * Run deterministic systems B0–B5.
   * Run Stage 25 controlled engine C1.
   * Run live Gemini G1 and hybrid pipeline H1 with quota and retry guards.
   * Evaluate T1/T2 only if native transformer checkpoints are genuinely present.
2. Disaggregate outcomes across mutually exclusive categories (native unmodified, native repaired, safety fallback, provider fallback).
3. Compute metrics separately for:
   * Full historical locked set ($N=135$).
   * Clean text-simplification subset ($N=39$).
4. Generate `stage28a_internal_locked_comparison.csv` and `stage28a_clean_subset_comparison.csv`.

### WP6 — ASSET External Benchmark Evaluation
1. Re-verify rights gate authorization for non-commercial benchmark research.
2. Execute the frozen configuration across the 359 official ASSET test sources in fixed `generic` mode.
3. Evaluate against 10 reference simplifications per source item.
4. Record latency, token usage, retry counts, and estimated cost.
5. Generate rights-compliant aggregate report: `stage28a_asset_comparison.csv`. Verify no raw text is exposed.

### WP7 — Statistical Analysis & Error Analysis
1. Implement `statistics.py`:
   * Predefine hypothesis families prior to locked result examination.
   * Primary: Wilcoxon signed-rank test and matched rank-biserial correlation ($r_{\text{rb}}$) on item-level metrics.
   * Corpus SacreBLEU: paired bootstrap difference and 95% CI (no paired significance test over single scalar).
   * Secondary sensitivity: paired t-test and Cohen's $d_z$.
   * Benjamini-Hochberg FDR adjustments applied per hypothesis family.
   * Paired stratified bootstrap 95% confidence intervals (2,000 iterations, seed 42) excluding undefined replicates.
2. Conduct systematic error analysis:
   * Meaning shifts, catastrophic deletions, unsupported information, unchanged outputs, over-simplification.
   * Performance breakdown by support tier (`Mild`, `Moderate`, `Strong`) and input complexity.
3. Author `stage28a_statistical_analysis.md` and `stage28a_error_analysis.md`.

### WP8 — Zero-Loss Accounting & Documentation
1. Implement `accounting.py` to enforce mutually exclusive inventory conservation:
   $$\text{ExpectedItems} = \text{NativeUnmodifiedDelivered} + \text{NativeRepairedDelivered} + \text{SafetyFallbackDelivered} + \text{ProviderFallbackDelivered} + \text{Failed} + \text{NotAttempted} + \text{Unaccounted}$$
   $$\text{Duplicates} = 0, \quad \text{MissingItems} = 0, \quad \text{Unaccounted} = 0$$
2. Compile deliverables:
   * `stage28a_governance_and_scope.md`
   * `stage28a_system_registry.csv`
   * `stage28a_safety_and_validation_report.md`
   * `stage28a_latency_cost_report.csv`
   * `stage28a_accounting_summary.md`
   * `stage28a_reproducibility_record.json`
   * `stage28a_completion_record.md`

### WP9 — Verification, Sealing & Checkpoint Tagging
1. Execute Stage 28A unit and integration test suite (`tests/model_comparison/`).
2. Run full backend regression test suite and verify all collected tests pass.
3. Run frontend production build (`npm run build`).
4. Verify historical immutability: zero diff against `stage-26-complete-v5` for Release `0.2.0` files and zero diff against `stage-27-infrastructure-complete-v3` for Stage 27 agreement infrastructure.
5. Compute complete 64-character SHA-256 checksums in `stage28a_manifest.sha256`.
6. Commit all artifacts to `feature/stage28-model-comparison`.
7. Create immutable tag: `stage-28a-complete`.

---

## 13. Required Deliverables

```text
docs/
├── stage28a_implementation_plan.md          # Comprehensive implementation plan (this document)
├── stage28a_governance_and_scope.md         # Mandatory governance boundaries, disclaimers, ethics status
├── stage28a_system_registry.csv             # Evaluated models B0-H1, T1-T2 with frozen parameters
├── stage28a_metric_protocol.md              # Mathematical formulas, BLEU separation, SARI EASSE parity
├── stage28a_internal_locked_comparison.csv  # 135-item full locked test comparison matrix
├── stage28a_clean_subset_comparison.csv     # 39-item clean text-simplification subset comparison
├── stage28a_asset_comparison.csv            # 359-item external ASSET benchmark comparison (aggregate only)
├── stage28a_safety_and_validation_report.md # Protected entity, number, negation, distractor audit
├── stage28a_latency_cost_report.csv         # Latency percentiles, token usage, cost estimates
├── stage28a_statistical_analysis.md         # Wilcoxon tests, effect sizes, bootstrap CIs, FDR
├── stage28a_error_analysis.md               # Qualitative error taxonomy and tier breakdown
├── stage28a_accounting_summary.md           # Zero-loss mutually exclusive item conservation reconciliations
├── stage28a_reproducibility_record.json     # Machine-readable environments, seeds, commit hashes
├── stage28a_completion_record.md            # Final milestone sign-off and stage boundary declaration
└── stage28a_manifest.sha256                 # 64-character SHA-256 checksums of all deliverables

data/model_comparison/stage28a/
├── registry/
│   ├── system_registry.json                 # Machine-readable system registry
│   ├── input_manifest.json                  # Ingested benchmark item manifest and hashes
│   └── stage28a_configuration_freeze.json   # Frozen execution parameters, models, and prompts
├── ledgers/
│   ├── internal_locked/                     # Protected internal item-by-item execution ledgers
│   └── asset/                               # Protected ASSET ledgers (Git-ignored raw text, hashes committed)
├── results/
│   ├── internal_full_results.json           # 135-item raw metric evaluations
│   ├── internal_clean_results.json          # 39-item raw metric evaluations
│   └── asset_results.json                   # 359-item rights-compliant aggregate results
└── manifests/
    └── stage28a_release_manifest.sha256     # Complete data release checksums
```

Raw external benchmark text, API credentials, protected answers, and sensitive operational logs remain strictly outside committed release artifacts.

---

## 14. Automated Verification Commands

```powershell
# 1. Prerequisite Tag Verification
git rev-parse "stage-27-infrastructure-complete-v3^{}"

# 2. Backend Model Comparison & Regression Tests
Push-Location backend
py -3.11 -m pytest tests/model_comparison/ -v
py -3.11 -m pytest tests/model_simplification/ -v
py -3.11 -m pytest tests/baseline_simplification/ -v
py -3.11 -m pytest tests/controlled_simplification/ -v
py -3.11 -m pytest tests/datasets/expert_review/ -v
py -3.11 -m pytest tests/ -q
Pop-Location

# 3. Frontend Production Build
Push-Location frontend
npm run build
Pop-Location

# 4. Immutability Invariant Verification
git diff --exit-code stage-26-complete-v5 -- data/simplification_corpus/releases/0.2.0
git diff --exit-code stage-27-infrastructure-complete-v3 -- backend/app/datasets/expert_review/agreement.py

# 5. Checkpoint Tag Verification
git rev-parse "stage-28a-start^{}"
git rev-parse "stage-28a-complete^{}"
```

---

## 15. Stage 28A Completion Criteria

Stage 28A is complete only when all the following criteria are satisfied:

- [ ] Prerequisite tag `stage-27-infrastructure-complete-v3` verified to resolve to commit `22eb001`.
- [ ] `stage-28a-start` tag created at the clean baseline commit from which `feature/stage28-model-comparison` is branched.
- [ ] Every included system (B0–B5, C1, G1, H1, T1, T2) has a frozen identifier, revision, and attribution rule.
- [ ] Systems T1 and T2 registered with status `NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS` unless native checkpoint produces valid inference.
- [ ] All evaluated systems receive identical evaluation inputs across both internal locked and ASSET benchmarks.
- [ ] Provider model metadata and pricing parameters resolved dynamically and frozen with snapshot hashes.
- [ ] Mutually exclusive delivery categories enforced: NativeUnmodified, NativeRepaired, SafetyFallback, ProviderFallback, Failed, NotAttempted, Unaccounted.
- [ ] Output text stored exclusively in protected internal ledgers; public release exports contain zero reconstructable raw text.
- [ ] Full historical locked set ($N=135$) and clean subset ($N=39$) results are separately reported with longitudinal reuse documented.
- [ ] ASSET benchmark evaluated across all 359 test items under a single frozen operating mode (`generic`) against 10 references per source with rights restrictions enforced.
- [ ] An automated test confirms that public/committed exports contain zero raw ASSET source or reference text.
- [ ] SARI component scores (Overall, Add, Keep, EASSE-parity Delete) are reported for all systems with EASSE parity verified.
- [ ] Mean Sentence BLEU-4 and Corpus SacreBLEU are reported in separate columns.
- [ ] Meaning preservation, protected elements, latency, token usage, and estimated costs are evaluated.
- [ ] Statistical testing evaluates item-level metrics via paired Wilcoxon signed-rank tests with matched rank-biserial effect sizes, while Corpus SacreBLEU is evaluated via paired bootstrap differences and 95% CIs (no paired scalar testing).
- [ ] Predefined hypothesis families corrected via Benjamini-Hochberg FDR.
- [ ] Zero-loss execution accounting confirms `duplicates = 0`, `missing_items = 0`, and `unaccounted = 0`.
- [ ] Release `0.2.0` files, historical benchmarks, and Stage 24–27 artifacts remain strictly immutable.
- [ ] No simulated Stage 27 review data is used as human evidence.
- [ ] All outputs and reports contain the mandatory governance boundary metadata and disclaimer.
- [ ] All tests in `tests/model_comparison/` pass.
- [ ] Full backend regression test suite passes (all collected backend tests pass; baseline before Stage 28A: 426/426 passed).
- [ ] Frontend production bundle builds cleanly.
- [ ] Complete 64-character SHA-256 manifests are generated and verified.
- [ ] Working tree is clean and `stage-28a-complete` tag is created without moving prior tags.

---

## 16. Stage 28B Deferred Handover Protocol

Following the completion of Stage 28A, when Stage 27 receives institutional ethics clearance and completes genuine qualified human review:

1. **Input Ingestion:** Stage 28B will ingest the expert-reviewed and adjudicated Release `0.3.0` reference subset.
2. **Correlation Analysis:** Automated metrics (SARI, SacreBLEU, FKGL) will be correlated against qualified human expert Likert scores across meaning preservation, grammatical correctness, vocabulary simplicity, sentence simplicity, and age appropriateness.
3. **Disagreement Analysis:** Instances where automated metrics diverge from qualified expert consensus will be analyzed.
4. **Ranking Re-evaluation:** Model rankings will be evaluated using empirical human preference data.
5. **Separate Versioning:** Stage 28B will be published as a distinct, supplementary package referencing Stage 28A as an immutable historical automated baseline.

---

## 17. Final Stage Boundary Declaration

At the conclusion of Stage 28A, the project establishes that English simplification methods have been evaluated reproducibly using automated metrics and frozen benchmarks. It makes no claim of clinical suitability, therapeutic efficacy for DLD, or unsupervised child-delivery approval.

```text
Stage 28A automated comparison: COMPLETE
Stage 27 human expert validation: PENDING
Stage 28B expert-aligned comparison: DEFERRED
Child-delivery approval: FALSE
```
