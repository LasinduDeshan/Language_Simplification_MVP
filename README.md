# English-First Adaptive Child-Friendly Language Support MVP

**Document Version:** 2.2  
**Scope:** English, Ages 4–8, Simulated Component Integration  
**Domain:** AI-Based Personalized Language Simplification for Children at Risk of Developmental Language Disorder (DLD)

---

## Architecture Overview

The application is structured as a modular monolith implementing the complete adaptive language cycle:
```text
Simulated Learner Profile & Response
  └──> Structured Language-Error & Concept Analysis
         └──> Personalized Child-Friendly Instruction (Mild / Moderate / Strong)
                └──> Progressive Retry Controller (Attempts 1 to 3 -> Adult Escalation)
                       └──> Formatted Integration Payloads (Component 1, 3 [AR], 4)
```

---

## Getting Started

### 1. Backend Setup & Run
```powershell
cd backend
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m app.database.seed
uvicorn app.main:app --reload
```
API Documentation: `http://localhost:8000/docs`  
Health Check: `http://localhost:8000/api/health`

### 2. Frontend Setup & Run
```powershell
cd frontend
npm install
npm run dev
```
Researcher Dashboard: `http://localhost:5173`

### 3. Automated Test Suite
```powershell
cd backend
python -m pytest tests/ -v
```

---

## Sprint 1 Deliverables Summary

- **FastAPI Project & REST API**: Explicit endpoints for `/api/tasks`, `/api/learners`, `/api/scenarios`, `/api/experiments`, `/api/experiments/{id}/initial-adaptation`, `/api/experiments/{id}/attempts`, and payload viewers.
- **Relational Data Foundation**: 10 SQLAlchemy tables with CheckConstraints, UniqueConstraints, and Foreign Key Indexes.
- **Alembic Migrations**: Initial migration generated and applied cleanly.
- **Seed Datasets**:
  - `data/application_tasks/seed_tasks.json`: 10 curated English tasks with AR metadata and relation-aware protected answers.
  - `data/learner_profiles/seed_learners.json`: 5 pseudonymous learner profiles (`CHILD-001` to `CHILD-005`).
  - `data/development_scenarios/seed_scenarios.json`: 20 preconfigured end-to-end scenarios.
  - `data/vocabulary_dictionary/seed_vocabulary.json`: Expert-reviewed age-graded word replacements.
- **Researcher Interface & Child Preview**:
  - Scenario Dashboard with live simulation and payload viewer.
  - Task Repository browser with filter pills and protected answer details.
  - Learner Profile browser with score cards.
  - Dedicated distraction-free Child Preview with Web Speech API audio playback.
