# Dataset Card: Adaptation Test Set (English MVP)

## 1. Summary
The **Adaptation Test Set** is a governed collection of test sample activities used specifically to evaluate Component 3's AI/NLP-based language simplification and personalized adaptation engine.

## 2. Governance & Ownership Boundaries
- **Canonical Component Owner:** Component 3 (AI/NLP Personalized Language Simplification).
- **Scope Restriction:** Component 3 does **not** own or distribute the production interactive Activity Bank (which is canonically owned by Component 2 / Curriculum Authoring).
- **Language & Age Range:** English (`en`), Ages 4–8 years.
- **Privacy Classification:** Public test samples / Synthetic simulation fixtures (no identifiable learner data).

## 3. Structure & Contents
- `en/component3_local_samples/c3_local_tasks.json`: 40 standardized test activities across 4 domains (Vocabulary, Grammar, Comprehension, Instruction Following).
- `en/component1_samples/`: Simulated screening profile mock input contracts.
- `en/component2_ar_samples/`: Mock Augmented Reality 3D spatial instruction test contracts.
- `draft_contracts/development_scenarios.json`: Multi-attempt simulation test scenarios.

## 4. Child-Safe Interface Protection
- **Masked Fields:** `protected_answer`, `acceptable_answers`, `target_word`, `target_structure`, `expected_concepts`.
- Child-facing runtime views (`get_child_activity()`) strictly exclude answer keys and evaluation rubrics. Full records are restricted to authorized evaluation services.
