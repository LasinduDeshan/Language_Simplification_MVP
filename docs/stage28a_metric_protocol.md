# Stage 28A Metric Protocol Specification

## 1. SARI Metric (EASSE Parity Verification)
- Formulation: Xu et al. (TACL 2016) / EASSE standard reference formulation.
- Target Pinned Version: EASSE 0.2.4 parity.
- Tokenization: Lowercase regex `\b\w+\b`.
- Fixture Count: 5 golden test fixtures.
- Maximum Absolute Delta: 0.000000.
- Allowed Tolerance: 1e-4.
- Parity Status: **PASSED**.

## 2. BLEU Metric Protocol
- **Sentence BLEU-4:** Sentence-level smoothed BLEU-4 with brevity penalty and add-1 smoothing. Reported in its own dedicated column.
- **Corpus SacreBLEU:** Standard benchmark-level SacreBLEU with official signature `nrefs:1|case:mixed|eff:no|tok:13a|smooth:exp|version:2.6.0`. Reported in its own dedicated column.
- **Statistical Invariant:** No paired significance test is claimed over a single corpus-level scalar. Differences evaluated via paired bootstrap resampling (2,000 iterations).

## 3. Readability & Surface Metrics
- Flesch-Kincaid Grade Level (FKGL): Pre- and post-simplification grades and grade reduction ($\Delta \text{FKGL}$).
- Compression Ratio: $\text{Length}_{\text{output}} / \text{Length}_{\text{input}}$.

## 4. Statistical Testing Protocol & Wilcoxon P-Method
- **Primary Non-Parametric Significance:** Two-sided paired Wilcoxon signed-rank test (`scipy.stats.wilcoxon(zero_method="wilcox", correction=True, alternative="two-sided")`).
- **P-Method Specification:** Labeled `asymptotic_normal` because evaluation item sets include ties and zero differences, prompting SciPy's continuity-corrected asymptotic normal approximation.
- **Identical Differences Convention:** When all item score differences are zero ($n_{\text{eff}}=0$), test status is set to `NOT_APPLICABLE_ALL_DIFFERENCES_ZERO`, with $p=1.0000$ and rank-biserial effect size $r_{\text{rb}}=0.0$ by defined reporting convention.
- **Multiplicity Correction:** Monotonic step-up Benjamini-Hochberg False Discovery Rate adjustment across predefined hypothesis families.
- **SARI Difference Tolerance:** Canonical baseline $B_0=14.38$ (exact unrounded 14.3770); individual system signed differences reconcile with an explicit numerical tolerance of $\le 0.01$.
