# Stage 15 LLM Validation and Privacy Policy

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Document Version:** 1.0.0  

---

## 1. Principles of LLM-Assisted Quality Evaluation

Large Language Models (LLMs) may provide advisory signals during dataset review, subject to strict governance constraints:

1. **Advisory Signal Only**:
   - LLM evaluations are supporting evidence, not ground truth.
   - LLM review cannot override deterministic or NLP rule failures.
   - LLM review cannot grant `approved_for_child_delivery` or `research_eligible`.

2. **Disabled by Default & Offline First**:
   - The default adapter is `DisabledLLMReviewAdapter` (returns `None`, zero network calls).
   - Test suites execute with mocked or disabled adapters by default.
   - Enabling external LLM review requires explicit opt-in via environment flag (`ENABLE_LLM_DATASET_VALIDATION=true`).

3. **Strict Privacy Safeguards**:
   - **Zero Interaction Data**: Learner interaction records, scores, or private sessions must **never** be sent to external LLM APIs.
   - **No Secrets or PII**: All prompt templates are sanitized and stripped of private metadata.
   - **Zero Input Logging**: Full prompt bodies and raw text inputs must never be logged to permanent log files.

4. **Structured Output & Deterministic Handling**:
   - Responses must adhere strictly to JSON schemas (`LLMReviewResponseV1`).
   - If an LLM returns malformed, unparseable, or inconclusive responses, the record is automatically routed to `manual_review_required` with an advisory flag.
   - Prompt template version, model identifier, and temperature ($0.0$) are recorded for reproducibility.
