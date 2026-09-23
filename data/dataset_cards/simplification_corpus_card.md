# Dataset Card: Simplification Corpus (English MVP)

## 1. Summary
The **Simplification Corpus** contains aligned text pairs of complex / original source instructions mapped to child-friendly, linguistically simplified target texts, enriched with metadata, transformation types, and linguistic validation annotations.

## 2. Governance & Ownership Boundaries
- **Canonical Component Owner:** Component 3.
- **Corpus Sources:** Current team-authored and locally generated original–simplified pairs. External benchmark datasets (ASSET, TurkCorpus, WikiLarge) are intentionally deferred to Stage 20.
- **Language & Age Range:** English (`en`), Ages 4–8 years.
- **Privacy Classification:** Non-identifiable text corpus.

## 3. Structure & Contents
- `en/draft/draft_pairs.json`: 196 original–simplified draft text pairs across lexical substitution, syntactic splitting, voice conversion, and audio cue transformations.
- `annotations/grammar_error_annotations.json`: Annotated grammatical error patterns and rubric evaluation test cases.

## 4. Cross-Layer Linkage
- Text pairs originating from Adaptation Test Set activities maintain an optional reference `source_activity_id` for provenance tracking.
