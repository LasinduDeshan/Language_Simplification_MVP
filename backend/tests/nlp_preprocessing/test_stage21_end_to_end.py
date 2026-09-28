"""
End-to-end tests for Stage 21 English NLP Preprocessing Pipeline
Validates full lifecycle from raw record adaptation -> pipeline -> feature extraction -> record integrity.
"""
from app.nlp_preprocessing.pipeline import NLPPreprocessingPipeline
from app.nlp_preprocessing.schemas import (
    SourceItemAdapter,
    SimplificationPairAdapter,
    AdaptationActivityAdapter,
    LexiconEntryAdapter
)

def test_end_to_end_pipeline_lifecycle():
    pipeline = NLPPreprocessingPipeline()
    
    # 1. Source item
    source_item = {
        "item_id": "SRC-E2E-01",
        "text": "The little red bird sang a sweet song in the morning.",
        "language": "en",
        "dataset_split": "development_candidate_train",
        "source_group_id": "SG-E2E-01"
    }
    src_instances = SourceItemAdapter.extract_text_instances(source_item)
    assert len(src_instances) == 1
    src_res = pipeline.process_text_instance(src_instances[0])
    assert src_res.processing_status == "success"
    assert src_res.features.surface.word_count == 11
    assert src_res.features.surface.sentence_count == 1
    
    # 2. Simplification pair
    pair_record = {
        "pair_id": "PAIR-E2E-01",
        "source_text": "The massive dinosaur traversed the dense forest.",
        "simplified_text": "The big dinosaur walked through the forest.",
        "target_level": "easy",
        "dataset_split": "development_candidate_validation",
        "source_group_id": "SG-E2E-02"
    }
    pair_instances = SimplificationPairAdapter.extract_text_instances(pair_record)
    assert len(pair_instances) == 2
    pair_res = [pipeline.process_text_instance(inst) for inst in pair_instances]
    assert all(r.processing_status == "success" for r in pair_res)
    assert pair_res[0].text_role == "source_text"
    assert pair_res[1].text_role == "simplified_text"
    
    # 3. Adaptation activity
    act_record = {
        "activity_id": "ACT-E2E-01",
        "instruction": "Click the green circle.",
        "correct_answer": "Green circle",
        "dataset_split": "development_candidate_train",
        "source_group_id": "SG-E2E-03"
    }
    act_instances = AdaptationActivityAdapter.extract_text_instances(act_record)
    act_res = [pipeline.process_text_instance(inst) for inst in act_instances]
    assert all(r.processing_status == "success" for r in act_res)
    assert act_res[0].text_role == "activity_instruction"
