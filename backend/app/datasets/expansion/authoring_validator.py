"""
Stage 20 Authoring Validator Module
Validates authored batches against Stage 14 schemas, provenance rules, and governance invariants.
"""
from typing import Dict, Any, List, Tuple
from app.datasets.expansion.schemas import (
    OriginalEducationalItem, SimplificationPairRecord,
    LexiconEntryRecord, AuthoringBatchPayload, AuthoringMethodEnum
)

class AuthoringValidator:
    def __init__(self):
        self.validation_errors: List[Dict[str, Any]] = []

    def validate_batch(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
        self.validation_errors = []
        
        valid_items = []
        valid_pairs = []
        valid_activities = []
        valid_lexicons = []
        
        failed_records = []
        review_records = []

        # 1. Validate Source Items
        raw_items = batch_data.get("source_items", [])
        for item_dict in raw_items:
            try:
                item = OriginalEducationalItem(**item_dict)
                # Invariant checks
                if item.approved_for_child_delivery or item.research_eligible:
                    review_records.append({
                        "id": item.source_item_id,
                        "type": "source_item",
                        "reason": "Draft invariant violation: research_eligible or approved_for_child_delivery is True"
                    })
                else:
                    valid_items.append(item.model_dump())
            except Exception as e:
                failed_records.append({
                    "id": item_dict.get("source_item_id", "UNKNOWN"),
                    "type": "source_item",
                    "error": str(e)
                })

        # 2. Validate Simplification Pairs
        raw_pairs = batch_data.get("simplification_pairs", [])
        for pair_dict in raw_pairs:
            try:
                pair = SimplificationPairRecord(**pair_dict)
                # Provenance rule: AI assistance cannot be labeled purely human_authored
                if (pair.provenance.authoring_method == AuthoringMethodEnum.HUMAN_AUTHORED and
                    pair.provenance.generation_model is not None):
                    review_records.append({
                        "id": pair.pair_id,
                        "type": "simplification_pair",
                        "reason": "AI generation model specified but authoring_method is human_authored"
                    })
                else:
                    valid_pairs.append(pair.model_dump())
            except Exception as e:
                failed_records.append({
                    "id": pair_dict.get("pair_id", "UNKNOWN"),
                    "type": "simplification_pair",
                    "error": str(e)
                })

        # 3. Validate Lexicon Entries & Circularity
        raw_lex = batch_data.get("lexicon_entries", [])
        lex_map = {}
        for lex_dict in raw_lex:
            try:
                lex = LexiconEntryRecord(**lex_dict)
                headword_norm = lex.normalized_form.lower().strip()
                replacement_norm = (lex.simple_replacement or "").lower().strip()
                
                # Check direct circularity A -> A
                if replacement_norm and headword_norm == replacement_norm:
                    review_records.append({
                        "id": lex.lexicon_id,
                        "type": "lexicon_entry",
                        "reason": f"Self-referential replacement: {headword_norm} -> {replacement_norm}"
                    })
                else:
                    lex_map[headword_norm] = replacement_norm
                    valid_lexicons.append(lex.model_dump())
            except Exception as e:
                failed_records.append({
                    "id": lex_dict.get("lexicon_id", "UNKNOWN"),
                    "type": "lexicon_entry",
                    "error": str(e)
                })

        # Circular chain check: A -> B -> A
        for hw, rep in lex_map.items():
            if rep in lex_map and lex_map[rep] == hw:
                review_records.append({
                    "id": f"CIRCULAR-{hw}-{rep}",
                    "type": "lexicon_entry",
                    "reason": f"Circular replacement chain detected: {hw} -> {rep} -> {hw}"
                })

        # 4. Activities pass-through validation
        raw_activities = batch_data.get("adaptation_activities", [])
        for act in raw_activities:
            if "activity_id" in act and "original_instruction" in act:
                valid_activities.append(act)
            else:
                failed_records.append({
                    "id": act.get("activity_id", "UNKNOWN"),
                    "type": "adaptation_activity",
                    "error": "Missing required fields: activity_id or original_instruction"
                })

        total_submitted = len(raw_items) + len(raw_pairs) + len(raw_activities) + len(raw_lex)
        total_valid = len(valid_items) + len(valid_pairs) + len(valid_activities) + len(valid_lexicons)

        return {
            "batch_id": batch_data.get("batch_id", "UNKNOWN"),
            "total_submitted": total_submitted,
            "total_valid": total_valid,
            "failed_count": len(failed_records),
            "review_count": len(review_records),
            "failed_records": failed_records,
            "review_records": review_records,
            "is_schema_valid": len(failed_records) == 0,
            "valid_data": {
                "source_items": valid_items,
                "simplification_pairs": valid_pairs,
                "adaptation_activities": valid_activities,
                "lexicon_entries": valid_lexicons
            }
        }
