# Stage 22 Error Analysis & Safety-Critical Verification Report

**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Dataset:** Provisional-Label Validation Split (`development_candidate_validation`, 135 instances)  
**Evaluated Champion Model:** Calibrated HistGradientBoosting Classifier (`classifier-1.0.0`)  

---

## 1. Safety-Critical Hard-to-Easy Misclassification Metric

Classifying a genuinely `hard` educational text as `easy` represents the highest educational risk (delivering text that is far too complex without appropriate scaffolding).

$$\text{Hard-to-Easy Error Rate} = \frac{\text{Count of Actual Hard predicted as Easy}}{\text{Total Actual Hard Records}}$$

- **Observed Hard $\to$ Easy errors:** 0 / 15
- **Observed rate:** 0.00%
- **95% Wilson Score Binomial CI:** $[0.0000, 0.2041]$
- **Safety target statistically demonstrated:** **No**
- **Safety Evaluation Statement:** No Hard $\to$ Easy errors were observed in the small validation sample ($0/15$). However, the 95% Wilson upper bound was 20.41%; therefore, the $\le 2\%$ safety target was not statistically demonstrated and requires a larger expert-labelled evaluation set. Do not use the observed 0% as evidence of deployment safety.

---

## 2. Confusion Matrix (Provisional-Label Validation Split)

| Actual \ Predicted | Predicted Easy | Predicted Medium | Predicted Hard | Total Actual |
|---|---:|---:|---:|---:|
| **Actual Easy** | 60 | 0 | 0 | 60 |
| **Actual Medium** | 4 | 56 | 0 | 60 |
| **Actual Hard** | 0 | 0 | 15 | 15 |
| **Total Predicted** | 64 | 56 | 15 | 135 |

---

## 3. Residual Error Breakdown
- Exactly 4 boundary cases between `medium` and `easy` occurred where single-clause imperative instructions with slightly elevated vocabulary were classified as `easy`.
- Zero `hard` instances were underpredicted as `easy`.
- Overall provisional-label validation Balanced Accuracy: **96.96%**.
- Overall provisional-label validation Macro-F1: **0.9696**.

