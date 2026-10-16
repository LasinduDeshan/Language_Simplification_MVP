# Stage 32 Morphology and Surface-Form Policy

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** Morphology and Surface-Form Preservation Policy  
**Stage:** Stage 32 — Sinhala Child-Vocabulary Lexicon Construction  
**Status:** Authoritative Policy Deliverable  

---

## 1. Policy Purpose & Boundaries

In Sinhala, morphological inflections, case markers, and postpositions create a diverse range of surface variants from common base roots. Overly aggressive stemming or automated lemmatization risks conflating distinct lexical roots, while purely unstemmed tokenization fractures frequency evidence across grammatical cases.

This policy enforces:
1. **Lossless Surface Evidence:** Observed corpus surface forms are preserved permanently and never overwritten by candidate lemmas.
2. **Rule-Based Hypotheses with Explicit Uncertainty:** Every candidate lemma assignment is tagged with `rule_id`, `rule_version: "1.0.0"`, confidence score, and a non-ground-truth disclaimer.
3. **Conservative Affix Stripping:** Rules fail closed: ambiguous multi-hypothesis matches route to `MANUAL_REVIEW_REQUIRED`.
4. **No Invention of Ground Truth:** Automated morphological hypotheses are engineering conveniences to assist future human experts; they are not authoritative linguistic facts.

---

## 2. Multi-Layer Representation

| Layer | Definition | Storage Field |
|---|---|---|
| **Surface Form** | Exact token string observed in the normalized text | `surface_forms[].surface_form` |
| **Canonical Form** | Primary dictionary lookup key (uninflected base or predominant form) | `canonical_form` |
| **Candidate Lemma** | Automated base-form hypothesis | `candidate_lemma` |
| **Morphological Family** | Structured list of rule-derived variant relationships | `morphology_hypotheses[]` |

---

## 3. Regular Nominal Suffix Catalogue (`rule_version: "1.0.0"`)

The conservative analyzer implements the following frozen nominal suffix patterns:

| Suffix | Rule ID | Confidence | Suffix Category |
|---|---|---:|---|
| `වල්` | `PLURAL_SUFFIX_WAL` | 0.85 | Plural marker (inanimate) |
| `වල` | `PLURAL_LOCATIVE_SUFFIX_WALA` | 0.85 | Plural locative / oblique |
| `වරු` | `PLURAL_SUFFIX_WARU` | 0.80 | Plural marker (animate/honorific) |
| `වරුන්` | `PLURAL_SUFFIX_WARUN` | 0.85 | Plural oblique / accusative |
| `යන්` | `PLURAL_SUFFIX_YAN` | 0.80 | Plural animate marker |
| `යින්` | `PLURAL_SUFFIX_YIN` | 0.80 | Plural animate marker |
| `ඉන්` | `PLURAL_SUFFIX_IN` | 0.75 | Plural / instrumental marker |
| `න්` | `PLURAL_SUFFIX_N` | 0.70 | Plural marker |
| `ගෙන්` | `CASE_ABLATIVE_GEN` | 0.85 | Ablative case marker |
| `ගෙ` | `CASE_GENITIVE_GE` | 0.80 | Genitive case marker |
| `ට` | `CASE_DATIV_TA` | 0.75 | Dative case marker |
| `ද` | `PARTICLE_QUESTION_DA` | 0.70 | Interrogative clitic |
| `ත්` | `PARTICLE_CONJUNCTION_TH` | 0.70 | Conjunction clitic |
| `ම` | `PARTICLE_EMPHASIS_MA` | 0.70 | Emphatic clitic |

---

## 4. Uncertainty & Tie-Break Governance

1. **Uninflected Defaults:** Tokens matching no regular affix rule default to `IDENTITY_CANONICAL` with `confidence: 1.0`.
2. **Ambiguous Hypotheses:** If multiple rules match with identical top confidence, the candidate lemma is retained but assigned `confidence: 0.50`, triggering routing to `MANUAL_REVIEW_REQUIRED`.
3. **Low-Confidence Cutoff:** Any hypothesis with confidence $< 0.70$ automatically sets the entry disposition to `MANUAL_REVIEW_REQUIRED`.
4. **Preservation Invariant:** In all cases, `entry.surface_forms` and `surface_form_mapping.jsonl` preserve the raw observed string.
