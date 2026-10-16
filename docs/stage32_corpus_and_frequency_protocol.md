# Stage 32 Corpus and Frequency Protocol

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** Corpus Ingestion and Frequency Accounting Protocol  
**Stage:** Stage 32 — Sinhala Child-Vocabulary Lexicon Construction  
**Status:** Authoritative Protocol Deliverable  

---

## 1. Protocol Purpose & Scope

This protocol establishes the authoritative methodology for reading the Stage 31 pilot corpus, executing deterministic tokenization via the sealed Stage 30 grapheme-safe tokenizer, and constructing the lossless **token occurrence ledger** (`token_occurrence_ledger.jsonl`).

It establishes:
1. Primary unweighted frequency calculations over the **150 canonical analytical records**.
2. Weighted parity diagnostics over the **180 provenance-preserving records** using cluster-normalized weights ($w_i = 1/|c|$).
3. Zero-loss occurrence accounting across all 4,072 observed token occurrences.
4. Physical storage decoupling of sentence concordances and isolated token strings to abstract protected URIs (`protected://sinhala_lexicon/...`).

---

## 2. Evidence Populations & Analytical Denominators

| Corpus Population | Records | Analytical Function in Stage 32 |
|---|---:|---|
| Canonical Analytical Corpus | 150 | Authoritative primary denominator for token frequency ($f_c$), document frequency ($df_c$), dispersion ($D_s$), and candidate extraction |
| Provenance-Preserving Corpus | 180 | Audit and parity verification view; evaluated exclusively with duplicate weights |
| Surplus Exact Duplicates | 30 | Preserved for source provenance; zero contribution to unweighted primary frequency |

### Mathematical Weighting Formulation

For provenance record $i$ in duplicate cluster $c$:

$$w_i = \frac{1}{|c|}$$

The weighted frequency for term $t$ is:

$$f_w(t) = \sum_{i=1}^{180} w_i \cdot \mathrm{count}(t, i)$$

The primary unweighted canonical frequency is:

$$f_{\mathrm{canonical}}(t) = \sum_{j=1}^{150} \mathrm{count}(t, j)$$

Parity diagnostic tolerance: $|f_w(t) - f_{\mathrm{canonical}}(t)| < 10^{-6}$.

---

## 3. Token Occurrence Ledger Architecture

Each token occurrence observed in the canonical analytical corpus is serialized as an immutable `TokenOccurrenceRecord` in `data/sinhala_lexicon/ledgers/token_occurrence_ledger.jsonl`.

### Offset Verification Contract
- **Interval Type:** `zero_based_half_open` `[normalized_start_code_point, normalized_end_code_point)`.
- **Integrity Guarantee:** The string sliced from the record's normalized text at code-point indices matches the isolated token text stored at `token_text_storage_ref` byte-for-byte.

### Storage Decoupling Architecture
- Sentence-level concordance contexts: `protected://sinhala_lexicon/contexts/SI-OCC-XXXXXXXX.json`
- Isolated token surface text: `protected://sinhala_lexicon/tokens/SI-OCC-XXXXXXXX.txt`
- Strictly zero restricted text passages or sentences are stored in the Git repository tree.

---

## 4. Empirical Token Occurrence Accounting

The authoritative run across the 150 canonical records produced the following exact accounting:

| Occurrence Category | Count | Proportion | Accounting Equation |
|---|---:|---:|---|
| **Included Candidate Occurrences** | 3,668 | 90.08% | `INCLUDED_CANDIDATE_OCCURRENCE` |
| **Excluded Token Class Occurrences** | 400 | 9.82% | Punctuation (348), Arabic/Sinhala numbers (52) |
| **Manual Review Occurrences** | 4 | 0.10% | Mixed script / special tokens |
| **Rejected Occurrences** | 0 | 0.00% | Security / PII violations |
| **Unaccounted Occurrences** | **0** | **0.00%** | **Target: 0** |
| **Total Token Occurrences** | **4,072** | **100.00%** | $\sum \text{All Categories}$ |

### Candidate Lexicon Yield
- **Distinct Candidate Surface Forms Extracted:** 1,010
- **Deterministic Entry ID Range:** `SI-LEX-000001` through `SI-LEX-001010`
