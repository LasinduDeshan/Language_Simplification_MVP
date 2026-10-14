# Stage 28A Statistical Analysis Report

**Protocol:** Predefined hypothesis families, paired Wilcoxon signed-rank tests ($r_{\text{rb}}$ effect sizes), paired bootstrap SacreBLEU differences, and Benjamini-Hochberg FDR correction.

---

## 1. Hypothesis Family 1: SARI Differences vs B0 (Identity Baseline)

### Primary Paired Wilcoxon Signed-Rank Test Results

> [!NOTE]
> **Wilcoxon P-Method & Configuration Specification:**
> Stage 28A explicitly uses SciPy's continuity-corrected asymptotic normal approximation with `zero_method="wilcox"`, `correction=True`, `alternative="two-sided"` and `method="approx"`. The p-method is accordingly labeled `asymptotic_normal`. For systems where all score differences are zero (effective $n=0$, i.e., B1 and B3 vs B0), the test status is designated `NOT_APPLICABLE_ALL_DIFFERENCES_ZERO`, with $p=1.0000$ and effect size $r_{\text{rb}}=0.0$ assigned by defined reporting convention.

| System ID | Evaluated System Name | Paired $N$ | Zero Diffs ($n_0$) | Effective Wilcoxon $n$ | Test Status | Zero Method | Alternative | p-Method | Continuity Corr. | Mean Diff | Median Diff | Wilcoxon $W$ | Raw $p$-value | B-H Adj. $q$-value | $r_{\text{rb}}$ Effect Size | Significant ($\alpha=0.05$) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **B1** | Lexical Substitution Baseline | 39 | 39 | 0 | `NOT_APPLICABLE_ALL_DIFFERENCES_ZERO` | `wilcox` | `two-sided` | `none` | `False` | +0.00 | +0.00 | 0.0 | 1.0000e+00 | 1.0000e+00 | 0.000 | **False** |
| **B2** | Sentence Splitting Baseline | 39 | 21 | 18 | `COMPUTED` | `wilcox` | `two-sided` | `asymptotic_normal` | `True` | +9.73 | +0.00 | 0.0 | 1.6092e-04 | 3.2183e-04 | 1.000 | **True** |
| **B3** | Syntactic Rules Baseline | 39 | 39 | 0 | `NOT_APPLICABLE_ALL_DIFFERENCES_ZERO` | `wilcox` | `two-sided` | `none` | `False` | +0.00 | +0.00 | 0.0 | 1.0000e+00 | 1.0000e+00 | 0.000 | **False** |
| **B4** | Combined Deterministic Baseline | 39 | 21 | 18 | `COMPUTED` | `wilcox` | `two-sided` | `asymptotic_normal` | `True` | +9.73 | +0.00 | 0.0 | 1.6092e-04 | 3.2183e-04 | 1.000 | **True** |
| **B5** | Offline Deterministic Fallback | 39 | 24 | 15 | `COMPUTED` | `wilcox` | `two-sided` | `asymptotic_normal` | `True` | +8.15 | +0.00 | 0.0 | 4.8266e-04 | 7.7225e-04 | 1.000 | **True** |
| **C1** | Stage 25 Controlled Engine | 39 | 27 | 12 | `COMPUTED` | `wilcox` | `two-sided` | `asymptotic_normal` | `True` | +11.07 | +0.00 | 0.0 | 2.3741e-03 | 3.1654e-03 | 1.000 | **True** |
| **H1** | Stage 26 Governed Hybrid Pipeline | 39 | 6 | 33 | `COMPUTED` | `wilcox` | `two-sided` | `asymptotic_normal` | `True` | +25.10 | +30.27 | 0.0 | 5.6126e-07 | 4.4901e-06 | 1.000 | **True** |
| **G1_native** | G1 Native-Only (Partial, n=29/39 matched) | 29 | 2 | 27 | `COMPUTED` | `wilcox` | `two-sided` | `asymptotic_normal` | `True` | +26.59 | +25.54 | 0.0 | 5.9207e-06 | 2.3683e-05 | 1.000 | **True** |

