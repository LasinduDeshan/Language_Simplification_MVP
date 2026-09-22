# English-First Adaptive Child-Friendly Language Support MVP (v2.2)
## Comprehensive Research Documentation & Empirical Benchmark Packaging

**Project:** English-First Adaptive Child-Friendly Language Support System  
**Target Population:** Children aged 4 to 8 at risk of Developmental Language Disorder (DLD)  
**Document Compliance:** Version 2.2 Specification  
**Architecture:** 6-Sprint Modular Full-Stack Research System  

---

## 1. Executive Summary

This repository houses the complete, validated research prototype for the **English-First Adaptive Child-Friendly Language Support System (MVP v2.2)**. The platform solves a critical challenge in educational technology: standard instruction generation engines frequently produce linguistically overwhelming, syntactically complex, or solution-leaking prompts that disadvantage children with Developmental Language Disorder (DLD).

The system implements a **multi-tiered adaptive pipeline** that:
1. **Analyzes child responses** across semantic concept matching, acoustic confidence gating ($\ge 0.70$), and offline DLD grammar error identification.
2. **Escalates support deterministically** across Attempts 1, 2, and 3 through explainable rule templates and hybrid LLM generation.
3. **Enforces strict child safety & anti-leakage**: Enforces $\le 8\text{--}10$ words target sentence length (maximum 12 words), zero punitive language, zero clinical jargon, and prevents task solutions or subject-answer relation bindings from premature revelation.
4. **Seamlessly interfaces with simulated external subsystems**: Dispatches structured payloads to Component 1 (Task Delivery), Component 3 (Augmented Reality Subsystem), and Component 4 (Learner Modeling / Analytics).
5. **Provides formal scientific evaluation**: Incorporates a 5-dimension Likert expert evaluation rubric and one-click modular data packaging (CSV, JSON, ZIP).

---

## 2. Clinical & Pedagogical Framework

Children with DLD encounter significant barriers with multi-clause instructions, passive voice, low-frequency abstract vocabulary, and ambiguous spatial prepositions.

### Developmental Constraints Enforced
| Constraint | Policy Boundary | Clinical Rationale |
| :--- | :--- | :--- |
| **Sentence Length** | Target $\le 8\text{--}10$ words; Strict Max $12$ words | Prevents phonological working memory overload. |
| **Action Density** | Single atomic action per instruction | Children with DLD struggle with multiple sequential commands in a single prompt. |
| **Vocabulary Level** | Pre-A1 / A1 CEFR; Concrete nouns & verbs | Abstract classroom jargon is systematically replaced with high-frequency concrete equivalents. |
| **Anti-Leakage** | Solution assertion & relation binding blocked | Preserves pedagogical validity; allows candidate options while forbidding answers. |
| **Affective Safety** | 0 punitive words (*"wrong"*, *"failed"*) | Encourages persistence and prevents educational anxiety. |
| **Jargon Privacy** | Clinical codes strictly hidden from child | Diagnostic codes (`missing_preposition`, `pronoun_case_error`) are researcher-facing only. |

---

## 3. System Architecture & 6-Sprint Roadmap

```
+-----------------------------------------------------------------------------------+
|                        RESEARCH FRONTEND INTERFACE (React + Vite)                  |
|  - Scenario Dashboard  - Safety Sandbox  - Personalization  - LLM Studio - Eval   |
+-----------------------------------------------------------------------------------+
                                         │
                                REST API (FastAPI)
                                         │
+-----------------------------------------------------------------------------------+
|                                 CORE BACKEND                                      |
|                                                                                   |
|  [Sprint 1: Foundation]    [Sprint 2: Analysis]      [Sprint 3: Personalization]  |
|  - 10 Relational Tables    - Semantic Concept Check  - PersonalizationController  |
|  - 10 Curated Tasks        - Acoustic Gating (<0.7)  - 3-Attempt Rule Templates   |
|  - 5 Learner Profiles      - spaCy DLD Grammar Rules - Explainable Reason Codes   |
|                                                                                   |
|  [Sprint 4: Safety/Retry]  [Sprint 5: LLM & Payloads] [Sprint 6: Eval & Exports]  |
|  - Relation-Aware Leakage  - Multi-Provider LLM      - 5-Dim Likert Rubric Rubric |
|  - Child Suitability Gate  - Hybrid Safety Fallback  - Modular CSV / ZIP Bundler  |
|  - 3-Attempt Retry Machine - External Payloads (1,3,4) - Dataset Export CLI        |
+-----------------------------------------------------------------------------------+
                                         │
                                   SQLAlchemy ORM
                                         │
+-----------------------------------------------------------------------------------+
|                     PERSISTENCE LAYER (SQLite: adaptive_learning.db)              |
|  - tasks                   - learner_profiles         - experiment_runs           |
|  - adaptations             - attempts                 - validation_results        |
|  - performance_patterns    - language_observations    - integration_events        |
|  - expert_evaluations                                                             |
+-----------------------------------------------------------------------------------+
```

