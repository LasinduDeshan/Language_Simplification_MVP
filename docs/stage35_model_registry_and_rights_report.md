# Stage 35 Model Registry and Rights Report

## 1. Candidate Model Registry & Dispositions
- **Gemini Zero-Shot (C1):** Requested `gemini-2.5-flash`. Disposition: `TIMESTAMP_PINNED_MUTABLE_SERVICE`. Hosted endpoint; provider returns mutable service interface.
- **mT5-base (C2):** Revision `2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f`. Disposition: `IMMUTABLY_PINNED`.
- **mBART-50 (C3):** Revision `e30b6cb8eb0d43a0b73cab73c7676b9863223a30`. Disposition: `IMMUTABLY_PINNED`. Forced BOS `si_LK`.

## 2. Upstream Licence Verification Evidence
- **google/mt5-base:** README SHA-256 `f7a22cd51c2a1b0e75275f19f64b06ca3f24415b27f648f8338b88effb6700d2`. Apache-2.0 per recorded upstream model-card evidence.
- **facebook/mbart-large-50:** README SHA-256 `578e2bc78084241ce8ec8833de0fb85e1f9b1a37af49912895428617dc62636f`. Associated fairseq licence SHA-256 `52412d7bc7ce4157ea628bbaacb8829e0a9cb3c58f57f99176126bc8cf2bfc85` (MIT Licence per fairseq upstream evidence).
- **Qualification:** Licence identification verified from pinned upstream model-card evidence. Independent legal review: NOT ESTABLISHED.
