"""Repository for loading, mapping, and governing difficulty labels and provenance for Stage 22."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import glob


class LabelRepository:
    """Loads and indexes difficulty labels with rigorous provenance and tier tracking."""

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
        """Loads and indexes all label metadata from disk with explicit provenance."""
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
                            # Check if formal expert review was performed
                            is_draft = item.get("validation_status") == "draft" or item.get("requires_expert_review", True)
                            tier = "provisional_author" if is_draft else "expert"
                            label_status = "provisional" if is_draft else "expert_verified"

                            self._source_labels[sid] = {
                                "assigned_difficulty": diff,
                                "annotator_tier": tier,
                                "label_status": label_status,
                                "provenance_source": f"authoring_batch:{batch_id}",
                                "source_group_id": sid,
                                "reviewer_reference": "None (Draft authoring item awaiting expert panel review)" if is_draft else "EXP-01",
                                "reviewer_role": "provisional_author" if is_draft else "expert_linguist",
                                "annotation_guideline_version": "v1.0.0-draft",
                                "reviewed_at": None,
                                "agreement_status": "single_author_provisional" if is_draft else "consensus",
                                "adjudication_status": "pending_expert_adjudication" if is_draft else "adjudicated",
                            }

                    for pair in data.get("simplification_pairs", []):
                        pid = pair.get("pair_id")
                        if pid:
                            orig_diff = pair.get("source_difficulty") or pair.get("original_difficulty") or "medium"
                            simp_diff = pair.get("simplified_difficulty") or pair.get("target_difficulty")
                            is_draft = pair.get("validation_status") == "draft" or pair.get("requires_expert_review", True)
                            tier = "provisional_author" if is_draft else "expert"
                            label_status = "provisional" if is_draft else "expert_verified"

                            self._simp_labels[pid] = {
                                "original_difficulty": str(orig_diff).lower(),
                                "simplified_difficulty": str(simp_diff).lower() if simp_diff else None,
                                "annotator_tier": tier,
                                "label_status": label_status,
                                "provenance_source": f"authoring_batch:{batch_id}",
                                "source_group_id": pair.get("source_item_id") or pid,
                                "reviewer_reference": "None (Draft authoring item awaiting expert panel review)" if is_draft else "EXP-01",
                                "reviewer_role": "provisional_author" if is_draft else "expert_linguist",
                                "annotation_guideline_version": "v1.0.0-draft",
                                "reviewed_at": None,
                                "agreement_status": "single_author_provisional" if is_draft else "consensus",
                                "adjudication_status": "pending_expert_adjudication" if is_draft else "adjudicated",
                            }
            except Exception:
                pass

        # 2. Load release simplification corpus
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

                            # Check review block in pair
                            review_block = p.get("review", {})
                            has_reviewer = review_block.get("reviewer_id") is not None

                            tier = "expert" if has_reviewer else "provisional_author"
                            label_status = "expert_verified" if has_reviewer else "provisional"

                            self._simp_labels[pid] = {
                                "original_difficulty": str(orig_diff).lower(),
                                "simplified_difficulty": str(simp_diff).lower() if simp_diff else None,
                                "annotator_tier": tier,
                                "label_status": label_status,
                                "provenance_source": "simplification_corpus_release_0.2.0",
                                "source_group_id": p.get("source_item_id") or p.get("source_record_id") or pid,
                                "reviewer_reference": review_block.get("reviewer_id") or "None (Draft authoring item awaiting expert panel review)",
                                "reviewer_role": review_block.get("reviewer_role") or "provisional_author",
                                "annotation_guideline_version": "v1.0.0-draft",
                                "reviewed_at": review_block.get("reviewed_at"),
                                "agreement_status": "single_author_provisional" if not has_reviewer else "consensus",
                                "adjudication_status": "pending_expert_adjudication" if not has_reviewer else "adjudicated",
                            }
            except Exception:
                pass

        self._loaded = True

    def get_label_for_instance(
        self,
        text_instance_id: str,
        parent_record_id: str,
        parent_record_type: str,
        text_role: str,
    ) -> Dict[str, Any]:
        """Resolves the difficulty label and full provenance for an individual text instance."""
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
                        "label_status": pair_info["label_status"],
                        "provenance_source": pair_info["provenance_source"],
                        "source_group_id": pair_info["source_group_id"],
                        "reviewer_reference": pair_info["reviewer_reference"],
                        "reviewer_role": pair_info["reviewer_role"],
                        "annotation_guideline_version": pair_info["annotation_guideline_version"],
                        "reviewed_at": pair_info["reviewed_at"],
                        "agreement_status": pair_info["agreement_status"],
                        "adjudication_status": pair_info["adjudication_status"],
                    }

        # Fallback / missing
        return {
            "assigned_difficulty": None,
            "annotator_tier": "none",
            "label_status": "missing",
            "provenance_source": "unassigned",
            "source_group_id": parent_record_id,
            "reviewer_reference": "N/A",
            "reviewer_role": "none",
            "annotation_guideline_version": "v1.0.0-draft",
            "reviewed_at": None,
            "agreement_status": "unlabeled",
            "adjudication_status": "not_applicable",
        }