---

## 4. Formal Research Hypotheses

- **Hypothesis 1 (Scaffolding Progression)**: Progressive simplification across Attempts 1, 2, and 3 (from simplified goal $\to$ single atomic sub-step $\to$ binary choice with pointing cues) achieves significantly higher concept attainment than static instruction repetition.
- **Hypothesis 2 (Anti-Leakage Boundary)**: Relation-aware leakage detection (`subject -> answer`) effectively distinguishes between pedagogical candidate presentation (*"Look at fish. Choose: water or tree?"*) and invalid solution disclosure (*"The fish lives in water"*).
- **Hypothesis 3 (Hybrid Safety Gate)**: Validating LLM candidate instructions prior to presentation eliminates the risk of hallucinated answers or excessive verbosity, with automated fallback to deterministic rules ensuring zero disruption.

---

## 5. Expert Evaluation Rubric (5 Likert Dimensions)

All adaptations can be evaluated by clinical and pedagogical experts on a 1–5 Likert scale:

1. **Age Appropriateness (1–5)**:
   - Evaluates syntactic simplicity, sentence length, and developmental suitability for children aged 4 to 8.
   - *5 = Ideal for young children; 1 = Complex adult syntax.*
2. **Clarity (1–5)**:
   - Evaluates whether the instruction specifies exactly one actionable step with unambiguous visual focus.
   - *5 = Crystal clear, direct command; 1 = Ambiguous or multi-step.*
3. **Grammar Correctness (1–5)**:
   - Evaluates grammatical simplicity while avoiding structures confusing to children with DLD (e.g. passive voice, nested relative clauses).
   - *5 = Grammatically flawless simple English; 1 = Confusing syntax or grammatical errors.*
4. **Meaning Preservation (1–5)**:
   - Evaluates whether the core learning objective is preserved without altering task goals or leaking the answer.
   - *5 = Perfectly aligned with task objective; 1 = Task goal altered or solution disclosed.*
5. **Personalization Suitability (1–5)**:
   - Evaluates alignment with the learner’s specific risk profile, English proficiency level, and current attempt scaffold tier.
   - *5 = Optimal support intensity; 1 = Mismatched difficulty.*

---

## 6. Research Data Exports Data Dictionary

The platform provides complete data export capabilities via `GET /api/export/...` and the CLI tool `scripts/export_benchmark_dataset.py`.

### 1. `experiments.csv`
| Column | Type | Description |
| :--- | :--- | :--- |
| `experiment_id` | UUID | Unique experiment run identifier |
| `learner_code` | String | Pseudonymized learner code (`CHILD-001` .. `CHILD-005`) |
| `task_code` | String | Task identifier (`TASK-ENG-001` .. `TASK-ENG-010`) |
| `generation_mode` | Enum | Generation strategy: `rule`, `llm`, `hybrid` |
| `status` | Enum | Run status: `active`, `completed`, `escalated` |
| `final_outcome` | Enum | Final outcome: `success`, `adult_support` |
| `attempts_count` | Integer | Total child attempts made ($1 \le n \le 3$) |
| `started_at` | ISO-8601 | Experiment initialization timestamp |
| `completed_at` | ISO-8601 | Experiment completion timestamp |

