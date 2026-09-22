import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal
from app.tasks.repository import task_repository
from app.validation.answer_leakage import answer_leakage_detector
from app.validation.child_suitability import child_suitability_checker
from app.validation.validator import adaptation_validator
from app.services.adaptation_service import adaptation_service
from app.services.experiment_service import experiment_service
from app.retry_controller.retry_manager import retry_manager
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

def test_relation_aware_answer_leakage_detection(db_session):
    """
    Verifies that AnswerLeakageDetector:
    1. Catches exact restricted solution phrases
    2. Catches subject-relation-answer binding
    3. Catches direct answer directives
    4. Permits candidate options when policy allows candidate presentation
    5. Does not falsely flag allowed instruction terms
    """
    task_map = {t.task_code: t for t in task_repository.get_all_tasks(db_session)}
    task_habitat = task_map["TASK-ENG-002"]  # Animal habitat

    # 1. Restricted phrase
    res1 = answer_leakage_detector.check_leakage("The fish lives in water", task_habitat)
    assert res1["is_leaked"] is True
    assert res1["leakage_type"] in ["restricted_phrase", "relation_binding"]

    # 2. Subject-relation-answer binding
    res2 = answer_leakage_detector.check_leakage("Put the fish in the water", task_habitat)
    assert res2["is_leaked"] is True
    assert res2["leakage_type"] in ["restricted_phrase", "relation_binding"]

    # 3. Direct answer directive
    res3 = answer_leakage_detector.check_leakage("The correct answer is water", task_habitat)
    assert res3["is_leaked"] is True
    assert res3["leakage_type"] == "direct_solution_directive"

    # 4. Scaffolding choice: Candidate presentation is allowed for TASK-ENG-002
    res4 = answer_leakage_detector.check_leakage("Look at fish. Choose: water or tree?", task_habitat)
    assert res4["is_leaked"] is False

    # 5. Allowed terms without answer reveal
    res5 = answer_leakage_detector.check_leakage("Put each animal in its home.", task_habitat)
    assert res5["is_leaked"] is False

def test_child_suitability_and_safety_filtering():
    """
    Verifies that ChildSuitabilityChecker:
    1. Blocks punitive/harsh language
    2. Blocks clinical/diagnostic jargon
    3. Flags sentence length > 12 words
    4. Approves clean child-friendly instructions
    """
    # 1. Punitive language
    res_punitive = child_suitability_checker.check_suitability("That was wrong, you failed. Try harder.")
    assert res_punitive["safety_valid"] is False
    assert res_punitive["child_suitable"] is False
    assert any("wrong" in v for v in res_punitive["violations"])

    # 2. Clinical jargon
    res_clinical = child_suitability_checker.check_suitability("This child has DLD and a low risk score.")
    assert res_clinical["safety_valid"] is False
    assert res_clinical["child_suitable"] is False
    assert any("dld" in v or "risk score" in v for v in res_clinical["violations"])

    # 3. Sentence length > 12 words
    long_instruction = "Before you pack away the crayons make sure that you also take the drawing paper and put it into the recycle bin."
    res_long = child_suitability_checker.check_suitability(long_instruction)
    assert res_long["sentence_length_valid"] is False
    assert res_long["maximum_words_in_sentence"] > 12

    # 4. Compliant instruction
    res_clean = child_suitability_checker.check_suitability(
        instruction="Put your crayons in the box.",
        supportive_message="You can do it!"
    )
    assert res_clean["safety_valid"] is True
    assert res_clean["sentence_length_valid"] is True
    assert res_clean["child_suitable"] is True

