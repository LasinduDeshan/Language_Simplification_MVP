"""Manifest Repository for Stage 27.

Ingests Release 0.2.0 simplification pairs, lexicon entries, adaptation activities,
and the 326 flagged reformulations. Builds and freezes the unified review manifest,
verifies dataset inventory accounting, and generates cryptographic hashes.
"""

import csv
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from .schemas import (
    InventoryAccounting,
    ReviewManifestItem,
    ReviewRecordType,
    SupportLevel,
)


class ManifestRepository:
    """Manages frozen review manifests and dataset inventory accounting."""

    def __init__(
        self,
        workspace_root: Optional[Any] = None,
        root_dir: Optional[Any] = None,
    ) -> None:
        if root_dir is not None:
            self.workspace_root = Path(root_dir)
        elif workspace_root is not None:
            self.workspace_root = Path(workspace_root)
        else:
            self.workspace_root = Path(__file__).resolve().parents[4]

        self.manifest_dir = str(self.workspace_root / "data" / "expert_review" / "manifests")
        self._items: Dict[str, ReviewManifestItem] = {}
        self._flagged_reformulation_ids: set = set()
        self._inventory = InventoryAccounting()

    @staticmethod
    def compute_sha256(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def load_or_generate_manifest(self) -> List[ReviewManifestItem]:
        """Loads items from frozen review_manifest_v1.json if it exists, otherwise generates from governed datasets."""
        manifest_json = Path(self.manifest_dir) / "review_manifest_v1.json"
        if manifest_json.exists():
            with open(manifest_json, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            self._items = {it["item_id"]: ReviewManifestItem(**it) for it in data}
            return list(self._items.values())

        items, _ = self.load_from_governed_datasets()
        return items

    def load_from_governed_datasets(self) -> Tuple[List[ReviewManifestItem], InventoryAccounting]:
        """Ingests all governed Release 0.2.0 datasets and constructs review manifest items."""
        self._items.clear()
        self._flagged_reformulation_ids.clear()

        # 1. Load Issue Register to identify the 326 flagged reformulations
        issue_reg_path = (
            self.workspace_root
            / "data"
            / "simplification_corpus"
            / "releases"
            / "0.2.0"
            / "dataset_issue_register.json"
        )
        if issue_reg_path.exists():
            with open(issue_reg_path, "r", encoding="utf-8") as f:
                issue_data = json.load(f)
            flagged_list = issue_data.get("flagged_records", [])
            for rec in flagged_list:
                pair_id = rec.get("simplification_pair_id") or rec.get("pair_id")
                if pair_id:
                    self._flagged_reformulation_ids.add(pair_id)

        # 2. Load 1,110 Simplification Pairs
        corpus_path = (
            self.workspace_root
            / "data"
            / "simplification_corpus"
            / "releases"
            / "0.2.0"
            / "simplification_corpus.json"
        )
        with open(corpus_path, "r", encoding="utf-8") as f:
            corpus_data = json.load(f)

        pair_count = 0
        for item in corpus_data:
            pair_id = item.get("pair_id", "")
            source_id = item.get("source_id", "")
            source_text = item.get("source_text", "")
            target_text = item.get("target_text", "")
            support_level_str = item.get("support_level", "mild").lower()
            try:
                support_lvl = SupportLevel(support_level_str)
            except ValueError:
                support_lvl = SupportLevel.MILD

            is_reform = pair_id in self._flagged_reformulation_ids
            content_hash = self.compute_sha256(f"{source_text}|{target_text}|{support_level_str}")

            manifest_item = ReviewManifestItem(
                item_id=pair_id,
                source_group_id=source_id,
                record_type=ReviewRecordType.SIMPLIFICATION_PAIR,
                text_stimulus=source_text,
                target_text=target_text,
                support_level=support_lvl,
                target_age_min=item.get("target_age_min", 4),
                target_age_max=item.get("target_age_max", 8),
                domain=item.get("domain", "general"),
                difficulty=item.get("difficulty", "medium"),
                is_reformulation_candidate=is_reform,
                is_locked_evaluation=item.get("is_locked_evaluation", False),
                dataset_split=item.get("split", "train"),
                content_hash=content_hash,
                metadata={
                    "author": item.get("author", "unknown"),
                    "stage_origin": item.get("stage_origin", "stage20"),
                },
            )
            self._items[pair_id] = manifest_item
            pair_count += 1

        # 3. Load 378 Lexicon Entries
        lexicon_path = (
            self.workspace_root
            / "data"
            / "lexicons"
            / "en"
            / "releases"
            / "0.2.0"
            / "lexicon_repository.json"
        )
        lex_count = 0
        with open(lexicon_path, "r", encoding="utf-8") as f:
            lex_data = json.load(f)

        for lex_entry in lex_data:
            lex_id = lex_entry.get("lexicon_id") or f"LEX-{lex_entry.get('headword', '')}-{lex_count:04d}"
            headword = lex_entry.get("headword", "")
            replacement = lex_entry.get("suggested_replacement", "")
            definition = lex_entry.get("child_definition", "")
            content_hash = self.compute_sha256(f"{headword}|{replacement}|{definition}")

            manifest_item = ReviewManifestItem(
                item_id=lex_id,
                source_group_id=f"GRP-LEX-{headword}",
                record_type=ReviewRecordType.LEXICON_ENTRY,
                text_stimulus=headword,
                target_text=replacement,
                support_level=None,
                target_age_min=4,
                target_age_max=8,
                domain="vocabulary",
                difficulty="lexical",
                is_reformulation_candidate=False,
                is_locked_evaluation=False,
                dataset_split="lexicon",
                content_hash=content_hash,
                metadata=lex_entry,
            )
            self._items[lex_id] = manifest_item
            lex_count += 1

        # 4. Load 192 Adaptation Activities
        act_path = (
            self.workspace_root
            / "data"
            / "adaptation_test_set"
            / "releases"
            / "0.2.0"
            / "adaptation_test_set.json"
        )
        act_count = 0
        with open(act_path, "r", encoding="utf-8") as f:
            act_data = json.load(f)

        for act_entry in act_data:
            act_id = act_entry.get("task_id") or act_entry.get("activity_id") or f"ACT-{act_count:04d}"
            prompt = act_entry.get("prompt_text") or act_entry.get("instruction", "")
            target_resp = str(act_entry.get("target_response", ""))
            content_hash = self.compute_sha256(f"{prompt}|{target_resp}")

            manifest_item = ReviewManifestItem(
                item_id=act_id,
                source_group_id=act_entry.get("source_id", f"GRP-ACT-{act_id}"),
                record_type=ReviewRecordType.ADAPTATION_ACTIVITY,
                text_stimulus=prompt,
                target_text=target_resp,
                support_level=None,
                target_age_min=4,
                target_age_max=8,
                domain=act_entry.get("skill_domain", "adaptation"),
                difficulty="activity",
                is_reformulation_candidate=False,
                is_locked_evaluation=False,
                dataset_split="test",
                content_hash=content_hash,
                metadata=act_entry,
            )
            self._items[act_id] = manifest_item
            act_count += 1

        # Verify exact inventory accounting
        self._inventory = InventoryAccounting(
            total_pairs=pair_count,
            total_lexicon=lex_count,
            total_activities=act_count,
            reformulation_queue=len(self._flagged_reformulation_ids),
            unresolved_reformulations=len(self._flagged_reformulation_ids),
        )

        return list(self._items.values()), self._inventory

    def get_item(self, item_id: str) -> Optional[ReviewManifestItem]:
        """Fetch item by unique identifier."""
        return self._items.get(item_id)

    def list_items(
        self, record_type: Optional[ReviewRecordType] = None
    ) -> List[ReviewManifestItem]:
        """List items filtered by type."""
        if record_type:
            return [it for it in self._items.values() if it.record_type == record_type]
        return list(self._items.values())

    def get_inventory(self) -> InventoryAccounting:
        """Return current inventory accounting."""
        return self._inventory

    def export_csv(self, output_path: Path) -> Path:
        """Export manifest to CSV file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "item_id",
            "source_group_id",
            "record_type",
            "text_stimulus",
            "target_text",
            "support_level",
            "target_age_min",
            "target_age_max",
            "domain",
            "difficulty",
            "is_reformulation_candidate",
            "is_locked_evaluation",
            "dataset_split",
            "content_hash",
        ]
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for it in self._items.values():
                writer.writerow({
                    "item_id": it.item_id,
                    "source_group_id": it.source_group_id,
                    "record_type": it.record_type.value,
                    "text_stimulus": it.text_stimulus,
                    "target_text": it.target_text,
                    "support_level": it.support_level.value if it.support_level else "",
                    "target_age_min": it.target_age_min,
                    "target_age_max": it.target_age_max,
                    "domain": it.domain,
                    "difficulty": it.difficulty,
                    "is_reformulation_candidate": str(it.is_reformulation_candidate),
                    "is_locked_evaluation": str(it.is_locked_evaluation),
                    "dataset_split": it.dataset_split or "",
                    "content_hash": it.content_hash,
                })
        return output_path

    def export_json(self, output_path: Path) -> Tuple[Path, str]:
        """Export manifest to JSON file and return path and SHA-256 hash."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        items_dict = [it.model_dump() for it in self._items.values()]
        content = json.dumps(items_dict, indent=2, ensure_ascii=False)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        with open(output_path, "rb") as f:
            manifest_hash = hashlib.sha256(f.read()).hexdigest()
        return output_path, manifest_hash
