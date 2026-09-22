# AI-Powered Adaptive Language Simplification System
## Complete System Technical & Functional Documentation

---

## 1. Executive Summary & Research Background

The **Adaptive Language Simplification System (ALSS)** is an evidence-based clinical and educational MVP engineered to assist children with Language Impairments (LI), Developmental Language Disorder (DLD), and associated cognitive processing challenges. 

Standard pedagogical software presents static instructional language that often imposes an unmanageable **extraneous cognitive load** on struggling learners. ALSS dynamically evaluates a child's linguistic capabilities (e.g., vocabulary mastery, syntax comprehension, working memory limits, processing speed) and progressively simplifies task instructions across lexical, syntactic, and multimodal dimensions.

Furthermore, ALSS incorporates an automated **Dynamic Profile Evolution & Risk Transition Engine**, transforming every learning interaction into a diagnostic data point that continuously updates the child's developmental profile, recalibrates their **Composite Language Index (CLI)**, and adjusts their clinical **Risk Classification** (High, Moderate, Low/Mild).

```
   ┌──────────────────────────────────────────────────────────────────┐
   │                    Learner Interaction Loop                     │
   └────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │               Dynamic Assessment Intake                │
       │   Learner Profile (Vocab, Grammar, Working Memory)     │
       └────────────────────────────┬───────────────────────────┘
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
       │       Dynamic Profile Evolution & Analytics Engine      │
       │   • Delta Score Calculation (Δ Vocab, Δ Grammar)       │
       │   • Composite Language Index (CLI) Recalibration       │
       │   • Risk Level Transition (High -> Moderate -> Low)    │
       │   • Full Session Snapshot Stored in Database           │
       └────────────────────────────────────────────────────────┘
```

---

## 2. Core Architectural Overview

The application follows a decoupled modern client-server architecture:

```
[ Frontend: React + Vite + Tailwind/CSS Modules ]
                    │
         HTTP / REST / WebSockets
                    │
                    ▼
[ Backend: FastAPI (Python 3.10+) ]
  ├── Simplification Service (NLP & LLM Engine - Google Gemini API)
  ├── Multi-Attempt Retry & Scaffolding Controller
  ├── Dynamic Profile Evolution Engine
  ├── Session & History Analytics Service
  └── Security, Privacy & Audit Logging Layer
                    │
                    ▼
[ Database Layer: SQLite / SQLAlchemy ORM ]
  ├── Learner Profiles
  ├── Interactive Tasks
  ├── Activity Sessions
  ├── Task Evaluation Histories (Diagnostic Archive)
  └── Audit Logs
```

### 2.1 Technology Stack

| Layer | Component / Tool | Role / Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite | High-performance interactive Single Page Application (SPA) |
| **Styling & UI** | Lucide-React, Custom CSS | Child-friendly, accessible design with high readability & contrast |
| **Backend** | FastAPI, Uvicorn | Asynchronous Python REST API framework |
| **AI / NLP** | Google Gemini API (`gemini-1.5-flash` / `gemini-pro`) | Real-time adaptive linguistic simplification & validation |
| **Database** | SQLite + SQLAlchemy ORM | Local relational storage of profiles, tasks, and historical session diagnostics |
| **Audio / Speech** | Web Speech API (TTS & STT) | Multimodal speech synthesis and speech-to-text input |

---

## 3. Dynamic Simplification & Scaffolding Pipeline

### 3.1 Three-Tier Simplification Strategy

When a learner receives an instructional prompt, ALSS applies three coordinated simplification layers based on the child's real-time baseline scores:

1. **Lexical Simplification**:
   - Replaces low-frequency or polysemous words (Tier 2/3) with high-frequency, concrete equivalents (Tier 1).
   - Constrains vocabulary to the child's estimated lexical age bracket.
2. **Syntactic & Structural Simplification**:
   - Deconstructs passive voice into direct Subject-Verb-Object (S-V-O) declarative structures.
   - Splits compound and complex sentences containing relative clauses, conditional triggers, or subordinate clauses into distinct sequential chunks.
   - Caps Maximum Sentence Length according to the child's working memory span (e.g., max 5-7 words for high-risk profiles).
3. **Multimodal & Visual Scaffolding**:
   - Augments textual instruction with color-coded key phrases, pictographic icons, and structured clue cards to reduce working memory strain.

---

## 4. Multi-Attempt Retry & Scaffolding Workflow

The system provides a structured 3-attempt pedagogical framework before escalating to adult caregiver intervention:

```
+-------------------------------------------------------------------------------+
|                             ATTEMPT 1: BASELINE                               |
| • Prompt simplified according to baseline profile                             |
| • Standard interactive choice or input UI                                     |
+---------------------------------------+---------------------------------------+
                                        │
                         [Incorrect / Timeout / Hint]
                                        ▼
+-------------------------------------------------------------------------------+
|                     ATTEMPT 2: LINGUISTIC SCAFFOLDING                         |
| • Instruction further simplified (shorter sentences, active voice)           |
| • Difficult vocabulary replaced with ultra-basic root words                   |
| • Audio narration automatically highlighted                                  |
+---------------------------------------+---------------------------------------+
                                        │
                         [Incorrect / Timeout / Hint]
                                        ▼
+-------------------------------------------------------------------------------+
|                       ATTEMPT 3: MULTIMODAL CUEING                            |
| • Minimalist directive (e.g., "Look at the big cat.")                        |
| • Visual Symbol / Icon representation injected                                |
| • High-contrast focus cue on target choices                                   |
+---------------------------------------+---------------------------------------+
                                        │
                                   [Incorrect]
                                        ▼
+-------------------------------------------------------------------------------+
|                       FALLBACK: ADULT HANDOVER                                |
| • Constructive feedback displayed for educator/parent                         |
| • Recommended verbal cue and physical prompt guidance                         |
| • Session recorded with adult support flag                                    |
+-------------------------------------------------------------------------------+
```

---

## 5. Dynamic Profile Evolution & Risk Transition Engine

### 5.1 Real-Time Score Adaptation Model

Every task completed updates the child's profile parameters using an evidence-based differential formula:

$$\Delta S = \alpha \cdot \text{OutcomeFactor} \cdot \text{DifficultyWeight} \cdot \text{AttemptPenalty}$$

Where:
- **Outcome Factor**: $+1.0$ for independent success, $+0.3$ to $+0.5$ for supported success, $-0.4$ for unassisted errors.
- **Attempt Penalty**:
  - Attempt 1: $1.0$ (Full credit)
  - Attempt 2: $0.65$ (Partial credit)
  - Attempt 3: $0.35$ (Minimal credit)
  - Adult Handover: $0.0$ to negative correction
- **Target Metrics Updated**:
  - `vocabulary_score` ($0 - 100$)
  - `grammar_score` ($0 - 100$)
  - `working_memory_score` ($0 - 100$)
  - `processing_speed_score` ($0 - 100$)
  - `attention_score` ($0 - 100$)

### 5.2 Composite Language Index (CLI)

The **Composite Language Index (CLI)** provides a single unified metric of the learner's overall language capability:

$$\text{CLI} = 0.35 \cdot \text{Vocab} + 0.35 \cdot \text{Grammar} + 0.15 \cdot \text{Memory} + 0.10 \cdot \text{ProcessingSpeed} + 0.05 \cdot \text{Attention}$$

### 5.3 Automated Risk Level Transition Rules

The clinical risk profile automatically updates based on the recalculated CLI and skill balances:

| Risk Level | Composite Language Index (CLI) Threshold | Description | Simplification Behavior |
| :--- | :--- | :--- | :--- |
| **High Risk** | $\text{CLI} < 45.0$ | Severe language comprehension and working memory barriers | Maximum simplification, max sentence length 5 words, symbol icons mandatory |
| **Moderate Risk** | $45.0 \le \text{CLI} < 75.0$ | Emerging syntax and vocabulary mastery with occasional scaffold needs | Moderate simplification, Tier 1/2 vocabulary blend, active voice |
| **Low / Mild Risk** | $\text{CLI} \ge 75.0$ | High functional competence; near age-appropriate language comprehension | Minimal simplification, rich vocabulary, standard sentence complexity |

When a learner with a **High Risk** profile consistently succeeds, their scores increase, and their risk classification dynamically shifts to **Moderate**, instantly adapting subsequent task instructions.

---

## 6. Database Schema & Data Models

The system persistence layer is built on SQLite with SQLAlchemy ORM models:

### 6.1 `LearnerProfile`
Stores learner demographic and linguistic assessment parameters:
- `id` (UUID, Primary Key)
- `learner_code` (e.g., `CHILD-002`)
- `name`, `age`, `native_language`
- `risk_level` (`high`, `moderate`, `low`)
- `vocabulary_score` (Float, 0-100)
- `grammar_score` (Float, 0-100)
- `working_memory_score` (Float, 0-100)
- `processing_speed_score` (Float, 0-100)
- `attention_score` (Float, 0-100)
- `composite_language_index` (Float, 0-100)
- `created_at`, `updated_at`

