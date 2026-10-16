# Stage 34 — Sampling, Assignment, and Blinding Protocol

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Stage:** Stage 34 — Sinhala Expert Linguistic and Child-Development Validation  
**Status:** Frozen Protocol and Generated Assignments — WP4 Complete  
**Prerequisite Baseline:** `stage-33-complete-v2` (`74481f4d09beeba42ccb9b9c32ff994e372af5bf`)  
**Assignment Seed:** `1034`  
**Assignment Ledger Hash (SHA-256):** `e4b7bd76065819ccbdf413220a754e4d9511bc965df6b411626987f1e536de19`

---

## 1. Population and Sampling Design

The evaluation population is derived dynamically from the sealed Stage 31 canonical analytical corpus and the Stage 33 final disposition ledger:
- **Total Canonical Items:** 150
  - Train: 124 records (61 selected rewrites, 2 all-blocked, 61 no-rule controls)
  - Validation: 13 records (3 selected rewrites, 1 all-blocked, 9 no-rule controls)
  - Locked Test: 13 records (7 selected rewrites, 0 all-blocked, 6 no-rule controls)
- **Zero Sampling Loss:** All 150 canonical corpus records are assigned for evaluation, ensuring 100% stratum and partition coverage.
- **Development vs Locked-Test Separation:** Training and qualification batches strictly use train partition examples; locked-test items are evaluated under blinded conditions without modifying Stage 33 rules or configurations.

---

## 2. Expertise-Aware Assignment Quotas

In accordance with Governance Invariant 19 and Invariant 24, each of the 150 primary evaluation items is deterministically assigned to a multi-disciplinary panel:

1. **At least 2 Sinhala-language-qualified reviews:**
   - Both `REV-S34-001` and `REV-S34-002` (Sinhala Linguists) are assigned to every item to evaluate linguistic acceptability, morphology, and meaning preservation.
2. **At least 2 developmental-suitability-qualified reviews:**
   - Two qualified developmental raters are assigned to every item, sampled deterministically from `REV-S34-003`, `REV-S34-004` (Educators), and `REV-S34-005` (Child Development Specialist).
3. **At least 3 independent reviewers overall:**
   - With 2 linguists and 2 developmental raters, every item receives exactly **4 independent reviews** ($4 \ge 3$).
4. **Computable Pair Guarantee:**
   - Every primary item contains $\ge 2$ qualified language ratings and $\ge 2$ qualified developmental ratings, ensuring Krippendorff's alpha is mathematically computable across both domains without single-rater dropouts.

---

## 3. Assignment Accounting and Ledger Sealing

- **Total Items Assigned:** 150
- **Total Assignments Generated:** 600 ($150 \times 4$)
- **Assignment Distribution:**
  - `REV-S34-001` (Linguist): 150 assignments
  - `REV-S34-002` (Linguist): 150 assignments
  - `REV-S34-003` (Educator): 100 assignments
  - `REV-S34-004` (Educator): 100 assignments
  - `REV-S34-005` (Child Dev): 100 assignments
  - `REV-S34-006` (Adjudicator): 0 first-pass assignments (reserved for independent adjudication)
  - `REV-S34-TEAM1` (Internal): 0 primary assignments (isolated from primary dataset)
- **Sealed Ledger:** `data/sinhala_expert_validation/assignments/assignment_ledger.jsonl`

---

## 4. Blinding Architecture and Safeguards

To prevent confirmation bias, halo effects, and benchmark leakage, the annotation interface enforces strict blinding:

1. **Partition Masking:** The item's split membership (`train`, `validation`, `locked_test`) is withheld.
2. **Rule Identity Masking:** Rule names, IDs (`SI-SNT-SPL-0001`, `SI-LEX-SUB-0001`), and transformation tags are stripped.
3. **Control Concealment:** Reviewers are not informed whether an item represents an algorithmically simplified candidate or an unchanged control.
4. **Peer Isolation:** Reviewers cannot inspect other reviewers' draft ratings, submitted annotations, or agreement statistics until after the production annotation phase is formally closed.
5. **No Model Scores Exposed:** Perplexity, BLEU, ranking scores, and guard logs are excluded from the reviewer view.
