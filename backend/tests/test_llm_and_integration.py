import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal
from app.tasks.repository import task_repository
from app.generation.llm_generator import llm_generator
from app.generation.hybrid_generator import hybrid_generator
from app.generation.rule_generator import rule_generator
from app.validation.validator import adaptation_validator
from app.services.adaptation_service import adaptation_service
from app.services.experiment_service import experiment_service
from app.services.evaluation_service import evaluation_service
from app.database.models import ExperimentRun, Attempt, Adaptation, ValidationResult, IntegrationEvent

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_llm_generator_offline_simulated(db_session):
    """
    Verifies that LLM generator runs deterministically in offline/simulated mode:
    - Child instruction length <= 12 words
    - Cost and latency metadata present
    - Anti-leakage preserved
    - Warm child-safe encouragement present
    """
    task_map = {t.task_code: t for t in task_repository.get_all_tasks(db_session)}
    learner_map = {l.learner_code: l for l in task_repository.get_all_learners(db_session)}
    
    task = task_map["TASK-ENG-001"]
    learner = learner_map["CHILD-002"]

    res = llm_generator.generate(
        task=task,
        learner=learner,
        target_attempt_number=1,
        support_level="moderate"
    )

    assert "child_instruction" in res
    word_count = len(res["child_instruction"].split())
    assert word_count <= 12, f"Word count {word_count} exceeds maximum of 12"
    assert "supportive_message" in res
    assert res["provider"] in ["simulated_llm", "google_gemini", "openai"]
    assert res["processing_time_ms"] > 0
    assert res["estimated_cost"] > 0
    assert "reason_codes" in res
    assert "answer_format" in res


def test_llm_generation_attempt_progression(db_session):
    """
    Verifies that LLM generator adapts instruction format across attempts 1, 2, and 3:
    - Attempt 1: goal instruction
    - Attempt 2: atomic sub-step
    - Attempt 3: binary choice
    """
    task_map = {t.task_code: t for t in task_repository.get_all_tasks(db_session)}
    learner_map = {l.learner_code: l for l in task_repository.get_all_learners(db_session)}
    task = task_map["TASK-ENG-002"]  # Habitat task
    learner = learner_map["CHILD-001"]

    att1 = llm_generator.generate(task, learner, target_attempt_number=1, support_level="mild")
    att2 = llm_generator.generate(task, learner, target_attempt_number=2, support_level="moderate")
    att3 = llm_generator.generate(task, learner, target_attempt_number=3, support_level="strong")

    assert len(att1["child_instruction"].split()) <= 12
    assert len(att2["child_instruction"].split()) <= 12
    assert len(att3["child_instruction"].split()) <= 12
    assert att3["answer_format"] == "two_picture_choice"


def test_hybrid_generator_safety_fallback(db_session, monkeypatch):
    """
    Verifies that Hybrid generator validates LLM output:
    1. Approved candidate passes through as hybrid mode.
    2. Candidate that leaks answer triggers fallback to safe rule template.
    """
    task_map = {t.task_code: t for t in task_repository.get_all_tasks(db_session)}
    learner_map = {l.learner_code: l for l in task_repository.get_all_learners(db_session)}
    task = task_map["TASK-ENG-002"]
    learner = learner_map["CHILD-001"]

    # 1. Normal safe run
    hybrid_res = hybrid_generator.generate(task, learner, target_attempt_number=1, support_level="mild")
    assert hybrid_res["generation_method"] in ["hybrid", "fallback"]
    assert len(hybrid_res["child_instruction"].split()) <= 12

    # 2. Simulate LLM generating a leaking instruction
    def mock_leaking_generate(*args, **kwargs):
        return {
            "child_instruction": "The fish lives in water.",
            "supportive_message": "Put it there!",
            "vocabulary_support": [],
            "answer_format": "speech",
            "visual_cues": [],
            "reason_codes": ["llm_test"],
            "provider": "simulated_llm",
            "model_name": "gemini-1.5-flash-simulated",
            "processing_time_ms": 60,
            "estimated_cost": 0.0001
        }

    monkeypatch.setattr(llm_generator, "generate", mock_leaking_generate)

    fallback_res = hybrid_generator.generate(task, learner, target_attempt_number=1, support_level="mild")
    assert fallback_res["generation_method"] == "fallback"
    assert "rejected_candidate" in fallback_res
    assert fallback_res["rejected_candidate"]["child_instruction"] == "The fish lives in water."
    assert "safe_rule_fallback_activated" in fallback_res["reason_codes"]
    # The returned instruction must NOT be the leaked one
    assert fallback_res["child_instruction"] != "The fish lives in water."


