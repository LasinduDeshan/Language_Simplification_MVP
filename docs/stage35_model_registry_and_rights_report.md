# Stage 35 Model and Evaluator Registry & Rights Report

**Stage:** Stage 35 — Comparative Evaluation of Gemini, mT5, and mBART for Sinhala Simplification  
**Status:** Frozen and Sealed  
**Governance Anchor:** `stage-34-complete-v2` at `79c0f2619096869090615090b662e9ce9c8e2a7e`  
**Registry Bundle Reference:** `data/model_comparison/stage35/registry/stage35_model_registry.json`  

---

## 1. Registered Models and Conditions

| Condition ID | Family | Requested Model ID | Checkpoint Revision / Version | Upstream Licence Evidence | Identity Disposition | Approved for Execution |
|---|---|---|---|---|---|---|
| `C0_RULE_BASELINE` | Rule Engine | `sinhala_rule_engine_v1.0_stage33` | `stage-33-sealed-rule-engine` | Internal Project Software (MIT-compatible) | `IMMUTABLY_PINNED` | Yes |
| `C1_GEMINI_ZERO_SHOT` | Cloud API | `gemini-2.5-flash` | Pinned flagship API endpoint | Google APIs Terms of Service | `VERSION_METADATA_CAPTURED` | Yes |
| `C2_MT5_ZERO_SHOT` | Sequence-to-Sequence | `google/mt5-base` | `2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f` | Apache-2.0 | `IMMUTABLY_PINNED` | Yes |
| `C3_MBART_ZERO_SHOT` | Multilingual DAE | `facebook/mbart-large-50-many-to-many-mmt` | `e30b6cb8eb0d43a0b73cab73c7676b9863223a30` | MIT | `IMMUTABLY_PINNED` | Yes |

---

## 2. Licensing Qualifications and Provenance Evidence

### 2.1 General Licensing Qualification
> **Licence identification verified from the pinned upstream model-card evidence.**  
> **Independent legal review: NOT ESTABLISHED.**

All licence findings recorded in this registry and report represent technical metadata verified against upstream repository model cards and commit snapshots. No formal legal opinion or institutional intellectual property clearance is asserted.

### 2.2 Model-Specific Provenance and Licence Evidence

1. **Condition C0 (`C0_RULE_BASELINE`):**
   - Immutably pinned at Stage 33 sealed commit (`74481f4d09beeba42ccb9b9c32ff994e372af5bf`).
   - Governed under the project's internal software rights.

2. **Condition C1 (`C1_GEMINI_ZERO_SHOT`):**
   - Governed under the Google APIs Terms of Service and Google Generative AI Additional Terms of Service.
   - Terms snapshot SHA-256: `4cf29b71a251786523098eef6623bc1106e5e89a5874c83758e57f12e505872c`.
   - Access requires explicit API key authorization (`GEMINI_API_KEY`). In the current dry run, live calls were disabled, and simulated responses were emitted.

3. **Condition C2 (`C2_MT5_ZERO_SHOT`):**
   - Pinned checkpoint revision: `2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f`.
   - Pinned upstream model card README SHA-256: `f7a22cd51c2a1b0e75275f19f64b06ca3f24415b27f648f8338b88effb6700d2`.
   - Model card upstream licence: Apache-2.0.
   - Pinned weights SHA-256: `05423871b6ba409890a59a721be5b376d8591efb0df3c15d742617f6c3ebf47b`.
   - Pinned tokenizer SentencePiece model SHA-256: `941d331904e57ecf01fcf264d88e0018d4d73ac6b16e1e7f3ea704ee303e3a47`.

4. **Condition C3 (`C3_MBART_ZERO_SHOT`):**
   - Pinned checkpoint revision: `e30b6cb8eb0d43a0b73cab73c7676b9863223a30`.
   - Pinned upstream model card README SHA-256: `578e2bc78084241ce8ec8833de0fb85e1f9b1a37af49912895428617dc62636f`.
   - **Fairseq Licence Provenance Link:** The Hugging Face `facebook/mbart-large-50-many-to-many-mmt` model repository directly links to and originates from Meta AI's `fairseq` research codebase (`github.com/facebookresearch/fairseq`). The associated `fairseq/LICENSE` file (SHA-256 `52412d7bc7ce4157ea628bbaacb8829e0a9cb3c58f57f99176126bc8cf2bfc85`) specifies the MIT Licence. The Hugging Face model card explicitly documents this provenance link, and the fairseq licence is documented as associated upstream evidence governing this exact weight artifact.
   - Pinned weights SHA-256: `5b8a06fae6396e987c8d9a4f4efb7074c7280aa3f631461ffea0c15ef9876e43`.
   - Pinned tokenizer SentencePiece model SHA-256: `8c9d0840134b22f183765e7143f67858c2a3e3ef917618032742913e9a7e65b2`.

---

## 3. Registered Evaluator Suite

| Evaluator Name | Model / Logic Reference | Pinned Revision / Hash | Role / Target Construct |
|---|---|---|---|
| Multilingual Semantic Encoder | `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` | `4328cf26390c98c5e3c738b4460a05b95f4911f5` | Automated semantic similarity proxy |
| Sinhala Morphology Engine | `stage30_stage33_frozen` | Internal verified module | Grammatical agreement proxy |
| Protected Span Policy | `data/sinhala_simplification/registry/protected_span_policy.json` | Hash verified | Deterministic span preservation check |

---

## 4. Execution Mode Attestation for Dry-Run Pipeline

During the Stage 35 dry run:
- **Condition C1 (Gemini):** Used `SIMULATED_RESPONSE`. Live provider calls: `NOT EXECUTED`.
- **Condition C2 (mT5):** Used `SIMULATED_RESPONSE`. Local weight loading and inference: `NOT ESTABLISHED`.
- **Condition C3 (mBART):** Used `SIMULATED_RESPONSE`. Local weight loading and inference: `NOT ESTABLISHED`.
