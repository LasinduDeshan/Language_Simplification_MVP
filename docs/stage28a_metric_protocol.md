# Stage 28A Metric Protocol Specification

## 1. SARI Metric (EASSE Parity)
- Formulation: Xu et al. (TACL 2016) / EASSE standard reference formulation.
- Target Pinned Version: EASSE 0.2.4 parity.
- Tokenization: Lowercase regex `\b\w+\b`.
- Components:
  - SARI Overall: Arithmetic mean of Add F1, Keep F1, and Delete precision across 1-gram to 4-grams.
  - SARI Add: F1-score on added n-grams rewarded against references.
  - SARI Keep: F1-score on retained n-grams rewarded against references.
  - SARI Delete: Deletion precision rewarded against reference deletions.
- Tolerance: Numerical delta $\le 1\text{e}-4$.

## 2. BLEU Metric Protocol
- **Sentence BLEU-4:** Sentence-level smoothed BLEU-4 with brevity penalty and add-1 smoothing. Reported in its own dedicated column.
- **Corpus SacreBLEU:** Standard benchmark-level SacreBLEU with official signature `nrefs:1|case:mixed|eff:no|tok:13a|smooth:exp|version:2.6.0`. Reported in its own dedicated column.
- **Statistical Invariant:** No paired significance test is claimed over a single corpus-level scalar.

## 3. Readability & Surface Metrics
- Flesch-Kincaid Grade Level (FKGL): Pre- and post-simplification grades and grade reduction ($\Delta \text{FKGL}$).
- Compression Ratio: $\text{Length}_{\text{output}} / \text{Length}_{\text{input}}$.

## 4. Deterministic Safety & Meaning Gates
- Protected entity preservation rate (named entities, subject nouns).
- Quantity and number preservation rate.
- Negation polarity preservation rate.
- Distractor answer leakage rate (zero tolerance).
- Lowest observed unsupported-information rate (automated tests cannot prove zero hallucination).
