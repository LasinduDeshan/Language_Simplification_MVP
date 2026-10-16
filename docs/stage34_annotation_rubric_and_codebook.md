# Stage 34 — Annotation Rubric and Codebook

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Stage:** Stage 34 — Sinhala Expert Linguistic and Child-Development Validation  
**Status:** Frozen and Sealed Specification — WP3 Complete  
**Rubric Version:** `S34-RUBRIC-V1`  
**Rubric Hash (SHA-256):** `80b60486002208f63df1b67caa82b7a90611907e11b617233595cb69b933de23`  
**Reason Codes Hash (SHA-256):** `4cf69ba83554f0059170dd7a8c7ebbfad598c34e11cb9e59c6cde77837f0d703`

---

## 1. Value Contract and Status Architecture

To eliminate ambiguity between valid unobserved data, inapplicable features, and missing entries, every dimension is structured as an explicit `{ status, score }` object:

- **`RATED`**: Reviewer assigns an authoritative score or categorical value within their qualified competency. `score` must be non-null and strictly valid.
- **`NOT_APPLICABLE`**: Dimension is structurally irrelevant for this item (e.g., `morphology_preservation` for unchanged controls or punctuation-only deletions). `score` must be `null`.
- **`CANNOT_ASSESS`**: The dimension falls outside the reviewer's declared professional competency (e.g., a linguist without child development credentials assessing `developmental_suitability`), or text context is insufficient. `score` must be `null`.
- **`MISSING`**: Permitted **only** in incomplete autosaved drafts. A submitted annotation containing `MISSING` in any mandatory dimension is fail-closed rejected upon submission.

---

## 2. Evaluation Dimensions

### 2.1 Meaning Preservation (Primary Critical Endpoint)
- **Scale:** 0–3 ordinal
- **Permitted Final Statuses:** `RATED`, `CANNOT_ASSESS`
- **Criteria:**
  - `3`: Complete preservation. All propositions, facts, modalities, entities, and causal relationships remain intact.
  - `2`: Minor drift. Subtle nuance variation that does not distort core truth (e.g., minor stylistic rephrasing).
  - `1`: Substantial drift. A key fact, negation, condition, or entity was omitted, inverted, or altered.
  - `0`: Major contradiction or critical loss. Candidate directly contradicts or discards the primary message.

### 2.2 Grammatical Acceptability (Primary Critical Endpoint)
- **Scale:** 0–3 ordinal
- **Permitted Final Statuses:** `RATED`, `CANNOT_ASSESS`
- **Criteria:**
  - `3`: Standard, well-formed Sinhala grammar and syntax.
  - `2`: Minor awkwardness or non-standard word order that remains intelligible to native speakers.
  - `1`: Substantial grammatical defect (e.g., broken postposition, case misalignment).
  - `0`: Severely broken or ungrammatical sentence structure.

### 2.3 Morphology Preservation (Secondary Agreement Diagnostic)
- **Scale:** 0–3 ordinal
- **Permitted Final Statuses:** `RATED`, `NOT_APPLICABLE`, `CANNOT_ASSESS`
- **Criteria:**
  - `3`: Flawless Sinhala inflection, verb stem conjugation, and agreement markers.
  - `2`: Minor inflectional deviation with no impact on meaning.
  - `1`: Morphological mismatch affecting voice, tense, or number.
  - `0`: Erroneous morphological form rendering words unrecognizable.

### 2.4 Fluency and Naturalness (Secondary Agreement Diagnostic)
- **Scale:** 0–3 ordinal
- **Permitted Final Statuses:** `RATED`, `CANNOT_ASSESS`
- **Criteria:**
  - `3`: Highly idiomatic, natural Sinhala phrasing appropriate for child narrative.
  - `2`: Acceptable fluency with minor stiffness or translation-like cadence.
  - `1`: Stilted, unnatural phrasing that sounds artificial.
  - `0`: Incomprehensible or highly unidiomatic Sinhala.

### 2.5 Simplicity Improvement (Secondary Agreement Diagnostic)
- **Scale:** Categorical (`SIMPLER`, `SAME`, `MORE_COMPLEX`, `UNCERTAIN`)
- **Permitted Final Statuses:** `RATED`, `CANNOT_ASSESS`
- **Criteria:**
  - `SIMPLER`: Sentence has lower clause depth, simpler vocabulary, or shorter span.
  - `SAME`: Complexity is largely unchanged compared to the source.
  - `MORE_COMPLEX`: Output is harder or more convoluted than the source.
  - `UNCERTAIN`: Mixed lexical and syntactic effects prevent clear determination.

