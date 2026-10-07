import os
import json
from typing import List, Optional, Union
from app.datasets.common.draft_models import DraftSimplificationPair
from app.datasets.simplification_corpus.schemas import SimplificationPairV1
from app.datasets.common.paths import (
    SIMPLIFICATION_DRAFT_DIR, SIMPLIFICATION_APPROVED_DIR, SIMPLIFICATION_RELEASE_DIR
)

class SimplificationCorpusRepository:
    """
    Repository interface for querying and saving original-simplified sentence pairs.
    Supports DATASET_SCHEMA_MODE='v1' (default) and 'stage13_compat'.
    """
    def __init__(self, draft_dir: Optional[str] = None, approved_dir: Optional[str] = None, release_dir: Optional[str] = None):
        self.draft_dir = draft_dir or SIMPLIFICATION_DRAFT_DIR
        self.approved_dir = approved_dir or SIMPLIFICATION_APPROVED_DIR
        self.release_dir = release_dir or os.path.join(SIMPLIFICATION_RELEASE_DIR, "0.1.0")
        self.schema_mode = os.environ.get("DATASET_SCHEMA_MODE", "v1")
        os.makedirs(self.draft_dir, exist_ok=True)
        os.makedirs(self.approved_dir, exist_ok=True)

    def get_v1_release_pairs(self) -> List[SimplificationPairV1]:
        pairs_file = os.path.join(self.release_dir, "simplification_corpus.json")
        if not os.path.exists(pairs_file):
            return []
        with open(pairs_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [SimplificationPairV1(**item) for item in raw]

    def get_draft_pairs(self) -> List[Union[SimplificationPairV1, DraftSimplificationPair]]:
        if self.schema_mode == "v1":
            v1_pairs = self.get_v1_release_pairs()
            if v1_pairs:
                return v1_pairs

        pairs_file = os.path.join(self.draft_dir, "draft_pairs.json")
        if not os.path.exists(pairs_file):
            return []
        with open(pairs_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [DraftSimplificationPair(**item) for item in raw]

    def get_approved_pairs(self) -> List[Union[SimplificationPairV1, DraftSimplificationPair]]:
        pairs_file = os.path.join(self.approved_dir, "approved_pairs.json")
        if not os.path.exists(pairs_file):
            return []
        with open(pairs_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if self.schema_mode == "v1":
            return [SimplificationPairV1(**item) for item in raw]
        return [DraftSimplificationPair(**item) for item in raw]

    def save_draft_pair(self, pair: Union[SimplificationPairV1, DraftSimplificationPair]) -> str:
        pairs = self.get_draft_pairs()
        pairs.append(pair)
        pairs_file = os.path.join(self.draft_dir, "draft_pairs.json")
        with open(pairs_file, "w", encoding="utf-8") as f:
            json.dump([p.model_dump(mode="json") for p in pairs], f, indent=2)
        return pair.pair_id
