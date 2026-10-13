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
