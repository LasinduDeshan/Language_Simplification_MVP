"""
Unit tests for deterministic baseline reproducibility across repeated runs.
"""
from app.baseline_simplification.runner import BaselineRunner
from app.baseline_simplification.schemas import BaselineMethodId, ProtectedElementSource

def test_deterministic_reproducibility_across_runs():
    runner = BaselineRunner()
    sample_items = [
        {"source_item_id": "SRC-001", "source_text": "The habitat was protected by Sam and the bears were happy.", "target_content_age": 6},
        {"source_item_id": "SRC-002", "source_text": "The miniature bird made a decision to fly away because it was scared.", "target_content_age": 6},
    ]

    for m in [BaselineMethodId.B0, BaselineMethodId.B1, BaselineMethodId.B2, BaselineMethodId.B3, BaselineMethodId.B4, BaselineMethodId.B5]:
        run1 = runner.run_on_items(m, sample_items, "internal", "0.2.0", "val", "RUN1", ProtectedElementSource.AUTOMATED_EXTRACTOR_ONLY)
        run2 = runner.run_on_items(m, sample_items, "internal", "0.2.0", "val", "RUN2", ProtectedElementSource.AUTOMATED_EXTRACTOR_ONLY)
        
        for r1, r2 in zip(run1, run2):
            assert r1.output_text == r2.output_text, f"Non-deterministic output for method {m}: '{r1.output_text}' != '{r2.output_text}'"
            assert r1.output_hash == r2.output_hash
            assert r1.quality_disposition == r2.quality_disposition
