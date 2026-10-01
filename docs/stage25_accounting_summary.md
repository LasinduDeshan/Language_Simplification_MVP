# Stage 25 — Corpus Accounting and Zero-Loss Balance Summary

## 1. Dataset Split Accounting (Release 0.2.0)

| Split Name | Source Groups | Outputs Generated per Tier | Total Stage 25 Outputs | Primary Purpose |
|---|---|---|---|---|
| **Development Candidate Train** | 210 | 210 Mild, 210 Mod, 210 Strong | **630** | Rule development and tuning |
| **Development Candidate Validation** | 45 | 45 Mild, 45 Mod, 45 Strong | **135** | Rule selection and freeze |
| **Locked Test Set** | 45 | 45 Mild, 45 Mod, 45 Strong | **135** | Final unbiased evaluation |
| **Total Corpus** | **300** | **300 Mild, 300 Mod, 300 Strong** | **900** | Full Cumulative Release |

## 2. Zero-Loss Accounting Equation
$$900 = \sum_{\text{Splits}} (\text{Mild} + \text{Moderate} + \text{Strong}) = 630 + 135 + 135$$
$$\text{Total Dispositions: } 702 \text{ Passed} + 198 \text{ Manual Review} + 0 \text{ Failed} + 0 \text{ Quarantined} = 900$$
