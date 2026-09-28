"""
Stage 21 Component & Adapter Registry
"""
from typing import Dict, Any, Type
from app.nlp_preprocessing.schemas import (
    SourceItemAdapter,
    SimplificationPairAdapter,
    AdaptationActivityAdapter,
    LexiconEntryAdapter
)

ADAPTER_REGISTRY: Dict[str, Any] = {
    "source_item": SourceItemAdapter,
    "simplification_pair": SimplificationPairAdapter,
    "adaptation_activity": AdaptationActivityAdapter,
    "lexicon_entry": LexiconEntryAdapter
}

def get_adapter(parent_type: str):
    if parent_type not in ADAPTER_REGISTRY:
        raise ValueError(f"Unknown parent record type: {parent_type}. Available: {list(ADAPTER_REGISTRY.keys())}")
    return ADAPTER_REGISTRY[parent_type]
