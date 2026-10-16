# Stage 33 — Sinhala Simplification Rule Governance and Scope

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Deterministic rule taxonomy, authorship metadata, rights separation, and semantic safety boundaries  
**Governance Checkpoint:** Stage 33 Technical Draft  

---

## 1. Governance Purpose

Stage 33 establishes a deterministic, auditable, and fail-closed Sinhala simplification-rule engine. It introduces frozen rule definitions for lexical substitution, phrase replacement, sentence splitting, and conservative syntactic simplification.

Passing Stage 33 technical gates verifies that configured transformations execute without silently altering protected meaning elements or violating Unicode invariants. It does **not** certify that outputs are human-validated Sinhala, developmentally appropriate, educationally effective, or approved for delivery to children.

---

## 2. Permitted Rule Taxonomy

Every Stage 33 rule must strictly belong to one of four permitted classes:

### 2.1 Lexical Substitution (`SI-LEX-SUB-XXXX`)
- Replaces an allowlisted lemma or surface form with an allowlisted simpler candidate.
- Requires explicit technical author attribution (`authoring_method: "technical_rule_authoring"`, `author_id_or_team: "stage33_technical_team"`).
- Target must be supported by Stage 31/32 evidence refs.
- Morphology and inflectional features must be preserved or the attempt is routed to manual review.
- Prohibited: frequency-only or band-only substitution (replacing a word merely because the target has a higher frequency or lower provisional band).

### 2.2 Phrase-Level Substitution (`SI-PHR-SUB-XXXX`)
- Replaces multi-token idioms, complex connective phrases, or verb clusters with an allowlisted simpler expression.
- Evaluated with longest-match-first priority.
- Partial replacement of overlapping phrases is prohibited.

### 2.3 Sentence Splitting (`SI-SNT-SPL-XXXX`)
- Splits compound sentences at allowlisted coordinating markers (e.g., `සහ`, `නමුත්`).
- Punctuation is reconstructed deterministically.
- **Constrained Subject Recovery:** Insertion of a grammatical subject into the second clause is permitted **only** when the exact subject noun phrase is verbatim copied from an unambiguous source span and mapped to it. Ambiguous referent recovery routes strictly to `MANUAL_REVIEW_REQUIRED` or unchanged fallback.

### 2.4 Conservative Syntactic Simplification (`SI-SYN-CON-XXXX`)
- Deletion of allowlisted redundant discourse fillers (e.g., `ඇත්තෙන්ම`) where core propositional meaning is preserved.
- Reordering of allowlisted sequential clauses where dependencies remain traceable.

---

## 3. Explicitly Prohibited Transformations

1. **Unrestricted synonymy:** No substitution derived merely from embeddings, surface similarity, or translation models.
2. **Frequency-only substitution:** Lower-frequency tokens may never be replaced merely because another token is more frequent.
3. **Free-form paraphrasing:** Neural generation (LLMs, sequence-to-sequence models) is prohibited in Stage 33.
4. **Altering protected spans:** Modifying numbers, dates, units, currencies, named entities, quotations, or technical terms without an explicit allowlist override.
5. **Negation or modality shifts:** Removing negation markers or altering the scope of conditional/modal expressions.
6. **Inventing referents:** Inventing subjects or referents during sentence splitting.
7. **Unicode corruption:** Splitting Sinhala grapheme clusters or introducing `U+FFFD`.

---

## 4. Rule Payload Rights Partitioning

Rule definitions derived from restricted or rights-encumbered sources are partitioned:
1. **Public Registry (`rule_registry_public.json`):**
   Contains opaque IDs, rule types, versions, priorities, status, required guards, and domain-separated keyed HMAC references (`source_pattern_ref`, `target_template_ref`). Contains zero restricted literal text.
2. **External Protected Payloads (`rule_payloads_protected.json`):**
   Quarantined in external storage under `SINHALA_SIMPLIFICATION_PROTECTED_ROOT`. Holds literal Sinhala phrases, concordances, and exact evidence spans.

---

## 5. Frozen Stage 33 Rule Registry Summary

| Rule ID | Version | Type | Priority | Evidence Ref | Required Guards |
|---|---|---|---|---|---|
| `SI-PHR-SUB-0001` | 1 | PHRASE_SUBSTITUTION | 150 | `SI-LEX-000675`, `000681` | ENTITY, NEGATION |
| `SI-PHR-SUB-0002` | 1 | PHRASE_SUBSTITUTION | 140 | `SI-LEX-000164`, `000216` | ENTITY, NEGATION |
| `SI-LEX-SUB-0001` | 1 | LEXICAL_SUBSTITUTION | 100 | `SI-LEX-000550`, `000185` | ENTITY, NEGATION |
| `SI-LEX-SUB-0002` | 1 | LEXICAL_SUBSTITUTION | 90 | `SI-LEX-000326`, `000325` | ENTITY, NEGATION |
| `SI-LEX-SUB-0003` | 1 | LEXICAL_SUBSTITUTION | 80 | `SI-LEX-000427` | ENTITY, NEGATION |
| `SI-SYN-CON-0001` | 1 | CONSERVATIVE_SYNTACTIC | 70 | `SI-SYN-FILLER-01` | ENTITY, NEGATION |
| `SI-SNT-SPL-0002` | 1 | SENTENCE_SPLIT | 60 | `SI-SPLIT-MARKER-02` | ENTITY, NEGATION, NUMBER |
| `SI-SNT-SPL-0001` | 1 | SENTENCE_SPLIT | 50 | `SI-LEX-000908` | ENTITY, NEGATION, NUMBER |

---

## 6. Meaning-Critical Protection & Detector Limitations

The protected-span detector identifies and preserves 12 categories:
1. `NAMED_ENTITY`
2. `NUMBER_NUMERIC`
3. `DATE_TIME`
4. `UNIT_MEASUREMENT`
5. `CURRENCY`
6. `NEGATION_MARKER`
7. `MODALITY_CONDITION`
8. `QUOTATION_DIRECT_SPEECH`
9. `IDENTIFIER_CODE_URL`
10. `PARENTHETICAL_REFERENCE`
11. `MIXED_SCRIPT_TERM`
12. `STAGE32_REVIEW_REQUIRED_VOCABULARY`

> [!WARNING]
> Automated named-entity and semantic scope detection is conservative and incomplete for Sinhala. The absence of a detector flag is not proof that a token is not a proper noun or meaning-critical element.
