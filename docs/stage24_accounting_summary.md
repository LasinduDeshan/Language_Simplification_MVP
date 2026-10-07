# Stage 24 — Mathematical Accounting Summary

**Verification Status:** Confirmed Zero Loss  
**Unaccounted Records:** 0  

## 1. Accounting Equations

For all methods and datasets:
$$\text{Eligible Inputs} = \text{Passed} + \text{Manual Review Required} + \text{Failed} + \text{Quarantined}$$
$$\text{Unaccounted Records} = 0$$

## 2. Internal Corpus Accounting (Release 0.2.0)

| Dataset Split | Source Groups | References per Source | Outputs per Baseline | Total Outputs across B0–B5 | Balance |
|---|---|---|---|---|---|
| Validation Split | 45 | 3 | 45 | 270 | 0 |
| Locked Test Split | 45 | 3 | 45 | 270 | 0 |

### Internal Locked Test Set Dispositions
| Method | Passed | Manual Review | Failed | Quarantined | Total |
|---|---|---|---|---|---|
| B0 (Identity) | 45 | 0 | 0 | 0 | 45 |
| B1 (Lexical) | 45 | 0 | 0 | 0 | 45 |
| B2 (Splitting) | 45 | 0 | 0 | 0 | 45 |
| B3 (Syntax) | 45 | 0 | 0 | 0 | 45 |
| B4 (Combined) | 42 | 0 | 3 | 0 | 45 |
| B5 (Fallback) | 45 | 0 | 0 | 0 | 45 |
| **Total** | **267** | **0** | **3** | **0** | **270** |

$$\sum_{B0}^{B5} (\text{Passed} + \text{ManualReview} + \text{Failed} + \text{Quarantined}) = 267 + 0 + 3 + 0 = 270$$

## 3. ASSET Benchmark Accounting (359 Source Groups)

| Baseline Method | Passed | Manual Review | Failed | Quarantined | Total |
|---|---|---|---|---|---|
| **B0 (Identity)** | 359 | 0 | 0 | 0 | 359 |
| **B1 (Lexical)** | 359 | 0 | 0 | 0 | 359 |
| **B2 (Splitting)** | 358 | 1 | 0 | 0 | 359 |
| **B3 (Syntax)** | 359 | 0 | 0 | 0 | 359 |
| **B4 (Combined)** | 347 | 1 | 11 | 0 | 359 |
| **B5 (Fallback)** | 207 | 91 | 61 | 0 | 359 |
| **Total** | **1,989** | **93** | **72** | **0** | **2,154** |

$$2,154 = \sum_{B0}^{B5} (\text{Passed} + \text{ManualReview} + \text{Failed} + \text{Quarantined}) = 1,989 + 93 + 72 + 0 = 2,154$$

## 4. Split and Contamination Isolation
- Locked internal test set: 45 source groups / 135 pairs (315 Stage 21 protected text instances) strictly isolated.
- Adaptation Test Set: 192 activities / 377 instances isolated (0 leakage).
