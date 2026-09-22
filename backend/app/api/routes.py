import os
import json
import io
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models import (
    Task, LearnerProfile, ActivitySession, Attempt, ActivityAsset, ActivityQuestion,
    ExperimentRun, Adaptation, ValidationResult, ExpertEvaluation, TaskResult
)
from app.schemas.schemas import (
    TaskResponse, LearnerProfileResponse, ActivitySessionCreate, ActivitySessionResponse,
    AttemptResponse, AttemptCreateInstruction, AttemptResponseInput, AttemptConfirmInput,
    AttemptReviewInput, ChildSafeViewResponse, ActivityAssetResponse,
    ExperimentRunCreate, ExperimentRunResponse, AdaptationResponse, AttemptCreate,
    ValidationResultResponse, ExpertEvaluationCreate, ExpertEvaluationResponse,
    AnalyzeResponseRequest, AnalyzeResponseResult, AdaptInstructionRequest, ValidateOutputRequest
)
from app.tasks.repository import task_repository, BASE_DATA_DIR
from app.services.session_service import session_service
from app.services.experiment_service import experiment_service
from app.services.adaptation_service import adaptation_service
from app.services.evaluation_service import evaluation_service
from app.retry_controller.retry_manager import retry_manager
from app.response_analysis.answer_checker import answer_checker
from app.grammar_analysis.grammar_extractor import grammar_extractor
from app.response_analysis.language_extractor import language_extractor
from app.validation.validator import adaptation_validator
from app.generation.rule_generator import rule_generator
from app.generation.llm_generator import llm_generator
from app.generation.hybrid_generator import hybrid_generator

router = APIRouter(prefix="/api")

# ----------------- Health -----------------
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Manual-Input English Adaptive Language Support MVP",
        "version": "2.2"
    }

# ----------------- Activities Catalog -----------------
@router.get("/activities", response_model=List[TaskResponse])
def get_activities(
    category: Optional[str] = Query(None, description="vocabulary, grammar, sentence_and_instruction, comprehension"),
    subskill: Optional[str] = None,
    age: Optional[int] = Query(None, ge=4, le=8),
    delivery_mode: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Task).filter(Task.is_active == True)
    if category:
        query = query.filter(Task.category == category)
    if subskill:
        query = query.filter(Task.subskill == subskill)
    if age:
        query = query.filter(Task.minimum_age <= age, Task.maximum_age >= age)
    tasks = query.all()
    if delivery_mode:
        tasks = [t for t in tasks if t.delivery_modes and delivery_mode in t.delivery_modes]
    return tasks

@router.get("/activities/categories")
def get_activity_categories(db: Session = Depends(get_db)):
    return {
        "categories": [
            {"id": "vocabulary", "name": "Vocabulary", "description": "Naming, matching, definitions, and category recognition"},
            {"id": "grammar", "name": "Grammar", "description": "Articles, prepositions, subject-verb agreement, and syntax"},
            {"id": "sentence_and_instruction", "name": "Sentence & Instruction", "description": "One/two/three-step instructions, before/after, and conditionals"},
            {"id": "comprehension", "name": "Comprehension", "description": "Short passages, story sequencing, and literal question answering"}
        ]
    }

