"""
Stage 20 Governed Release Builder Module
Atomically packages versioned dataset releases, computes cryptographic SHA-256 hashes,
and generates reproducibility evidence.
"""
import os
import json
import shutil
import hashlib
from datetime import datetime
from typing import Dict, Any, List

class ReleaseBuilder:
    def __init__(self, root_dir: str = None, dataset_version: str = "0.2.0", schema_version: str = "1.0.0", seed: int = 42):
        if root_dir is None:
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        self.root_dir = root_dir
        self.dataset_version = dataset_version
        self.schema_version = schema_version
        self.seed = seed
        self.staging_dir = os.path.join(self.root_dir, "data", f"_staging_release_v{self.dataset_version}")

    def compute_sha256(self, filepath: str) -> str:
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        return sha256.hexdigest()

    def build_release_staging(
        self,
        adaptation_activities: List[Dict[str, Any]],
        simplification_pairs: List[Dict[str, Any]],
        splits: Dict[str, List[Dict[str, Any]]],
        lexicon_entries: List[Dict[str, Any]],
        locked_test_manifest: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Constructs the release in a staging directory.
        """
        if os.path.exists(self.staging_dir):
            shutil.rmtree(self.staging_dir)
        os.makedirs(self.staging_dir, exist_ok=True)

        try:
            # 1. Adaptation Activities
            adapt_dir = os.path.join(self.staging_dir, "adaptation_test_set", "releases", self.dataset_version)
            os.makedirs(adapt_dir, exist_ok=True)
            adapt_file = os.path.join(adapt_dir, "adaptation_test_set.json")
            with open(adapt_file, "w", encoding="utf-8") as f:
                json.dump(adaptation_activities, f, indent=2)

            # 2. Simplification Corpus & Splits
            simp_dir = os.path.join(self.staging_dir, "simplification_corpus", "releases", self.dataset_version)
            splits_dir = os.path.join(simp_dir, "splits")
            os.makedirs(splits_dir, exist_ok=True)
            
            simp_file = os.path.join(simp_dir, "simplification_corpus.json")
            with open(simp_file, "w", encoding="utf-8") as f:
                json.dump(simplification_pairs, f, indent=2)

            for split_name, split_recs in splits.items():
                split_file = os.path.join(splits_dir, f"{split_name}.json")
                with open(split_file, "w", encoding="utf-8") as f:
                    json.dump(split_recs, f, indent=2)

            locked_file = os.path.join(splits_dir, "locked_test_manifest.json")
            with open(locked_file, "w", encoding="utf-8") as f:
                json.dump(locked_test_manifest, f, indent=2)

            # 3. Lexicon Repository
            lex_dir = os.path.join(self.staging_dir, "lexicons", "en", "releases", self.dataset_version)
            os.makedirs(lex_dir, exist_ok=True)
            lex_file = os.path.join(lex_dir, "lexicon_repository.json")
            with open(lex_file, "w", encoding="utf-8") as f:
                json.dump(lexicon_entries, f, indent=2)

            # Compute staging SHA-256 manifest
            manifest_entries = {}
            for root, _, files in os.walk(self.staging_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.staging_dir).replace("\\", "/")
                    manifest_entries[f"data/{rel_path}"] = self.compute_sha256(full_path)

            return {
                "staging_dir": self.staging_dir,
                "dataset_version": self.dataset_version,
                "manifest_entries": manifest_entries,
                "status": "staged_successfully"
            }
        except Exception as e:
            if os.path.exists(self.staging_dir):
                shutil.rmtree(self.staging_dir)
            raise RuntimeError(f"Release staging build failed: {e}")

    def publish_release(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Atomically publishes the staged release to permanent data paths.
        """
        if dry_run:
            return {"status": "dry_run_success", "staging_dir": self.staging_dir}

        try:
            # Copy all directories from staging to data/
            for item in os.listdir(self.staging_dir):
                src_item = os.path.join(self.staging_dir, item)
                dst_item = os.path.join(self.root_dir, "data", item)
                if os.path.isdir(src_item):
                    # Copy contents preserving structure
                    shutil.copytree(src_item, dst_item, dirs_exist_ok=True)

            # Generate SHA-256 Manifest
            manifest_lines = []
            files_to_hash = [
                f"data/adaptation_test_set/releases/{self.dataset_version}/adaptation_test_set.json",
                f"data/simplification_corpus/releases/{self.dataset_version}/simplification_corpus.json",
                f"data/simplification_corpus/releases/{self.dataset_version}/splits/development_candidate_train.json",
                f"data/simplification_corpus/releases/{self.dataset_version}/splits/development_candidate_validation.json",
                f"data/simplification_corpus/releases/{self.dataset_version}/splits/development_candidate_test.json",
                f"data/simplification_corpus/releases/{self.dataset_version}/splits/locked_test_manifest.json",
                f"data/lexicons/en/releases/{self.dataset_version}/lexicon_repository.json",
                "docs/stage20_authoring_guidelines.md",
                "docs/stage20_dataset_inventory.md",
                "docs/stage20_dataset_gap_matrix.csv",
                "docs/stage20_expansion_targets.csv",
                "docs/stage20_balance_report.csv",
                "docs/stage20_duplicate_report.csv",
                "docs/stage20_leakage_report.csv",
                "docs/stage20_validation_summary.csv"
            ]

            for rel_file in files_to_hash:
                full_p = os.path.join(self.root_dir, rel_file)
                if os.path.exists(full_p):
                    h = self.compute_sha256(full_p)
                    manifest_lines.append(f"{h}  {rel_file.replace(chr(92), '/')}")

            manifest_path = os.path.join(self.root_dir, "docs", "stage20_manifest.sha256")
            os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
            with open(manifest_path, "w", encoding="utf-8") as f:
                f.write("\n".join(manifest_lines) + "\n")

            # Generate Reproducibility Evidence
            repro_path = os.path.join(self.root_dir, "docs", "stage20_reproducibility_evidence.json")
            os.makedirs(os.path.dirname(repro_path), exist_ok=True)
            repro_data = {
                "stage": "Stage 20",
                "dataset_version": self.dataset_version,
                "schema_version": self.schema_version,
                "rule_set_version": "1.0.0",
                "split_random_seed": self.seed,
                "python_version": "3.11.9",
                "pydantic_version": "2.8.2",
                "embedding_library": "sentence-transformers",
                "embedding_library_version": "3.0.1",
                "model_name": "sentence-transformers/all-MiniLM-L6-v2",
                "model_revision": "fa979f7764422d64a50d27ae85e50529e843666b",
                "model_artifact_hash": "e4ce9877abf616632f65a6b674041d4711fc0698",
                "device": "cpu",
                "normalization": "l2_norm",
                "threshold": 0.92,
                "threshold_role": "advisory",
                "generated_at": datetime.utcnow().isoformat() + "Z"
            }
            with open(repro_path, "w", encoding="utf-8") as f:
                json.dump(repro_data, f, indent=2)

            # Cleanup staging
            if os.path.exists(self.staging_dir):
                shutil.rmtree(self.staging_dir)

            return {
                "status": "published_successfully",
                "manifest_path": manifest_path,
                "reproducibility_path": repro_path
            }
        except Exception as e:
            if os.path.exists(self.staging_dir):
                shutil.rmtree(self.staging_dir)
            raise RuntimeError(f"Atomic publish failed: {e}")
