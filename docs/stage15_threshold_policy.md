# Stage 15 Quality Thresholds and Scoring Policy

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Document Version:** 1.0.0  

---

## 1. Quality Dimensions and Weighting

For Simplification Corpus pairs, overall quality score $S \in [0, 100]$ is computed as a weighted sum across 5 dimensions:

| Quality Dimension | Weight ($w_i$) | Focus | Primary Signals |
| :--- | :---: | :--- | :--- |
| **Meaning Preservation** | 30% | Retention of core semantics, facts, entities, numbers, and negations | Negation consistency, entity preservation, key term retention |
| **Grammar & Fluency** | 20% | Syntactic correctness and child-friendly natural phrasing | Grammar check error rate, sentence structure validity |
| **Simplicity Improvement** | 20% | Measurable reduction in syntactic/lexical complexity | Token compression, ASL reduction, difficult word reduction |
| **Age Appropriateness** | 15% | Vocabulary and sentence structure suitability for ages 4–8 | Syllable count proxy, word length, age-band lexicon alignment |
| **Safety & Answer Boundary** | 15% | Zero task leakage, zero distractor corruption, safe vocabulary | Answer leakage scanner, content safety allowlist |

---

## 2. Mutually Exclusive Precedence & Status Resolution

The overall status of a record is determined by a strict hierarchical precedence to eliminate any ambiguity:

```text
1. Any CRITICAL failure triggered?
   └── YES ──> Status = "quarantined"
   └── NO
        │
2. Any ERROR rule failed OR Overall Score < 70.0?
   └── YES ──> Status = "automatic_check_failed"
   └── NO
        │
3. Any WARNING rule triggered OR 70.0 <= Overall Score < 85.0?
   └── YES ──> Status = "manual_review_required"
   └── NO
        │
4. All checks passed AND Overall Score >= 85.0?
   └── YES ──> Status = "automatic_check_passed"
```

---

## 3. Dimension-Specific Threshold Configuration

| Dimension / Metric | Warning Threshold | Error Threshold | Critical Threshold |
| :--- | :---: | :---: | :---: |
| **Compression Ratio** ($L_{\text{simp}} / L_{\text{orig}}$) | $> 1.20$ or $< 0.30$ | $> 1.50$ or $< 0.15$ | N/A |
| **Average Sentence Length (ASL)** | $> 15$ tokens | $> 22$ tokens | N/A |
| **Negation Inconsistency** | N/A | Inverted negation | N/A |
| **Number / Quantity Mismatch** | Quantity altered | Quantity missing | N/A |
| **Support Monotonicity** | Strong $>$ Moderate complexity | Strong $\gg$ Mild complexity | N/A |
| **Answer Key Leakage** | N/A | N/A | Exposed in child view |
| **PII / Unallowlisted Export** | N/A | N/A | Direct identifier present |
| **Lexicon Circularity** | N/A | Cycle detected ($A \rightarrow B \rightarrow A$) | N/A |

---

## 4. Record Accounting Guarantee

For any validation run on $N$ records:
$$N = N_{\text{passed}} + N_{\text{failed}} + N_{\text{review\_required}} + N_{\text{quarantined}}$$
$$\Delta N = 0 \quad (\text{No record may be dropped or double counted})$$
