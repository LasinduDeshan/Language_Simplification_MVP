# Stage 22 Probability Calibration & Review Routing Report

**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Model:** Random Forest Classifier (B4) / HistGradientBoosting (B5)  
**Calibration Method:** Isotonic Regression (Fitted on Training Out-of-Fold Predictions)  

---

## 1. Probability Calibration Metrics (Validation Split)

| Model Candidate | Raw Macro-F1 | Raw ECE | Calibrated ECE | Hard-to-Easy Safety Error |
|---|---|---|---|---|
| **B0 Majority Baseline** | 0.2121 | 0.0374 | N/A | 100.0% (Failed) |
| **B1 Transparent Rule Baseline** | 0.2352 | 0.4178 | N/A | 0.0% (Passed) |
| **B2 Multinomial Logistic Regression** | 0.9089 | 0.0962 | 0.0412 | 0.0% (Passed) |
| **B3 Constrained Decision Tree** | 0.6144 | 0.0380 | 0.0365 | 0.0% (Passed) |
| **B4 Random Forest Classifier** | 0.9696 | 0.1099 | **0.0337** | 0.0% (Passed) |
| **B5 HistGradientBoosting Classifier** | 0.9696 | 0.0404 | **0.0337** | 0.0% (Passed) |

---

## 2. Review Routing Policy Summary

- **Confidence Threshold ($\tau$):** 0.80
- **Margin Threshold ($\Delta$):** 0.15
- **Out-of-Distribution Envelope:** $[Q_{0.01}, Q_{0.99}]$ on continuous training features
- **Review Queue Routing:** Automatically diverts unconfident, low-margin, parser-failed, or out-of-distribution instances for human expert review.
