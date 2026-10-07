"""
Unit tests for Pipeline Determinism
Validates that repeated pipeline runs produce byte-for-byte identical output structures and hashes.
"""
from app.nlp_preprocessing.pipeline import NLPPreprocessingPipeline
from app.nlp_preprocessing.schemas import TextInstance

def test_pipeline_determinism_identical_runs():
    pipeline = NLPPreprocessingPipeline()
    
    inst = TextInstance(
        text_instance_id="DET-TEST-01",
        parent_record_id="PARENT-01",
        parent_record_type="source_item",
        text_role="source_text",
        text="The quiet brown cat slept under the large green tree.",
        language="en",
        dataset_split="development_candidate_train",
        source_group_id="SG-01"
    )
    
    rec1 = pipeline.process_text_instance(inst)
    rec2 = pipeline.process_text_instance(inst)
    
    assert rec1.text_hash == rec2.text_hash
    assert rec1.feature_hash == rec2.feature_hash
    assert rec1.record_hash == rec2.record_hash
    assert rec1.normalized_text == rec2.normalized_text
    assert rec1.features.model_dump() == rec2.features.model_dump()
