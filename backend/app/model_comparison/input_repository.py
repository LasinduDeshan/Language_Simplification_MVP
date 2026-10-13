"""
Input Repository for Stage 28A Preliminary English Model Comparison.
Loads and validates:
1. Internal locked benchmark: Full historical set (135 items) and Clean subset (39 items)
2. ASSET external benchmark: Official test split (359 items) with 10 references per source
"""
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.model_comparison.schemas import ComparisonItemInput


class InputRepository:
    def __init__(self, repo_root: Optional[Path] = None):
        if repo_root is None:
            # Walk up to repo root
            self.repo_root = Path(__file__).resolve().parent.parent.parent.parent
        else:
            self.repo_root = repo_root

        self.internal_locked_file = (
            self.repo_root
            / "data"
            / "baseline_simplification"
            / "evaluation_inputs"
            / "internal_locked_test_groups.json"
        )
        self.clean_subset_manifest_file = (
            self.repo_root
            / "data"
            / "model_simplification"
            / "registry"
            / "stage26_clean_subset_manifest.json"
        )
        self.issue_register_file = (
            self.repo_root
            / "data"
            / "simplification_corpus"
            / "releases"
            / "0.2.0"
            / "dataset_issue_register.json"
        )
        self.asset_dir = (
            self.repo_root / "data" / "external_english" / "asset" / "raw"
        )

    def compute_file_sha256(self, file_path: Path) -> str:
        """Calculate 64-char lowercase hexadecimal SHA-256 checksum of a file."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def load_internal_locked_full(self) -> List[ComparisonItemInput]:
        """
        Load all 45 source groups across 3 support tiers (mild, moderate, strong)
        yielding exactly 135 evaluation items.
        """
        if not self.internal_locked_file.exists():
            raise FileNotFoundError(f"Locked test file not found: {self.internal_locked_file}")

        with open(self.internal_locked_file, "r", encoding="utf-8") as f:
            groups = json.load(f)

        items: List[ComparisonItemInput] = []
        for g in groups:
            gid = g.get("source_group_id") or g.get("source_item_id")
            src = g["source_text"]
            refs = g.get("reference_texts") or [src]
            prot = g.get("protected_terms", [])
            age = g.get("target_content_age", 6)

            for tier in ["mild", "moderate", "strong"]:
                item_id = f"{gid}_{tier}"
                items.append(
                    ComparisonItemInput(
                        item_id=item_id,
                        source_group_id=gid,
                        source_text=src,
                        support_level=tier,
                        target_age=age,
                        protected_terms=prot,
                        reference_texts=refs,
                        dataset_name="internal_locked_full",
                    )
                )

        if len(items) != 135:
            raise ValueError(f"Expected 135 internal locked items, got {len(items)}")

        return items

    def load_internal_locked_clean(self) -> List[ComparisonItemInput]:
        """
        Load the 13 clean text-simplification source groups across 3 tiers (39 items).
        """
        full_items = self.load_internal_locked_full()

        if self.clean_subset_manifest_file.exists():
            with open(self.clean_subset_manifest_file, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            clean_item_ids = set(manifest.get("item_ids", []))
            clean_items = [it for it in full_items if it.item_id in clean_item_ids]
        else:
            # Fallback to issue register filtering
            with open(self.issue_register_file, "r", encoding="utf-8") as f:
                reg = json.load(f)
            flagged = {
                r.get("source_item_id")
                for r in reg.get("flagged_records", [])
                if r.get("source_item_id")
            }
            clean_items = [it for it in full_items if it.source_group_id not in flagged]

        if len(clean_items) != 39:
            raise ValueError(f"Expected 39 clean subset items, got {len(clean_items)}")

        for it in clean_items:
            it.dataset_name = "internal_locked_clean"

        return clean_items

    def load_asset_test_split(self, operating_mode: str = "generic") -> List[ComparisonItemInput]:
        """
        Load the 359 official ASSET test sources with 10 reference simplifications each.
        Predeclared fixed operating mode (default: 'generic', or 'moderate').
        """
        orig_file = self.asset_dir / "asset.test.orig"
        if not orig_file.exists():
            raise FileNotFoundError(f"ASSET test source file not found: {orig_file}")

        with open(orig_file, "r", encoding="utf-8") as f:
            orig_lines = [line.strip() for line in f if line.strip()]

        ref_files = [self.asset_dir / f"asset.test.simp.{i}" for i in range(10)]
        for rf in ref_files:
            if not rf.exists():
                raise FileNotFoundError(f"ASSET test reference file not found: {rf}")

        all_refs: List[List[str]] = [[] for _ in range(len(orig_lines))]
        for rf in ref_files:
            with open(rf, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                if len(lines) != len(orig_lines):
                    raise ValueError(f"Reference file {rf.name} line count mismatch: {len(lines)} vs {len(orig_lines)}")
                for idx, line in enumerate(lines):
                    all_refs[idx].append(line)

        items: List[ComparisonItemInput] = []
        for idx, (src, refs) in enumerate(zip(orig_lines, all_refs)):
            item_id = f"ASSET-TEST-{idx+1:04d}"
            items.append(
                ComparisonItemInput(
                    item_id=item_id,
                    source_group_id=f"ASSET-SG-{idx+1:04d}",
                    source_text=src,
                    support_level=operating_mode,
                    target_age=6,
                    protected_terms=[],
                    reference_texts=refs,
                    dataset_name="asset_test",
                )
            )

        if len(items) != 359:
            raise ValueError(f"Expected 359 ASSET test items, got {len(items)}")

        return items
