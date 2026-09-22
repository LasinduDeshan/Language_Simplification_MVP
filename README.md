# AI-Powered Adaptive Child-Friendly Language Simplification System (MVP)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF.svg?logo=vite)](https://vitejs.dev/)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4.svg?logo=google)](https://ai.google.dev/)
[![SQLite](https://img.shields.io/badge/Database-SQLite%20%2F%20SQLAlchemy-003B57.svg?logo=sqlite)](https://sqlite.org/)

**Scope:** English Language Comprehension, Ages 4–8  
**Domain:** Personalized Real-Time Language Simplification & Diagnostic Profile Evolution for Children with Language Impairments (LI) and Developmental Language Disorder (DLD)  
**Comprehensive System Documentation:** [SYSTEM_DOCUMENTATION.md](file:///c:/Users/Lasindu/Documents/GitHub/Language_Simplification_MVP/SYSTEM_DOCUMENTATION.md)  
**System Concept & Theory:** [SYSTEM_CONCEPT.md](file:///c:/Users/Lasindu/Documents/GitHub/Language_Simplification_MVP/SYSTEM_CONCEPT.md)  
**Research Specification:** [RESEARCH_README.md](file:///c:/Users/Lasindu/Documents/GitHub/Language_Simplification_MVP/RESEARCH_README.md)

---

## 🌟 Key Features & Capabilities

### 1. Dynamic Cognitive Load Reduction & Simplification
- **Lexical Simplification**: Dynamically substitutes Tier 2/3 abstract vocabulary with age-appropriate Tier 1 root words.
- **Syntactic & Structural Chunking**: Converts complex, passive-voice sentences into short, active Subject-Verb-Object (S-V-O) sequences tailored to working memory capacity.
- **Multimodal Visual Scaffolding**: Enriches instructional prompts with pictographic symbols, color tags, and visual focus cues.

### 2. Multi-Attempt Retry & Scaffolding Controller
- **Attempt 1 (Baseline Adaptive)**: Instruction simplified based on the child's baseline profile.
- **Attempt 2 (Linguistic Scaffolding)**: Additional lexical simplification, shorter phrases, and voice synthesis support.
- **Attempt 3 (Visual Cueing)**: High-contrast symbol-assisted visual cues and minimalist directives.
- **Fallback (Adult Handover)**: Actionable diagnostic feedback and guided verbal prompt recommendations for educators and caregivers.

### 3. Real-Time Dynamic Profile Evolution & Risk Transition
- **Automated Score Deltas ($\Delta$)**: Updates `vocabulary_score`, `grammar_score`, `working_memory_score`, and `processing_speed_score` in real time based on task outcomes and attempt efficiency.
- **Composite Language Index (CLI)**: Recalculates a unified weighted language score after every interaction.
- **Risk Level Progression**: Automatically shifts risk levels (e.g. **High $\rightarrow$ Moderate $\rightarrow$ Low**) as the child demonstrates sustained improvement.

### 4. Comprehensive Diagnostic & Evaluation History
- Stores every completed task interaction in `task_evaluation_history` table.
- Records pre-session scores, post-session scores, exact deltas, attempt snapshots, response times, and educator diagnostic notes.
- Dedicated UI to review chronological progress, trend charts, and risk evolution history.

### 5. Multimodal Voice Interaction
- Integrated **Web Speech API** for both Text-to-Speech (TTS) natural voice read-aloud and Speech-to-Text (STT) voice recognition responses.

---

## 🏛️ Architecture Overview

```
[ Frontend: React + Vite + Lucide Icons ]
                    │
           REST API / JSON Payloads
                    │
                    ▼
[ Backend: FastAPI (Python 3.10+) ]
  ├── Simplification Service (Google Gemini API + Deterministic Fallbacks)
  ├── Multi-Attempt Retry & Scaffolding Controller
  ├── Dynamic Profile Evolution Engine (CLI & Risk Transitions)
  ├── Task & Session Evaluation History Service
  └── Security, Privacy & Audit Logging Layer
                    │
                    ▼
[ Persistence Layer: SQLite + SQLAlchemy ORM ]
  ├── Learner Profiles (Demographics, Baseline Metrics, Risk Levels)
  ├── Tasks Repository (Multi-Domain Exercises & AR Payloads)
  ├── Activity Sessions (Session States & Attempt Counters)
  └── Task Evaluation Histories (Diagnostic Archive & Score Deltas)
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** and **npm**
- **Google Gemini API Key**

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
   DATABASE_URL=sqlite:///./language_simplification.db
   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   DEBUG=True
   ```

5. Initialize and seed the database:
   ```bash
   python -m alembic upgrade head
   python -m app.database.seed
   ```

6. Start the FastAPI development server:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```
   - Swagger API Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/api/health`

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
├── README.md                      # Project Overview & Setup Guide
├── SYSTEM_DOCUMENTATION.md        # Comprehensive Architecture & Technical Specifications
├── SYSTEM_CONCEPT.md              # Theoretical & Pedagogical Foundations
├── RESEARCH_README.md             # Research & Experimental Design Notes
├── backend/                       # FastAPI Backend Application
│   ├── app/
│   │   ├── api/                   # REST API Routers (Learners, Tasks, Sessions, Scenarios)
│   │   ├── core/                  # Configuration, Settings & Constants
│   │   ├── database/              # SQLAlchemy Models, Session, and Seed Data
│   │   ├── retry_controller/      # Multi-Attempt Scaffolding & Fallback Manager
│   │   ├── security/              # Data Privacy, Input Sanitization & Audit Logging
│   │   └── services/              # Simplification, LLM Engine, Profile Evolution
│   ├── tests/                     # Automated Pytest Suite
│   ├── alembic/                   # Database Migrations
│   └── requirements.txt           # Python Dependencies
├── frontend/                      # React SPA Application
│   ├── src/
│   │   ├── components/            # Guided Playground, Diagnostics View, Learner Manager
│   │   ├── App.jsx                # Root Application & Navigation
│   │   └── main.jsx               # Entry Point
│   ├── package.json               # Frontend Dependencies & Scripts
│   └── vite.config.js             # Vite Build Configuration
└── data/                          # Seed Data & Research Datasets
    ├── application_tasks/         # Curated Task Datasets
    ├── learner_profiles/          # Pseudonymous Learner Profiles
    ├── development_scenarios/     # Preconfigured Simulation Scenarios
    └── research_exports/          # Experimental Evaluation Exports
```

---

## 🔬 Research & Clinical Impact

- **Extraneous Load Reduction**: Decreases syntactic processing barriers to enable accurate assessment of underlying knowledge.
- **Dynamic Scaffolding**: Promotes autonomous completion while preventing frustration through graduated support.
- **Empirical Evolution**: Provides clinicians and educators with fine-grained performance trajectories and actionable intervention recommendations.

---

## 📄 License
This project is developed as part of ongoing research in AI-Assisted Language Simplification and Cognitive Accessibility for Children.
