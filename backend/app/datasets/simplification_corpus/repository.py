import os
import json
from typing import List, Optional, Dict, Any
from app.datasets.common.draft_models import DraftSimplificationPair
from app.datasets.common.paths import SIMPLIFICATION_DRAFT_DIR, SIMPLIFICATION_APPROVED_DIR

class SimplificationCorpusRepository:
    """
    Repository interface for querying and saving original-simplified sentence pairs.
    Rules:
    - Never accept or promote unreviewed learner interaction transcripts automatically.
    - Requires explicit human/expert approval before promoting draft pairs to approved status.
    """
    def __init__(self, draft_dir: Optional[str] = None, approved_dir: Optional[str] = None):
        self.draft_dir = draft_dir or SIMPLIFICATION_DRAFT_DIR
        self.approved_dir = approved_dir or SIMPLIFICATION_APPROVED_DIR
        os.makedirs(self.draft_dir, exist_ok=True)
        os.makedirs(self.approved_dir, exist_ok=True)

    def get_draft_pairs(self) -> List[DraftSimplificationPair]:
        pairs_file = os.path.join(self.draft_dir, "draft_pairs.json")
        if not os.path.exists(pairs_file):
            return []
        with open(pairs_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [DraftSimplificationPair(**item) for item in raw]

    def get_approved_pairs(self) -> List[DraftSimplificationPair]:
        pairs_file = os.path.join(self.approved_dir, "approved_pairs.json")
        if not os.path.exists(pairs_file):
            return []
        with open(pairs_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [DraftSimplificationPair(**item) for item in raw]

    def save_draft_pair(self, pair: DraftSimplificationPair) -> str:
        """
        Saves a candidate simplification pair into draft storage.
        """
        pairs = self.get_draft_pairs()
        pairs.append(pair)
        pairs_file = os.path.join(self.draft_dir, "draft_pairs.json")
        with open(pairs_file, "w", encoding="utf-8") as f:
            json.dump([p.model_dump(mode="json") for p in pairs], f, indent=2)
        return pair.pair_id