### 6.2 `Task`
Defines pedagogical exercises and language activities:
- `id` (UUID, Primary Key)
- `task_code` (e.g., `TASK-GRAM-001`)
- `title`, `description`
- `category` (`vocabulary`, `grammar`, `comprehension`, `executive_function`)
- `target_skill` (e.g., `word_order_svo`, `tier2_adjectives`)
- `baseline_instruction` (Original unsimplified prompt)
- `difficulty` (`easy`, `medium`, `hard`)
- `content_payload` (JSON options, correct answers, symbols)

### 6.3 `TaskEvaluationHistory` (Diagnostic Archive)
Maintains an immutable audit log of every task executed:
- `id` (UUID, Primary Key)
- `session_id` (ForeignKey `activity_sessions.id`)
- `learner_id` (ForeignKey `learner_profiles.id`)
- `learner_code` (String, e.g. `CHILD-002`)
- `learner_age` (Integer)
- `task_id` (ForeignKey `tasks.id`)
- `task_code` (String, e.g. `TASK-GRAM-001`)
- `task_title`, `category`, `target_skill`, `difficulty`
- `final_outcome` (`success`, `completed_with_adult_support`, `adult_support_required`)
- `attempts_count` (1, 2, or 3)
- `independent_success` (Boolean)
- `score_before` (JSON dictionary of pre-session metrics)
- `score_after` (JSON dictionary of post-session metrics)
- `score_deltas` (JSON dictionary of calculated $\Delta$ changes)
- `risk_changed` (Boolean flag)
- `composite_language_index` (Float, post-session CLI)
- `attempt_history` (JSON array of attempt snapshots: instructions, selections, times)
- `diagnostic_notes` (Educator / clinician summary notes)
- `created_at` (Timestamp)

---

## 7. Backend API Specification

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/learners/` | List all registered learner profiles |
| `GET` | `/api/v1/learners/{id}` | Retrieve specific learner profile with full metrics |
| `POST` | `/api/v1/learners/` | Create a new learner profile |
| `GET` | `/api/v1/tasks/` | Fetch pedagogical tasks filtered by category or skill |
| `POST` | `/api/v1/simplify/instruction` | Generate real-time multi-level simplification for a task |
| `POST` | `/api/v1/sessions/evaluate-task` | Submit completed task, calculate score deltas, evolve profile, record history |
| `GET` | `/api/v1/sessions/evaluations/learner/{code}` | Retrieve diagnostic evaluation history for a learner |
| `GET` | `/api/v1/sessions/evaluations/latest` | Fetch most recent evaluation across all sessions |
| `POST` | `/api/v1/scenarios/run` | Execute automated test scenarios against research benchmarks |

---

## 8. Frontend Interface & Key Components

1. **Guided Playground (`GuidedPlayground.jsx`)**:
   - Primary child-facing task execution view.
   - Interactive speech synthesizer (Read Aloud) and voice recognition.
   - Real-time scaffolding reveal on retry (text chunking, visual cues).
   - Instant diagnostic outcome modal with score delta ($\Delta$) visualization.
2. **Diagnostic History & Analytics (`EvaluationHistoryView.jsx`)**:
   - Chronological breakdown of all completed sessions.
   - Pre vs. Post score comparisons with color-coded delta indicators ($+\Delta$, $-\Delta$).
   - Risk transition timeline (e.g., tracking evolution from High $\rightarrow$ Moderate).
   - Attempt-by-attempt diagnostic transcript reader.
3. **Learner Management & Dashboard (`LearnerProfiles.jsx`)**:
   - Radar charts and metric bars for Vocabulary, Grammar, Memory, and Processing Speed.
   - Rapid learner switching for multi-child clinical sessions.
4. **Scenario Evaluation Lab (`ScenarioEvaluation.jsx`)**:
   - Batch evaluation tool to validate simplification algorithms against standard DLD baseline datasets.

---

## 9. Setup & Execution Instructions

### 9.1 Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Valid Google Gemini API Key (set in `.env`)

### 9.2 Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### 9.3 Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 9.4 Environment Variables Configuration
**Backend (`backend/.env`)**:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
DATABASE_URL=sqlite:///./language_simplification.db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DEBUG=True
```

---

## 10. Research Validation & Future Extensions

1. **Longitudinal Learning Curve Tracking**:
   - Advanced Bayesian Knowledge Tracing (BKT) to model memory decay and retention over multi-week intervals.
2. **Multilingual DLD Adaptation**:
   - Cross-lingual transfer for bilingual learners experiencing code-switching and dual-language syntactic challenges.
3. **Acoustic & Prosodic Simplification**:
   - Dynamic modulation of speech rate, fundamental frequency ($F_0$), and syllable pauses during TTS playback based on processing speed deficits.
