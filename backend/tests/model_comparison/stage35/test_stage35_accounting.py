"""
Verification of 9-Level Accounting for Stage 35.
Asserts Unaccounted = 0 across all levels.
"""

import json
from pathlib import Path

def test_nine_level_zero_loss_accounting():
    summary_path = Path("data/model_comparison/stage35/evaluations/stage35_accounting_summary.json")
    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data["level_1_inputs"]["unaccounted"] == 0
    assert data["level_2_executions"]["unaccounted"] == 0
    assert data["level_3_attempts"]["unaccounted"] == 0
    assert data["level_4_responses_vs_failures"]["unaccounted"] == 0
    assert data["level_5a_selected_responses"]["unaccounted"] == 0
    assert data["level_5b_terminal_failures"]["unaccounted"] == 0
    assert data["level_6_metric_cells"]["unaccounted"] == 0
    assert data["level_9_condition_decisions"]["unaccounted"] == 0
    assert data["level_10_human_accounting"] == "NOT_APPLICABLE_AUTOMATED_TECHNICAL_ONLY"
