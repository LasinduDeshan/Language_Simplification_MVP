import os
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models import (
    Task, LearnerProfile, ExperimentRun, Attempt, Adaptation, ValidationResult, ExpertEvaluation
)
from app.schemas.schemas import (
    TaskResponse, LearnerProfileResponse, ExperimentRunCreate, ExperimentRunResponse,
    AdaptationResponse, AttemptCreate, AttemptResponse, ValidationResultResponse,
    ExpertEvaluationCreate, ExpertEvaluationResponse, Component1OutputPayload,
    Component4AnalyticsPayload, Component3ARPayload, AnalyzeResponseRequest,
    AnalyzeResponseResult, AdaptInstructionRequest, ValidateOutputRequest
)
from app.tasks.repository import task_repository, BASE_DATA_DIR
from app.services.experiment_service import experiment_service
from app.services.adaptation_service import adaptation_service
from app.services.evaluation_service import evaluation_service

router = APIRouter(prefix="/api")

# ----------------- Health -----------------
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "English-First Adaptive Child-Friendly Language Support MVP",
        "version": "2.2"
    }

# ----------------- Tasks -----------------
@router.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return task_repository.get_all_tasks(db)

@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = task_repository.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# ----------------- Learners -----------------
@router.get("/learners", response_model=List[LearnerProfileResponse])
def get_learners(db: Session = Depends(get_db)):
    return task_repository.get_all_learners(db)

