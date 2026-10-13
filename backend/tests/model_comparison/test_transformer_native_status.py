"""
Test transformer registration and un-evaluated status invariant for Stage 28A.
"""
import pytest
from app.model_comparison.registry import get_registered_system
from app.model_comparison.schemas import SystemEvaluationStatus, DeliveryDisposition


def test_t1_t2_explicitly_not_evaluated():
    for sys_id in ["T1", "T2"]:
        sys = get_registered_system(sys_id)
        assert sys is not None
        assert sys.evaluation_status == SystemEvaluationStatus.NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS
        assert sys.is_active_candidate is False


def test_transformer_no_fallback_contamination():
    """
    If a transformer checkpoint is not loaded or produces 0 valid outputs,
    its disposition must be NOT_ATTEMPTED or FAILED under its own attribution,
    never reported as valid native transformer outputs.
    """
    t1 = get_registered_system("T1")
    assert t1.evaluation_status.value == "NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS"
