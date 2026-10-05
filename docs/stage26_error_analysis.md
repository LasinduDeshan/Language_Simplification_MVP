# Stage 26 — Error Analysis & Diagnostic Report

**Document Version:** 1.1.0  
**Date:** 2026-10-05  
**Authoritative Prerequisite Tag:** `stage-25-complete-v2`  

---

## 1. Diagnostic Taxonomy & Error Modes

| Error Mode ID | Category | Description | Mitigation Strategy | Enforcement Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| `ERR_ANS_LEAK` | Security / Task Boundary | Model reveals target exercise answer in instruction | Server-Side HMAC Answer Guard | Automatic reject $\rightarrow$ Fallback to `controlled_stage25` |
| `ERR_MARKDOWN_FENCE` | Structural Format | Generative model wraps output in ``` markdown fences | Controlled Surface Repair | Strip markdown delimiters & re-verify gates |
| `ERR_CASE_PREFIX` | Formatting | Lowercase sentence start or step numbering malformed | Controlled Surface Repair | Uppercase start & normalize step prefix |
| `ERR_SIMILARITY_LOW` | Meaning Preservation | Advisory semantic cosine similarity $< 0.85$ | Stage 25 12-Gate Validator | Mark disposition `manual_review_required` |
| `ERR_PROVIDER_TIMEOUT`| Provider Availability | External API latency timeout / connection error | Circuit Breaker & Backoff | Transparent fallback to `controlled_stage25` |

---

## 2. Gate Activations & Repair Statistics (Locked Test Set: $N=135$)

| Validation Gate | Invocations | Native Violations | Repaired & Recovered | Terminal Failures |
| :--- | :---: | :---: | :---: | :---: |
| `VAL_ANSWER_BOUNDARY` | 135 | 0 | 0 | 0 |
| `VAL_MARKDOWN_FENCES` | 135 | 0 | 0 | 0 |
| `VAL_STEP_NUMBERING` | 135 | 0 | 0 | 0 |
| `VAL_SEMANTIC_SIMILARITY` | 135 | 0 | 0 | 0 |
| `VAL_ACTION_PRESERVATION` | 135 | 0 | 0 | 0 |