### Benjamini-Hochberg Step-Up Procedure (Family 1, m=8)

| Rank ($k$) | System ID | Raw $p$-value | Step-Up Multiplier ($m/k$) | Preliminary Adj. | Monotonic $q$-value | Significant ($\alpha=0.05$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | **H1** | 5.6126e-07 | 8/1 (8.00x) | 4.4901e-06 | **4.4901e-06** | **True** |
| 2 | **G1_native** | 5.9207e-06 | 8/2 (4.00x) | 2.3683e-05 | **2.3683e-05** | **True** |
| 3 | **B2** | 1.6092e-04 | 8/3 (2.67x) | 4.2911e-04 | **3.2183e-04** | **True** |
| 4 | **B4** | 1.6092e-04 | 8/4 (2.00x) | 3.2183e-04 | **3.2183e-04** | **True** |
| 5 | **B5** | 4.8266e-04 | 8/5 (1.60x) | 7.7225e-04 | **7.7225e-04** | **True** |
| 6 | **C1** | 2.3741e-03 | 8/6 (1.33x) | 3.1654e-03 | **3.1654e-03** | **True** |
| 7 | **B1** | 1.0000e+00 | 8/7 (1.14x) | 1.1429e+00 | **1.0000e+00** | **False** |
| 8 | **B3** | 1.0000e+00 | 8/8 (1.00x) | 1.0000e+00 | **1.0000e+00** | **False** |

---

## 2. Hypothesis Family 2: SARI Differences vs C1 (Stage 25 Controlled Engine)

### Primary Paired Wilcoxon Signed-Rank Test Results

> [!NOTE]
> **Wilcoxon P-Method & Configuration Specification:**
> Stage 28A explicitly uses SciPy's continuity-corrected asymptotic normal approximation with `zero_method="wilcox"`, `correction=True`, `alternative="two-sided"` and `method="approx"`.

| System ID | Evaluated System Name | Paired $N$ | Zero Diffs ($n_0$) | Effective Wilcoxon $n$ | Test Status | Zero Method | Alternative | p-Method | Continuity Corr. | Mean Diff | Median Diff | Wilcoxon $W$ | Raw $p$-value | B-H Adj. $q$-value | $r_{\text{rb}}$ Effect Size | Significant ($\alpha=0.05$) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **B4** | Combined Deterministic Baseline | 39 | 18 | 21 | `COMPUTED` | `wilcox` | `two-sided` | `asymptotic_normal` | `True` | -1.33 | +0.00 | 105.0 | 7.2544e-01 | 7.2544e-01 | 0.091 | **False** |
| **H1** | Stage 26 Governed Hybrid Pipeline | 39 | 14 | 25 | `COMPUTED` | `wilcox` | `two-sided` | `asymptotic_normal` | `True` | +14.04 | +11.49 | 15.0 | 7.6262e-05 | 1.5264e-04 | 0.908 | **True** |
| **G1_native** | G1 Native-Only (Partial, n=29/39 matched) | 29 | 3 | 26 | `COMPUTED` | `wilcox` | `two-sided` | `asymptotic_normal` | `True` | +18.42 | +23.99 | 22.0 | 1.0176e-04 | 1.5264e-04 | 0.875 | **True** |

### Benjamini-Hochberg Step-Up Procedure (Family 2, m=3)

| Rank ($k$) | System ID | Raw $p$-value | Step-Up Multiplier ($m/k$) | Preliminary Adj. | Monotonic $q$-value | Significant ($\alpha=0.05$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | **H1** | 7.6262e-05 | 3/1 (3.00x) | 2.2879e-04 | **1.5264e-04** | **True** |
| 2 | **G1_native** | 1.0176e-04 | 3/2 (1.50x) | 1.5264e-04 | **1.5264e-04** | **True** |
| 3 | **B4** | 7.2544e-01 | 3/3 (1.00x) | 7.2544e-01 | **7.2544e-01** | **False** |

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
