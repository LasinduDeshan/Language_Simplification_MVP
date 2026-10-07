"""
Unit tests for Batch Processing and Record Isolation
Ensures batch processing handles mixed splits and isolates individual record exceptions.
"""
from app.nlp_preprocessing.pipeline import NLPPreprocessingPipeline
from app.nlp_preprocessing.schemas import TextInstance

def test_process_batch_mixed_records():
    pipeline = NLPPreprocessingPipeline()
    
    instances = [
        TextInstance(
            text_instance_id="BATCH-01",
            parent_record_id="P-01",
            parent_record_type="source_item",
            text_role="source_text",
            text="The sun rises in the east.",
            language="en",
            dataset_split="development_candidate_train",
            source_group_id="SG-01"
        ),
        TextInstance(
            text_instance_id="BATCH-02",
            parent_record_id="P-02",
            parent_record_type="source_item",
            text_role="source_text",
            text="Birds fly over the trees.",
            language="en",
            dataset_split="development_candidate_validation",
            source_group_id="SG-02"
        ),
        TextInstance(
            text_instance_id="BATCH-03",
            parent_record_id="P-03",
            parent_record_type="source_item",
            text_role="source_text",
            text="Locked test item text.",
            language="en",
            dataset_split="development_candidate_test",
            source_group_id="SG-03"
        )
    ]
    
    results = pipeline.process_batch(instances)
    assert len(results) == 3
    assert results[0].processing_status == "success"
    assert results[1].processing_status == "success"
    assert results[2].processing_status == "skipped_locked_test"