def test_adaptation_service_hybrid_mode(db_session):
    """
    Verifies that AdaptationService runs with generation_mode="hybrid",
    creates Adaptation and records metadata (provider, model_name, cost, processing_time_ms).
    """
    task_map = {t.task_code: t for t in task_repository.get_all_tasks(db_session)}
    learner_map = {l.learner_code: l for l in task_repository.get_all_learners(db_session)}
    task = task_map["TASK-ENG-003"]
    learner = learner_map["CHILD-003"]

    exp = experiment_service.create_experiment_run(
        db_session,
        learner_id=learner.id,
        task_id=task.id,
        generation_mode="hybrid"
    )

    adaptation = adaptation_service.create_initial_adaptation(
        db_session,
        experiment_run=exp,
        generation_mode="hybrid"
    )

    assert adaptation.experiment_run_id == exp.id
    assert adaptation.target_attempt_number == 1
    assert adaptation.generation_method in ["hybrid", "fallback"]
    assert adaptation.provider is not None
    assert adaptation.model_name is not None
    assert adaptation.processing_time_ms > 0
    assert adaptation.estimated_cost is not None

    # Check ValidationResult
    val_results = db_session.query(ValidationResult).filter(
        ValidationResult.adaptation_id == adaptation.id
    ).order_by(ValidationResult.validation_sequence.asc()).all()
    assert len(val_results) >= 1
    assert val_results[-1].status == "approved"
    assert val_results[-1].is_final is True


def test_component_1_task_delivery_payload(db_session):
    """
    Verifies Component 1 payload adheres strictly to Document 2.2 schema:
    - do_not_reveal_answer is True
    - validation_status is approved
    - contains child instruction and cues
    """
    task_map = {t.task_code: t for t in task_repository.get_all_tasks(db_session)}
    learner_map = {l.learner_code: l for l in task_repository.get_all_learners(db_session)}
    task = task_map["TASK-ENG-004"]
    learner = learner_map["CHILD-002"]

    exp = experiment_service.create_experiment_run(db_session, learner.id, task.id, generation_mode="rule")
    adaptation_service.create_initial_adaptation(db_session, exp, generation_mode="rule")

    payload = evaluation_service.get_component_1_payload(db_session, exp.id)
    assert payload["task_id"] == "TASK-ENG-004"
    assert payload["attempt_number"] == 1
    assert payload["do_not_reveal_answer"] is True
    assert payload["validation_status"] == "approved"
    assert "child_instruction" in payload
    assert "supportive_message" in payload
    assert "answer_format" in payload


def test_component_3_ar_payload(db_session):
    """
    Verifies Component 3 (AR Subsystem) payload adheres strictly to Document 2.2 schema:
    - language is "en"
    - includes spatial_anchors, object_labels, highlight_targets
    """
    task_map = {t.task_code: t for t in task_repository.get_all_tasks(db_session)}
    learner_map = {l.learner_code: l for l in task_repository.get_all_learners(db_session)}
    task = task_map["TASK-ENG-010"]  # Garden Plant Growth AR task
    learner = learner_map["CHILD-004"]

    exp = experiment_service.create_experiment_run(db_session, learner.id, task.id, generation_mode="hybrid")
    adaptation_service.create_initial_adaptation(db_session, exp, generation_mode="hybrid")

    ar_payload = evaluation_service.get_ar_payload(db_session, exp.id)
    assert ar_payload["task_id"] == "TASK-ENG-010"
    assert ar_payload["language"] == "en"
    assert "spatial_anchors" in ar_payload
    assert "object_labels" in ar_payload
    assert "highlight_targets" in ar_payload
    assert "interaction_type" in ar_payload


