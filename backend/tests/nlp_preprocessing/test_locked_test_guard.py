"""
Unit tests for Mode A Locked Test Split Isolation Guard
Ensures records with split 'development_candidate_test' are skipped without parsing in standard release runs.
"""
from app.nlp_preprocessing.pipeline import NLPPreprocessingPipeline
from app.nlp_preprocessing.config import PreprocessingConfig
from app.nlp_preprocessing.schemas import TextInstance

def test_locked_test_guard_in_mode_a():
    # Mode A: allow_locked_test = False
    config = PreprocessingConfig(allow_locked_test=False)
    pipeline = NLPPreprocessingPipeline(config=config)
    
    inst = TextInstance(
        text_instance_id="LOCKED-001",
        parent_record_id="PARENT-LOCKED",
        parent_record_type="source_item",
        text_role="source_text",
        text="This is an isolated test sentence that must never leak.",
        language="en",
        dataset_split="development_candidate_test",
        source_group_id="SG-LOCKED"
    )
    
    rec = pipeline.process_text_instance(inst)
    
    assert rec.processing_status == "skipped_locked_test"
    assert rec.normalized_text == "[LOCKED_TEST_PROTECTED]"
    assert rec.sentences == []
    assert rec.text_hash == "LOCKED_TEST_HASH"