### 2. `adaptations.csv`
| Column | Type | Description |
| :--- | :--- | :--- |
| `adaptation_id` | UUID | Unique adaptation identifier |
| `experiment_run_id` | UUID | Foreign key to experiment run |
| `task_code` | String | Associated task code |
| `learner_code` | String | Targeted learner profile |
| `target_attempt_number` | Integer | Scaffolding tier (1, 2, or 3) |
| `support_level` | Enum | Intensity: `mild`, `moderate`, `strong` |
| `generation_method` | Enum | Generator used: `rule`, `llm`, `hybrid`, `fallback` |
| `child_instruction` | String | The actual simplified instruction presented |
| `word_count` | Integer | Total words in instruction ($\le 12$) |
| `answer_format` | Enum | Response modality (`speech`, `two_picture_choice`, etc.) |
| `provider` | String | Generation provider (e.g. `local_rule_engine`, `simulated_llm`) |
| `model_name` | String | Model identifier (`rule_v1`, `gemini-1.5-flash-simulated`) |
| `processing_time_ms` | Integer | Generator response latency in milliseconds |
| `estimated_cost` | Decimal | Incurred token cost in USD |

### 3. `attempts.csv`
| Column | Type | Description |
| :--- | :--- | :--- |
| `attempt_id` | UUID | Unique attempt record identifier |
| `experiment_run_id` | UUID | Foreign key to experiment run |
| `adaptation_id` | UUID | Foreign key to exact adaptation displayed |
| `attempt_number` | Integer | Attempt sequence number (1, 2, or 3) |
| `instruction_shown` | String | Text of instruction displayed to child |
| `speech_transcript` | String | Cleaned child speech transcript |
| `speech_confidence` | Float | ASR confidence score ($0.0 \le c \le 1.0$) |
| `concept_result` | Enum | Evaluated outcome: `correct`, `partial`, `incorrect`, `unclear` |
| `response_time_ms` | Integer | Child response latency in milliseconds |
| `completion_status` | Enum | `completed`, `skipped`, `incomplete` |

### 4. `expert_evaluations.csv`
| Column | Type | Description |
| :--- | :--- | :--- |
| `evaluation_id` | UUID | Unique evaluation identifier |
| `adaptation_id` | UUID | Foreign key to evaluated adaptation |
| `evaluator_code` | String | Pseudonymized expert code (`SLP-EXPERT-01`, etc.) |
| `generation_method` | String | Generator method evaluated (`rule`, `llm`, `hybrid`) |
| `age_appropriateness` | Integer (1–5) | Likert score: Age Appropriateness |
| `clarity` | Integer (1–5) | Likert score: Clarity |
| `grammar_correctness` | Integer (1–5) | Likert score: Grammar Correctness |
| `meaning_preservation`| Integer (1–5) | Likert score: Meaning Preservation |
| `personalization_suitability` | Integer (1–5) | Likert score: Personalization Suitability |
| `mean_score` | Float | Average Likert score across 5 dimensions |
| `comments` | Text | Qualitative clinical feedback |

---

## 7. Reproduction & Execution Guidelines

### 1. Running the Automated Test Suite (41 Tests)
Execute all test suites across Sprints 1 through 6:
```powershell
cd backend
python -m pytest tests/ -v
```

### 2. Exporting Research Datasets via CLI
Dump the complete benchmark dataset directly to `data/research_exports/`:
```powershell
python scripts/export_benchmark_dataset.py
```

### 3. Starting the Backend Server
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Interactive OpenAPI Swagger Docs available at: `http://127.0.0.1:8000/docs`.

### 4. Starting the Frontend Research Interface
```powershell
cd frontend
npm run dev
```
Access the application at `http://localhost:5173/`.
Navigate to:
- **"Evaluation & Research"** tab: Live 5-dimension Likert scoring, aggregate benchmark radar/bar charts, and one-click ZIP/CSV export center.
- **"LLM & Integrations"** tab: Side-by-side Rule vs LLM vs Hybrid generator comparator and 3D AR tabletop visualizer simulator.
- **"Safety & Retry"** tab: Live 7-preset anti-leakage sandbox and 3-attempt state machine simulator.
- **"Dashboard & Simulation"** tab: End-to-end 20 development scenario browser and child delivery preview.
