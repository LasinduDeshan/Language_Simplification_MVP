# Stage 27 Expert Rating Rubric: Dimensions, Scales, and Evaluation Standards

**Component:** Component 3 — AI and NLP Based Language Simplification  
**Scope:** English educational language support for children aged 4–8  
**Prerequisite:** `stage-26-complete-v5` (`1a67bd4`)  
**Rubric Version:** `1.0.0`  
**Protocol Status:** Authoritative Evaluation Standard  

---

## 1. Five-Point Rating Scale Anchors

Every dimension is scored on an integer scale from 1 to 5. The qualitative anchors reflect early developmental literacy standards for children aged 4–8:

| Score | Descriptor | Operational Definition | Pedagogical Implications |
| :---: | :--- | :--- | :--- |
| **1** | **Unacceptable** | Severe semantic distortion, hallucination, gross grammatical breakdown, or age-inappropriate content. | Unusable in educational contexts; must be rejected or rewritten. |
| **2** | **Major Revision Required** | Core meaning partially preserved, but excessive syntactic complexity, dense vocabulary, or awkward phrasing poses a severe comprehension barrier. | Requires substantial restructuring before pedagogical use. |
| **3** | **Acceptable with Revision** | Propositional meaning intact; comprehensible to the target age, but contains minor phrasing, punctuation, or vocabulary that could be improved. | Can be retained with minor editor touch-up. |
| **4** | **Good** | Clear, grammatically correct, age-appropriate, and well-aligned with the declared support tier. | High-quality educational language ready for research evaluation. |
| **5** | **Excellent** | Exemplary child-friendly language, highly natural when read aloud, optimal syntactic scaffolding, and engaging tone. | Gold-standard reference exemplar for model benchmarking. |

---

## 2. Ten Evaluation Dimensions

### Dimension 1: Meaning Preservation
- **Definition:** The extent to which the simplified text preserves the core propositions, truth conditions, and educational intent of the original item without distortion, factual invention, or loss of key information.
- **Scoring Guide:**
  * **5:** Complete proposition preservation; zero factual loss; exact logical equivalence.
  * **4:** Core propositions preserved; minor contextual simplification that does not alter truth value.
  * **3:** Core proposition recognizable, but nuanced qualifier or secondary fact omitted.
  * **2:** Significant factual omission or minor unintended meaning shift.
  * **1:** Propositional contradiction, polarity reversal, or total distortion of source meaning.

### Dimension 2: Grammatical Correctness
- **Definition:** Adherence to standard English morphology, syntax, agreement, and punctuation.
- **Scoring Guide:**
  * **5:** Flawless grammar, proper inflection, correct agreement, and clean punctuation.
  * **4:** Minor stylistic punctuation irregularity with no grammatical error.
  * **3:** Minor grammatical slip that does not impede comprehension (e.g., missing comma, awkward article).
  * **2:** Pronoun-antecedent or subject-verb disagreement causing confusion.
  * **1:** Severe syntactic collapse, fragmented clauses, or ungrammatical word order.

### Dimension 3: Fluency and Naturalness
- **Definition:** How idiomatic, smooth, and natural the sentence sounds when spoken or read aloud to a child aged 4–8.
- **Scoring Guide:**
  * **5:** Delightfully smooth, conversational, and natural; sounds like an experienced early-years teacher.
  * **4:** Natural and fluent; standard classroom English.
  * **3:** Understandable but slightly stiff or robotic phrasing.
  * **2:** Unnatural phrasing, awkward collocations, or unnatural word sequences.
  * **1:** Incoherent, unidiomatic, or translation-like output.

### Dimension 4: Vocabulary Simplicity
- **Definition:** Replacement of low-frequency, abstract, or multisyllabic vocabulary with frequent, concrete, early-acquired words appropriate for ages 4–8.
- **Scoring Guide:**
  * **5:** All vocabulary accessible to early learners; complex concepts glossed or replaced with familiar lemmas.
  * **4:** Vocabulary well-simplified; at most one slightly challenging word supported by context.
  * **3:** Moderate vocabulary; some abstract or Tier-2 words remain without support.
  * **2:** Several words exceed typical 4–8 developmental vocabulary norms.
  * **1:** Dense, technical, or archaic vocabulary completely unsuited for young children.

