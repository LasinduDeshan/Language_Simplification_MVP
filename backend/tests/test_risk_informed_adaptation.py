import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.adaptation_decision_service import AdaptationDecisionService, normalize_text_nfc
from app.localization.activity_catalog import (
    get_governed_activity_localization,
    enrich_child_view_localization
)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def decision_service():
    return AdaptationDecisionService()

def test_initial_strategy_by_support_level(decision_service):
    res_low = decision_service.select_initial_strategy({'recommended_support_level': 'LOW'})
    assert res_low['strategy_code'] == 'ORIGINAL_BASELINE'
    assert res_low['adaptation_strategy'] == 'original_baseline'
    assert 'INITIAL_SUPPORT_LOW' in res_low['reason_codes']
    assert res_low['approved_for_child_delivery'] is False

    res_mod = decision_service.select_initial_strategy({'recommended_support_level': 'MODERATE'})
    assert res_mod['strategy_code'] == 'MILD_SUPPORT'
    assert res_mod['adaptation_strategy'] == 'mild_support'
    assert 'INITIAL_SUPPORT_MODERATE' in res_mod['reason_codes']

    res_high = decision_service.select_initial_strategy({'recommended_support_level': 'HIGH'})
    assert res_high['strategy_code'] == 'STRONG_SCAFFOLD'
    assert res_high['adaptation_strategy'] == 'strong_scaffold'
    assert 'INITIAL_SUPPORT_HIGH' in res_high['reason_codes']

def test_initial_strategy_handles_alias_levels(decision_service):
    assert decision_service.select_initial_strategy({'recommended_support_level': 'mild'})['strategy_code'] == 'ORIGINAL_BASELINE'
    assert decision_service.select_initial_strategy({'recommended_support_level': 'strong'})['strategy_code'] == 'STRONG_SCAFFOLD'
    assert decision_service.select_initial_strategy({'recommended_support_level': 'UNKNOWN'})['strategy_code'] == 'MILD_SUPPORT'

def test_transition_correct_timely_maintains(decision_service):
    class DummyAttempt:
        adaptation_strategy = 'MILD_SUPPORT'
        presented_instruction = 'Look at the animal. What is its name?'

    evidence = {'correct': True, 'response_time_ms': 5000, 'expected_time_ms': 15000}
    decision = decision_service.select_next_strategy(DummyAttempt(), evidence)
    assert decision['next_strategy_code'] == 'MILD_SUPPORT'
    assert 'CORRECT_AND_TIMELY' in decision['reason_codes']
    assert decision['action'] == 'complete_or_maintain'

def test_transition_first_incorrect_escalates_one_level(decision_service):
    class DummyAttempt:
        adaptation_strategy = 'ORIGINAL_BASELINE'
        presented_instruction = 'Look at the animal and tell me its name.'

    evidence = {'correct': False, 'previous_errors': 0}
    decision = decision_service.select_next_strategy(DummyAttempt(), evidence)
    assert decision['next_strategy_code'] == 'MILD_SUPPORT'
    assert 'FIRST_INCORRECT_RESPONSE' in decision['reason_codes']
    assert decision['action'] == 'escalate'

def test_transition_repeated_incorrect_escalates_to_strong(decision_service):
    class DummyAttempt:
        adaptation_strategy = 'MILD_SUPPORT'
        presented_instruction = 'Look at the animal. What is its name?'

    evidence = {'correct': False, 'previous_errors': 1}
    decision = decision_service.select_next_strategy(DummyAttempt(), evidence)
    assert decision['next_strategy_code'] in ['STRONG_SCAFFOLD', 'STRONG_DECOMPOSED_STEP']
    assert 'REPEATED_INCORRECT_RESPONSE' in decision['reason_codes']

def test_transition_timeout_pathway(decision_service):
    class DummyAttempt:
        adaptation_strategy = 'ORIGINAL_BASELINE'
        presented_instruction = 'Look at the animal and tell me its name.'

    evidence = {'correct': False, 'timeout': True}
    decision = decision_service.select_next_strategy(DummyAttempt(), evidence)
    assert 'TIMEOUT_OR_NO_RESPONSE' in decision['reason_codes']
    assert 'EXTENDED_RESPONSE_TIME' in decision['additional_support']
    assert 'AUDIO_PROMPT_REPEAT' in decision['additional_support']

