# Stage 35 Metrics and Statistical Analysis Plan

**Stage:** Stage 35 — Comparative Evaluation of Gemini, mT5, and mBART for Sinhala Simplification  
**Specification Reference:** `data/model_comparison/stage35/registry/stage35_metrics_and_gates_spec.json`  

---

## 1. Frozen Diagnostic Proxy Metrics

Stage 35 measures five automated diagnostic metrics across all selected responses:

1. **`automated_gate_pass`:** Binary indicator (1.0 / 0.0) reflecting whether the response cleared all critical safety checks (no script violation, no protected-span mutation, no truncation).
2. **`semantic_similarity_proxy`:** Automated cosine similarity between multilingual sentence embeddings of input and output.
3. **`grammaticality_proxy`:** Deterministic grammatical agreement proxy verified by the frozen Sinhala morphological engine.
4. **`simplification_proxy`:** Lexical length and complexity reduction metric relative to input source text.
5. **`protected_span_intact`:** Exact substring verification for registered protected entities.

---

## 2. Level 6 Metric Cell Accounting

With 47 selected responses and 5 frozen metrics:
$$\text{Expected Metric Cells} = 47 \times 5 = 235$$
$$\text{Diagnostic Cells Computed} = 235$$
$$\text{Eligible Empirical Comparison Cells} = 0$$
$$\text{Missing Cells} = 0$$

All 235 diagnostic cells were successfully computed to verify pipeline operational integrity. Because responses were generated via offline simulation fixtures, none represent empirical model performance measurements.

---

## 3. Level 8 Statistical Comparison Reconciliation

Across the four evaluated conditions ($C_0, C_1, C_2, C_3$), there are $\binom{4}{2} = 6$ pairwise condition comparisons:
1. $C_0$ vs $C_1$
2. $C_0$ vs $C_2$
3. $C_0$ vs $C_3$
4. $C_1$ vs $C_2$
5. $C_1$ vs $C_3$
6. $C_2$ vs $C_3$

### Statistical Accounting Breakdown
- **Dry-Run Comparison Computations:** 6
- **Empirical Statistical Comparisons:** 0
- **Empirical Comparisons Not Estimable:** 6
- **Zero-Loss Accounting:** $\text{Unaccounted} = 0$

> **Methodological Qualification:** Statistical calculations over simulated fixtures verify data structures, hypothesis-testing routines, and comparison code paths. They do not constitute empirical model comparisons, and no empirical statistical inferences regarding model quality or rankings are drawn.
