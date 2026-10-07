"""
Unit tests for Mode B Declared Final Verification Run
Validates that locked test records are processed only when allow_locked_test is explicitly enabled.
"""
from app.nlp_preprocessing.pipeline import NLPPreprocessingPipeline
from app.nlp_preprocessing.config import PreprocessingConfig
from app.nlp_preprocessing.schemas import TextInstance

def test_final_verification_mode_b_processing():
    # Mode B: allow_locked_test = True
    config = PreprocessingConfig(allow_locked_test=True)
    pipeline = NLPPreprocessingPipeline(config=config)
    
    inst = TextInstance(
        text_instance_id="LOCKED-002",
        parent_record_id="PARENT-LOCKED-02",
        parent_record_type="source_item",
        text_role="source_text",
        text="The small dog happily chased the tennis ball.",
        language="en",
        dataset_split="development_candidate_test",
        source_group_id="SG-LOCKED-02"
    )
    
    rec = pipeline.process_text_instance(inst)
    
    assert rec.processing_status == "success"
    assert rec.normalized_text == "The small dog happily chased the tennis ball."
    assert len(rec.sentences) == 1
    assert rec.text_hash != "LOCKED_TEST_HASH"
