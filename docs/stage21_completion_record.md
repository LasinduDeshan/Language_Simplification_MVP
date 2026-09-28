# Stage 21 — Stage Completion & Reconciliation Report

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Stage Name:** Stage 21 — Finalize the English NLP Preprocessing Pipeline  
**Scope:** English, Children Aged 4–8  
**Pipeline Version:** `1.0.0`  
**Source Dataset Version:** `0.2.0`  
**Schema Version:** `1.0.0`  
**Git Commit:** `34894eccd033a853833aa3196d10d046b1669668`  
**Git Tag:** `stage-21-complete`  
**Release Directory:** `data/preprocessed_features/en/source-0.2.0/pipeline-1.0.0/`  
**Status:** **STAGE 21 FORMALLY COMPLETED & RECONCILED**  

---

## 1. Executive Summary & Reproducibility Metadata

Stage 21 transforms governed raw English educational text from the Stage 20 release (`v0.2.0`) into consistent, traceable, and versioned linguistic representations for subsequent complexity classification and simplification modeling.

### 1.1 Complete Model & Pipeline Reproducibility Registry

| Resource | Version | Hash Algorithm | Full Checksum / Artifact Hash | Role & Usage |
|---|---|---|---|---|
| **`spacy`** | `3.7.5` | SHA-256 | `a4959dbbe0df1eb017c66dc2834b9d04495632870bbbeba67d9f71295b9000a6` | Primary production parsing engine runtime |
| **`en_core_web_sm`** | `3.7.1` | SHA-256 | `e7f85a492e00bd85f80b284b30852cf7f9591b540c3de0bf1737978ca3cbc5f0` | Pre-trained tok2vec, POS, tagger, dep-parser, NER |
| **`stanza`** | `1.14.0` | SHA-256 | `5a772c676d183df5a6104bc1ecff13b0ebf791da07cbcc737f1e564d95e0c5aa` | Secondary diagnostic concordance comparator |
| **`Stanza English UD`** | `1.14.0-en` | SHA-256 | `485e1358cb6bb5bc4f40f0ec50b86a877543a6d71bcf5ff52be7839ec51726a4` | Universal Dependencies reference benchmark |
| **`fastText / LID`** | `heuristic_v1` | SHA-256 | `9dfcf3312c9c7f66a87c125df9db86f562b87e224f8d975a5c689104bce3763f` | Deterministic Latin & function-word density gate |
| **`Internal Lexicon`** | `0.2.0` | SHA-256 | `75bbd12bf78bb078a6e7a0e676045585155af3961f83c3aa5e0d099b764f66e3` | Child vocabulary repository (`lexicon_repository.json`) |
| **`Pipeline Configuration`** | `1.0.0` | SHA-256 | `6dda1f6d8066335966f5fffbc917f1d5ce9200ec626816c11c29adaca0acbcb9` | Frozen Pydantic v2 `PreprocessingConfig` |