### Dimension 5: Sentence-Structure Simplicity
- **Definition:** Reduction of syntactic complexity, avoidance of center-embedded clauses, passives, nested prepositional phrases, and lengthy conjunctions.
- **Scoring Guide:**
  * **5:** Clean, short subject-verb-object structures; active voice; single-clause sentences where appropriate.
  * **4:** Mostly simple sentences; compound sentences use basic coordinating conjunctions (*and*, *but*).
  * **3:** Slightly long sentences or complex subordinate clauses that could be split.
  * **2:** Dense subordinate clauses, passives, or center-embedded structures taxing working memory.
  * **1:** Convoluted sentence structure causing parsing breakdown for young learners.

### Dimension 6: Age Appropriateness (Ages 4–8)
- **Definition:** Suitability of conceptual depth, tone, and cognitive load for early childhood stages (Reception to Year 3 / Pre-K to Grade 2).
- **Scoring Guide:**
  * **5:** Perfectly calibrated to developmental psychology and cognitive capacity of 4–8 year olds.
  * **4:** Age-appropriate concepts and warm, supportive tone.
  * **3:** Marginally advanced concepts; acceptable for older 7–8 year olds but demanding for 4–5 year olds.
  * **2:** Content or tone misaligned with early childhood developmental expectations.
  * **1:** Adult-oriented concepts, frightening imagery, or completely inappropriate developmental level.

### Dimension 7: Support-Level Appropriateness
- **Definition:** Fidelity to the declared simplification tier:
  - **Mild:** Light lexical substitution, minimal syntactic change, preserving sentence structure.
  - **Moderate:** Substantial lexical simplification, sentence splitting, active voice transformation.
  - **Strong:** Maximum support: shortest manageable sentences, high-frequency core vocabulary, explicit sequenced steps.
- **Scoring Guide:**
  * **5:** Exact match to declared support level; optimal differentiation along the support gradient.
  * **4:** Good alignment with minor overlap with adjacent tier.
  * **3:** Support level slightly higher or lower than declared tier.
  * **2:** Noticeable tier mismatch (e.g., Strong tier is more complex than Mild tier).
  * **1:** Complete tier inversion or failure to simplify.

### Dimension 8: Instruction Clarity
- **Definition:** For imperative or task prompts, clarity and directness of what the child is asked to do.
- **Scoring Guide:**
  * **5:** Crystal-clear actionable directive; single unambiguous task goal.
  * **4:** Clear instruction with minor non-essential wording.
  * **3:** Understandable instruction, but requires slight adult scaffolding to clarify.
  * **2:** Ambiguous directive; child may not understand what action is expected.
  * **1:** Misleading, conflicting, or unintelligible instructions.

### Dimension 9: Protected-Element Preservation
- **Definition:** Preservation of protected entities, quantities, answer constraints, negation, relations, and instructional intent, using exact matching where required and expert-confirmed semantic preservation otherwise. Answer terms must never be exposed to the child merely because they are protected.
- **Scoring Guide:**
  * **5:** 100% preservation of all protected entities, numbers, and key constraint relations; zero answer disclosure.
  * **4:** All key entities and quantities intact; minor legitimate pronominalization confirmed safe.
  * **3:** Entity replaced with hypernym or pronoun requiring slight context deduction.
  * **2:** Protected number or entity slightly altered (e.g., "three apples" changed to "some apples").
  * **1:** Protected entity or count corrupted, or assessment answer leaked in prompt.

### Dimension 10: Overall Child-Language Suitability
- **Definition:** Holistic pedagogical synthesis evaluating whether the text is ready for inclusion in research-quality early-childhood simplification corpora.
- **Scoring Guide:**
  * **5:** Outstanding educational resource; highly recommended for reference benchmarking.
  * **4:** Solid educational resource; ready for benchmarking without changes.
  * **3:** Usable resource with minor revision.
  * **2:** Substandard resource requiring expert rewrite.
  * **1:** Unusable; should be quarantined or discarded.

---

## 3. Critical Failure Checks, Workflow Flags, and Authorizations

To eliminate false overrides, all record-level indicators are divided into three distinct functional groups:

### 3.1 Group 1: Critical Failure Flags (Booleans)
If **any** of the following 10 flags is set to `true`, the record **cannot receive provisional expert approval**, regardless of whether numerical dimension ratings average 4.0 or 5.0:

```python
critical_failure = any([
    meaning_changed,                  # Semantic distortion, contradiction, or polarity flip
    important_information_removed,    # Essential educational fact dropped
    unsupported_information_added,    # Hallucinated or invented detail
    negation_changed,                 # Polarity inverted (e.g., 'did not find' -> 'found')
    quantity_or_number_changed,       # Counts, numerals, or units altered
    entity_changed,                   # Target character, object, or place corrupted
    spatial_relation_changed,         # Positional relations flipped (e.g., 'under' -> 'on')
    temporal_or_action_order_changed, # Sequence of actions/events corrupted
    answer_leakage_detected,          # Prompt reveals the target assessment answer
    unsafe_or_inappropriate_content,  # Content harmful, frightening, or inappropriate for children
])
```