def test_minimal_safe_instruction_detection_and_governed_reuse(decision_service):
    class DummyAttempt:
        id = 'ATT-PREV-001'
        adaptation_strategy = 'STRONG_SCAFFOLD'
        presented_instruction = 'Look at the animal. Choose: cat or dog.'

    cat = get_governed_activity_localization('VOC-NAMING-001')
    evidence = {'correct': False, 'previous_errors': 1}

    decision = decision_service.select_next_strategy(DummyAttempt(), evidence, activity=cat)
    assert decision['next_strategy_code'] == 'UNCHANGED_REUSE'
    assert decision['reuse_declared'] is True
    assert 'VISUAL_CHOICE_HIGHLIGHTING' in decision['additional_support']
    assert 'TOUCH_RESPONSE_MODE' in decision['additional_support']
    assert decision['reuse_lineage']['reuse_reason_code'] == 'MINIMAL_SAFE_INSTRUCTION_ALREADY_REACHED'

def test_nfc_normalization_detects_identical_strings():
    text1 = "\u0db4\u0dd6\u0dc3\u0dcf"
    text2 = normalize_text_nfc("\u0db4\u0dd6\u0dc3\u0dcf")
    assert normalize_text_nfc(text1) == text2

def test_sinhala_child_view_never_shows_english():
    class DummyTask:
        id = "TASK-EN-ONLY"
        task_code = "TASK-EN-ONLY"
        title = "English Task"
        options = None
        tokens = None

    class DummyAttempt:
        support_level = "mild"
        presented_instruction = "Look at the animal."
        presented_instruction_si = None

    view = {"presented_instruction": "Look at the animal.", "options": []}
    enriched = enrich_child_view_localization(view, DummyTask(), DummyAttempt())
    assert enriched.get("instruction_si") is None
    assert enriched.get("content_language_status", {}).get("si") == "UNAVAILABLE"

def test_voc_naming_001_catalog_has_all_governed_strategies():
    cat = get_governed_activity_localization('VOC-NAMING-001')
    assert cat is not None
    sv = cat['support_versions']

    required_strategies = [
        'ORIGINAL_BASELINE', 'MILD_SUPPORT', 'MODERATE_SUPPORT',
        'STRONG_SCAFFOLD', 'STRONG_DECOMPOSED_STEP', 'UNCHANGED_REUSE'
    ]
    for s in required_strategies:
        assert s in sv, f"Strategy {s} missing from VOC-NAMING-001"
        assert sv[s]['en'] and len(sv[s]['en'].split()) >= 2
        assert sv[s]['si'] and len(sv[s]['si']) >= 5

def test_end_to_end_risk_recommendation_intake(client):
    lrn_res = client.get('/api/learners/CHILD-001')
    assert lrn_res.status_code == 200
    learner = lrn_res.json()

    s_low = client.post('/api/activity-sessions', json={
        'learner_id': learner['id'],
        'task_id': 'VOC-NAMING-001',
        'recommended_support_level': 'LOW',
        'source_recommendation_id': 'REC-TEST-LOW-001'
    }).json()
    assert s_low['initial_support_level'] == 'mild'

    att1_low = client.post(f"/api/activity-sessions/{s_low['id']}/attempts").json()['attempt']
    assert att1_low['adaptation_strategy'] == 'original_baseline'
    assert att1_low['presented_instruction'] == 'Look at the animal and tell me its name.'
    lineage_low = att1_low['automatic_analysis_snapshot']['simplification_lineage']
    assert lineage_low['strategy_code'] == 'ORIGINAL_BASELINE'
    assert lineage_low['approved_for_child_delivery'] is False
    assert lineage_low['score_interpretation'] == 'INDEPENDENT_BASELINE'

    s_high = client.post('/api/activity-sessions', json={
        'learner_id': learner['id'],
        'task_id': 'VOC-NAMING-001',
        'recommended_support_level': 'HIGH',
        'source_recommendation_id': 'REC-TEST-HIGH-001'
    }).json()
    assert s_high['initial_support_level'] == 'strong'

    att1_high = client.post(f"/api/activity-sessions/{s_high['id']}/attempts").json()['attempt']
    assert att1_high['adaptation_strategy'] == 'strong_scaffold'
    assert att1_high['presented_instruction'] == 'Look at the animal. Choose: cat or dog.'
    lineage_high = att1_high['automatic_analysis_snapshot']['simplification_lineage']
    assert lineage_high['strategy_code'] == 'STRONG_SCAFFOLD'
    assert lineage_high['approved_for_child_delivery'] is False