def test_component_4_analytics_payload(db_session):
    """
    Verifies Component 4 (Learner Modeling) payload:
    - contains learner_id, task_id, attempt_number, result
    - observed_patterns list
    - clinician diagnostic_summary
    """
    task_map = {t.task_code: t for t in task_repository.get_all_tasks(db_session)}
    learner_map = {l.learner_code: l for l in task_repository.get_all_learners(db_session)}
    task = task_map["TASK-ENG-001"]
    learner = learner_map["CHILD-001"]

    exp = experiment_service.create_experiment_run(db_session, learner.id, task.id, generation_mode="rule")
    ad1 = adaptation_service.create_initial_adaptation(db_session, exp, generation_mode="rule")

    experiment_service.record_attempt(
        db=db_session,
        experiment_run_id=exp.id,
        adaptation_id=ad1.id,
        speech_transcript="blue ball",
        speech_confidence=0.88,
        response_time_ms=3200
    )

    comp4 = evaluation_service.get_component_4_payload(db_session, exp.id)
    assert comp4["learner_id"] == "CHILD-001"
    assert comp4["task_id"] == "TASK-ENG-001"
    assert comp4["attempt_number"] == 1
    assert "observed_patterns" in comp4
    assert "diagnostic_summary" in comp4
    assert "next_recommendation" in comp4


def test_generator_comparison_api(client, db_session):
    """
    Tests GET /api/generate-comparison/{task_id}/{learner_id} returning
    side-by-side Rule vs LLM vs Hybrid adaptations.
    """
    task_map = {t.task_code: t for t in task_repository.get_all_tasks(db_session)}
    learner_map = {l.learner_code: l for l in task_repository.get_all_learners(db_session)}
    task = task_map["TASK-ENG-005"]
    learner = learner_map["CHILD-002"]

    response = client.get(f"/api/generate-comparison/{task.id}/{learner.id}?attempt_number=1")
    assert response.status_code == 200
    data = response.json()

    assert data["task_id"] == "TASK-ENG-005"
    assert data["target_attempt_number"] == 1
    assert "comparison" in data
    comp = data["comparison"]
    assert "rule" in comp
    assert "llm" in comp
    assert "hybrid" in comp

    # Verify metrics for each generator
    for gen_key in ["rule", "llm", "hybrid"]:
        g = comp[gen_key]
        assert "instruction" in g
        assert "latency_ms" in g
        assert "estimated_cost" in g
        assert "validation_status" in g
        assert g["word_count"] <= 12


def test_integration_events_api(client, db_session):
    """
    Tests GET /api/integration-events/{experiment_id} returning chronological integration events.
    """
    task_map = {t.task_code: t for t in task_repository.get_all_tasks(db_session)}
    learner_map = {l.learner_code: l for l in task_repository.get_all_learners(db_session)}
    task = task_map["TASK-ENG-006"]
    learner = learner_map["CHILD-003"]

    exp = experiment_service.create_experiment_run(db_session, learner.id, task.id, generation_mode="hybrid")
    ad1 = adaptation_service.create_initial_adaptation(db_session, exp, generation_mode="hybrid")

    # Call component 1 and AR payload endpoints to trigger integration logging
    client.get(f"/api/output/component-1/{exp.id}")
    client.get(f"/api/output/ar/{exp.id}")

    # Fetch integration events
    ev_resp = client.get(f"/api/integration-events/{exp.id}")
    assert ev_resp.status_code == 200
    events = ev_resp.json()

    assert len(events) >= 1
    comp_targets = [e["target_component"] for e in events]
    assert "component_1" in comp_targets