### 3.2 Group 2: Workflow & Operational Flags (Booleans)
These flags control review logistics and queue routing, not automatic rejection:
- `requires_revision`: Flagged by reviewer for minor text edit or phrasing adjustment.
- `requires_adjudication`: Reviewer ratings or classifications diverged beyond tolerance.
- `requires_expert_recheck`: Material revision requires secondary independent sign-off.

### 3.3 Group 3: Final Authorization Decisions
These flags define the governance and downstream research eligibility:
- `eligible_for_stage28_evaluation`: Record achieved `expert_approved` or `approved_with_revision` and is eligible for Stage 28 comparative benchmarking (`true` / `false`).
- `recommended_for_supervised_child_delivery_review`: Authorizes consideration within a supervised research study only; does **not** provide ethics approval, parental consent, safeguarding clearance, or production software deployment (`true` / `false`).
- `approved_for_unsupervised_child_delivery`: **UNIVERSAL INVARIANT: ALWAYS FALSE in Stage 27.**

---

## 4. Support-Tier Progression & Monotonicity Rubric

Reviewers evaluate all three simplified tiers side-by-side with the source sentence:
$$\text{Source Text} \longrightarrow \text{Mild Tier} \longrightarrow \text{Moderate Tier} \longrightarrow \text{Strong Tier}$$

Reviewers check:
1. **Complexity Monotonicity:** Does complexity decrease monotonically from Source $\to$ Mild $\to$ Moderate $\to$ Strong?
2. **Meaning Invariance:** Is the core propositional meaning consistent across all three tiers?
3. **Appropriate Differentiation:** Is there meaningful differentiation between tiers without trivial repetition?

**Monotonicity Failure Codes:**
- `ERR_TIER_INVERSION`: A higher support tier is more syntactically or lexically complex than a lower tier.
- `ERR_TIER_IDENTICAL`: Two adjacent tiers are verbatim identical without justification.
- `ERR_TIER_OVER_SIMPLIFICATION`: Mild tier is over-simplified, eliminating vocabulary distinction.
- `ERR_TIER_MEANING_DRIFT`: Meaning shifted between Moderate and Strong tiers.

---

## 5. English Lexicon Review Rubric

Reviewers evaluate candidate vocabulary entries against 12 linguistic criteria:

1. **Normalized Headword:** Lowercased base lemma.
2. **Intended Word Sense:** Contextual meaning clearly specified.
3. **Part of Speech:** Valid grammatical category (noun, verb, adj, adv).
4. **Candidate Replacement:** Age-appropriate synonym.
5. **Replacement Simplicity:** Genuinely simpler than headword, supported by cited developmental norms where available; otherwise recorded as expert judgement requiring provenance.
6. **Target Age Band:** Calibrated for 4–5, 6–7, or 7–8 years.
7. **Child-Friendly Definition:** Direct, concrete explanation without meta-linguistic jargon.
8. **Illustrative Sentence:** Clear example in everyday child contexts.
9. **Circularity Check:** Definition does not use the headword or its close derivatives.
10. **Sense Alignment:** Replacement fits natural syntactic slots without semantic mismatch.
11. **Cognitive Accessibility:** Replacement does not introduce secondary abstract polysemy.
12. **Missing Synonyms Flag:** Identification of missing early-acquired alternatives.

**Lexicon Dispositions:** `approved`, `approved_with_revision`, `wrong_word_sense`, `replacement_not_simpler`, `age_tier_incorrect`, `definition_not_child_friendly`, `circular_definition`, `rejected`.

---

## 6. Adaptation Activity Review Rubric

The 192 Component 3 local adaptation-test activities and permitted fixtures are evaluated across 6 structural dimensions:

1. **Instruction Simplicity:** Phrasing is accessible and unambiguous for children aged 4–8.
2. **Skill Alignment:** Validly assesses the declared skill (e.g., word-picture matching, chronological sequencing, pronoun selection).
3. **Distractor Quality & Safety:** Distractors are plausible, non-confusing, and do not disclose or overlap with the correct answer.
4. **Sequence Determinism:** Sentence-ordering and action-sequencing activities possess exactly one logically defensible correct order.
5. **Answer Protection:** Stimulus prompt does not inadvertently reveal the answer key.
6. **Child-Facing Isolation:** All administrative scores, hashes, error codes, and reviewer notes are stripped from child views.
