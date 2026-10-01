# Stage 25 — Dataset Issue Register & Quality Disposition

**Document ID:** STAGE25-DATASET-DEFECT-001  
**Source Corpus Release:** Stage 20 (0.2.0 Internal Release)  
**Status:** Registered for Future Expert Review & Remediation  
**Governance Policy:** Frozen locked test items remain unmodified during Stage 25; defects are catalogued and marked inconclusive.

---

## 1. Executive Summary & Defect Discovery

During the formal Moderate-tier investigation in Stage 25, an analysis of the lowest-performing SARI pairs revealed that several internal Stage 20 draft authoring references were **not direct text simplifications**. Instead, they represented **pedagogical task reformulations**, **response-mode adaptations**, and **activity-format transformations**.

### Impact on Metrics
- **Moderate Tier-Matched SARI (16.33):** Marked as **inconclusive** due to reference misclassification in the Stage 20 draft benchmark.
- **Multi-Reference SARI (29.86):** Remains valid as a cross-reference comparative metric.
- **Stage 25 Engine Behavior:** Correctly preserved semantic structure and educational imperatives without inventing external question prompts.

---

## 2. Taxonomy for Future Dataset Releases

Future corpus curation will strictly segregate candidate pairs into 5 mutually exclusive operational classes:

1. `text_simplification`: Controlled lexical and syntactic simplification preserving prompt format and response mode.
2. `instruction_rephrasing`: Clarifying instruction wording while keeping the same task structure.
3. `activity_format_transformation`: Converting declarative text into multiple-choice or interactive exercises.
4. `question_generation`: Generating comprehension questions from source passages.
5. `response_mode_adaptation`: Modifying the expected learner physical or digital interaction (e.g. naming $\rightarrow$ pointing).

---

## 3. Flagged Locked-Test Draft Reference Defect Register

| Source Item ID | Pair ID | Source Text | Draft Reference Text | Record Type | Review Reason |
|---|---|---|---|---|---|
| `SRC-EN-GRA-0228` | `SIMP-EN-000685` | The curious kitten ran around the wooden fence. | Where did the kitten run? Choose: around. | `activity_format_transformation` | Converted sentence to multiple-choice question |
| `SRC-EN-GRA-0229` | `SIMP-EN-000688` | The curious kitten ran near the wooden fence. | Where did the kitten run? Choose: near. | `activity_format_transformation` | Converted sentence to multiple-choice question |
| `SRC-EN-VOC-0103` | `SIMP-EN-000310` | State the common name of the depicted lion. | Look at the picture. Point to the lion. | `response_mode_adaptation` | Naming request changed to pointing activity |
| `SRC-EN-VOC-0113` | `SIMP-EN-000340` | State the common name of the depicted whale. | Look at the picture. Point to the whale. | `response_mode_adaptation` | Naming request changed to pointing activity |
| `SRC-EN-VOC-0115` | `SIMP-EN-000346` | State the common name of the depicted frog. | Look at the picture. Point to the frog. | `response_mode_adaptation` | Naming request changed to pointing activity |
| `SRC-EN-VOC-0116` | `SIMP-EN-000349` | State the common name of the depicted duck. | Look at the picture. Point to the duck. | `response_mode_adaptation` | Naming request changed to pointing activity |
| `SRC-EN-VOC-0112` | `SIMP-EN-000337` | State the common name of the depicted dolphin. | Look at the picture. Point to the dolphin. | `response_mode_adaptation` | Naming request changed to pointing activity |
| `SRC-EN-GRA-0212` | `SIMP-EN-000637` | Yesterday, the student ate a creative project. | It happened yesterday. Choose the past verb: ate. | `task_reformulation` | Semantic implausibility in source; reformulates to grammar QA |
| `SRC-EN-GRA-0210` | `SIMP-EN-000631` | Yesterday, the student drew a creative project. | It happened yesterday. Choose the past verb: drew. | `task_reformulation` | Reformulates to grammar QA selection |
| `SRC-EN-VOC-0140` | `SIMP-EN-000421` | Observe the character engaging in dancing across the field. | What is happening? The character is dancing. | `question_generation` | Observation instruction converted to question-answer |

---

## 4. Remediation Plan
- **Stage 25 Execution:** No post-hoc tuning or dataset modification occurred on the locked test slice.
- **Next Dataset Stage:** Affected records will be re-annotated by expert linguists into `text_simplification` ground truths vs. separate scaffolding task sets.
