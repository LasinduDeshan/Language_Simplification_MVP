# Stage 24 — Baseline Simplification Error Analysis

**Analysis Date:** 2026-09-30  
**Scope:** Error classification across B0–B5 on Internal and ASSET datasets  

## 1. Error Categorization Taxonomy

| Error Category | Description | Primary Method Affected | Mitigation Mechanism |
|---|---|---|---|
| **E1: Fragment Risk** | Incomplete clause after split lacking finite verb or subject | B2 (Sentence Splitting) | `OutputValidator` finite-verb check and imperative allowlist |
| **E2: Meaning Drift / Entity Drop** | Loss of proper names or core participants during aggressive substitution | B1, B4 | Protected element masking before lexical substitution |
| **E3: Negation Inversion** | Dropping 'not' or adding ungrounded negation | B4 | Protected meaning negation polarity validator with automatic rollback |
| **E4: Over-Truncation** | Naive length truncation cutting essential clauses | B5 (Offline Fallback) | Flagged as heuristic comparator; isolated from controlled engines |
| **E5: Lexical Sense Mismatch** | Polysemous word substitution in incorrect grammatical sense | B1 | POS-tag and lemma constrained lookup |

## 2. Operation Rollback Behavior in B4
- In B4, individual step rollbacks successfully prevented 11 structural and entity violations on ASSET and 3 on the internal locked test set.
- Successfully reverted steps that resulted in structurally sound outputs received final disposition `automatic_check_passed` without failing the entire pipeline.
