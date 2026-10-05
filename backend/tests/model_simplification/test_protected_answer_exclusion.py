"""
Tests for Server-Side HMAC Answer Non-Disclosure Guard.
Tests low-entropy token protection ('cat', 'red', '3') and leakage detection.
"""

from app.model_simplification.hmac_answer_guard import HmacAnswerGuard


def test_hmac_answer_guard_leakage_detection():
    guard = HmacAnswerGuard(key_version="v1.0.0", secret_key=b"test_secret_key_123")
    
    # 1. Compute HMAC (version recorded, not raw secret)
    hmac_val = guard.compute_answer_hmac("cat")
    assert hmac_val.startswith("hmac:v1.0.0:")
    
    # 2. Check direct leakage
    candidate_leaked = "The answer is cat. Choose the cat."
    leaked, leaked_items = guard.check_leakage(candidate_leaked, ["cat", "dog"])
    assert leaked is True
    assert "cat" in leaked_items
    
    # 3. Check non-leaked text
    candidate_safe = "Point to the domestic animal shown in the picture."
    leaked_safe, items = guard.check_leakage(candidate_safe, ["cat", "dog"])
    assert leaked_safe is False
    assert len(items) == 0


def test_hmac_answer_guard_low_entropy_tokens():
    guard = HmacAnswerGuard()
    
    # Low-entropy numerical/color answers
    answers = ["3", "red", "circle"]
    candidate = "Select the 3 red objects."
    
    leaked, leaked_items = guard.check_leakage(candidate, answers)
    assert leaked is True
    assert "3" in leaked_items
    assert "red" in leaked_items