# ----------------- Scenarios -----------------
@router.get("/scenarios")
def get_scenarios():
    scenarios_file = os.path.join(BASE_DATA_DIR, "development_scenarios", "seed_scenarios.json")
    if os.path.exists(scenarios_file):
        with open(scenarios_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@router.post("/scenarios")
def create_scenario(scenario: Dict[str, Any]):
    scenarios_file = os.path.join(BASE_DATA_DIR, "development_scenarios", "seed_scenarios.json")
    scenarios = []
    if os.path.exists(scenarios_file):
        with open(scenarios_file, "r", encoding="utf-8") as f:
            scenarios = json.load(f)
    scenarios.append(scenario)
    with open(scenarios_file, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, indent=2)
    return {"message": "Scenario added successfully", "scenario": scenario}

# ----------------- Experiments -----------------
@router.post("/experiments", response_model=ExperimentRunResponse)
def create_experiment(exp_in: ExperimentRunCreate, db: Session = Depends(get_db)):
    return experiment_service.create_experiment_run(
        db,
        learner_id=exp_in.learner_id,
        task_id=exp_in.task_id,
        generation_mode=exp_in.generation_mode
    )

@router.get("/experiments/{id}", response_model=ExperimentRunResponse)
def get_experiment(id: str, db: Session = Depends(get_db)):
    exp = db.query(ExperimentRun).filter(ExperimentRun.id == id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="ExperimentRun not found")
    return exp

@router.post("/experiments/{id}/initial-adaptation", response_model=AdaptationResponse)
def generate_initial_adaptation(id: str, db: Session = Depends(get_db)):
    exp = db.query(ExperimentRun).filter(ExperimentRun.id == id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="ExperimentRun not found")
    
    # Check if initial adaptation already exists
    existing = db.query(Adaptation).filter(
        Adaptation.experiment_run_id == id,
        Adaptation.target_attempt_number == 1
    ).first()
    if existing:
        return existing

    return adaptation_service.create_initial_adaptation(db, exp, generation_mode=exp.generation_mode)

@router.post("/experiments/{id}/attempts")
def record_attempt(id: str, attempt_in: AttemptCreate, db: Session = Depends(get_db)):
    try:
        result = experiment_service.record_attempt(
            db=db,
            experiment_run_id=id,
            adaptation_id=attempt_in.adaptation_id,
            speech_transcript=attempt_in.speech_transcript,
            speech_confidence=attempt_in.speech_confidence,
            selected_answer=attempt_in.selected_answer,
            response_time_ms=attempt_in.response_time_ms,
            completion_status=attempt_in.completion_status
        )
        return {
            "attempt": AttemptResponse.model_validate(result["attempt"]),
            "next_adaptation": AdaptationResponse.model_validate(result["next_adaptation"]) if result["next_adaptation"] else None,
            "experiment_status": result["experiment_status"],
            "final_outcome": result["final_outcome"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/experiments/{id}/history")
def get_experiment_history(id: str, db: Session = Depends(get_db)):
    exp = db.query(ExperimentRun).filter(ExperimentRun.id == id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    attempts = db.query(Attempt).filter(Attempt.experiment_run_id == id).order_by(Attempt.attempt_number).all()
    adaptations = db.query(Adaptation).filter(Adaptation.experiment_run_id == id).order_by(Adaptation.target_attempt_number).all()

    return {
        "experiment": ExperimentRunResponse.model_validate(exp),
        "learner": LearnerProfileResponse.model_validate(exp.learner),
        "task": TaskResponse.model_validate(exp.task),
        "adaptations": [AdaptationResponse.model_validate(a) for a in adaptations],
        "attempts": [AttemptResponse.model_validate(att) for att in attempts]
    }

# ----------------- Standalone Analysis & Validation -----------------
@router.post("/analyze-response", response_model=AnalyzeResponseResult)
def analyze_response(req: AnalyzeResponseRequest, db: Session = Depends(get_db)):
    task = task_repository.get_task_by_id(db, req.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    concept_res = experiment_service._evaluate_concept(task, req.speech_transcript, None)
    observations = []
    
    # Check speech confidence gating
    is_confirmed = req.speech_confidence >= 0.70
    t_lower = req.speech_transcript.lower()

    if "live water" in t_lower or "crayons box" in t_lower:
        observations.append({
            "category": "grammar",
            "observation_code": "missing_preposition",
            "evidence": req.speech_transcript,
            "confidence": req.speech_confidence,
            "confirmed": is_confirmed
        })
    elif "she kick" in t_lower or "he play" in t_lower:
        observations.append({
            "category": "grammar",
            "observation_code": "subject_verb_agreement",
            "evidence": req.speech_transcript,
            "confidence": req.speech_confidence,
            "confirmed": is_confirmed
        })

    # Vocabulary difficulty check
    for v in task_repository.get_vocabulary_dictionary():
        if v["word"].lower() in req.speech_transcript.lower() or v["word"].lower() in task.original_instruction.lower():
            if req.learner_age < v["minimum_age"]:
                observations.append({
                    "category": "vocabulary",
                    "observation_code": f"unfamiliar_{v['word']}",
                    "evidence": v["word"],
                    "confidence": 0.9,
                    "confirmed": True
                })

    return {
        "concept_result": concept_res,
        "concept_matches": task.acceptable_answers,
        "observations": observations,
        "speech_confidence_acceptable": is_confirmed
    }

@router.post("/adapt-instruction")
def adapt_instruction(req: AdaptInstructionRequest, db: Session = Depends(get_db)):
    learner = task_repository.get_learner_by_id(db, req.learner_id)
    task = task_repository.get_task_by_id(db, req.task_id)
    if not learner or not task:
        raise HTTPException(status_code=404, detail="Learner or Task not found")

    support_level = adaptation_service.determine_support_level(learner, req.attempt_number)
    return adaptation_service.generate_child_friendly_instruction(
        task, learner, req.attempt_number, support_level
    )

@router.post("/validate-output")
def validate_output(req: ValidateOutputRequest, db: Session = Depends(get_db)):
    task = task_repository.get_task_by_id(db, req.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Simple validation checks
    words = req.child_instruction.split()
    length_valid = len(words) <= 12
    leakage = False
    
    # Check restricted solution phrases
    prot = task.protected_answers or {}
    restricted = prot.get("restricted_solution_phrases", [])
    for phrase in restricted:
        if phrase.lower() in req.child_instruction.lower():
            leakage = True
            break

    status_str = "rejected" if leakage else ("approved" if length_valid else "review_required")
    return {
        "language_valid": True,
        "age_appropriate": True,
        "meaning_preserved": True,
        "answer_leakage": leakage,
        "sentence_length_valid": length_valid,
        "average_words_per_sentence": float(len(words)),
        "maximum_words_in_sentence": len(words),
        "status": status_str,
        "failure_reasons": ["protected_answer_revealed"] if leakage else ([] if length_valid else ["exceeds_target_length"])
    }

# ----------------- Integration Payloads (Comp 1, 4, AR) -----------------
@router.get("/output/component-1/{experiment_id}")
def get_comp1_output(experiment_id: str, db: Session = Depends(get_db)):
    payload = evaluation_service.get_component_1_payload(db, experiment_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Payload not available for experiment")
    return payload

@router.get("/output/component-4/{experiment_id}")
def get_comp4_output(experiment_id: str, db: Session = Depends(get_db)):
    payload = evaluation_service.get_component_4_payload(db, experiment_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Payload not available for experiment")
    return payload

@router.get("/output/ar/{experiment_id}")
def get_ar_output(experiment_id: str, db: Session = Depends(get_db)):
    payload = evaluation_service.get_ar_payload(db, experiment_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Payload not available for experiment")
    return payload

# ----------------- Expert Evaluation & Export -----------------
@router.post("/expert-evaluations", response_model=ExpertEvaluationResponse)
def submit_evaluation(eval_in: ExpertEvaluationCreate, db: Session = Depends(get_db)):
    return evaluation_service.submit_expert_evaluation(
        db,
        adaptation_id=eval_in.adaptation_id,
        evaluator_code=eval_in.evaluator_code,
        age_appropriateness=eval_in.age_appropriateness,
        clarity=eval_in.clarity,
        grammar_correctness=eval_in.grammar_correctness,
        meaning_preservation=eval_in.meaning_preservation,
        personalization_suitability=eval_in.personalization_suitability,
        comments=eval_in.comments
    )

@router.get("/export/experiments/json")
def export_json(db: Session = Depends(get_db)):
    return evaluation_service.export_experiments_json(db)

@router.get("/export/experiments/csv")
def export_csv(db: Session = Depends(get_db)):
    csv_data = evaluation_service.export_experiments_csv(db)
    return Response(content=csv_data, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=experiments_export.csv"
    })