def test_multi_sequence_validation_and_fallback(db_session):
    """
    Verifies that when a candidate output is rejected (e.g. answer leakage):
    - Sequence 1 is recorded as status='rejected', is_final=False
    - A safe rule fallback is generated as Sequence 2 with status='approved', is_final=True
    - The adaptation is created with generation_method='fallback'
    """
    tasks = task_repository.get_all_tasks(db_session)
    learners = task_repository.get_all_learners(db_session)
    task = [t for t in tasks if t.task_code == "TASK-ENG-001"][0]
    learner = [l for l in learners if l.learner_code == "CHILD-001"][0]

    # Create an experiment run
    exp = experiment_service.create_experiment_run(db_session, learner.id, task.id)

    # Bad candidate that leaks the answer
    bad_candidate = {
        "child_instruction": "Put crayons in the box and paper in green bin.",
        "supportive_message": "Do not get it wrong!",
        "support_level": "moderate",
        "answer_format": "tap_and_place",
        "visual_cues": ["highlight_box"]
    }

    adaptation = adaptation_service.create_initial_adaptation(
        db_session,
        exp,
        candidate_override=bad_candidate
    )

    assert adaptation is not None
    assert adaptation.generation_method == "fallback"

    # Query validation results for this adaptation
    val_results = db_session.query(ValidationResult).filter(
        ValidationResult.adaptation_id == adaptation.id
    ).order_by(ValidationResult.validation_sequence).all()

    assert len(val_results) == 2
    # Sequence 1: Rejected
    assert val_results[0].validation_sequence == 1
    assert val_results[0].status == "rejected"
    assert val_results[0].is_final is False
    assert val_results[0].answer_leakage is True

    # Sequence 2: Approved fallback
    assert val_results[1].validation_sequence == 2
    assert val_results[1].status == "approved"
    assert val_results[1].is_final is True
    assert val_results[1].answer_leakage is False

def test_retry_state_machine_full_escalation(db_session):
    """
    Tests complete 3-attempt escalation progression:
    Attempt 1 (unsuccessful) -> Attempt 2 (unsuccessful) -> Attempt 3 (unsuccessful) -> Adult Escalation.
    Verifies non-punitive child message and researcher diagnostic summary.
    """
    tasks = task_repository.get_all_tasks(db_session)
    learners = task_repository.get_all_learners(db_session)
    task = [t for t in tasks if t.task_code == "TASK-ENG-002"][0]
    learner = [l for l in learners if l.learner_code == "CHILD-001"][0]

    # 1. Start experiment & create initial adaptation
    exp = experiment_service.create_experiment_run(db_session, learner.id, task.id)
    ad1 = adaptation_service.create_initial_adaptation(db_session, exp)
    assert ad1.target_attempt_number == 1

    # 2. Attempt 1: Incorrect response
    res1 = experiment_service.record_attempt(
        db=db_session,
        experiment_run_id=exp.id,
        adaptation_id=ad1.id,
        speech_transcript="Fish live in a tree.",
        speech_confidence=0.92,
        response_time_ms=7000
    )
    assert res1["attempt"].attempt_number == 1
    assert res1["attempt"].concept_result in ["incorrect", "unclear"]
    assert res1["experiment_status"] == "active"
    assert res1["next_adaptation"] is not None
    assert res1["next_adaptation"].target_attempt_number == 2

    ad2 = res1["next_adaptation"]

    # 3. Attempt 2: Partial/Incorrect response
    res2 = experiment_service.record_attempt(
        db=db_session,
        experiment_run_id=exp.id,
        adaptation_id=ad2.id,
        speech_transcript="Fish in a tree.",
        speech_confidence=0.88,
        response_time_ms=6000
    )
    assert res2["attempt"].attempt_number == 2
    assert res2["experiment_status"] == "active"
    assert res2["next_adaptation"] is not None
    assert res2["next_adaptation"].target_attempt_number == 3

    ad3 = res2["next_adaptation"]

    # 4. Attempt 3: Incorrect response -> triggers adult escalation
    res3 = experiment_service.record_attempt(
        db=db_session,
        experiment_run_id=exp.id,
        adaptation_id=ad3.id,
        speech_transcript="I don't know.",
        speech_confidence=0.95,
        response_time_ms=5000
    )
    assert res3["attempt"].attempt_number == 3
    assert res3["next_adaptation"] is None
    assert res3["experiment_status"] == "escalated"
    assert res3["final_outcome"] == "adult_support"

    # Check escalation payload
    esc = res3["escalation_payload"]
    assert esc is not None
    assert "teacher or helper" in esc["child_message"].lower()
    assert esc["child_visual_theme"] == "helper_hands"
    assert "CHILD-001" in esc["researcher_summary"]
    assert esc["attempt_count"] == 3

    # Check integration events in DB
    events = db_session.query(IntegrationEvent).filter(
        IntegrationEvent.experiment_run_id == exp.id
    ).all()
    event_targets = [e.target_component for e in events]
    assert "component_1" in event_targets
    assert "component_4" in event_targets

