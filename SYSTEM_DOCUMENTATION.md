# AI-Powered Adaptive Language Simplification System
## Complete System Technical & Responsibility Boundaries Documentation (Stage 12)

---

## 1. Executive Summary & Responsibility Boundaries

The **Adaptive Language Simplification System (ALSS)** is an educational support application for children aged 4–8 who may experience language-learning difficulties or may be at risk of Developmental Language Disorder (DLD). 

It personalizes child-friendly English instructions, evaluates activity performance, and maintains four educational indicators: **vocabulary**, **grammar**, **comprehension**, and **instruction-following** performance. These indicators are automatically updated from confirmed learning interactions and are shared with the Personalized Recommendation and Learning Analytics Module (Component 4). 

The component does **not** diagnose DLD and does **not** independently alter the DLD risk indicator received from the screening component (Component 1).

> [!IMPORTANT]
> **Non-Diagnostic Disclaimer:**  
> This application provides educational language support and research-oriented performance tracking. It is **not a diagnostic instrument** and does not replace assessment or advice from qualified speech-language professionals.

```
   ┌──────────────────────────────────────────────────────────────────┐
   │               Component 1: DLD Screening Intake                  │
   │           Read-Only Screening Snapshot (Low / Mod / High)        │
   └────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │           Adaptive Simplification Pipeline             │
       │  • Lexical Substitution (Tier 2/3 -> Tier 1)           │
       │  • Syntactic Chunking & Active S-V-O Transformation     │
       │  • Multimodal Symbol / Visual Cue Scaffolding          │
       └────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │         Multi-Attempt Scaffolding Controller           │
       │   Attempt 1: Baseline Adaptive Instruction             │
       │   Attempt 2: High-Level Linguistic Simplification       │
       │   Attempt 3: Symbol-Assisted Visual Scaffolding        │
       │   Fallback: Adult / Educator Guided Handover           │
       └────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │       Educational Performance Update Engine             │
       │   • Updates primary task domain (Vocab, Gram, etc.)    │
       │   • Increments domain evidence counters                │
       │   • Recalibrates recommended support level             │
       │   • Leaves Component 1 screening risk untouched        │
       └────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │      Component 4: Learning Analytics & Export           │
       │   • Four educational domain scores & evidence counts   │
       │   • Longitudinal trends calculated by Component 4      │
       └────────────────────────────────────────────────────────┘
```

---

## 2. Component Ownership & Inter-System Contracts

| Information / Variable | Component Owner | May this component update it? | Integration Notes |
| :--- | :--- | :---: | :--- |
| **DLD Risk Indicator** | **Component 1** / Authorized Expert | **No** | Stored as a read-only snapshot (`screening_risk_level`). |
| **Screening Version & Date** | **Component 1** | **No** | Used for traceability and audit logs. |
| **Vocabulary Performance** | **This Component** | **Yes** | Updated automatically from vocabulary tasks. |
| **Grammar Performance** | **This Component** | **Yes** | Updated automatically from grammar tasks. |
| **Comprehension Performance** | **This Component** | **Yes** | Updated automatically from comprehension tasks. |
| **Instruction Performance** | **This Component** | **Yes** | Updated automatically from instruction tasks. |
| **Educational Support Level** | **This Component** | **Yes** | Calculates `recommended_support_level` (`mild`, `moderate`, `strong`). |
| **Longitudinal Trend Analytics** | **Component 4** | **By Component 4** | Based on repeated activity evidence over time. |
| **Next Activity Recommendation** | **Component 4** | **By Component 4** | Ingested by this component for activity selection. |
| **Clinical DLD Diagnosis** | **Qualified Expert** | **Never** | Outside the software's responsibility. |

### 2.1 Current Integration Status (Stage 12 Mock Mode)

During Stage 12, group components communicate via local contracts and mock adapters:

```json
{
  "component_1": "mock",
  "component_2_ar": "not_connected",
  "component_4": "not_connected",
  "is_simulated": true,
  "research_eligible": false
}
```

- **Component 1 (Screening)**: Reads simulated profiles from `data/integration_fixtures/component1_inputs/`.
- **Component 2 (AR)**: Generates validated local AR payloads under `data/integration_previews/component2_ar_outputs/`.
- **Component 4 (Analytics)**: Exports four-domain performance payloads under `data/integration_previews/component4_outputs/` with `risk_modified_by_component_3: false`.

---

## 3. Four-Domain Educational Performance Tracking

### 3.1 Primary Domain Targeting
After a confirmed activity session, the system updates **only** the educational performance domain targeted by the activity:

- **Vocabulary Task** $\rightarrow$ updates `vocabulary_score` and increments `vocabulary_evidence_count`.
- **Grammar Task** $\rightarrow$ updates `grammar_score` and increments `grammar_evidence_count`.
- **Comprehension Task** $\rightarrow$ updates `comprehension_score` and increments `comprehension_evidence_count`.
- **Sentence & Instruction Task** $\rightarrow$ updates `instruction_following_score` and increments `instruction_evidence_count`.

### 3.2 Performance Score Formula
Every score update follows the evidence formula:

$$\Delta S = \alpha \cdot \text{BaseDelta}(\text{Outcome}, \text{Attempt}) \cdot \text{DifficultyMultiplier} + \text{SyntaxAdjustment}$$

