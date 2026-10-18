# Stage 36 — Semantic-Risk and Simplification Diagnostics Specification

**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Modules:** `backend/app/sinhala_output_validation/validators/v4_v5_semantic_fidelity.py`, `backend/app/sinhala_output_validation/validators/v6_v8_diagnostics.py`  

---

## 1. Validator V5: Omission, Unsupported Insertion & Hallucination Risk

- **Novel Token Ratio:** Evaluates the proportion of novel non-source content tokens in candidate text.
- **Thresholds:**
  - $\text{Novel Ratio} > 0.65$: Hard rejection for unsupported insertion / hallucination risk (`REJ_UNSUPPORTED_INSERTION`, Severity `CRITICAL`).
  - $0.45 < \text{Novel Ratio} \le 0.65$: Advisory warning for high lexical divergence (`WARN_HIGH_LEXICAL_DIVERGENCE`, Severity `WARNING`).

---

## 2. Validator V6: Semantic-Risk Proxy Diagnostic

- **Methodology:** Computes character 3-gram Jaccard overlap between source and candidate texts.
- **Classification:** **Semantic-risk proxy diagnostic**. Character n-gram Jaccard serves strictly as an automated diagnostic risk indicator to catch catastrophic semantic collapse ($< 0.20$).
- **Governance Constraint:** This diagnostic metric **cannot override a hard failure** on any preceding gate, nor can it independently establish semantic equivalence between source and candidate.
- **Severity on Collapse ($< 0.20$):** `CRITICAL`
- **Reason Code:** `REJ_CRITICAL_SEMANTIC_RISK`

---

## 3. Validator V7: Grammaticality & Orthography Proxy

- **Orthographic Consistency:**
  - Consecutive virama (hal-kirima) signs (`\u0DCA\u0DCA`) represent corrupted orthography $\rightarrow$ `REJ_INVALID_UNICODE` (Severity `CRITICAL`).
  - Orphaned leading dependent vowel signs $\rightarrow$ `REJ_INVALID_UNICODE` (Severity `CRITICAL`).
- **Delimiter Balance:**
  - Unmatched parentheses, brackets, or braces route to the manual review queue $\rightarrow$ `REV_FLUENCY_ANOMALY` (Severity `REVIEW`).

---

## 4. Validator V8: Simplification Gain Diagnostic

- **Readability Telemetry:**
  - Calculates average word length in Sinhala characters: $\text{gain} = \text{avg\_len}(\text{source}) - \text{avg\_len}(\text{candidate})$.
  - Emits telemetry under `diagnostic_metrics`:
    - `src_avg_word_length`
    - `cand_avg_word_length`
    - `simplification_gain_proxy`
- **Severity:** `DIAGNOSTIC` (never rejects on its own).
- **Reason Code:** `DIAG_SIMPLIFICATION_METRICS`
