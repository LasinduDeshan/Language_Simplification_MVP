"""Repository for loading and filtering Stage 21 preprocessed linguistic feature records."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
import json


class FeatureRepository:
    """Loads Stage 21 preprocessed linguistic feature records and metadata."""

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is not None:
            self.base_dir = Path(base_dir)
        else:
            default_path = Path("data/preprocessed_features/en/source-0.2.0/pipeline-1.0.0")
            if default_path.exists():
                self.base_dir = default_path
            else:
                current = Path(__file__).resolve().parent
                found = None
                for parent in [current, *current.parents]:
                    candidate = parent / "data" / "preprocessed_features" / "en" / "source-0.2.0" / "pipeline-1.0.0"
                    if candidate.exists():
                        found = candidate
                        break
                self.base_dir = found or default_path
        self.features_csv_path = self.base_dir / "linguistic_features.csv"
        self.records_jsonl_path = self.base_dir / "preprocessed_records.jsonl"
        self.mappings_json_path = self.base_dir / "parent_to_text_mappings.json"
        self._review_ids: Optional[set[str]] = None

    def _load_review_instance_ids(self) -> set[str]:
        """Loads the exact 163 manual_review_required text instance IDs from preprocessed_records.jsonl."""
        if self._review_ids is not None:
            return self._review_ids

        review_ids = set()
        if self.records_jsonl_path.exists():
            with open(self.records_jsonl_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        decision = record.get("language_verification", {}).get("decision")
                        status = record.get("processing_status")
                        if decision == "manual_review_required" or status == "manual_review_required":
                            review_ids.add(record["text_instance_id"])
                    except Exception:
                        pass
        self._review_ids = review_ids
        return self._review_ids

    def load_features_df(self) -> pd.DataFrame:
        """Loads the linguistic features CSV with reconciled Stage 21 manual_review_required flags."""
        if not self.features_csv_path.exists():
            raise FileNotFoundError(f"Linguistic features CSV not found at {self.features_csv_path}")
        df = pd.read_csv(self.features_csv_path)

        review_ids = self._load_review_instance_ids()
        df["manual_review_required"] = df["text_instance_id"].isin(review_ids)
        return df

    def load_features_records(self) -> List[Dict[str, Any]]:
        """Loads features as a list of dictionary records with manual_review_required flags."""
        df = self.load_features_df()
        return df.to_dict(orient="records")

    def load_parent_mappings(self) -> Dict[str, Any]:
        """Loads parent to text instance mappings."""
        if not self.mappings_json_path.exists():
            return {}
        with open(self.mappings_json_path, "r", encoding="utf-8") as f:
            return json.load(f)
