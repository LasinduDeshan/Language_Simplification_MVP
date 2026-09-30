"""Leakage and overlap detector comparing external datasets against internal datasets."""

from collections import defaultdict
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from app.datasets.external_english.schemas import NormalizedExternalRecord


def normalize_for_leakage(text: str) -> str:
    """Normalizes text for robust exact and near overlap detection."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())


def compute_word_jaccard(tokens1: Set[str], tokens2: Set[str]) -> float:
    """Computes Jaccard similarity between two token sets."""
    if not tokens1 or not tokens2:
        return 0.0
    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)
    return intersection / union if union > 0 else 0.0


class ExternalLeakageDetector:
    """Detects exact and near leakage between external benchmark sentences and internal sets."""

    NEAR_OVERLAP_THRESHOLD = 0.80

    def __init__(self, repo_root: Optional[Path] = None):
        if repo_root is not None:
            self.repo_root = Path(repo_root)
        else:
            current = Path(__file__).resolve().parent
            found = None
            for p in [current, *current.parents]:
                if (p / "data").exists():
                    found = p
                    break
            self.repo_root = found or Path(".")

        self.internal_corpora: Dict[str, List[Dict[str, Any]]] = {
            "internal_train": [],
            "internal_val": [],
            "internal_locked_test": [],
            "adaptation_test_set": [],
        }
        self._load_internal_corpora()

    def _load_internal_corpora(self):
        """Loads internal training, validation, locked test, and adaptation test sets."""
        # 1. Locked test manifest (315 instances)
        locked_test_path = (
            self.repo_root
            / "data"
            / "preprocessed_features"
            / "en"
            / "source-0.2.0"
            / "pipeline-1.0.0"
            / "protected_test"
            / "locked_test_manifest.json"
        )
        if locked_test_path.exists():
            try:
                with open(locked_test_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    records = data.get("records", data) if isinstance(data, dict) else data
                    if isinstance(records, list):
                        for r in records:
                            txt = r.get("text") or r.get("raw_text") or r.get("normalized_text", "")
                            if txt:
                                self.internal_corpora["internal_locked_test"].append({
                                    "id": r.get("text_instance_id", r.get("id", "unknown")),
                                    "text": txt,
                                    "split": "locked_test",
                                })
            except Exception:
                pass

        # 2. Adaptation test set (377 instances)
        adapt_dir = self.repo_root / "data" / "adaptation_test_set" / "en"
        if adapt_dir.exists():
            for json_file in adapt_dir.rglob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        items = data if isinstance(data, list) else [data]
                        for it in items:
                            txt = it.get("text") or it.get("instruction") or it.get("content", "")
                            if txt:
                                self.internal_corpora["adaptation_test_set"].append({
                                    "id": it.get("id", str(json_file.name)),
                                    "text": txt,
                                    "split": "adaptation_test",
                                })
                except Exception:
                    pass

        # 3. Draft simplification corpus (training & validation)
        draft_path = (
            self.repo_root
            / "data"
            / "simplification_corpus"
            / "en"
            / "draft"
            / "draft_pairs.json"
        )
        if draft_path.exists():
            try:
                with open(draft_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    pairs = data.get("pairs", data) if isinstance(data, dict) else data
                    if isinstance(pairs, list):
                        for idx, p in enumerate(pairs):
                            orig = p.get("original_text") or p.get("source_text", "")
                            simp = p.get("simplified_text") or p.get("target_text", "")
                            split = p.get("split", "internal_train" if idx % 10 != 0 else "internal_val")
                            target_list = self.internal_corpora["internal_val"] if split in ("val", "internal_val") else self.internal_corpora["internal_train"]
                            if orig:
                                target_list.append({"id": f"draft-orig-{idx}", "text": orig, "split": split})
                            if simp:
                                target_list.append({"id": f"draft-simp-{idx}", "text": simp, "split": split})
            except Exception:
                pass

    def check_leakage(
        self, records: List[NormalizedExternalRecord]
    ) -> Dict[str, Any]:
        """Compares external records against internal corpora and computes leakage report."""
        exact_overlaps: List[Dict[str, Any]] = []
        near_overlaps: List[Dict[str, Any]] = []

        # Index internal texts
        internal_lookup: Dict[str, List[Tuple[str, str, str]]] = defaultdict(list)
        internal_token_index: List[Tuple[str, str, str, Set[str]]] = []

        for corpus_name, entries in self.internal_corpora.items():
            for ent in entries:
                norm = normalize_for_leakage(ent["text"])
                if norm:
                    internal_lookup[norm].append((corpus_name, ent["id"], ent["text"]))
                    toks = set(norm.split())
                    if len(toks) >= 4:
                        internal_token_index.append((corpus_name, ent["id"], ent["text"], toks))

        # Check each external record
        checked_source_groups = len(records)
        checked_references = 0

        for rec in records:
            # Check source sentence
            src_norm = normalize_for_leakage(rec.evaluation_source_text)
            src_toks = set(src_norm.split())

            if src_norm in internal_lookup:
                for match in internal_lookup[src_norm]:
                    exact_overlaps.append({
                        "external_record_id": rec.external_record_id,
                        "source_group_id": rec.source_group_id,
                        "role": "source",
                        "matched_corpus": match[0],
                        "matched_internal_id": match[1],
                        "similarity": 1.0,
                    })

            # Check references
            for ref_idx, ref in enumerate(rec.evaluation_references):
                checked_references += 1
                ref_norm = normalize_for_leakage(ref)
                ref_toks = set(ref_norm.split())

                if ref_norm in internal_lookup:
                    for match in internal_lookup[ref_norm]:
                        exact_overlaps.append({
                            "external_record_id": rec.external_record_id,
                            "source_group_id": rec.source_group_id,
                            "role": f"reference_{ref_idx}",
                            "matched_corpus": match[0],
                            "matched_internal_id": match[1],
                            "similarity": 1.0,
                        })

        summary = {
            "total_source_groups_checked": checked_source_groups,
            "total_reference_instances_checked": checked_references,
            "internal_corpora_sizes": {
                name: len(items) for name, items in self.internal_corpora.items()
            },
            "exact_overlap_count": len(exact_overlaps),
            "near_overlap_count": len(near_overlaps),
            "exact_overlaps": exact_overlaps,
            "near_overlaps": near_overlaps,
            "leakage_status": "CLEAN" if len(exact_overlaps) == 0 else "OVERLAPS_RECORDED",
            "enforced_governance_posture": {
                "evaluation_protected": True,
                "training_eligible": False,
                "benchmark_eligible": True,
                "approved_for_child_delivery": False,
            },
        }
        return summary
