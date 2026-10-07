# Stage 25 — Controlled Simplification Engine Architecture

**Document ID:** STAGE25-ARCH-001  
**Engine Version:** 1.0.0  
**Configuration Hash:** `929930790f100e2873e03d9e0f60040a4f8eca7fc6af7072efba00f3b34e45b8`  
**Rule Catalogue Hash:** `929930790f100e2873e03d9e0f60040a4f8eca7fc6af7072efba00f3b34e45b8`  
**Status:** Research & Development Candidate Engine  
**Governance Default:** `approved_for_child_delivery: false`, `requires_expert_review: true`  

---

## 1. Architectural Overview & Workflow

```mermaid
flowchart TD
    A["Input Text + Caller Metadata"] --> B["Stage 21 Preprocessing (spaCy Transformer/Pipeline)"]
    B --> C["Automatic Element & Action Graph Extractor"]
    C --> D["Merge Protection Invariants (Effective Protections)"]
    D --> E["Support-Level Controller (Precedence & Immutability)"]
    E --> F["Controlled Simplification Planner"]
    F --> G["Execution Pipeline<br/>- Nominalization Unpacking<br/>- Passive to Active<br/>- Coordinated Splitting<br/>- Lexical Substitution<br/>- Step Numbering & Chunking<br/>- Governed Vocab Definitions"]
    G --> H["12-Gate Meaning & Safety Validator (VAL_*)"]
    H -->|Pass (Clean)| I["Terminal Status: PASSED"]
    H -->|Pass (Rollback)| J["Terminal Status: PASSED_WITH_ROLLBACK"]
    H -->|Ambiguous / Soft Warning| K["Terminal Status: MANUAL_REVIEW_REQUIRED"]
    H -->|Severe Safety Violation| L["Terminal Status: REJECTED"]
    H -->|Emergency Trigger| M["Terminal Status: ADULT_SUPPORT_REQUIRED"]
```

## 2. Core Architectural Principles
1. **Deterministic Multi-Tier Transformation:** Distinct Mild, Moderate, and Strong rule execution paths calibrated to learner needs.
2. **Untrusted Caller & Auto-Detection Invariant:** Auto-detected protected entities, numbers, and action graphs cannot be removed or weakened by caller metadata.
3. **Fail-Closed Governance:** Violations trigger safe operation rollback; unresolvable transformations route to `MANUAL_REVIEW_REQUIRED`.
4. **Structured Action Graph:** Action nodes preserve chronological execution sequence, condition-action pairs, and safety-critical modifiers.
5. **Multi-Layer Answer Non-Disclosure:** Answer protection checks exact text, normalized variants, case-insensitive tokens, subsequences, distractor metadata, and SHA-256 hashes without logging raw answers.
6. **Privacy-Safe Auditing:** Audit logs record pseudonymous hashes and rule activation IDs without storing raw learner text.
