# Stage 25 — Corpus Accounting and Zero-Loss Balance Summary

## 1. Dataset Split Accounting (Release 0.2.0)

| Split Name | Source Groups | Outputs Generated per Tier | Total Stage 25 Outputs | Primary Purpose |
|---|---|---|---|---|
| **Development Candidate Train** | 210 | 210 Mild, 210 Mod, 210 Strong | **630** | Rule development and tuning |
| **Development Candidate Validation** | 45 | 45 Mild, 45 Mod, 45 Strong | **135** | Rule selection and freeze |
| **Locked Test Set** | 45 | 45 Mild, 45 Mod, 45 Strong | **135** | Final unbiased evaluation (reused benchmark) |
| **Total Corpus** | **300** | **300 Mild, 300 Mod, 300 Strong** | **900** | Full Cumulative Release |

---

## 2. Complete 5-Terminal-Status Balance Accounting

$$900 = \text{Passed} + \text{PassedWithRollback} + \text{ManualReview} + \text{Rejected} + \text{AdultSupport}$$

| Split | Passed | Passed with Rollback | Manual Review | Rejected | Adult Support Required | Total |
|---|---|---|---|---|---|---|
| **Development Candidate Train** | 513 | 0 | 117 | 0 | 0 | **630** |
| **Development Candidate Validation** | 108 | 0 | 27 | 0 | 0 | **135** |
| **Locked Test Set** | 93 | 0 | 42 | 0 | 0 | **135** |
| **Total Corpus** | **714** | **0** | **186** | **0** | **0** | **900** |

*Zero-Loss Accounting Check: $714 + 0 + 186 + 0 + 0 = 900$ (100.0% exact equality).*
