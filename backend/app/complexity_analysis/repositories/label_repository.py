"""Repository for loading, mapping, and governing difficulty labels for Stage 22."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import glob


class LabelRepository:
    """Loads and indexes difficulty labels across source items and simplification pairs."""

    def __init__(
        self,
        authoring_batches_dir: Path = Path("data/dataset_expansion/stage20/authoring_batches"),
        simplification_corpus_path: Path = Path("data/simplification_corpus/releases/0.2.0/simplification_corpus.json"),
    ):
        self.authoring_batches_dir = authoring_batches_dir
        self.simplification_corpus_path = simplification_corpus_path
        self._source_labels: Dict[str, Dict[str, Any]] = {}
        self._simp_labels: Dict[str, Dict[str, Any]] = {}
        self._loaded = False

    def load_all_labels(self) -> None:
        """Loads and indexes all label metadata from disk."""
        # 1. Load source items & simplification pairs from authoring batches
        batch_files = glob.glob(str(self.authoring_batches_dir / "*.json"))
        for bf in batch_files:
            try:
                with open(bf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    batch_id = data.get("batch_id", "STAGE20-BATCH")

                    for item in data.get("source_items", []):
                        sid = item.get("source_item_id")
                        if sid:
                            diff = item.get("source_difficulty", "medium").lower()
                            self._source_labels[sid] = {
                                "assigned_difficulty": diff,
                                "annotator_tier": "reviewer_consensus",
                                "provenance_source": f"authoring_batch:{batch_id}",
                                "source_group_id": sid,
                            }

                    for pair in data.get("simplification_pairs", []):
                        pid = pair.get("pair_id")
                        if pid:
                            orig_diff = pair.get("source_difficulty") or pair.get("original_difficulty") or "medium"
                            simp_diff = pair.get("simplified_difficulty") or pair.get("target_difficulty")
                            self._simp_labels[pid] = {
                                "original_difficulty": str(orig_diff).lower(),
                                "simplified_difficulty": str(simp_diff).lower() if simp_diff else None,
                                "annotator_tier": "reviewer_consensus",
                                "provenance_source": f"authoring_batch:{batch_id}",
                                "source_group_id": pair.get("source_item_id") or pid,
                            }
            except Exception as e:
                pass

        # 2. Load release simplification corpus (1,110 pairs)
        if self.simplification_corpus_path.exists():
            try:
                with open(self.simplification_corpus_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    pairs = data if isinstance(data, list) else data.get("pairs", [])
                    for p in pairs:
                        pid = p.get("pair_id") or p.get("id")
                        if pid:
                            orig_diff = p.get("original_difficulty") or p.get("source_difficulty") or "medium"
                            simp_diff = p.get("simplified_difficulty")
                            if hasattr(orig_diff, "value"):
                                orig_diff = orig_diff.value
                            if hasattr(simp_diff, "value"):
                                simp_diff = simp_diff.value

                            # Index both raw PID and normalized if needed
                            self._simp_labels[pid] = {
                                "original_difficulty": str(orig_diff).lower(),
                                "simplified_difficulty": str(simp_diff).lower() if simp_diff else None,
                                "annotator_tier": "expert",
                                "provenance_source": "simplification_corpus_release_0.2.0",
                                "source_group_id": p.get("source_item_id") or p.get("source_record_id") or pid,
                            }
            except Exception as e:
                pass

        self._loaded = True

    def get_label_for_instance(
        self,
        text_instance_id: str,
        parent_record_id: str,
        parent_record_type: str,
        text_role: str,
    ) -> Dict[str, Any]:
        """Resolves the difficulty label and provenance for an individual text instance."""
        if not self._loaded:
            self.load_all_labels()

        # Check source items
        if parent_record_type == "source_item" and text_role == "source_text":
            if parent_record_id in self._source_labels:
                return self._source_labels[parent_record_id]

        # Check simplification pairs
        if parent_record_type == "simplification_pair":
            if parent_record_id in self._simp_labels:
                pair_info = self._simp_labels[parent_record_id]
                diff = pair_info["original_difficulty"] if text_role == "source_text" else pair_info["simplified_difficulty"]
                if diff:
                    return {
                        "assigned_difficulty": diff,
                        "annotator_tier": pair_info["annotator_tier"],
                        "provenance_source": pair_info["provenance_source"],
                        "source_group_id": pair_info["source_group_id"],
                    }
                else:
                    # Simplified text without independent expert label -> provisional or unannotated
                    return {
                        "assigned_difficulty": None,
                        "annotator_tier": "none",
                        "provenance_source": pair_info["provenance_source"],
                        "source_group_id": pair_info["source_group_id"],
                    }

        # Fallback / missing
        return {
            "assigned_difficulty": None,
            "annotator_tier": "none",
            "provenance_source": "unassigned",
            "source_group_id": parent_record_id,
        }
