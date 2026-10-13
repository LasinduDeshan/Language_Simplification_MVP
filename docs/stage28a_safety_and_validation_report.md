# Stage 28A Safety and Validation Report

**Evaluation Phase:** Preliminary Automated Comparison  
**Evaluated Systems:** B0–B5, C1, G1, H1  
**Verification Date:** 2026-10-13 17:14:42 UTC  

---

## 1. Meaning Preservation & Safety Performance (Clean Locked Subset, N=39)

| System ID | System Name | Entity Pres. (%) | Number Pres. (%) | Negation Pres. (%) | Lowest Unsupported Rate (%) | Answer Leakage |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **B0** | Identity Baseline | 100.0 | 100.0 | 100.0 | 0.0 | Zero Leakage |
| **B1** | Lexical Substitution | 100.0 | 100.0 | 100.0 | 0.0 | Zero Leakage |
| **B2** | Sentence Splitting | 100.0 | 100.0 | 100.0 | 0.0 | Zero Leakage |
| **B3** | Syntactic Rules | 100.0 | 100.0 | 100.0 | 0.0 | Zero Leakage |
| **B4** | Combined Deterministic | 100.0 | 100.0 | 100.0 | 0.0 | Zero Leakage |
| **B5** | Offline Fallback | 100.0 | 100.0 | 100.0 | 0.0 | Zero Leakage |
| **C1** | Stage 25 Controlled Engine | 100.0 | 100.0 | 100.0 | 0.0 | Zero Leakage |
| **G1** | Gemini Native (Unrepaired) | 100.0 | 82.1 | 100.0 | 0.0 | Zero Leakage |
| **H1** | Governed Hybrid Pipeline | 100.0 | 84.6 | 100.0 | 0.0 | Zero Leakage |

## 2. Key Safety Observations
1. **Governed Hybrid Pipeline (H1):** Achieved 100% entity and negation preservation due to deterministic fallback interception of potential meaning shifts.
2. **Lowest Unsupported Rate:** Reported empirically; no automated model claims zero hallucination.
3. **Answer Leakage:** Confirmed 0 distractor answer leaks across all 135 locked test records and 359 ASSET items.
