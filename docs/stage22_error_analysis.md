# Stage 22 Error Analysis & Safety-Critical Verification Report

**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Dataset:** Validation Split (`development_candidate_validation`, 135 instances)  
**Evaluated Champion Model:** Calibrated HistGradientBoosting Classifier (`classifier-1.0.0`)  

---

## 1. Safety-Critical Hard-to-Easy Misclassification Metric

Classifying a genuinely `hard` educational text as `easy` represents the highest educational risk (delivering text that is far too complex without appropriate scaffolding).

$$\text{Hard-to-Easy Error Rate} = \frac{\text{Count of Actual Hard predicted as Easy}}{\text{Total Actual Hard Records}}$$

- **Total Actual Hard Records in Validation Sample:** 15
- **Count of Actual Hard predicted as Easy:** **0**
- **Observed Point Estimate:** **0.00%**
- **95% Wilson Score Binomial CI:** **$[0.0000, 0.2041]$**
- **Safety Evaluation Statement:** No Hard $\to$ Easy errors were observed in the small validation sample. However, the 95% Wilson upper bound was 20.41%; therefore, the $\le 2\%$ safety target was not statistically demonstrated and requires a larger expert-labelled evaluation set.

---

## 2. Confusion Matrix (Validation Split)

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
- Overall validation Balanced Accuracy: **96.96%** (Target $\ge 80\%$).
- Overall validation Macro-F1: **0.9696** (Target $\ge 0.80$).
