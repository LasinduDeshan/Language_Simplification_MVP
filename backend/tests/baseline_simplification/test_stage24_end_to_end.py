"""
End-to-end integration tests for Stage 24 English Baseline Simplification suite.
"""
from app.baseline_simplification.runner import BaselineRunner
from app.baseline_simplification.evaluator import BaselineEvaluator
from app.baseline_simplification.schemas import BaselineMethodId, ProtectedElementSource

def test_stage24_e2e_pipeline():
    runner = BaselineRunner()
    evaluator = BaselineEvaluator()
    
    items = [
        {
            "source_item_id": "SRC-E2E-001",
            "source_group_id": "GRP-E2E-001",
            "source_text": "The small rabbit made a decision to jump because the dog was barking.",
            "target_content_age": 6,
            "reference_texts": [
                "The small rabbit decided to jump because the dog was barking.",
                "The little bunny decided to hop because the dog barked.",
                "The rabbit decided to jump away from the loud dog.",
            ],
        }
    ]
    gt_map = {
        "GRP-E2E-001": {
            "orig": items[0]["source_text"],
            "refs": items[0]["reference_texts"],
        }
    }

    for m in [BaselineMethodId.B0, BaselineMethodId.B1, BaselineMethodId.B2, BaselineMethodId.B3, BaselineMethodId.B4, BaselineMethodId.B5]:
        records = runner.run_on_items(
            m, items, "internal_e2e", "0.2.0", "test", f"E2E-{m.value}", ProtectedElementSource.AUTOMATED_EXTRACTOR_ONLY
        )
        assert len(records) == 1
        res = evaluator.evaluate_dataset_outputs(records, gt_map)
        assert res["total_records"] == 1
        assert "sari" in res["metrics"]
        assert "corpus_bleu" in res["metrics"]
