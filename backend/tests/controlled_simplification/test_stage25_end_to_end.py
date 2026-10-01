"""
End-to-end integration tests for Stage 25 Controlled Simplification Engine.
"""

import pytest
from app.controlled_simplification.engine import ControlledSimplificationEngine
from app.controlled_simplification.schemas import (
    SimplificationRequest,
    SupportLevel,
    LearnerProfileContext,
    TerminalStatus
)
from app.controlled_simplification.evaluation_protocol import EvaluationOrchestrator, bootstrap_ci


def test_full_controlled_engine_end_to_end():
    engine = ControlledSimplificationEngine()
    test_items = [
        "Before placing the red ball inside the box, carefully select the smaller blue object.",
        "Make a selection of the brightest star and place it near the moon.",
        "The small green frog was caught by the boy in the garden.",
        "Listen quietly to the story before opening the storybook."
    ]

    for item in test_items:
        for tier in [SupportLevel.MILD, SupportLevel.MODERATE, SupportLevel.STRONG]:
            req = SimplificationRequest(
                request_id=f"E2E-{tier.value}",
                text=item,
                target_support_level=tier
            )
            res = engine.simplify(req)
            assert res.applied_support_level == tier
            assert res.status in {TerminalStatus.PASSED, TerminalStatus.PASSED_WITH_ROLLBACK, TerminalStatus.MANUAL_REVIEW_REQUIRED}
            assert len(res.simplified_text) > 0
            assert res.governance_metadata.approved_for_child_delivery is False


def test_evaluation_orchestrator_and_bootstrap_significance():
    sources = [
        "Before placing the red ball inside the box, carefully select the smaller blue object.",
        "The book was read by the teacher."
    ]
    predictions = [
        "1. Pick the smaller blue object.\n2. Put the red ball in the box.",
        "The teacher read the book."
    ]
    references = [
        "1. Pick the small blue thing.\n2. Put the red ball in the box.",
        "The teacher read the book."
    ]

    tier_res = EvaluationOrchestrator.evaluate_tier_matched(sources, predictions, references)
    assert tier_res["sari"] > 0.0
    assert tier_res["corpus_bleu"] > 0.0

    # Bootstrap test
    scores_a = [35.0, 40.0, 45.0, 50.0]
    scores_b = [30.0, 32.0, 35.0, 40.0]
    mean_diff, ci_low, ci_high, cohen_d = bootstrap_ci(scores_a, scores_b)
    assert mean_diff > 0.0
    assert ci_low <= mean_diff <= ci_high
    assert cohen_d > 0.0
