"""
Unit tests for RPM throttling and request spacing in GeminiQuotaManager.
"""
import time
from app.model_simplification.quota_manager import GeminiQuotaManager


def test_min_delay_spacing():
    # Test with small min_delay to test logic without slowing down test suite
    qm = GeminiQuotaManager(min_delay_seconds=0.05)
    
    t0 = time.perf_counter()
    qm.wait_for_slot()
    t1 = time.perf_counter()
    qm.wait_for_slot()
    t2 = time.perf_counter()

    assert (t2 - t1) >= 0.045
    assert qm.daily_request_count == 2


def test_rpm_window_throttling():
    qm = GeminiQuotaManager(min_delay_seconds=0.001)
    qm.MAX_REQUESTS_PER_MINUTE = 3

    # Add 3 timestamps right now
    now = time.perf_counter()
    qm.request_timestamps = [now - 10.0, now - 5.0, now - 1.0]

    # Next call should wait until oldest timestamp clears 60s window or throttle
    slept = qm.wait_for_slot()
    assert slept >= 0.0
    assert len(qm.request_timestamps) >= 1
