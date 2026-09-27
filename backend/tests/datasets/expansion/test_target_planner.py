"""
Unit tests for Stage 20 Target Planner.
"""
import pytest
from app.datasets.expansion.target_planner import TargetPlanner

def test_target_planner_totals():
    planner = TargetPlanner()
    totals = planner.get_totals()
    
    assert totals["total_source_items"] == 300
    assert totals["total_simplification_pairs"] == 900
    assert totals["total_adaptation_activities"] == 120
    assert totals["total_lexicon_entries"] == 350
    
    # Check domain totals sum to 300
    domain_sum = (
        totals["total_vocab_items"] +
        totals["total_grammar_items"] +
        totals["total_comp_items"] +
        totals["total_instruction_items"]
    )
    assert domain_sum == 300
    
    # Check 5 batches configured
    assert len(planner.batch_plan) == 5
    assert planner.batch_plan[0]["source_items"] == 80
    assert planner.batch_plan[1]["source_items"] == 50
    assert planner.batch_plan[2]["source_items"] == 50
    assert planner.batch_plan[3]["source_items"] == 50
    assert planner.batch_plan[4]["source_items"] == 70
