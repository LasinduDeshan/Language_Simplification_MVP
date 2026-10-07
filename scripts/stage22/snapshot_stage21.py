"""Step 0: Verify Stage 21 inputs and dataset integrity."""

import sys
from pathlib import Path
import pandas as pd

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from app.complexity_analysis.repositories.feature_repository import FeatureRepository


def main():
    repo = FeatureRepository()
    print("Verifying Stage 21 feature repository...")
    df = repo.load_features_df()
    print(f"Total Stage 21 text instances loaded: {len(df)}")
    assert len(df) == 3617, f"Expected 3,617 text instances, got {len(df)}"

    splits = df["dataset_split"].value_counts().to_dict()
    print("Dataset split distribution:", splits)

    roles = df["text_role"].value_counts().to_dict()
    print("Text role distribution:", roles)

    parent_types = df["parent_record_type"].value_counts().to_dict()
    print("Parent record type distribution:", parent_types)

    print("Stage 21 inputs successfully verified!")


if __name__ == "__main__":
    main()
