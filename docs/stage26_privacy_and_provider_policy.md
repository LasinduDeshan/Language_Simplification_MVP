# Stage 26 Privacy & Provider Policy

**Stage:** Stage 26 — Pretrained Model / LLM-Based English Simplification  
**Version:** 2.1.0  
**Scope:** External LLM APIs (Gemini) and Local Transformer Inferences (mT5, mBART)  
**Status:** Approved  

---

## 1. Zero-Leakage Architecture Invariants

1. **Answer Confidentiality Guarantee:**
   - Raw answers, answer hashes, and internal answer references (`answer_boundary_ref`) are **never** transmitted over external network connections or included in external provider payloads.
   - Answer boundaries are verified locally using `HMACAnswerGuard` with a keyed local HMAC and normalized token matching.
2. **Pre-Dispatch Collision Inspection:**
   - Before external API dispatch, all `exact_preservation` tokens are checked against the protected answer boundary.
   - If an exact-preservation element overlaps an answer token, dispatch is blocked immediately, and the item is routed for authorized review.
3. **Allowlist Payload Serialization:**
   - External API payloads are constructed strictly through `ProviderPayloadSerializer` allowlisting only:
     - `text`
     - `language`
     - `target_age`
     - `support_level`
     - `content_type`
     - `response_mode`
     - `exact_preservation`
     - `prompt_instructions`
   - Child IDs, learner codes, screening risk labels, profile scores, and session logs are stripped.
4. **Attributed Fallback Guarantee:**
   - If an external provider is unavailable or fails validation, the Stage 25 deterministic engine generates the fallback output.
   - Fallback outputs are explicitly attributed to `stage25_rule_engine` and never counted as successful provider generations.
