# AI-Powered Adaptive Child-Friendly Language Support System (MVP)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF.svg?logo=vite)](https://vitejs.dev/)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4.svg?logo=google)](https://ai.google.dev/)
[![SQLite](https://img.shields.io/badge/Database-SQLite%20%2F%20SQLAlchemy-003B57.svg?logo=sqlite)](https://sqlite.org/)

**Scope:** English Language Comprehension & Instruction Personalization, Ages 4–8  
**Domain:** Educational Language Simplification, Multi-Attempt Scaffolding, and Learning Performance Tracking  
**System Documentation:** [SYSTEM_DOCUMENTATION.md](file:///c:/Users/Lasindu/Documents/GitHub/Language_Simplification_MVP/SYSTEM_DOCUMENTATION.md)  
**System Concept & Theory:** [SYSTEM_CONCEPT.md](file:///c:/Users/Lasindu/Documents/GitHub/Language_Simplification_MVP/SYSTEM_CONCEPT.md)  
**Research Specification:** [RESEARCH_README.md](file:///c:/Users/Lasindu/Documents/GitHub/Language_Simplification_MVP/RESEARCH_README.md)

> [!IMPORTANT]
> **Educational & Non-Diagnostic Disclaimer:**  
> This application provides educational language support and research-oriented performance tracking. It is **not a diagnostic instrument** and does not replace assessment, screening, or advice from qualified speech-language pathologists or medical professionals.

---

## 🏛️ Responsibility Boundaries & Component Architecture

In accordance with the multi-component research framework, the system maintains strict responsibility boundaries:

| Information / Responsibility | Owner | May this component update it? | Boundary Notes |
| :--- | :--- | :---: | :--- |
| **DLD Risk Indicator** | **Component 1** / Authorized Clinician | **No** | Stored as a **read-only screening snapshot** (`screening_risk_level`). |
| **Screening Provenance** | **Component 1** | **No** | Version and assessment timestamps for traceability. |
| **Vocabulary Performance** | **This Component** | **Yes** | Updated automatically from confirmed vocabulary tasks. |
| **Grammar Performance** | **This Component** | **Yes** | Updated automatically from confirmed grammar tasks. |
| **Comprehension Performance** | **This Component** | **Yes** | Updated automatically from confirmed comprehension tasks. |
| **Instruction-Following Performance** | **This Component** | **Yes** | Updated automatically from confirmed sentence & instruction tasks. |
| **Educational Support Level** | **This Component** | **Yes** | Calculates `recommended_support_level` (`mild`, `moderate`, `strong`) for scaffolding. |
| **Longitudinal Trend Analytics** | **Component 4** | **By Component 4** | Component 4 receives domain scores and evidence to calculate long-term progression. |
| **Clinical Diagnosis** | **Qualified Expert** | **Never** | Clinical diagnoses are outside the software's scope. |

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

## 🌟 Key Features & Capabilities

### 1. Dynamic Cognitive Load Reduction & Simplification
- **Lexical Simplification**: Dynamically substitutes Tier 2/3 abstract vocabulary with age-appropriate Tier 1 root words.
- **Syntactic & Structural Chunking**: Converts complex, passive-voice sentences into short, active Subject-Verb-Object (S-V-O) sequences tailored to working memory limits.
- **Multimodal Visual Scaffolding**: Enriches instructional prompts with pictographic symbols, color tags, and visual focus cues.

### 2. Multi-Attempt Retry & Scaffolding Controller
- **Attempt 1 (Baseline Adaptive)**: Instruction simplified based on the child's baseline profile.
- **Attempt 2 (Linguistic Scaffolding)**: Additional lexical simplification, shorter phrases, and voice synthesis support.
- **Attempt 3 (Visual Cueing)**: High-contrast symbol-assisted visual cues and minimalist directives.
- **Fallback (Adult Handover)**: Actionable educational feedback and guided verbal prompt recommendations for educators and caregivers.

### 3. Automated 4-Domain Educational Performance Tracking
- **Primary Domain Targeting**: Completed activities update only the specific domain targeted by the task:
  - `vocabulary_score` & `vocabulary_evidence_count`
  - `grammar_score` & `grammar_evidence_count`
  - `comprehension_score` & `comprehension_evidence_count`
  - `instruction_following_score` & `instruction_evidence_count`
- **Recommended Support Level**: Continuously recalculates `recommended_support_level` (`mild`, `moderate`, `strong`) for pedagogical adaptation without modifying clinical screening risk.
- **Idempotent Single Application**: Ensures duplicate submissions cannot alter scores multiple times.

### 4. Cross-Component Integration Contracts & Previews
- **Component 1 (Screening)**: Validated mock adapter loading simulated screening profiles with `is_simulated: true`.
- **Component 2 (AR)**: Local AR payload preview generation (`data/integration_previews/component2_ar_outputs/`).
- **Component 4 (Analytics)**: Structured performance export contract (`data/integration_previews/component4_outputs/`) with explicit `risk_modified_by_component_3: false`.

### 5. Protected Child View
- Distraction-free, friendly child view strictly hiding all risk levels, performance scores, grammar error codes, and clinical terms.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** and **npm**
- **Google Gemini API Key** (optional for live LLM generation; rule-based fallback works offline)

---

### 1. Backend Setup

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```powershell
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables in `backend/.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   DATABASE_URL=sqlite:///./adaptive_learning.db
   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   DEBUG=True
   COMPONENT1_MODE=mock
   COMPONENT2_MODE=mock
   COMPONENT4_MODE=mock
   ENABLE_COMPONENT1_EXTERNAL_IMPORT=false
   ```

5. Apply database migrations:
   ```bash
   python -m alembic upgrade head
   ```

6. Start the FastAPI development server:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```
   - Swagger API Documentation: `http://localhost:8000/docs`
   - Integration Status: `http://localhost:8000/api/integration/status`

---

### 2. Frontend Setup

1. In a new terminal, navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   - Application URL: `http://localhost:5173`

---

### 3. Automated Test Suite

Run backend automated unit and integration tests:
```bash
cd backend
python -m pytest tests/ -v
```

---

## 📁 Repository Structure

```
Language_Simplification_MVP/
├── README.md                      # Project Overview & Quick Start
├── SYSTEM_DOCUMENTATION.md        # Comprehensive Architecture & Technical Specifications
├── SYSTEM_CONCEPT.md              # Theoretical & Pedagogical Foundations
├── RESEARCH_README.md             # Research & Experimental Design Notes
├── backend/                       # FastAPI Backend Application
│   ├── app/
│   │   ├── api/                   # REST API Routers & Integration Previews
│   │   ├── core/                  # Settings & Integration Modes
│   │   ├── database/              # SQLAlchemy Models & Migrations
│   │   ├── integrations/          # Component 1, AR, and Component 4 Mock Adapters
│   │   │   ├── common/            # Integration Statuses & Error Hierarchy
│   │   │   ├── component1/        # Component 1 Screening Input Contract
│   │   │   ├── component2_ar/     # Component 2 AR Output Contract
│   │   │   └── component4/        # Component 4 Performance Export Contract
│   │   ├── personalization/       # Profile Updater (4-Domain Scoring & Support Level)
│   │   ├── retry_controller/      # Multi-Attempt Scaffolding & Escalation Manager
│   │   ├── security/              # Data Privacy & Input Sanitizer
│   │   └── services/              # Session, Adaptation & Simplification Services
│   ├── tests/                     # Automated Pytest Suite
│   └── requirements.txt           # Python Dependencies
├── frontend/                      # React SPA Application
│   ├── src/
│   │   ├── components/            # Guided Playground, Learner Browser, Results History
│   │   ├── services/api.js        # API Client & Integration Endpoints
│   │   └── App.jsx                # Navigation & Root Layout
│   └── package.json               # Frontend Dependencies & Scripts
└── data/                          # Seed Data & Integration Fixtures
    ├── integration_fixtures/      # Golden Test Fixtures (Component 1, AR, Component 4)
    ├── integration_previews/      # Generated Local Previews
    ├── application_tasks/         # Curated Task Repository
    └── learner_profiles/          # Simulated Learner Profiles
```

---

## 🔬 Limitations & Ethical Research Statement

The performance indicators are derived from interactions within this application and are intended to support educational personalization and research analysis. They must not be interpreted as standardized clinical assessment results. The DLD risk indicator is received from the separate screening component (Component 1) and is not automatically changed by the language simplification component.
