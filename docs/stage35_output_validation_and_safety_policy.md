# Stage 35 Output Validation and Safety Policy

**Stage:** Stage 35 — Comparative Evaluation of Gemini, mT5, and mBART for Sinhala Simplification  
**Implementation Reference:** `backend/app/model_comparison/stage35/evaluator.py`  
**Specification Reference:** `data/model_comparison/stage35/registry/stage35_evaluator_spec.json`  

---

## 1. Output Validation Architecture

Every generated model response or simulation attempt is processed through a deterministic multi-stage validator enforcing:
1. **Script Integrity Gate:** Verifies that text contains valid Sinhala unicode code points (`U+0D80` to `U+0DFF`) and rejects replacement characters (`U+FFFD`).
2. **Protected-Span Preservation Gate:** Validates that entities (named entities, numerals, units, and dates) identified in the input are strictly preserved in the output without alteration or omission.
3. **Length and Non-Empty Gate:** Rejects empty strings and truncated sentences.
4. **Proxy Metrics Computation:** Measures automated semantic similarity, grammatical agreement, and simplification proxies.

---

## 2. Mutually Exclusive Disposition Mapping (Levels 4, 5A, 5B)

The accounting system enforces strict mutual exclusivity between responses and failures:
- **Level 4 Response Selected:** Every started attempt that produces an output payload is classified as a response and assigned exactly one Level 5A disposition. Its Level 5B terminal failure disposition is strictly `None`.
- **Level 4 Terminal Execution Failure:** Every started attempt that fails due to timeout, refusal, rate limiting, or runtime crash is assigned exactly one Level 5B disposition. Its Level 5A response disposition is strictly `None`.

```text
Level 4: Started (47) = Selected Responses (47) + Terminal Failures (0)
Level 5A: Selected Responses (47) = Valid Changed (0) + Valid Unchanged (39) + Rejected Protected Span (8)
Level 5B: Terminal Failures (0) = Refused (0) + Timeout (0) + Rate Limited (0) + Crash (0)
```

---

## 3. Child Delivery Prohibition Enactment

Under no circumstances may Stage 35 outputs be routed to child-facing interfaces or deployed unsupervised:
- `approved_for_child_delivery` is immutably set to `False` across all Stage 35 records.
- `approved_for_unsupervised_child_delivery` is immutably set to `False`.
- `requires_expert_review` is immutably set to `True`.
