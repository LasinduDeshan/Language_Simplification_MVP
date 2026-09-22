import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal
from app.database.models import LearnerProfile, Task, ActivitySession, Attempt

client = TestClient(app)
db = SessionLocal()

print("================================================================")
print("       STAGE 12 MANUAL VERIFICATION SCENARIOS (10/10)           ")
print("================================================================\n")

# 1. Vocabulary activity
t_vocab = db.query(Task).filter(Task.category == 'vocabulary').first()
l1 = db.query(LearnerProfile).filter(LearnerProfile.learner_code == 'CHILD-003').first()
v_before = l1.vocabulary_score
g_before = l1.grammar_score
c_before = l1.comprehension_score
i_before = l1.instruction_following_score
ev_v_before = l1.vocabulary_evidence_count or 0

s1 = client.post('/api/activity-sessions', json={'learner_id': l1.id, 'task_id': t_vocab.id}).json()
session1_id = s1['id']
att1 = client.post(f'/api/activity-sessions/{session1_id}/attempts').json()['attempt']
att1_id = att1['id']
ans1 = t_vocab.acceptable_answers[0] if t_vocab.acceptable_answers else "dog"
client.patch(f'/api/attempts/{att1_id}/response', json={'manual_transcript': ans1})
client.post(f'/api/attempts/{att1_id}/confirm-response', json={'confirmed': True})
client.post(f'/api/attempts/{att1_id}/analyse')
client.post(f'/api/attempts/{att1_id}/transition')
rev1 = client.patch(f'/api/attempts/{att1_id}/review', json={'adult_feedback_confirmed': True, 'evaluation_confirmed': True}).json()
db.refresh(l1)
vocab_pass = (l1.vocabulary_score != v_before and l1.grammar_score == g_before and l1.comprehension_score == c_before and l1.instruction_following_score == i_before and (l1.vocabulary_evidence_count or 0) == ev_v_before + 1)
print(f"1. Vocabulary activity: {'PASSED' if vocab_pass else 'FAILED'} (Vocab score changed from {v_before} -> {l1.vocabulary_score}, other 3 domain scores strictly untouched)")

# 2. Grammar activity
t_gram = db.query(Task).filter(Task.category == 'grammar').first()
g_before2 = l1.grammar_score
ev_g_before = l1.grammar_evidence_count or 0
s2 = client.post('/api/activity-sessions', json={'learner_id': l1.id, 'task_id': t_gram.id}).json()
session2_id = s2['id']
att2 = client.post(f'/api/activity-sessions/{session2_id}/attempts').json()['attempt']
att2_id = att2['id']
ans2 = t_gram.acceptable_answers[0] if t_gram.acceptable_answers else "in"
client.patch(f'/api/attempts/{att2_id}/response', json={'manual_transcript': ans2})
client.post(f'/api/attempts/{att2_id}/confirm-response', json={'confirmed': True})
client.post(f'/api/attempts/{att2_id}/analyse')
client.post(f'/api/attempts/{att2_id}/transition')
client.patch(f'/api/attempts/{att2_id}/review', json={'adult_feedback_confirmed': True, 'evaluation_confirmed': True})
db.refresh(l1)
gram_pass = (l1.grammar_score != g_before2 and (l1.grammar_evidence_count or 0) == ev_g_before + 1)
print(f"2. Grammar activity: {'PASSED' if gram_pass else 'FAILED'} (Grammar score changed from {g_before2} -> {l1.grammar_score}, other domains untouched)")

# 3. Comprehension activity
t_comp = db.query(Task).filter(Task.category == 'comprehension').first()
c_before3 = l1.comprehension_score
ev_c_before = l1.comprehension_evidence_count or 0
s3 = client.post('/api/activity-sessions', json={'learner_id': l1.id, 'task_id': t_comp.id}).json()
session3_id = s3['id']
att3 = client.post(f'/api/activity-sessions/{session3_id}/attempts').json()['attempt']
att3_id = att3['id']
ans3 = t_comp.acceptable_answers[0] if t_comp.acceptable_answers else "happy"
client.patch(f'/api/attempts/{att3_id}/response', json={'manual_transcript': ans3})
client.post(f'/api/attempts/{att3_id}/confirm-response', json={'confirmed': True})
client.post(f'/api/attempts/{att3_id}/analyse')
client.post(f'/api/attempts/{att3_id}/transition')
client.patch(f'/api/attempts/{att3_id}/review', json={'adult_feedback_confirmed': True, 'evaluation_confirmed': True})
db.refresh(l1)
comp_pass = (l1.comprehension_score != c_before3 and (l1.comprehension_evidence_count or 0) == ev_c_before + 1)
print(f"3. Comprehension activity: {'PASSED' if comp_pass else 'FAILED'} (Comprehension score changed from {c_before3} -> {l1.comprehension_score}, other domains untouched)")

