import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.response_analysis.answer_checker import answer_checker
from app.grammar_analysis.grammar_extractor import grammar_extractor
from app.response_analysis.language_extractor import language_extractor
from app.tasks.repository import task_repository
from app.database.db import SessionLocal

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

def test_concept_vs_grammar_separation(db_session):
    """
    Critical research test:
    - 'Fish live water.' has a grammar error (missing preposition), but concept is CORRECT.
    - 'Fish live in a tree.' has perfect grammar, but concept is INCORRECT.
    """
    task = task_repository.get_task_by_id(db_session, "TASK-ENG-002")
    assert task is not None

    # Case A: Correct concept, grammar error
    res_a = answer_checker.evaluate_answer(task, "Fish live water.")
    assert res_a["concept_result"] == "correct"

    gram_a = grammar_extractor.analyze_grammar("Fish live water.", speech_confidence=0.92)
    obs_codes_a = [o["observation_code"] for o in gram_a["observations"]]
    assert "missing_preposition" in obs_codes_a
    assert gram_a["observations"][0]["confirmed"] is True

    # Case B: Incorrect concept, grammatically sound
    res_b = answer_checker.evaluate_answer(task, "Fish live in a tree.")
    assert res_b["concept_result"] == "incorrect"

    gram_b = grammar_extractor.analyze_grammar("Fish live in a tree.", speech_confidence=0.95)
    obs_codes_b = [o["observation_code"] for o in gram_b["observations"]]
    assert "missing_preposition" not in obs_codes_b

def test_subject_verb_agreement_vs_concept(db_session):
    """
    - 'She kick the ball.' -> Concept correct, Grammar: subject_verb_agreement
    - 'He is kicking the ball.' -> Concept incorrect (wrong pronoun for girl), Grammar: sound
    """
    task = task_repository.get_task_by_id(db_session, "TASK-ENG-009")
    assert task is not None

    # Case A: Correct concept, subject-verb disagreement
    res_a = answer_checker.evaluate_answer(task, "She kick the ball.")
    assert res_a["concept_result"] == "correct"

    gram_a = grammar_extractor.analyze_grammar("She kick the ball.", speech_confidence=0.91)
    obs_codes_a = [o["observation_code"] for o in gram_a["observations"]]
    assert "subject_verb_agreement" in obs_codes_a

    # Case B: Incorrect concept (wrong gender pronoun), correct grammar
    res_b = answer_checker.evaluate_answer(task, "He is kicking the ball.")
    assert res_b["concept_result"] == "incorrect"

    gram_b = grammar_extractor.analyze_grammar("He is kicking the ball.", speech_confidence=0.95)
    obs_codes_b = [o["observation_code"] for o in gram_b["observations"]]
    assert "subject_verb_agreement" not in obs_codes_b

def test_speech_confidence_gating():
    """
    Low speech confidence (<0.70) must mark grammar observations as unconfirmed
    to avoid false pattern induction.
    """
    transcript = "Fish live water."

    # Normal confidence -> confirmed
    gram_high = grammar_extractor.analyze_grammar(transcript, speech_confidence=0.85)
    assert gram_high["speech_confidence_acceptable"] is True
    assert gram_high["observations"][0]["confirmed"] is True

    # Low confidence -> unconfirmed
    gram_low = grammar_extractor.analyze_grammar(transcript, speech_confidence=0.58)
    assert gram_low["speech_confidence_acceptable"] is False
    assert gram_low["observations"][0]["confirmed"] is False
    assert gram_low["observations"][0]["unconfirmed_reason"] == "low_speech_confidence"

def test_word_order_and_copula_rules():
    """Test noun-adjective inversion and omitted copula rules."""
    # Inverted word order
    wo_res = grammar_extractor.analyze_grammar("I put the ball blue in the box.", speech_confidence=0.90)
    wo_codes = [o["observation_code"] for o in wo_res["observations"]]
    assert "incorrect_word_order" in wo_codes

    # Omitted copula
    cop_res = grammar_extractor.analyze_grammar("Red triangle next to yellow square.", speech_confidence=0.90)
    cop_codes = [o["observation_code"] for o in cop_res["observations"]]
    assert "omitted_copula" in cop_codes

def test_missing_article_rule():
    """Test missing article before singular countable noun."""
    art_res = grammar_extractor.analyze_grammar("Put cat under desk.", speech_confidence=0.90)
    art_codes = [o["observation_code"] for o in art_res["observations"]]
    assert "missing_article" in art_codes

def test_vocabulary_and_instruction_following(db_session):
    """Test vocabulary difficulty detector and step-dropoff identification."""
    task_cat = task_repository.get_task_by_id(db_session, "TASK-ENG-002")
    
    # 6yo learner encountering "habitat" (minimum age 8)
    vocab_obs = language_extractor.analyze_vocabulary_and_comprehension(
        transcript="Fish live in their habitat.",
        task=task_cat,
        learner_age=6
    )
    obs_codes = [o["observation_code"] for o in vocab_obs]
    assert "unfamiliar_habitat" in obs_codes
    entry = next(o for o in vocab_obs if o["observation_code"] == "unfamiliar_habitat")
    assert entry["simple_alternative"] == "home"

    # Classroom task two-step dropoff
    task_clean = task_repository.get_task_by_id(db_session, "TASK-ENG-001")
    step_obs = language_extractor.analyze_vocabulary_and_comprehension(
        transcript="I put the crayons.",
        task=task_clean,
        learner_age=5
    )
    step_codes = [o["observation_code"] for o in step_obs]
    assert "difficulty_with_two_step_instruction" in step_codes

def test_analyze_response_api_endpoint(client):
    """Test POST /api/analyze-response returns structured observations and concept evaluation."""
    response = client.post("/api/analyze-response", json={
        "task_id": "TASK-ENG-002",
        "speech_transcript": "Fish live water.",
        "speech_confidence": 0.92,
        "learner_age": 6
    })
    assert response.status_code == 200
    data = response.json()
    assert data["concept_result"] == "correct"
    assert data["speech_confidence_acceptable"] is True
    
    obs_codes = [o["observation_code"] for o in data["observations"]]
    assert "missing_preposition" in obs_codes


def test_grammar_test_cases_api_endpoint(client):
    """Test GET /api/grammar-test-cases returns 8 seeded test cases."""
    response = client.get("/api/grammar-test-cases")
    assert response.status_code == 200
    cases = response.json()
    assert len(cases) >= 8
    test_ids = [c["test_id"] for c in cases]
    assert "GRAMMAR-TEST-001" in test_ids
    assert "GRAMMAR-TEST-005" in test_ids
