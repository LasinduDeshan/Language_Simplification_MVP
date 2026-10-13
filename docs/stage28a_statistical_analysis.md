# Stage 28A Statistical Analysis Report

**Analysis Protocol:** Predefined hypothesis families, paired Wilcoxon signed-rank tests ($r_{\text{rb}}$ effect sizes), paired bootstrap SacreBLEU differences, and Benjamini-Hochberg FDR correction.

---

## 1. Hypothesis Family 1: SARI Improvement over B0 (Identity) on Clean Locked Subset (N=39)

| System ID | System Name | Mean SARI Diff | Wilcoxon W | Raw p-value | B-H Adj. p-value | $r_{\text{rb}}$ Effect Size | Significant ($\alpha=0.05$) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **B1** | Lexical Substitution Baseline | +0.00 | 0.0 | 1.0000e+00 | 1.0000e+00 | 0.000 | False |
| **B2** | Sentence Splitting Baseline | +9.73 | 0.0 | 1.4718e-04 | 2.9000e-04 | 1.000 | True |
| **B3** | Syntactic Rules Baseline | +0.00 | 0.0 | 1.0000e+00 | 1.0000e+00 | 0.000 | False |
| **B4** | Combined Deterministic Baseline | +9.73 | 0.0 | 1.4718e-04 | 2.9000e-04 | 1.000 | True |
| **B5** | Offline Deterministic Fallback | +8.15 | 0.0 | 4.3231e-04 | 6.9000e-04 | 1.000 | True |
| **C1** | Stage 25 Controlled Engine | +11.06 | 0.0 | 2.0811e-03 | 2.7700e-03 | 1.000 | True |
| **G1** | Gemini Native Simplification | +24.76 | 0.0 | 5.3581e-07 | 0.0000e+00 | 1.000 | True |
| **H1** | Stage 26 Governed Hybrid Pipeline | +25.10 | 0.0 | 5.3581e-07 | 0.0000e+00 | 1.000 | True |

---

## 2. Hypothesis Family 2: SARI Difference vs C1 (Stage 25 Controlled Engine) on Clean Locked Subset (N=39)

| System ID | System Name | Mean SARI Diff vs C1 | Wilcoxon W | Raw p-value | B-H Adj. p-value | $r_{{\text{{rb}}}}$ Effect Size | Significant ($\alpha=0.05$) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **B1** | Lexical Substitution Baseline | -11.06 | 0.0 | 2.0811e-03 | 3.6400e-03 | -1.000 | True |
| **B2** | Sentence Splitting Baseline | -1.33 | 105.0 | 7.1231e-01 | 7.1231e-01 | 0.091 | False |
| **B3** | Syntactic Rules Baseline | -11.06 | 0.0 | 2.0811e-03 | 3.6400e-03 | -1.000 | True |
| **B4** | Combined Deterministic Baseline | -1.33 | 105.0 | 7.1231e-01 | 7.1231e-01 | 0.091 | False |
| **B5** | Offline Deterministic Fallback | -2.91 | 99.0 | 5.6226e-01 | 7.1231e-01 | -0.143 | False |
| **G1** | Gemini Native Simplification | +13.70 | 22.0 | 9.6566e-05 | 3.4000e-04 | 0.875 | True |
| **H1** | Stage 26 Governed Hybrid Pipeline | +14.04 | 15.0 | 7.2082e-05 | 3.4000e-04 | 0.908 | True |

---

## 3. Corpus SacreBLEU Differences vs B0 (Paired Bootstrap 95% Confidence Intervals, 2000 Iterations)

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
| **G1** | Gemini Native Simplification | 42.97 | -18.99 | -24.87 | -13.1 | 2000/2000 |
| **H1** | Stage 26 Governed Hybrid Pipeline | 44.27 | -17.68 | -23.05 | -11.93 | 2000/2000 |
