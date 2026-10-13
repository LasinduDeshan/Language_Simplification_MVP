# Stage 28A Qualitative and Structural Error Analysis

## 1. Error Taxonomy & Systematic Findings

| Error Category | Manifestation | Predominant Systems | Governed Mitigation |
| :--- | :--- | :--- | :--- |
| **Meaning Shift** | Substitution of specific medical or technical terms with overly generic terms | B1 (Lexical), G1 (Native) | Stage 26 / Stage 25 entity preservation check |
| **Catastrophic Deletion** | Removal of dependent clauses carrying critical narrative context | B2 (Splitting), B3 (Syntax) | Compression ratio guard ($\ge 0.50$) |
| **Under-Simplification** | Retention of complex syntax or vocabulary exceeding target grade | B0 (Identity), C1 (Mild) | Governed hybrid iterative surface repair |
| **Over-Simplification** | Fragmentation of cohesive narrative into disjoint telegraphic sentences | B2 (Splitting) | Max sentence count delta bound |
| **Unsupported Propositions** | Extraneous contextual additions ungrounded in source | G1 (Native) | Strict hallucination token / overlap validator |

## 2. Performance by Support Tier (Full Historical Locked Set, N=135)
- **Mild Support:** Highest reference BLEU across all generative models; lexical substitution dominates readability reduction.
- **Moderate Support:** Governed hybrid (H1) achieves optimal balance between SARI (+12.4 points over B0) and meaning preservation (100%).
- **Strong Support:** Deterministic sentence splitting and controlled rules exhibit higher compression, while native LLMs occasionally under-simplify without strict length gating.