@router.get("/activities/{id}", response_model=TaskResponse)
def get_activity(id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter((Task.id == id) | (Task.task_code == id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Activity not found")
    return task

@router.get("/activities/{id}/assets", response_model=List[ActivityAssetResponse])
def get_activity_assets(id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter((Task.id == id) | (Task.task_code == id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Activity not found")
    return task.assets

# ----------------- Learners -----------------
@router.get("/learners", response_model=List[LearnerProfileResponse])
def get_learners(db: Session = Depends(get_db)):
    return db.query(LearnerProfile).all()

@router.get("/learners/{id}", response_model=LearnerProfileResponse)
def get_learner(id: str, db: Session = Depends(get_db)):
    learner = db.query(LearnerProfile).filter((LearnerProfile.id == id) | (LearnerProfile.learner_code == id)).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    return learner

# ----------------- Activity Session Lifecycle -----------------
@router.post("/activity-sessions", response_model=ActivitySessionResponse)
def create_activity_session(req: ActivitySessionCreate, db: Session = Depends(get_db)):
    try:
        session = session_service.create_session(
            db=db,
            learner_id=req.learner_id,
            task_id=req.task_id,
            generation_mode=req.generation_mode,
            created_by=req.created_by
        )
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/activity-sessions/{id}", response_model=ActivitySessionResponse)
def get_activity_session(id: str, db: Session = Depends(get_db)):
    session = db.query(ActivitySession).filter(ActivitySession.id == id).first()
    if not session:
        raise HTTPException(status_code=404, detail="ActivitySession not found")
    return session

@router.post("/activity-sessions/{id}/attempts")
def create_attempt(id: str, req: AttemptCreateInstruction = AttemptCreateInstruction(), db: Session = Depends(get_db)):
    """
    Creates the attempt record, determines support level, selects/generates instruction,
    and stores the exact presented instruction BEFORE rendering it to the child.
    """
    try:
        result = session_service.create_attempt(
            db=db,
            session_id=id,
            generation_mode=req.generation_mode
        )
        return {
            "attempt": AttemptResponse.model_validate(result["attempt"]),
            "child_view": result["child_view"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/attempts/{id}/response", response_model=AttemptResponse)
def record_attempt_response(id: str, req: AttemptResponseInput, db: Session = Depends(get_db)):
    """Adult records the child's response, completion status, response time, and notes."""
    try:
        attempt = session_service.record_response(
            db=db,
            attempt_id=id,
            response_source=req.response_source,
            manual_transcript=req.manual_transcript,
            selected_option=req.selected_option,
            selected_items=req.selected_items,
            ordered_items=req.ordered_items,
            response_time_ms=req.response_time_ms,
            completion_status=req.completion_status,
            assistance_level=req.assistance_level,
            adult_notes=req.adult_notes
        )
        return attempt
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/attempts/{id}/confirm-response", response_model=AttemptResponse)
def confirm_attempt_response(id: str, req: AttemptConfirmInput = AttemptConfirmInput(), db: Session = Depends(get_db)):
    """Adult confirms accuracy of transcribed response before automated analysis."""
    try:
        attempt = session_service.confirm_response(
            db=db,
            attempt_id=id,
            confirmed=req.confirmed,
            manual_transcript=req.manual_transcript
        )
        return attempt
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/attempts/{id}/analyse")
def analyse_confirmed_attempt(id: str, db: Session = Depends(get_db)):
    """
    Analyzes confirmed response.
    Enforces adult_confirmed == True before running analysis.
    """
    try:
        result = session_service.analyse_attempt(db=db, attempt_id=id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/attempts/{id}/review", response_model=AttemptResponse)
def review_attempt(id: str, req: AttemptReviewInput, db: Session = Depends(get_db)):
    """Adult reviews/overrides concept and target-skill results."""
    try:
        attempt = session_service.review_attempt(
            db=db,
            attempt_id=id,
            final_concept_result=req.final_concept_result,
            final_target_skill_result=req.final_target_skill_result,
            final_retry_required=req.final_retry_required,
            override_reason=req.override_reason,
            reviewed_by_user_id=req.reviewed_by_user_id,
            adult_notes=req.adult_notes
        )
        return attempt
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/attempts/{id}/transition")
def transition_attempt(id: str, db: Session = Depends(get_db)):
    """Finalizes attempt, evaluates outcome, and determines next action."""
    try:
        result = session_service.transition_attempt(db=db, attempt_id=id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/activity-sessions/{id}/child-view", response_model=ChildSafeViewResponse)
def get_child_view(id: str, attempt_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Returns pure child-safe payload stripped of diagnostic scores and research logs."""
    try:
        return session_service.get_child_view(db=db, session_id=id, attempt_id=attempt_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/activity-sessions/{id}/history")
def get_session_history(id: str, db: Session = Depends(get_db)):
    """Full session audit history for authorized adults."""
    try:
        hist = session_service.get_session_history(db=db, session_id=id)
        return {
            "session": ActivitySessionResponse.model_validate(hist["session"]),
            "learner": LearnerProfileResponse.model_validate(hist["learner"]),
            "task": TaskResponse.model_validate(hist["task"]),
            "attempts": [AttemptResponse.model_validate(a) for a in hist["attempts"]],
            "events_count": len(hist["events"])
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/activity-sessions/{id}/complete", response_model=ActivitySessionResponse)
def complete_activity_session(id: str, db: Session = Depends(get_db)):
    session = db.query(ActivitySession).filter(ActivitySession.id == id).first()
    if not session:
        raise HTTPException(status_code=404, detail="ActivitySession not found")
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session

# ----------------- Retry State Inspection -----------------
@router.get("/retry-state/{experiment_id}")
def get_retry_state(experiment_id: str, db: Session = Depends(get_db)):
    try:
        return retry_manager.get_retry_state(db, experiment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ----------------- Evaluations & Analytics -----------------
@router.post("/evaluations", response_model=ExpertEvaluationResponse)
def submit_evaluation(eval_in: ExpertEvaluationCreate, db: Session = Depends(get_db)):
    try:
        return evaluation_service.submit_expert_evaluation(
            db=db,
            adaptation_id=eval_in.adaptation_id,
            evaluator_code=eval_in.evaluator_code,
            age_appropriateness=eval_in.age_appropriateness,
            clarity=eval_in.clarity,
            grammar_correctness=eval_in.grammar_correctness,
            meaning_preservation=eval_in.meaning_preservation,
            personalization_suitability=eval_in.personalization_suitability,
            comments=eval_in.comments
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/evaluations/adaptation/{adaptation_id}")
def get_evaluations_for_adaptation(adaptation_id: str, db: Session = Depends(get_db)):
    return evaluation_service.get_evaluations_for_adaptation(db, adaptation_id)

@router.get("/evaluation-statistics")
def get_evaluation_statistics(db: Session = Depends(get_db)):
    return evaluation_service.get_evaluation_statistics(db)

@router.get("/evaluations/benchmarks")
def get_benchmark_evaluations(db: Session = Depends(get_db)):
    return evaluation_service.get_benchmark_evaluations(db)

# ----------------- Research Data Exports -----------------
@router.get("/export/experiments.json")
def export_experiments_json(db: Session = Depends(get_db)):
    data = evaluation_service.export_experiments_json(db)
    return Response(
        content=json.dumps(data, indent=2, default=str),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=experiments_export.json"}
    )

@router.get("/export/csv/{entity_name}")
def export_csv(entity_name: str, db: Session = Depends(get_db)):
    csv_str = evaluation_service.export_csv(db, entity_name)
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={entity_name}_export.csv"}
    )

@router.get("/export/research-bundle.zip")
def export_research_bundle_zip(db: Session = Depends(get_db)):
    zip_bytes = evaluation_service.export_research_bundle_zip(db)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=research_bundle.zip"}
    )

@router.get("/generator-comparison/{task_id}/{learner_id}")
def get_generator_comparison(task_id: str, learner_id: str, db: Session = Depends(get_db)):
    return evaluation_service.get_generator_comparison(db, task_id, learner_id)

@router.get("/integration-events/{experiment_id}")
def get_integration_events(experiment_id: str, db: Session = Depends(get_db)):
    return evaluation_service.get_integration_events(db, experiment_id)

# ----------------- Legacy Routes (Preserved for compatibility) -----------------
@router.get("/tasks", response_model=List[TaskResponse])
def get_tasks_legacy(db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.is_active == True).all()

@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task_legacy(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter((Task.id == task_id) | (Task.task_code == task_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/scenarios")
def get_scenarios():
    scenarios_file = os.path.join(BASE_DATA_DIR, "development_scenarios", "seed_scenarios.json")
    if os.path.exists(scenarios_file):
        with open(scenarios_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@router.get("/grammar-test-cases")
def get_grammar_test_cases():
    test_cases_file = os.path.join(BASE_DATA_DIR, "grammar_test_cases", "seed_grammar_cases.json")
    if os.path.exists(test_cases_file):
        with open(test_cases_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

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
    existing = db.query(Adaptation).filter(
        Adaptation.experiment_run_id == id,
        Adaptation.target_attempt_number == 1
    ).first()
    if existing:
        return existing
    return adaptation_service.create_initial_adaptation(db, exp, generation_mode=exp.generation_mode)

@router.post("/experiments/{id}/attempts")
def record_attempt_legacy(id: str, attempt_in: AttemptCreate, db: Session = Depends(get_db)):
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

@router.post("/analyze-response", response_model=AnalyzeResponseResult)
def analyze_response(req: AnalyzeResponseRequest, db: Session = Depends(get_db)):
    task = db.query(Task).filter((Task.id == req.task_id) | (Task.task_code == req.task_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    eval_res = answer_checker.evaluate_answer(task, req.speech_transcript, None)
    grammar_res = grammar_extractor.analyze_grammar(
        req.speech_transcript,
        speech_confidence=req.speech_confidence
    )
    vocab_obs = language_extractor.analyze_vocabulary_and_comprehension(
        transcript=req.speech_transcript,
        task=task,
        learner_age=req.learner_age,
        concept_result=eval_res["concept_result"]
    )
    combined_observations = grammar_res.get("observations", []) + vocab_obs

    return {
        "concept_result": eval_res["concept_result"],
        "target_skill_result": eval_res.get("target_skill_result", "correct"),
        "concept_matches": eval_res["matched_concepts"] or task.acceptable_answers,
        "observations": combined_observations,
        "speech_confidence_acceptable": True
    }

@router.post("/adapt-instruction")
def adapt_instruction(req: AdaptInstructionRequest, db: Session = Depends(get_db)):
    learner = db.query(LearnerProfile).filter((LearnerProfile.id == req.learner_id) | (LearnerProfile.learner_code == req.learner_id)).first()
    task = db.query(Task).filter((Task.id == req.task_id) | (Task.task_code == req.task_id)).first()
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
    learner = db.query(LearnerProfile).filter((LearnerProfile.id == learner_id) | (LearnerProfile.learner_code == learner_id)).first()
    task = db.query(Task).filter((Task.id == task_id) | (Task.task_code == task_id)).first()
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
    task = db.query(Task).filter((Task.id == req.task_id) | (Task.task_code == req.task_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    learner = None
    if req.learner_id:
        learner = db.query(LearnerProfile).filter((LearnerProfile.id == req.learner_id) | (LearnerProfile.learner_code == req.learner_id)).first()

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
        "is_final": True
    }

@router.get("/integration-payloads/component-1/{experiment_id}")
def get_comp1_payload(experiment_id: str, db: Session = Depends(get_db)):
    return evaluation_service.get_component1_payload(db, experiment_id)

@router.get("/integration-payloads/component-4/{experiment_id}")
def get_comp4_payload(experiment_id: str, db: Session = Depends(get_db)):
    return evaluation_service.get_component4_payload(db, experiment_id)

@router.get("/integration-payloads/component-3-ar/{experiment_id}")
def get_ar_payload(experiment_id: str, db: Session = Depends(get_db)):
    return evaluation_service.get_ar_payload(db, experiment_id)

# ----------------- Expert Evaluations -----------------
@router.post("/expert-evaluations", response_model=ExpertEvaluationResponse)
def submit_expert_evaluation(req: ExpertEvaluationCreate, db: Session = Depends(get_db)):
    try:
        eval_record = evaluation_service.submit_expert_evaluation(
            db=db,
            adaptation_id=req.adaptation_id,
            evaluator_code=req.evaluator_code,
            age_appropriateness=req.age_appropriateness,
            clarity=req.clarity,
            grammar_correctness=req.grammar_correctness,
            meaning_preservation=req.meaning_preservation,
            personalization_suitability=req.personalization_suitability,
            comments=req.comments
        )
        return eval_record
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/expert-evaluations/stats")
@router.get("/expert-evaluations/statistics")
def get_evaluation_statistics(db: Session = Depends(get_db)):
    return evaluation_service.get_evaluation_statistics(db)

@router.get("/expert-evaluations/adaptation/{adaptation_id}")
def get_evaluations_for_adaptation(adaptation_id: str, db: Session = Depends(get_db)):
    return evaluation_service.get_evaluations_for_adaptation(db, adaptation_id)

# ----------------- Research Data Exports -----------------
@router.get("/export/experiments/json")
def export_experiments_json(db: Session = Depends(get_db)):
    return evaluation_service.export_experiments_json(db)

@router.get("/export/experiments/csv")
def export_experiments_csv(db: Session = Depends(get_db)):
    csv_data = evaluation_service.export_experiments_csv(db)
    return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=experiments.csv"})

@router.get("/export/adaptations/csv")
def export_adaptations_csv(db: Session = Depends(get_db)):
    csv_data = evaluation_service.export_adaptations_csv(db)
    return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=adaptations.csv"})

@router.get("/export/attempts/csv")
def export_attempts_csv(db: Session = Depends(get_db)):
    csv_data = evaluation_service.export_attempts_csv(db)
    return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=attempts.csv"})

@router.get("/export/evaluations/csv")
@router.get("/export/expert-evaluations/csv")
def export_evaluations_csv(db: Session = Depends(get_db)):
    csv_data = evaluation_service.export_evaluations_csv(db)
    return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=expert_evaluations.csv"})

@router.get("/export/research-bundle/zip")
def export_research_bundle_zip(db: Session = Depends(get_db)):
    zip_bytes = evaluation_service.export_research_bundle_zip(db)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=research_dataset_bundle.zip"}
    )

# ----------------- Multi-Generator Comparison -----------------
@router.get("/generate-comparison/{task_id}/{learner_id}")
def generate_comparison(
    task_id: str,
    learner_id: str,
    attempt_number: int = Query(1, ge=1, le=3),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter((Task.id == task_id) | (Task.task_code == task_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    learner = db.query(LearnerProfile).filter((LearnerProfile.id == learner_id) | (LearnerProfile.learner_code == learner_id)).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")

    rule_res = rule_generator.generate(task=task, learner=learner, target_attempt_number=attempt_number, support_level="moderate")
    rule_val = adaptation_validator.validate_candidate(task, rule_res, learner)

    llm_res = llm_generator.generate(task=task, learner=learner, target_attempt_number=attempt_number, support_level="moderate")
    llm_val = adaptation_validator.validate_candidate(task, llm_res, learner)

    hybrid_res = hybrid_generator.generate(task=task, learner=learner, target_attempt_number=attempt_number, support_level="moderate")
    hybrid_val = adaptation_validator.validate_candidate(task, hybrid_res, learner)

    return {
        "task_id": task.task_code,
        "learner_id": learner.learner_code,
        "target_attempt_number": attempt_number,
        "comparison": {
            "rule": {
                "instruction": rule_res["child_instruction"],
                "supportive_message": rule_res["supportive_message"],
                "vocabulary_support": rule_res["vocabulary_support"],
                "answer_format": rule_res["answer_format"],
                "visual_cues": rule_res["visual_cues"],
                "word_count": len(rule_res["child_instruction"].split()),
                "latency_ms": rule_res.get("processing_time_ms", 12),
                "estimated_cost": rule_res.get("estimated_cost", 0.0),
                "validation_status": rule_val["status"],
                "semantic_score": rule_val["semantic_score"]
            },
            "llm": {
                "instruction": llm_res["child_instruction"],
                "supportive_message": llm_res["supportive_message"],
                "vocabulary_support": llm_res["vocabulary_support"],
                "answer_format": llm_res["answer_format"],
                "visual_cues": llm_res["visual_cues"],
                "word_count": len(llm_res["child_instruction"].split()),
                "latency_ms": llm_res.get("processing_time_ms", 120),
                "estimated_cost": llm_res.get("estimated_cost", 0.0001),
                "validation_status": llm_val["status"],
                "semantic_score": llm_val["semantic_score"]
            },
            "hybrid": {
                "instruction": hybrid_res["child_instruction"],
                "supportive_message": hybrid_res["supportive_message"],
                "vocabulary_support": hybrid_res["vocabulary_support"],
                "answer_format": hybrid_res["answer_format"],
                "visual_cues": hybrid_res["visual_cues"],
                "word_count": len(hybrid_res["child_instruction"].split()),
                "latency_ms": hybrid_res.get("processing_time_ms", 140),
                "estimated_cost": hybrid_res.get("estimated_cost", 0.0001),
                "validation_status": hybrid_val["status"],
                "semantic_score": hybrid_val["semantic_score"]
            }
        }
    }

# ----------------- Integration Output Aliases -----------------
@router.get("/output/component-1/{experiment_id}")
def get_output_component_1(experiment_id: str, db: Session = Depends(get_db)):
    return evaluation_service.get_component_1_payload(db, experiment_id)

@router.get("/output/component-4/{experiment_id}")
def get_output_component_4(experiment_id: str, db: Session = Depends(get_db)):
    return evaluation_service.get_component_4_payload(db, experiment_id)

@router.get("/output/ar/{experiment_id}")
def get_output_ar(experiment_id: str, db: Session = Depends(get_db)):
    return evaluation_service.get_ar_payload(db, experiment_id)

@router.get("/integration-events/{experiment_id}")
def get_integration_events_for_experiment(experiment_id: str, db: Session = Depends(get_db)):
    return evaluation_service.get_integration_events(db, experiment_id)


# ─────────────────────────────────────────────
# Task Results History Endpoints
# ─────────────────────────────────────────────

@router.get("/results")
def list_task_results(
    learner_code: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    outcome: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Returns all stored task results (immutable session outcome records).
    Supports filtering by learner_code, category (vocabulary/grammar/comprehension/sentence_and_instruction),
    and outcome (success/adult_support_required/completed_with_adult_support).
    Also returns aggregate statistics.
    """
    results = session_service.get_task_results(
        db=db,
        learner_code=learner_code,
        category=category,
        outcome=outcome,
        limit=limit
    )

    # Compute aggregate metrics
    total = len(results)
    successes = sum(1 for r in results if r.final_outcome == "success")
    escalations = sum(1 for r in results if r.final_outcome == "adult_support_required")
    avg_attempts = round(sum(r.attempts_count for r in results) / total, 2) if total else 0
    avg_grammar_delta = round(
        sum(r.score_deltas.get("grammar", 0) for r in results) / total, 2
    ) if total else 0
    avg_vocab_delta = round(
        sum(r.score_deltas.get("vocabulary", 0) for r in results) / total, 2
    ) if total else 0

    return {
        "results": [
            {
                "id": r.id,
                "learner_code": r.learner_code,
                "learner_age": r.learner_age,
                "task_code": r.task_code,
                "task_title": r.task_title,
                "category": r.category,
                "target_skill": r.target_skill,
                "difficulty": r.difficulty,
                "final_outcome": r.final_outcome,
                "attempts_count": r.attempts_count,
                "independent_success": r.independent_success,
                "score_before": r.score_before,
                "score_after": r.score_after,
                "score_deltas": r.score_deltas,
                "risk_before": r.risk_before,
                "risk_after": r.risk_after,
                "risk_changed": r.risk_changed,
                "composite_language_index": r.composite_language_index,
                "attempt_history": r.attempt_history,
                "diagnostic_notes": r.diagnostic_notes,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None
            }
            for r in results
        ],
        "aggregate": {
            "total": total,
            "successes": successes,
            "adult_escalations": escalations,
            "mastery_rate_pct": round(successes / total * 100, 1) if total else 0,
            "avg_attempts": avg_attempts,
            "avg_grammar_delta": avg_grammar_delta,
            "avg_vocab_delta": avg_vocab_delta
        }
    }


@router.get("/results/{result_id}")
def get_task_result_detail(result_id: str, db: Session = Depends(get_db)):
    """Returns full detail for a single task result record including attempt history."""
    try:
        r = session_service.get_task_result_by_id(db=db, result_id=result_id)
        return {
            "id": r.id,
            "learner_code": r.learner_code,
            "learner_age": r.learner_age,
            "task_code": r.task_code,
            "task_title": r.task_title,
            "category": r.category,
            "target_skill": r.target_skill,
            "difficulty": r.difficulty,
            "final_outcome": r.final_outcome,
            "attempts_count": r.attempts_count,
            "independent_success": r.independent_success,
            "score_before": r.score_before,
            "score_after": r.score_after,
            "score_deltas": r.score_deltas,
            "risk_before": r.risk_before,
            "risk_after": r.risk_after,
            "risk_changed": r.risk_changed,
            "composite_language_index": r.composite_language_index,
            "attempt_history": r.attempt_history,
            "diagnostic_notes": r.diagnostic_notes,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/results/{result_id}", status_code=204)
def delete_task_result(result_id: str, db: Session = Depends(get_db)):
    """Delete a specific task result (for testing/cleanup)."""
    r = db.query(TaskResult).filter(TaskResult.id == result_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="TaskResult not found")
    db.delete(r)
    db.commit()


@router.post("/results/backfill")
def backfill_task_results(db: Session = Depends(get_db)):
    """Backfills TaskResult records for all existing completed sessions that lack them."""
    count = session_service.backfill_task_results(db=db)
    return {"backfilled": count, "message": f"Created {count} new TaskResult records from existing sessions."}
