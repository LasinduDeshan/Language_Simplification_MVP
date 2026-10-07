# Stage 20 Authoring Guidelines: Internal English Dataset Expansion

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Target Scope:** English, Children aged 4–8 (Preschool to Early Elementary)  
**Schema Version:** `1.0.0` | **Target Dataset Version:** `0.2.0`  

---

## 1. Overview & Core Principles

All newly authored records for Stage 20 must adhere to strict pedagogical, linguistic, and governance standards. Every record authored during expansion is maintained in an immutable audit state and defaults to:

```json
{
  "validation_status": "draft",
  "research_eligible": false,
  "approved_for_child_delivery": false,
  "requires_expert_review": true
}
```

---

## 2. Three Distinct Record Types & Linking Schema

Every authored unit is split across three distinct record types with bidirectional linkages:

1. **Adaptation Activity (`activity_id`)**: A complete interactive educational activity containing instructions, visual stimulus, multiple choice options, expected response, protected answer, and scoring metrics.
2. **Original Educational Item (`source_item_id`)**: The baseline linguistic stimulus/instruction requiring simplification.
3. **Simplification Pair (`pair_id`)**: A single support-level transformation (Mild, Moderate, Strong) paired with its original item.

```json
{
  "activity_id": "C3-EN-GRA-0101",
  "source_item_id": "SRC-EN-GRA-0101",
  "simplification_pair_ids": [
    "SIMP-EN-000301",
    "SIMP-EN-000302",
    "SIMP-EN-000303"
  ]
}
```

---

## 3. Support Level Tiering Specifications

Each original educational item must be authored with three distinct support levels:

### 3.1 Mild Support
- **Linguistic Goal**: Minor lexical substitution of rare or high-syllable words while preserving the overall sentence structure and clause boundaries.
- **Operations**: `lexical_substitution`, `reference_clarification`.
- **Constraint**: Do not unnecessarily fragment single-clause sentences.

### 3.2 Moderate Support
- **Linguistic Goal**: Sentence splitting and explicit sequential ordering for multi-action instructions.
- **Operations**: `sentence_splitting`, `clause_simplification`, `temporal_reordering`.
- **Constraint**: Limit clause depth to $\le 1$ subordinate clause. Maximum sentence length: 10–12 words.

### 3.3 Strong Support
- **Linguistic Goal**: Direct, atomic, child-friendly presentation with explicit numbered/bulleted action steps and concrete vocabulary.
- **Operations**: `atomic_step_segmentation`, `vocabulary_elaboration`, `direct_imperative`.
- **Constraint**: One action per sentence. Use explicit step indicators (1., 2. or First, Next).

---

## 4. Protected Meaning Units & Forbidden Modifications

All annotated protected meaning units must be preserved across Mild, Moderate, and Strong tiers.

### Invariant Preservation Rules:
1. **Entities & Objects**: If the source refers to a `blue teddy bear`, simplifications cannot substitute `red dog` or omit `teddy bear`.
2. **Quantities & Numbers**: Numerical quantities (e.g., `two`, `three`, `half`) must remain exact.
3. **Colours & Visual Attributes**: Visual attributes in stimulus-linked tasks must remain identical.
4. **Negation Polarity**: Negative constraints (`do not touch`, `except`, `without`) must never be inverted to positive commands.
5. **Action Order**: Temporal dependencies (`first X, then Y`) must maintain the logical execution sequence.
6. **Protected Answers & Objectives**: The correct answer key and task objective must never be compromised or leaked into prompt text.

---

## 5. Domain-Specific Authoring Specifications

### 5.1 Vocabulary Activities (Target: 25% ±5%)
- Object identification, word-to-picture matching, simple category sorting, child definition selection.
- Target age: 4–8. Simple concrete nouns, common action verbs, basic adjectives.

### 5.2 Grammar Activities (Target: 25% ±5%)
- Word ordering, singular/plural selection, preposition placement (`beside`, `under`, `behind`), subject-verb agreement, simple past/present tense.
- Target age: 5–8.

### 5.3 Comprehension Activities (Target: 25% ±5%)
- Short narrative passages (2–4 sentences), WH-questions (Who, What, Where), direct cause-and-effect, sequencing of events.
- Target age: 6–8.

### 5.4 Instruction-Following Activities (Target: 25% ±5%)
- Multi-step directions, conditional instructions (`if X then Y`), object manipulation, classroom action directions.
- Target age: 4–8.

---

## 6. Lexicon Entry Authoring Guidelines

Every child-friendly lexicon entry must define:
- `headword`: Base word (e.g. `gigantic`).
- `normalized_form`: Lowercase, whitespace-trimmed form.
- `pos`: Part of speech (`noun`, `verb`, `adjective`, `adverb`, `preposition`).
- `sense_id`: Disambiguated sense identifier (`sense_1`, `sense_2`).
- `age_min` & `age_max`: Target developmental age band (e.g., `4-6` or `6-8`).
- `difficulty_tier`: `easy`, `medium`, or `hard`.
- `simple_replacement`: Simpler synonym (e.g., `huge`, `very big`).
- `child_definition`: Simple definition using familiar language (e.g., `very, very big`).
- `example_sentence`: Concrete example sentence suited for children.

### Prohibited Lexicon Patterns:
- Circular definition chains ($A \to B \to A$).
- Replacement harder than the source word.
- Incompatible part-of-speech replacements.
- Empty or malformed example sentences.

---

## 7. Provenance & Lineage Recording

Every record must include complete provenance:
- `authoring_method`: One of `human_authored`, `human_authored_with_ai_assistance`, `rule_generated`, `llm_generated_draft`, `derived_from_internal_source`.
- `created_by`: Author username or team ID.
- `created_at`: ISO-8601 UTC timestamp.
- `batch_id`: Batch identifier (e.g., `STAGE20-BATCH-PILOT`).
- `revision_id`: `REV-001` (or `REV-002` for corrected records).
- `human_edited`: `true` or `false`.

> [!CAUTION]
> AI-assisted drafts must never be marked as `human_authored`.
