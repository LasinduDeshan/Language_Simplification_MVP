# Stage 32 Provisional Banding Protocol

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** Provisional Automated Vocabulary Banding Protocol  
**Stage:** Stage 32 — Sinhala Child-Vocabulary Lexicon Construction  
**Status:** Authoritative Protocol Deliverable  

---

## 1. Protocol Purpose & Governance Boundaries

Stage 32 assigns automated, technical review bands to candidate Sinhala lexical items to structure and prioritize future human expert review (Stage 34). 

### Critical Disclaimers
1. **Not Child-Age Validated:** Provisional bands are workflow engineering labels. They do NOT establish age of acquisition, developmental suitability, reading comprehension, or pedagogical appropriateness for children aged 4–8.
2. **Not Classroom-Ready:** Automated frequency or word-length thresholds do not guarantee that a word is understood by or safe for children.
3. **No Clinical Inference:** Automated lexicon metrics do not interface with screening risk levels, diagnostic tools, or individual child profiles.

---

## 2. Calibration Isolation & Predeclaration Protocol

To eliminate evaluation contamination:
1. **Predeclared Training Subset:** Thresholds are calibrated strictly on a predeclared development subset drawn from records with `split == "train"`.
2. **Evaluation Split Isolation:** No record or split group belonging to `validation` or `locked_test` may ever enter threshold calibration.
3. **Reproducibility Controls:** Group selection algorithm is deterministic using frozen seed `42`.
4. **Configuration Freeze:** Calibration parameters are frozen in `stage32_configuration.json` and sealed by SHA-256 hash before applying to untouched records.

---

## 3. Provisional Band Rule Architecture

| Provisional Band | Canonical Frequency ($f_c$) | Source Dispersion ($D_s$) | Complexity Metric | Quality Flags |
|---|---|---|---|---|
| `FOUNDATIONAL_CANDIDATE` | $f_c \ge 15$ | $D_s \ge 0.50$ | Graphemes $\le 5$ | 0 quality flags |
| `EARLY_CANDIDATE` | $8 \le f_c \le 14$ | $D_s \ge 0.40$ | Graphemes $\le 7$ | 0 quality flags |
| `DEVELOPING_CANDIDATE` | $3 \le f_c \le 7$ | Unconstrained | Graphemes $\le 10$ | 0 quality flags |
| `ADVANCED_CANDIDATE` | $f_c \le 2$ or Syllables $\ge 4$ | Unconstrained | Any length | 0 quality flags |
| `SPECIALIZED_OR_PROPER_CANDIDATE` | Technical / Named entity | Low / Single source | High length | Named entity flags |
| `REVIEW_REQUIRED` | Ambiguous / Low confidence | Any | Any | Sensitive / OCR flags, or multi-rule tie |
| `EXCLUDED_NON_LEXICAL` | Non-lexical symbols | N/A | Malformed | Non-lexical disposition |

---

## 4. Multi-Rule Tie-Break Governance

If a candidate satisfies criteria for more than one provisional band (e.g., overlapping boundary conditions), the engine strictly avoids arbitrary winner selection:
- The candidate is routed directly to `REVIEW_REQUIRED` with `band_confidence: 0.60` and `band_evidence: ["multi_rule_precedence_tie"]`.
- The final band classification is deferred to independent human expert review in Stage 34.