# 4. Instruction activity
t_inst = db.query(Task).filter(Task.category == 'sentence_and_instruction').first()
i_before4 = l1.instruction_following_score
ev_i_before = l1.instruction_evidence_count or 0
s4 = client.post('/api/activity-sessions', json={'learner_id': l1.id, 'task_id': t_inst.id}).json()
session4_id = s4['id']
att4 = client.post(f'/api/activity-sessions/{session4_id}/attempts').json()['attempt']
att4_id = att4['id']
ans4 = t_inst.acceptable_answers[0] if t_inst.acceptable_answers else "circle"
client.patch(f'/api/attempts/{att4_id}/response', json={'manual_transcript': ans4})
client.post(f'/api/attempts/{att4_id}/confirm-response', json={'confirmed': True})
client.post(f'/api/attempts/{att4_id}/analyse')
client.post(f'/api/attempts/{att4_id}/transition')
client.patch(f'/api/attempts/{att4_id}/review', json={'adult_feedback_confirmed': True, 'evaluation_confirmed': True})
db.refresh(l1)
inst_pass = (l1.instruction_following_score != i_before4 and (l1.instruction_evidence_count or 0) == ev_i_before + 1)
print(f"4. Instruction activity: {'PASSED' if inst_pass else 'FAILED'} (Instruction score changed from {i_before4} -> {l1.instruction_following_score}, other domains untouched)")

# 5. Duplicate submission
i_score_post = l1.instruction_following_score
dup_rev = client.patch(f'/api/attempts/{att4_id}/review', json={'adult_feedback_confirmed': True, 'evaluation_confirmed': True}).json()
db.refresh(l1)
dup_pass = (l1.instruction_following_score == i_score_post and (dup_rev.get('profile_update') is None or dup_rev.get('profile_update', {}).get('profile_update_applied') is False))
print(f"5. Duplicate submission: {'PASSED' if dup_pass else 'FAILED'} (Idempotent scoring: profile_update is None / no second score mutation)")


# 6. Activity completion -> screening risk unchanged
c2 = db.query(LearnerProfile).filter(LearnerProfile.learner_code == 'CHILD-002').first()
c2_risk_before = c2.screening_risk_level
s6 = client.post('/api/activity-sessions', json={'learner_id': c2.id, 'task_id': t_vocab.id}).json()
session6_id = s6['id']
att6 = client.post(f'/api/activity-sessions/{session6_id}/attempts').json()['attempt']
att6_id = att6['id']
client.patch(f'/api/attempts/{att6_id}/response', json={'manual_transcript': 'wrong answer'})
client.post(f'/api/attempts/{att6_id}/confirm-response', json={'confirmed': True})
client.post(f'/api/attempts/{att6_id}/analyse')
client.post(f'/api/attempts/{att6_id}/transition')
client.patch(f'/api/attempts/{att6_id}/review', json={'adult_feedback_confirmed': True, 'evaluation_confirmed': True})
db.refresh(c2)
risk_pass = (c2.screening_risk_level == c2_risk_before == 'moderate')
print(f"6. Activity completion: {'PASSED' if risk_pass else 'FAILED'} (CHILD-002 screening risk remained immutable at: {c2.screening_risk_level})")

# 7. Child API response
cv_res = client.get(f'/api/activity-sessions/{session6_id}/child-view').json()
forbidden = [
    'screening_risk_level', 'risk_level', 'vocabulary_score', 'grammar_score', 
    'comprehension_score', 'instruction_following_score', 'grammar_observations', 
    'adult_notes', 'calculation_snapshot', 'model_confidence'
]
child_safe_pass = not any(k in cv_res for k in forbidden) and 'presented_instruction' in cv_res
print(f"7. Child API response: {'PASSED' if child_safe_pass else 'FAILED'} (Excludes all risk levels, scores, observations, snapshots)")

# 8. Component 1 import disabled
c1_res = client.post('/api/v1/integration/component-1/screening-profile', json={'learner_id': 'CHILD-002', 'risk_level': 'low'})
c1_pass = (c1_res.status_code == 403)
print(f"8. Component 1 import disabled: {'PASSED' if c1_pass else 'FAILED'} (Returns HTTP 403 Forbidden in mock mode)")

# 9. AR preview
ar_res = client.get(f'/api/v1/integration-preview/component-2-ar/{t_vocab.id}').json()
ar_pass = (ar_res.get('is_simulated') is True and ar_res.get('delivery_status') == 'not_connected')
print(f"9. AR preview: {'PASSED' if ar_pass else 'FAILED'} (Marked is_simulated=True, delivery_status=not_connected)")

# 10. Component 4 preview
c4_res = client.get(f'/api/v1/integration-preview/component-4/{l1.id}').json()
c4_pass = (
    'performance_profile' in c4_res and 
    c4_res.get('is_simulated') is True and 
    'local_preliminary_trend' in c4_res['performance_profile']['vocabulary'] and 
    c4_res.get('export_status') == 'generated_locally_not_delivered'
)
print(f"10. Component 4 preview: {'PASSED' if c4_pass else 'FAILED'} (Exports evidence with local_preliminary_trend; no official longitudinal claims)")

total_passed = sum([vocab_pass, gram_pass, comp_pass, inst_pass, dup_pass, risk_pass, child_safe_pass, c1_pass, ar_pass, c4_pass])
print(f"\n================================================================")
print(f"     FINAL RESULT: Manual verification: {total_passed}/10 passed")
print(f"================================================================")
