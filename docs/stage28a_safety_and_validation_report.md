# Stage 28A Safety and Validation Report

**Evaluation Phase:** Preliminary Automated Comparison  
**Evaluated Systems:** B0–B5, C1, G1, H1  
**Verification Date:** 2026-10-14 08:45:18 UTC  
**Expert Validated:** `false`  
**Child Suitability Demonstrated:** `false`  
**Approved for Child Delivery:** `false`  

---

## 1. Meaning Preservation & Safety Performance (Clean Locked Subset, N=39)

| System ID | System Name | Entity Pres. (%) | Number Pres. (%) | Negation Pres. (%) | Lowest Unsupported Rate (%) | Answer Leakage Detection |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **B0** | Identity Baseline | 100.0% | 100.0% | 100.0% | 0.0% | No distractor leakage detected ($n=39$) |
| **B1** | Lexical Substitution | 100.0% | 100.0% | 100.0% | 0.0% | No distractor leakage detected ($n=39$) |
| **B2** | Sentence Splitting | 97.4% | 100.0% | 100.0% | 2.6% | No distractor leakage detected ($n=39$) |
| **B3** | Syntactic Rules | 100.0% | 100.0% | 100.0% | 0.0% | No distractor leakage detected ($n=39$) |
| **B4** | Combined Deterministic | 97.4% | 100.0% | 100.0% | 2.6% | No distractor leakage detected ($n=39$) |
| **B5** | Offline Fallback | 100.0% | 100.0% | 100.0% | 0.0% | No distractor leakage detected ($n=39$) |
| **C1** | Stage 25 Controlled Engine | 100.0% | 100.0% | 100.0% | 0.0% | No distractor leakage detected ($n=39$) |
| **G1** | Gemini Native-Only ($n=29$) | 100.0% | 100.0% | 100.0% | 0.0% | No distractor leakage detected ($n=29$) |
| **H1** | Governed Hybrid Pipeline | 100.0% | 100.0% | 100.0% | 0.0% | No distractor leakage detected ($n=39$) |

## 2. Qualified Safety Finding
No distractor leakage was detected by the configured automated checks across $n=39$ clean-subset outputs.
Governed Hybrid Pipeline (**H1**) achieved 100% entity and negation preservation due to deterministic fallback interception of potential shifts.
