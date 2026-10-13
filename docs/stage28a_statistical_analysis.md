# Stage 28A Statistical Analysis Report

**Protocol:** Predefined hypothesis families, paired Wilcoxon signed-rank tests ($r_{\text{rb}}$ effect sizes), paired bootstrap SacreBLEU differences, and Benjamini-Hochberg FDR correction.

---

## 1. Hypothesis Family 1: SARI Differences vs B0 (Identity Baseline)

| System ID | Evaluated System Name | Denominator ($N$) | Mean SARI Diff | Median SARI Diff | Wilcoxon $W$ | Raw $p$-value | B-H Adj. $q$-value | $r_{\text{rb}}$ Effect Size | Significant ($\alpha=0.05$) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **B1** | Lexical Substitution Baseline | 39 | +0.00 | +0.00 | 0.0 | 1.0000e+00 | 1.0000e+00 | 0.000 | **False** |
| **B2** | Sentence Splitting Baseline | 39 | +9.73 | +0.00 | 0.0 | 1.4718e-04 | 2.9000e-04 | 1.000 | **True** |
| **B3** | Syntactic Rules Baseline | 39 | +0.00 | +0.00 | 0.0 | 1.0000e+00 | 1.0000e+00 | 0.000 | **False** |
| **B4** | Combined Deterministic Baseline | 39 | +9.73 | +0.00 | 0.0 | 1.4718e-04 | 2.9000e-04 | 1.000 | **True** |
| **B5** | Offline Deterministic Fallback | 39 | +8.15 | +0.00 | 0.0 | 4.3231e-04 | 6.9000e-04 | 1.000 | **True** |
| **C1** | Stage 25 Controlled Engine | 39 | +11.07 | +0.00 | 0.0 | 2.0811e-03 | 2.7700e-03 | 1.000 | **True** |
| **H1** | Stage 26 Governed Hybrid Pipeline | 39 | +25.10 | +30.27 | 0.0 | 5.3581e-07 | 0.0000e+00 | 1.000 | **True** |
| **G1_native** | G1 Native-Only (Partial, n=29/39 matched) | 29 | +26.59 | +25.54 | 0.0 | 5.5931e-06 | 2.0000e-05 | 1.000 | **True** |

---

## 2. Hypothesis Family 2: SARI Differences vs C1 (Stage 25 Controlled Engine)

| System ID | Evaluated System Name | Denominator ($N$) | Mean SARI Diff | Median SARI Diff | Wilcoxon $W$ | Raw $p$-value | B-H Adj. $q$-value | $r_{\text{rb}}$ Effect Size | Significant ($\alpha=0.05$) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **B4** | Combined Deterministic Baseline | 39 | -1.33 | +0.00 | 105.0 | 7.1231e-01 | 7.1231e-01 | 0.091 | **False** |
| **H1** | Stage 26 Governed Hybrid Pipeline | 39 | +14.04 | +11.49 | 15.0 | 7.2082e-05 | 1.4000e-04 | 0.908 | **True** |
| **G1_native** | G1 Native-Only (Partial, n=29/39 matched) | 29 | +18.42 | +23.99 | 22.0 | 9.6566e-05 | 1.4000e-04 | 0.875 | **True** |

---

## 3. Corpus SacreBLEU Differences vs B0 (Paired Bootstrap 95% Confidence Intervals, 2,000 Iterations)

> [!NOTE]
> Corpus SacreBLEU is a single corpus scalar. Wilcoxon signed-rank cannot operate on a single scalar. Differences are evaluated via paired bootstrap resampling of complete evaluation items.

| System ID | System Name | Corpus SacreBLEU | Difference vs B0 | 95% CI Lower | 95% CI Upper | Valid Replicates |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **B1** | Lexical Substitution Baseline | 61.96 | +0.00 | 0.0 | 0.0 | 2000/2000 |
| **B2** | Sentence Splitting Baseline | 52.99 | -8.97 | -12.52 | -5.65 | 2000/2000 |
| **B3** | Syntactic Rules Baseline | 61.96 | +0.00 | 0.0 | 0.0 | 2000/2000 |
| **B4** | Combined Deterministic Baseline | 52.99 | -8.97 | -12.52 | -5.65 | 2000/2000 |
| **B5** | Offline Deterministic Fallback | 60.77 | -1.19 | -2.43 | -0.04 | 2000/2000 |
| **C1** | Stage 25 Controlled Engine | 60.41 | -1.54 | -3.49 | 0.66 | 2000/2000 |
| **H1** | Stage 26 Governed Hybrid Pipeline | 44.27 | -17.68 | -23.05 | -11.93 | 2000/2000 |