### 2.6 Vocabulary Accessibility (Secondary Agreement Diagnostic)
- **Scale:** 0–3 ordinal
- **Permitted Final Statuses:** `RATED`, `CANNOT_ASSESS`
- **Criteria:**
  - `3`: Fully accessible to 4–8 year old Sinhala-speaking children.
  - `2`: Mostly accessible words; 1 word may require incidental adult explanation.
  - `1`: Contains multiple formal, literary, or advanced words beyond ages 4–8.
  - `0`: Advanced, archaic, or bureaucratic vocabulary entirely inaccessible to young children.

### 2.7 Sentence-Structure Suitability (Secondary Agreement Diagnostic)
- **Scale:** 0–3 ordinal
- **Permitted Final Statuses:** `RATED`, `CANNOT_ASSESS`
- **Criteria:**
  - `3`: Direct single clause or simple coordinate sentence; minimal memory load.
  - `2`: Moderate sentence length with manageable subordinate clauses.
  - `1`: Complex sentence with multiple embedded clauses challenging working memory.
  - `0`: Dense, deeply nested multi-clause construction unsuitable for early literacy.

### 2.8 Developmental Suitability (Primary Critical Endpoint)
- **Scale:** 0–3 ordinal
- **Permitted Final Statuses:** `RATED`, `CANNOT_ASSESS`
- **Reviewer Quota:** Requires evaluation by qualified Early-Childhood Educators or Child-Development Specialists.
- **Criteria:**
  - `3`: Highly appropriate developmental themes and cognitive load for ages 4–8.
  - `2`: Generally suitable; concepts are accessible with standard adult mediation.
  - `1`: Cognitive concepts or abstraction levels too mature for ages 4–8.
  - `0`: Severe developmental mismatch.

### 2.9 Safety Flag
- **Scale:** Categorical (`NO_FLAG`, `POTENTIAL_CONCERN`, `UNSUITABLE`, `UNCERTAIN`)
- **Permitted Final Statuses:** `RATED`, `CANNOT_ASSESS`
- **Criteria:**
  - `NO_FLAG`: Wholesome, safe, child-friendly content.
  - `POTENTIAL_CONCERN`: Ambiguous tone or sensitive theme requiring monitoring.
  - `UNSUITABLE`: Content involves violence, fear, distress, or explicit harm.
  - `UNCERTAIN`: Context is inadequate to evaluate safety.

### 2.10 Overall Disposition (Primary Critical Endpoint)
- **Scale:** Categorical (`ACCEPT_DRAFT`, `ACCEPT_WITH_MINOR_EDIT`, `REVISE`, `REJECT`, `ESCALATE`)
- **Permitted Final Statuses:** `RATED` (Mandatory rating for every submitted annotation)

---

## 3. Controlled Reason Codes

When any defect, reduction in score, or safety concern is identified, reviewers must attach at least one governed reason code:
- `SEMANTIC_OMISSION`: Essential meaning omitted.
- `SEMANTIC_ADDITION`: Unsupported claims introduced.
- `SEMANTIC_CONTRADICTION`: Meaning contradicts source.
- `ENTITY_OR_NUMBER_CHANGED`: Entity, pronoun, or number altered.
- `NEGATION_OR_MODALITY_CHANGED`: Epistemic certainty or polarity flipped.
- `TEMPORAL_OR_CAUSAL_RELATION_CHANGED`: Sequence or causality disrupted.
- `GRAMMAR_ERROR`: Syntactic violation.
- `MORPHOLOGY_ERROR`: Inflectional or agreement error.
- `UNNATURAL_SINHALA`: Unidiomatic phrasing.
- `REGISTER_MISMATCH`: Clash of literary and spoken forms.
- `NOT_SIMPLER`: Output failed to reduce complexity.
- `VOCABULARY_TOO_ADVANCED`: Words beyond age band.
- `SENTENCE_STRUCTURE_TOO_COMPLEX`: Syntactic memory load excessive.
- `DEVELOPMENTAL_CONCERN`: Cognitive mismatch for ages 4–8.
- `SAFETY_CONCERN`: Harmful, scary, or distressing content.
- `SOURCE_AMBIGUOUS`: Source text unclear.
- `INSUFFICIENT_CONTEXT`: Context insufficient for judgment.
- `ANNOTATION_INTERFACE_ERROR`: Rendering/UI defect.
- `OTHER_EXPLAINED`: Other reasoned defect documented in protected storage.

---

## 4. Rubric Immutability Policy

Under Governance Invariant 20, once the rubric is frozen and production evaluation on the locked test set commences, **no adjudicator, reviewer, or investigator may alter the rubric, scales, or reason codes**. Any proposed modifications must be recorded as recommendations in the Stage 34 completion report for future stages.
