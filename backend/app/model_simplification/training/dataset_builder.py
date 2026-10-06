"""
Stage 26 Training Dataset Builder.
Extracts clean, eligible 3-tier source groups from the training eligibility manifest
and constructs prompt/target dataset pairs for seq2seq model training.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple


class Seq2SeqDatasetBuilder:
    """
    Builds clean seq2seq training instances strictly from eligible groups in the manifest.
    """

    def __init__(self, repo_root: Path = None):
        if repo_root is None:
            self.repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        else:
            self.repo_root = Path(repo_root)

        self.corpus_path = self.repo_root / "data" / "simplification_corpus" / "releases" / "0.2.0" / "simplification_corpus.json"
        self.manifest_path = self.repo_root / "data" / "model_simplification" / "registry" / "stage26_training_eligibility_manifest.json"

    def build_dataset(self) -> List[Dict[str, Any]]:
        """
        Builds list of clean {input_prompt, target_text, tier, age, pair_id, group_id} records.
        """
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Training eligibility manifest not found at {self.manifest_path}")

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        eligible_group_ids = {g["source_group_id"] for g in manifest.get("eligible_groups", [])}

        with open(self.corpus_path, "r", encoding="utf-8") as f:
            corpus = json.load(f)

        v2_corpus = [p for p in corpus if p.get("dataset_version") == "0.2.0"]

        training_samples: List[Dict[str, Any]] = []

        for pair in v2_corpus:
            group_id = pair.get("source_item_id") or pair.get("source_activity_id") or pair.get("source_record_id")
            if group_id not in eligible_group_ids:
                continue

            tier = pair.get("support_level", "moderate").lower()
            age = pair.get("target_age", 6)
            source_text = pair.get("source_text", "").strip()
            target_text = pair.get("target_text", "").strip()
            pair_id = pair.get("pair_id")

            # Input formatting
            prompt = f"simplify english {tier} for {age} year old: {source_text}"

            training_samples.append({
                "pair_id": pair_id,
                "source_group_id": group_id,
                "support_level": tier,
                "target_age": age,
                "input_text": prompt,
                "target_text": target_text,
                "source_text": source_text,
            })

        return training_samples

    def save_json(self, out_path: Path) -> int:
        samples = self.build_dataset()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(samples, f, indent=2)
        return len(samples)
