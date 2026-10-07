# Dataset Card: Adaptation Test Set (English MVP)

## 1. Summary
The **Adaptation Test Set** is a governed collection of test sample activities used specifically to evaluate Component 3's AI/NLP-based language simplification and personalized adaptation engine.

- **Schema Version:** `1.0.0`
- **Dataset Content Version:** `0.1.0` (Internal Draft)
- **JSON Schema:** `data/schemas/1.0.0/adaptation_record.schema.json`

## 2. Governance & Ownership Boundaries
- **Canonical Component Owner:** Component 3 (AI/NLP Personalized Language Simplification).
- **Scope Restriction:** Component 3 does **not** own or distribute the production interactive Activity Bank (which is canonically owned by Component 2 / Curriculum Authoring).
- **Language & Age Range:** English (`en`), Ages 4–8 years.
- **Privacy Classification:** Public test samples / Synthetic simulation fixtures (no identifiable learner data).
- **Licence:** `project-internal` (restrictive defaults).

## 3. Structure & Contents
- `releases/0.1.0/adaptation_test_set.json`: 40 standardized test activities across 4 domains (Vocabulary, Grammar, Comprehension, Instruction Following).
- `en/component1_samples/`: Simulated screening profile mock input contracts.
- `en/component2_ar_samples/`: Mock Augmented Reality 3D spatial instruction test contracts.
- `draft_contracts/development_scenarios.json`: Multi-attempt simulation test scenarios.

## 4. Child-Safe Interface Protection
- **Masked Fields:** `protected` (`answer`, `elements`, `acceptable_answers`), `protected_answer`, `target_word`, `target_structure`, `expected_concepts`.
- Child-facing runtime views (`get_child_activity()`) strictly exclude answer keys and evaluation rubrics. Full records are restricted to authorized evaluation services.