def test_retry_state_machine_early_success(db_session):
    """
    Verifies that if an attempt succeeds on Attempt 2, the experiment completes immediately
    without generating Attempt 3.
    """
    tasks = task_repository.get_all_tasks(db_session)
    learners = task_repository.get_all_learners(db_session)
    task = [t for t in tasks if t.task_code == "TASK-ENG-002"][0]
    learner = [l for l in learners if l.learner_code == "CHILD-003"][0]

    exp = experiment_service.create_experiment_run(db_session, learner.id, task.id)
    ad1 = adaptation_service.create_initial_adaptation(db_session, exp)

    # Attempt 1: Incorrect
    res1 = experiment_service.record_attempt(
        db=db_session,
        experiment_run_id=exp.id,
        adaptation_id=ad1.id,
        speech_transcript="Fish tree.",
        speech_confidence=0.9
    )
    assert res1["experiment_status"] == "active"
    ad2 = res1["next_adaptation"]
    assert ad2 is not None

    # Attempt 2: Correct response ("water")
    res2 = experiment_service.record_attempt(
        db=db_session,
        experiment_run_id=exp.id,
        adaptation_id=ad2.id,
        speech_transcript="Fish live in water.",
        speech_confidence=0.95
    )
    assert res2["attempt"].concept_result == "correct"
    assert res2["experiment_status"] == "completed"
    assert res2["final_outcome"] == "success"
    assert res2["next_adaptation"] is None

def test_api_validate_output_and_retry_state(client, db_session):
    """
    Tests POST /api/validate-output and GET /api/retry-state/{id} endpoints.
    """
    task = task_repository.get_all_tasks(db_session)[0]
    learner = task_repository.get_all_learners(db_session)[0]

    # Test /api/validate-output with compliant instruction
    payload_good = {
        "task_id": task.id,
        "child_instruction": "Put your crayons in the box.",
        "supportive_message": "Good job!",
        "target_attempt_number": 1,
        "support_level": "moderate"
    }
    resp1 = client.post("/api/validate-output", json=payload_good)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["status"] == "approved"
    assert data1["safety_valid"] is True
    assert data1["answer_leakage"] is False

    # Test /api/validate-output with leaked answer
    payload_bad = {
        "task_id": task.id,
        "child_instruction": "The answer is crayons in box and paper in bin.",
        "supportive_message": "Do not fail!",
        "target_attempt_number": 1,
        "support_level": "moderate"
    }
    resp2 = client.post("/api/validate-output", json=payload_bad)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["status"] == "rejected"
    assert data2["answer_leakage"] is True

    # Test /api/retry-state/{id}
    exp = experiment_service.create_experiment_run(db_session, learner.id, task.id)
    ad1 = adaptation_service.create_initial_adaptation(db_session, exp)

    resp3 = client.get(f"/api/retry-state/{exp.id}")
    assert resp3.status_code == 200
    state_data = resp3.json()
    assert state_data["experiment_id"] == exp.id
    assert state_data["status"] == "active"
    assert len(state_data["adaptations"]) >= 1
