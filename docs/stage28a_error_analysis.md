# Stage 28A Qualitative and Structural Error Analysis

## 1. Candidate Performance Profiles
- **Best frozen Stage 24 baseline:** **B4 (Combined Deterministic Baseline)** — Canonical Stage 28A SARI: **24.11**. *(Stage 24 historical baseline was 36.84 under earlier non-EASSE tokenization).*
- **Best offline controlled system:** **C1 (Stage 25 Controlled Engine)** — Canonical Stage 28A SARI: **25.44**, 100% entity and negation preservation.
- **Best request-level governed automated pipeline:** **H1 (Governed Hybrid Pipeline)** — Canonical Stage 28A SARI: **39.48**, evaluated across all 39 requests, including 28 native Gemini deliveries, 1 safety fallback, and 10 provider fallbacks.
- **Diagnostic native LLM evaluation:** **G1 Native-Only (Partial, $n=29/39$)** — Canonical Stage 28A SARI: **40.65**, evaluating strictly the 29 items receiving native LLM responses without fallback imputation.

## 2. Error Taxonomy & Systematic Findings
- **Meaning Shifts:** Monitored via entity and negation preservation. Governed hybrid (H1) successfully routes shifts to deterministic fallback.
- **Catastrophic Deletion:** B2 (Splitting) occasionally removed subordinate clauses carrying descriptive context, dropping entity preservation to 97.4%.
- **Over-Simplification:** B4 occasionally produced choppy sentences without discourse cohesion.
- **Under-Simplification:** B0 and mild B1 retained grade 7+ vocabulary.
