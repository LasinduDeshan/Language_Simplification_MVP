# Stage 24 — Baseline Simplification Policy

**Document ID:** STAGE24-POL-001  
**Version:** 1.0.0  
**Effective Date:** 2026-09-30  
**Status:** Approved  

## 1. Scope & Purpose
This policy governs the implementation, evaluation, and attribution of deterministic baseline simplification methods (B0–B5) for English text targeting children aged 4–8 years.

## 2. Evaluation Unit Standard
- **Internal Corpus:** Generic baselines (B0–B5) generate exactly one output per unique source group, evaluated against all 3 reference simplifications (Mild, Moderate, Strong) using multi-reference corpus metrics.
- **Locked Test Set:** 45 source groups produce 45 outputs per baseline, totaling 270 outputs across B0–B5.
- **ASSET Corpus:** Evaluates 359 source groups against 10 references each using fixed generic configuration `target_age_band = "4-8"`.

## 3. Lexical Age-Gating & Schema Governance
- Lexical substitution is governed by developmental age tiers.
- A source word is eligible for substitution when its developmental difficulty exceeds `target_content_age`.
- Replacement words must be within `target_content_age`.
- Learner-level personalization attributes (screening risk tiers, test scores) are strictly prohibited in generic baselines.

## 4. Protected Meaning & Safety Governance
The following elements must be strictly preserved invariant under simplification:
1. Named entities & proper participants
2. Quantities, numbers, and measurements
3. Visual cue colors and shapes
4. Negation polarity and scope
5. Temporal and spatial relational ordering
6. Task intent and answer references

## 5. Output Dispositions & Rollback Decoupling
Rollback is an operational event, not a terminal error disposition.
- Unsafe operation reverted and final output valid -> `automatic_check_passed`
- Reverted output remains ambiguous -> `manual_review_required`
- No valid output remains -> `automatic_check_failed`
- Safety/privacy violation -> `quarantined`

## 6. Prohibited Practices & Attribution
- Zero transformer fine-tuning or live external LLM API calls in primary baseline benchmarks.
- Heuristic fallback outputs (B5) are strictly attributed to `deterministic_fallback` and never to Gemini or external LLMs.
- All baseline outputs carry `approved_for_child_delivery: false` and `requires_expert_review: true`.