- **Documented Features:** **28 observable linguistic feature fields** defined in [`stage21_feature_dictionary.csv`](file:///c:/Users/Lasindu/Documents/GitHub/Language_Simplification_MVP/docs/stage21_feature_dictionary.csv).
- **Zero Difficulty Prediction:** Strictly observable linguistic representations extracted; 0 synthetic labels or difficulty classifications assigned.

---

## 2. Comprehensive Entity & Text Instance Reconciliation

### 2.1 Source-Item Accounting & Legacy Text Preservation
- **Cumulative Source Items Tracked:** **370**
- **Processed Source Items (Stage 20 Expansion Batches):** **300**
- **Legacy / Baseline Source Items (Stages 1–19):** **70**
- **Unaccounted Source Items:** **0**

> [!NOTE]
> **Legacy Source Text Preservation:** The 70 legacy source records were not directly processed by `SourceItemAdapter` (which processed the 300 newly authored Stage 20 expansion source items), but their source text is 100% active and preprocessed through the 210 carried simplification pairs (`pair_role = source_text`). Thus, no legacy source text is omitted from the preprocessed corpus.

### 2.2 Text Instance Extraction Accounting (Theoretical Max vs. Extracted)

| Parent Entity Type | Records Ingested | Base Expected Fields / Record | Potential Fields | Extracted Non-Empty Instances | Category Breakdown of Absent / Additional Fields | Net Absent Fields |
|---|---|---|---|---|---|---|
| **Source Items** | 300 | 1 | 300 | 300 | None (100% populated) | 0 |
| **Simplification Pairs** | 1,110 | 2 | 2,220 | 2,220 | None (100% populated: 1,110 original + 1,110 simplified) | 0 |
| **Adaptation Activities** | 192 | 2 | 384 | 377 | • Instructions extracted: 192<br>• Prompts extracted: 182 (10 absent child prompts)<br>• Optional passages extracted: 3 | 7 |
| **Lexicon Entries** | 378 | 2 | 756 | 720 | • Definitions extracted: 378 (100% populated)<br>• Example sentences extracted: 342 (36 absent examples)<br>• Missing definition fields: 0 | 36 |
| **Total** | **1,980** | — | **3,660** | **3,617** | **Mutually Exclusive Non-Overlapping Categories** | **43** |

#### Mutually Exclusive Absent Field Accounting
- **Activities lacking optional child prompt:** **10**
- **Activities containing optional reading passage:** **3**
- **Net activity field variance from base 384:** **7**
- **Lexicon entries lacking optional example sentence:** **36**
- **Lexicon entries lacking child definition:** **0**
- **Total absent optional text fields:** **43** $(3,660 - 3,617 = 43)$
- **Unaccounted text instances:** **0**

---

## 3. Zero-Loss Accounting & Processing Status

| Metric | Record Count | Percentage | Reconciliation Status |
|---|---|---|---|
| **Raw Text Instances Extracted** | **3,617** | 100.0% | `EXTRACTED` |
| **Unique Normalized Texts Processed** | **1,266** | 35.0% | `PROCESSED_DEDUPLICATED` |
| **Duplicate Text Instances (Mapped/Cached)** | **2,351** | 65.0% | `CACHED_ASSOCIATED` |
| **Parent-to-Text Associations Preserved** | **3,617** | 100.0% | `PRESERVED_MANY_TO_MANY` |
| **Primary Pipeline Success** | **3139** | 86.8% | `RECONCILED_SUCCESS` |
| **Fallback Pipeline Success** | **0** | 0.0% | `ZERO_FAILURES` |
| **Manual Review Required** | **163** | 4.5% | `RECONCILED_ROUTED_REVIEW` |
| **Skipped Locked Test Records (Mode A Isolation)** | **315** | 8.7% | `GUARDED_ISOLATION` |
| **Processing Failed** | **0** | 0.0% | `ZERO_ERRORS` |
| **Unaccounted Records** | **0** | **0.0%** | **`ZERO_LOSS_VERIFIED`** |

$$\text{Total Accounted} = 3139 \text{ (Success)} + 0 \text{ (Fallback)} + 163 \text{ (Review)} + 315 \text{ (Locked Test)} + 0 \text{ (Failed)} = \mathbf{3,617}$$

---

## 4. Locked-Test Split Isolation & Cross-Adapter Protection

To prevent direct or indirect test contamination, locked-test protection operates strictly across all four identifiers: `pair_id`, `source_item_id`, `source_group_id`, and `text_hash`.

- **Locked Test Simplification Pairs:** 135 pairs (270 text instances)
- **Locked Test Source Items (Excluded from Dev):** 45 source items (45 text instances)
- **Locked Test Source Groups Excluded from Dev:** 45 source groups
- **Total Locked Test Instances Skipped (Mode A):** **315**
- **Locked Test Manifest Contents:** Blinded identifiers and cryptographic hashes only; 0 raw text strings
- **Locked Text Hashes in Train/Validation Feature Output:** **0**
- **Cross-Adapter Locked-Test Leakage:** **0**

---

## 5. Disposition & Breakdown of the 163 Manual-Review Records

Zero processing failures occurred across the corpus. A total of 163 records (4.5%) were safely routed for manual review due to low function-word density in specialized short pedagogical phrases:

| Review Reason / Fallback Category | Count | Example Content Pattern | Disposition |
|---|---|---|---|
| `zero_english_function_words` | 143 | Isolated short phrases (*deposit drawing*, *noun labels*) | Included in Stage 21 output; **Ineligible for Stage 22 training** until review sign-off |
| `low_english_function_word_density` | 20 | Very brief multi-word instructions | Included in Stage 21 output; **Ineligible for Stage 22 training** until review sign-off |

- **Manual-review records:** 163
- **Included in Stage 21 governed output:** Yes (full audit trail & zero data loss)
- **Eligible for Stage 22 training:** **No**
- **Eligible after review resolution:** Yes
- **Review reasons documented:** Yes

---

## 6. Governed Release Manifest & Artifacts

| File | Description | SHA-256 Checksum |
|---|---|---|
| `preprocessed_records.jsonl` | Linguistic records (tokens, sentences, features, hashes) | `1f78efe18b4e701397100f75c19b42f030ddcef121b69dbc4791299b793a7a48` |
| `parent_to_text_mappings.json` | Many-to-many parent-to-text association mappings | `6573fdd80a03d8e28f062c1ec8cd70a283236d9925c9919a4324f25ec93c4495` |
| `linguistic_features.csv` | Flat tabular representation of extracted features | `2c0d97e3f6ac98fd8420a7ab6287706d3e2bddb4ade3c962a7e2a8928461a100` |
| `reconciliation_report.csv` | Governed zero-loss reconciliation audit report | `31b129ac5a8dd68b17291d1621d100000482b367e2bec3d4d0798bf03abc8a01` |
| `dataset_manifest.json` | Master release manifest with metadata and checksums | `99a51a52fc096c32014ef04234be4179363d828bb67ebe412ac693df9025cf8f` |
| `protected_test/locked_test_manifest.json` | Isolated locked-test manifest (blinded hashes only) | `73c81b977ecb93c445bcfdc55accafc80e71a5d048cb13051e78882bed03e90b` |
| `docs/stage21_spacy_stanza_comparison.md` | Inter-parser concordance evaluation report | `5ff97a0124c778a9e0b769afa412de8993cbb9f3e2c91dbdcde9e913831f5486` |
| `docs/stage21_feature_dictionary.csv` | Governed dictionary defining all 28 feature metrics | `70f48e0eb29126d2b818a61a8e0e9150286d0bf72bba06332a266f3b07078419` |

---

## 7. Stage 21 Sign-Off Checklist

- [x] Cumulative source item accounting reconciled (370 cumulative, 300 processed Stage 20 expansion, 70 baseline).
- [x] Mutually exclusive absent text instance categories verified (3,660 potential - 43 absent optional fields = 3,617 extracted).
- [x] Multi-tier locked test protection verified across `pair_id`, `source_item_id`, `source_group_id`, `text_hash` (0 leakage).
- [x] 163 manual review records categorized, reasons documented, and excluded from Stage 22 training eligibility.
- [x] Full model and pipeline reproducibility registry pinned with exact SHA-256 hashes.
- [x] All 28 test modules pass (40/40 tests) in `backend/tests/nlp_preprocessing/`.
- [x] All 224 backend tests passing with 100% green status.
- [x] Frontend build validated (`vite build` succeeded).
- [x] Checksum manifest sealed in `docs/stage21_manifest.sha256`.
