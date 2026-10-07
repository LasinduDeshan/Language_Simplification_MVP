"""
Unit tests for parent-to-text relational mappings
Validates complete, non-duplicated many-to-many mappings
"""
from app.nlp_preprocessing.schemas import SimplificationPairAdapter, SourceItemAdapter

def test_many_to_many_parent_text_mappings():
    src_record = {"source_item_id": "SRC-01", "original_text": "Look at the stars."}
    pair_record = {
        "pair_id": "SIMP-01",
        "source_item_id": "SRC-01",
        "original_text": "Look at the stars.",
        "simplified_text": "Look at the bright stars."
    }
    
    src_inst = SourceItemAdapter.extract_text_instances(src_record)
    pair_inst = SimplificationPairAdapter.extract_text_instances(pair_record)
    
    # Both SRC-01 and SIMP-01 reference identical source text "Look at the stars."
    all_instances = src_inst + pair_inst
    assert len(all_instances) == 3
    
    # Mapping registry simulation
    mapping_table = []
    for inst in all_instances:
        mapping_table.append({
            "parent_id": inst.parent_record_id,
            "text_instance_id": inst.text_instance_id,
            "text_role": inst.text_role
        })
    
    assert len(mapping_table) == 3
    assert mapping_table[0]["parent_id"] == "SRC-01"
    assert mapping_table[1]["parent_id"] == "SIMP-01"
    assert mapping_table[1]["text_role"] == "source_text"
    assert mapping_table[2]["text_role"] == "simplified_text"