Where:
- **Base Delta**:
  - Independent Success (Attempt 1): $+5.0$
  - Supported Success (Attempt 2): $+3.0$
  - Supported Success (Attempt 3): $+1.5$
  - Adult Supported Completion: $+2.0$
  - Multi-Attempt Escalation: $-2.5$
- **Difficulty Multiplier**: Easy ($1.0$), Medium ($1.2$), Hard ($1.5$).
- **Syntax Adjustment**: Clean syntax bonus ($+1.0$) or persistent error impact ($-1.0$) for grammar tasks.

### 3.3 Separation of Screening Risk from Educational Support
The clinical risk indicator received from Component 1 (`screening_risk_level`: `low`, `moderate`, `high`) is **immutable** during activity processing. 

This component calculates `recommended_support_level`:
- **Strong Support**: When Composite Learning Support Index $< 48.0$ or target domain score $< 40.0$.
- **Mild Support**: When Composite Learning Support Index $\ge 70.0$ and target domain score $\ge 65.0$.
- **Moderate Support**: All intermediate performance brackets.

---

## 4. Multi-Attempt Scaffolding Pipeline

The system employs a 3-attempt pedagogical framework before adult caregiver escalation:

1. **Attempt 1 (Baseline Adaptive)**: Instruction simplified based on the child's baseline profile and recommended support level.
2. **Attempt 2 (Linguistic Scaffolding)**: Additional lexical simplification, atomic sub-steps, and natural voice read-aloud.
3. **Attempt 3 (Visual Scaffolding)**: High-contrast symbol-assisted visual cues and minimalist directives.
4. **Fallback (Adult Handover)**: Actionable feedback and guided verbal cue recommendations for educators and caregivers.

---

## 5. Database Schema & Data Models

### 5.1 `LearnerProfile`
Stores learner demographics, Component 1 screening metadata, and educational performance scores:
- `id` (UUID, Primary Key)
- `learner_code` (e.g. `CHILD-002`)
- `age` (4–8)
- `screening_risk_level` (String: `low`, `moderate`, `high` — read-only from Component 1)
- `recommended_support_level` (String: `mild`, `moderate`, `strong`)
- `screening_source` (String, default `component_1`)
- `screening_version` (String, default `c1-1.0`)
- `screening_assessed_at` (DateTime)
- `vocabulary_score`, `grammar_score`, `comprehension_score`, `instruction_following_score` (Float, 0–100)
- `vocabulary_evidence_count`, `grammar_evidence_count`, `comprehension_evidence_count`, `instruction_evidence_count` (Integer)
- `performance_scoring_version` (String, default `1.0`)

### 5.2 `TaskResult` (Learning & Evaluation Archive)
Maintains an immutable record of every completed activity session:
- `id` (UUID, Primary Key)
- `session_id`, `learner_id`, `task_id`
- `learner_code`, `task_code`, `task_title`, `category`, `target_skill`, `difficulty`
- `final_outcome`, `attempts_count`, `independent_success`
- `score_before`, `score_after`, `score_deltas`
- `screening_risk_level` (read-only snapshot)
- `recommended_support_level`
- `target_domain` (e.g. `grammar`)
- `evidence_count_before`, `evidence_count_after`
- `score_update_applied` (Boolean flag for idempotency)
- `score_update_event_id` (UUID)
- `scoring_version` (default `1.0`)
- `calculation_snapshot` (JSON input weights & deltas)
- `attempt_history` (JSON array of attempt snapshots)
- `educational_summary_notes` (Educator / clinician summary notes)
- `is_simulated` (Boolean, default `True`)
- `research_eligible` (Boolean, default `False`)
- `completed_at` (DateTime)

---

## 6. Backend API Specification

| Endpoint | Method | Responsibility / Description |
| :--- | :---: | :--- |
| `/api/activities` | `GET` | List curated English language tasks filtered by category/age. |
| `/api/learners` | `GET` | Retrieve learner educational profiles with screening metadata. |
| `/api/activity-sessions` | `POST` | Initialize a new supervised learning activity session. |
| `/api/activity-sessions/{id}/attempts` | `POST` | Generate multi-attempt adaptive instruction with scaffolding. |
| `/api/attempts/{id}/response` | `PATCH` | Record transcribed response and assistance level. |
| `/api/attempts/{id}/confirm-response` | `POST` | Adult confirms transcribed response before scoring. |
| `/api/attempts/{id}/transition` | `POST` | Complete attempt, update primary domain score, persist TaskResult. |
| `/api/results` | `GET` | Query longitudinal learning & evaluation history records. |
| `/api/integration/status` | `GET` | Returns status of external components (`mock`, `not_connected`). |
| `/api/integration-preview/component-4/{id}` | `GET` | Generate local Component 4 performance export preview. |
| `/api/integration-preview/component-2-ar/{id}` | `GET` | Generate local Component 2 AR instruction preview. |
| `/api/integration/component-1/screening-profile` | `POST` | Authorized external screening profile import (guarded in mock mode). |

---

## 7. Limitations Statement

The performance indicators are derived from interactions within this application and are intended to support educational personalization and research analysis. They must not be interpreted as standardized clinical assessment results. The DLD risk indicator is received from the separate screening component (Component 1) and is not automatically changed by the language simplification component.
