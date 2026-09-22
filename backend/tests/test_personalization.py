import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal
from app.tasks.repository import task_repository
from app.personalization.controller import personalization_controller
from app.generation.rule_generator import rule_generator
from app.services.adaptation_service import adaptation_service

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

def test_support_level_matrix_for_all_learners(db_session):
    """
    Verifies support level matrix based on learner risk profile and developmental scores:
    - High risk / low scores (<45) -> Strong
    - Moderate risk / emerging English -> Moderate
    - Low risk with high scores (>=65) -> Mild
    """
    learners = task_repository.get_all_learners(db_session)
    learner_map = {l.learner_code: l for l in learners}

    # CHILD-003: low risk, vocab 78, grammar 74, developing -> Mild on Attempt 1
    c3 = learner_map["CHILD-003"]
    res_c3 = personalization_controller.determine_support_level(c3, target_attempt_number=1)
    assert res_c3["support_level"] == "mild"
    assert "base_risk_low" in res_c3["reason_codes"]

    # Moderate risk learner (CHILD-002): Moderate on Attempt 1
    c_mod = next(l for l in learners if (l.risk_support_level or "").lower() == "moderate")
    res_c_mod = personalization_controller.determine_support_level(c_mod, target_attempt_number=1)
    assert res_c_mod["support_level"] == "moderate"
    assert "base_risk_moderate" in res_c_mod["reason_codes"]

    # High risk learner (CHILD-001): Strong on Attempt 1
    c_high = next(l for l in learners if (l.risk_support_level or "").lower() == "high")
    res_c_high = personalization_controller.determine_support_level(c_high, target_attempt_number=1)
    assert res_c_high["support_level"] == "strong"
    assert "base_risk_high" in res_c_high["reason_codes"]

    # Emerging English level learner (CHILD-001 / CHILD-002): At least Moderate on Attempt 1
    c_em = next(l for l in learners if (l.english_level or "").lower() == "emerging")
    res_c_em = personalization_controller.determine_support_level(c_em, target_attempt_number=1)
    assert res_c_em["support_level"] in ["moderate", "strong"]
    assert "english_level_emerging" in res_c_em["reason_codes"]

def test_attempt_escalation_logic(db_session):
    """
    Verifies progressive retry escalation across Attempts 1, 2, and 3:
    CHILD-003 (Low risk): Attempt 1 (Mild) -> Attempt 2 (Moderate) -> Attempt 3 (Strong).
    """
    c3 = task_repository.get_learner_by_id(db_session, "CHILD-003")
    
    # Attempt 1 -> mild
    res1 = personalization_controller.determine_support_level(c3, target_attempt_number=1)
    assert res1["support_level"] == "mild"

    # Attempt 2 -> moderate (escalated by +1)
    res2 = personalization_controller.determine_support_level(c3, target_attempt_number=2)
    assert res2["support_level"] == "moderate"
    assert "attempt_2_retry_escalation" in res2["reason_codes"]

    # Attempt 3 -> strong (maximum support)
    res3 = personalization_controller.determine_support_level(c3, target_attempt_number=3)
    assert res3["support_level"] == "strong"
    assert "attempt_3_maximum_support" in res3["reason_codes"]

def test_sentence_length_limits_all_30_permutations(db_session):
    """
    Critical developmental requirement:
    Target <= 8-10 words per sentence, strict maximum 12 words.
    Verify across all 10 seed tasks and all 3 attempts (30 adaptations).
    """
    tasks = task_repository.get_all_tasks(db_session)
    c1 = task_repository.get_learner_by_id(db_session, "CHILD-001")
    assert len(tasks) >= 10

    for task in tasks:
        for attempt_num in [1, 2, 3]:
            for sup_level in ["mild", "moderate", "strong"]:
                gen = rule_generator.generate(
                    task=task,
                    learner=c1,
                    target_attempt_number=attempt_num,
                    support_level=sup_level
                )
                inst = gen["child_instruction"]
                words = inst.split()
                # Strict hard limit is 12 words
                assert len(words) <= 12, f"Instruction for {task.task_code} Att {attempt_num} ({sup_level}) exceeded 12 words: '{inst}' ({len(words)} words)"
                # Must not be empty
                assert len(words) >= 2, f"Instruction too short for {task.task_code}"
                # Must have warm supportive message
                assert gen["supportive_message"] is not None
                # Must specify answer format
                assert gen["answer_format"] in [
                    "speech", "drag_and_drop", "tap_and_place", "two_picture_choice",
                    "single_tap_selection", "tap_selection", "tap_and_hold", "word_ordering"
                ]

def test_vocabulary_replacement_in_rules(db_session):
    """
    Verifies that vocabulary replacement substitutes difficult words
    with age-appropriate alternatives for young learners.
    """
    c_young = task_repository.get_learner_by_id(db_session, "CHILD-004") # age 4
    task_hab = task_repository.get_task_by_id(db_session, "TASK-ENG-002")
    
    # Task 2 original instruction contains "habitat" (min_age 8)
    gen = rule_generator.generate(
        task=task_hab,
        learner=c_young,
        target_attempt_number=1,
        support_level="moderate"
    )
    # The rule template for Task 2 uses "home" instead of "habitat"
    assert "habitat" not in gen["child_instruction"].lower()
    assert "home" in gen["child_instruction"].lower()

def test_preview_progression_api_endpoint(client):
    """Test GET /api/preview-progression/{task_id}/{learner_id} returns all 3 attempts."""
    response = client.get("/api/preview-progression/TASK-ENG-002/CHILD-003")
    assert response.status_code == 200
    data = response.json()
    assert "progression" in data
    assert len(data["progression"]) == 3

    # Check Attempt 1, 2, 3 progression
    att1 = data["progression"][0]
    att2 = data["progression"][1]
    att3 = data["progression"][2]

    assert att1["attempt_number"] == 1
    assert att2["attempt_number"] == 2
    assert att3["attempt_number"] == 3

    assert att1["support_level"] == "mild"
    assert att2["support_level"] == "moderate"
    assert att3["support_level"] == "strong"

    # Check word count is under 12
    assert att1["word_count"] <= 12
    assert att2["word_count"] <= 12
    assert att3["word_count"] <= 12

def test_adapt_instruction_api_endpoint(client):
    """Test POST /api/adapt-instruction returns complete adaptation payload."""
    response = client.post("/api/adapt-instruction", json={
        "task_id": "TASK-ENG-001",
        "learner_id": "CHILD-002",
        "attempt_number": 2,
        "generation_mode": "rule"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["task_code"] == "TASK-ENG-001"
    assert data["attempt_number"] == 2
    assert data["support_level"] == "strong"  # moderate learner escalated to strong on attempt 2
    assert "paper" in data["child_instruction"].lower() or "bin" in data["child_instruction"].lower()
    assert data["word_count"] <= 12
    assert len(data["reason_codes"]) > 0
