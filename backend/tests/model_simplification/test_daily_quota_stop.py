"""
Unit tests for daily quota limit and safety reserve enforcement.
"""
from app.model_simplification.quota_manager import GeminiQuotaManager


def test_daily_quota_limit_enforced():
    qm = GeminiQuotaManager(max_daily_requests=5)
    qm.daily_request_count = 4

    ok, msg = qm.can_proceed()
    assert ok is True

    qm.daily_request_count = 5
    ok, msg = qm.can_proceed()
    assert ok is False
    assert "Daily quota limit reached" in msg
    assert "Safety reserve preserved" in msg


def test_error_classification_distinguishes_transient_vs_daily():
    # Transient rate limit (RPM)
    transient = GeminiQuotaManager.classify_error(429, "Too Many Requests")
    assert transient == "RATE_LIMIT_FAILED"

    # Daily quota limit
    daily = GeminiQuotaManager.classify_error(429, "Quota exceeded: PerDay free_tier_usage_limit reached")
    assert daily == "DAILY_QUOTA_FAILED"

    # Resource exhausted 403
    resource_exhausted = GeminiQuotaManager.classify_error(403, "RESOURCE_EXHAUSTED: daily quota reached")
    assert resource_exhausted == "DAILY_QUOTA_FAILED"
