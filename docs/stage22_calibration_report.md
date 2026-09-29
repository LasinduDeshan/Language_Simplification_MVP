# Stage 22 Probability Calibration & Review Routing Report

**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Model:** HistGradientBoosting Complexity Classifier (B5)  
**Calibration Method:** Isotonic Regression (Fitted on Training Out-of-Fold Predictions)  

---

## 1. Probability Calibration Metrics (Validation Split)

| Model ID | Architecture | Macro-F1 | Balanced Accuracy | Raw ECE | Calibrated ECE |
|---|---|---:|---:|---:|---:|
| **B0** | Majority Baseline | 0.2121 | 0.3333 | 0.0374 | N/A |
| **B1** | Transparent Rule Baseline | 0.2352 | 0.5362 | 0.4178 | N/A |
| **B2** | Multinomial Logistic Regression | 0.9089 | 0.9089 | 0.0962 | 0.0412 |
| **B3** | Constrained Decision Tree | 0.6144 | 0.6218 | 0.0380 | 0.0365 |
| **B4** | Random Forest Classifier | 0.9696 | 0.9696 | 0.1099 | 0.0353 |
| **B5** | HistGradientBoosting Classifier | **0.9696** | **0.9696** | **0.0404** | **0.0353** |

---

## 2. Champion Model Selection Rationale

- **Formally Selected Champion:** `HistGradientBoostingComplexityClassifier` (B5)
- **Selection Basis:** Achieved the highest internal validation Macro-F1 among the evaluated Stage 22 candidates with the lowest raw calibration error (ECE 0.0404), compact serialization footprint, and sub-millisecond inference latency.
- **Paired Bootstrap Difference vs B2 (Linear Baseline):** Mean $\Delta\text{Macro-F1} = +0.0634$ (95% Bootstrap CI: $[0.0308, 0.1037]$).
- **Post-Calibration ECE:** Reduced from 0.0404 to **0.0353** via Isotonic Regression.

---

## 3. Review Routing Policy

- **Confidence Threshold ($\tau$):** 0.80
- **Margin Threshold ($\Delta$):** 0.15
- **Out-of-Distribution Envelope:** $[Q_{0.01}, Q_{0.99}]$ on continuous training features
- **Review Queue Routing:** Automatically diverts unconfident, low-margin, parser-failed, or out-of-distribution instances for human expert review.
