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
from app.response_analysis.answer_checker import answer_checker
from app.grammar_analysis.grammar_extractor import grammar_extractor
from app.response_analysis.language_extractor import language_extractor
from app.validation.validator import adaptation_validator
from app.retry_controller.retry_manager import retry_manager

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

# ----------------- Grammar Test Cases -----------------
@router.get("/grammar-test-cases")
def get_grammar_test_cases():
    test_cases_file = os.path.join(BASE_DATA_DIR, "grammar_test_cases", "seed_grammar_cases.json")
    if os.path.exists(test_cases_file):
        with open(test_cases_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

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
            "final_outcome": result["final_outcome"],
            "escalation_payload": result.get("escalation_payload")
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

    # 1. Concept analysis
    eval_res = answer_checker.evaluate_answer(task, req.speech_transcript, None)
    
    # 2. Grammar error extraction using spaCy + rules + confidence gating
    grammar_res = grammar_extractor.analyze_grammar(
        req.speech_transcript,
        speech_confidence=req.speech_confidence
    )
    
    # 3. Vocabulary & instruction extraction
    vocab_obs = language_extractor.analyze_vocabulary_and_comprehension(
        transcript=req.speech_transcript,
        task=task,
        learner_age=req.learner_age,
        concept_result=eval_res["concept_result"]
    )

    combined_observations = grammar_res.get("observations", []) + vocab_obs

    return {
        "concept_result": eval_res["concept_result"],
        "concept_matches": eval_res["matched_concepts"] or task.acceptable_answers,
        "observations": combined_observations,
        "speech_confidence_acceptable": grammar_res["speech_confidence_acceptable"]
    }


@router.post("/adapt-instruction")
def adapt_instruction(req: AdaptInstructionRequest, db: Session = Depends(get_db)):
    learner = task_repository.get_learner_by_id(db, req.learner_id)
    task = task_repository.get_task_by_id(db, req.task_id)
    if not learner or not task:
        raise HTTPException(status_code=404, detail="Learner or Task not found")

    support_details = adaptation_service.determine_support_details(learner, req.attempt_number)
    support_level = support_details["support_level"]
    gen_data = adaptation_service.generate_child_friendly_instruction(
        task=task,
        learner=learner,
        target_attempt_number=req.attempt_number,
        support_level=support_level,
        generation_mode=req.generation_mode
    )
    combined_reason_codes = list(dict.fromkeys(support_details["reason_codes"] + gen_data["reason_codes"]))
    
    return {
        "task_code": task.task_code,
        "task_title": task.title,
        "learner_code": learner.learner_code,
        "attempt_number": req.attempt_number,
        "support_level": support_level,
        "base_support": support_details["base_support"],
        "child_instruction": gen_data["child_instruction"],
        "supportive_message": gen_data["supportive_message"],
        "vocabulary_support": gen_data["vocabulary_support"],
        "answer_format": gen_data["answer_format"],
        "visual_cues": gen_data["visual_cues"],
        "reason_codes": combined_reason_codes,
        "word_count": len(gen_data["child_instruction"].split()),
        "generation_method": "rule"
    }

@router.get("/preview-progression/{task_id}/{learner_id}")
def preview_progression(task_id: str, learner_id: str, db: Session = Depends(get_db)):
    """Returns side-by-side adaptations for Attempts 1, 2, and 3 for a given task and learner."""
    learner = task_repository.get_learner_by_id(db, learner_id)
    task = task_repository.get_task_by_id(db, task_id)
    if not learner or not task:
        raise HTTPException(status_code=404, detail="Learner or Task not found")

    attempts_data = []
    for att_num in [1, 2, 3]:
        sup_details = adaptation_service.determine_support_details(learner, att_num)
        gen = adaptation_service.generate_child_friendly_instruction(
            task=task,
            learner=learner,
            target_attempt_number=att_num,
            support_level=sup_details["support_level"],
            generation_mode="rule"
        )
        combined_reasons = list(dict.fromkeys(sup_details["reason_codes"] + gen["reason_codes"]))
        attempts_data.append({
            "attempt_number": att_num,
            "support_level": sup_details["support_level"],
            "child_instruction": gen["child_instruction"],
            "supportive_message": gen["supportive_message"],
            "vocabulary_support": gen["vocabulary_support"],
            "answer_format": gen["answer_format"],
            "visual_cues": gen["visual_cues"],
            "reason_codes": combined_reasons,
            "word_count": len(gen["child_instruction"].split())
        })

    return {
        "task": TaskResponse.model_validate(task),
        "learner": LearnerProfileResponse.model_validate(learner),
        "progression": attempts_data
    }

@router.post("/validate-output")
def validate_output(req: ValidateOutputRequest, db: Session = Depends(get_db)):
    task = task_repository.get_task_by_id(db, req.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    learner = None
    if req.learner_id:
        learner = task_repository.get_learner_by_id(db, req.learner_id)

    candidate_data = {
        "child_instruction": req.child_instruction,
        "supportive_message": req.supportive_message,
        "support_level": req.support_level,
        "target_attempt_number": req.target_attempt_number
    }

    eval_res = adaptation_validator.validate_candidate(task, candidate_data, learner)
    return {
        "language_valid": eval_res["language_valid"],
        "age_appropriate": eval_res["age_appropriate"],
        "meaning_preserved": eval_res["meaning_preserved"],
        "answer_leakage": eval_res["answer_leakage"],
        "sentence_length_valid": eval_res["sentence_length_valid"],
        "support_level_valid": eval_res["support_level_valid"],
        "safety_valid": eval_res["safety_valid"],
        "average_words_per_sentence": eval_res["average_words_per_sentence"],
        "maximum_words_in_sentence": eval_res["maximum_words_in_sentence"],
        "semantic_score": eval_res["semantic_score"],
        "status": eval_res["status"],
        "failure_reasons": eval_res["failure_reasons"],
        "leakage_details": eval_res.get("leakage_details", {}),
        "suitability_details": eval_res.get("suitability_details", {})
    }

@router.get("/retry-state/{experiment_id}")
def get_retry_state(experiment_id: str, db: Session = Depends(get_db)):
    try:
        return retry_manager.get_retry_state(db, experiment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


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
