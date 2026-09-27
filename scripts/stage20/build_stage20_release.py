"""
Stage 20 Script: Build Stage 20 Release
Atomically generates the v0.2.0 governed dataset releases and computes SHA-256 manifests.
"""
import os
import sys
import json
import argparse

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.datasets.expansion.split_builder import SplitBuilder
from app.datasets.expansion.release_builder import ReleaseBuilder

def main():
    parser = argparse.ArgumentParser(description="Build Stage 20 v0.2.0 Dataset Release")
    parser.add_argument("--dry-run", action="store_true", help="Run staging build without publishing")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for group-aware splitting")
    parser.add_argument("--output-version", type=str, default="0.2.0", help="Dataset release version")
    args = parser.parse_args()

    print("=" * 60)
    print(f"STAGE 20: Building Dataset Release v{args.output_version} (Dry-Run: {args.dry_run})")
    print("=" * 60)

    # 1. Load Baseline v0.1.0 records
    adapt_v1_path = os.path.join(ROOT_DIR, "data", "adaptation_test_set", "releases", "0.1.0", "adaptation_test_set.json")
    simp_v1_path = os.path.join(ROOT_DIR, "data", "simplification_corpus", "releases", "0.1.0", "simplification_corpus.json")
    lex_v1_path = os.path.join(ROOT_DIR, "data", "lexicons", "en", "releases", "0.1.0", "lexicon_repository.json")

    with open(adapt_v1_path, "r", encoding="utf-8") as f:
        adapt_base = json.load(f)
    with open(simp_v1_path, "r", encoding="utf-8") as f:
        simp_base = json.load(f)
    with open(lex_v1_path, "r", encoding="utf-8") as f:
        lex_base = json.load(f)

    # 2. Load all 5 newly authored expansion batches
    batch_dir = os.path.join(ROOT_DIR, "data", "dataset_expansion", "stage20", "authoring_batches")
    new_sources = []
    new_pairs = []
    new_acts = []
    new_lex = []

    for filename in sorted(os.listdir(batch_dir)):
        if filename.endswith(".json"):
            filepath = os.path.join(batch_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                new_sources.extend(data.get("source_items", []))
                new_pairs.extend(data.get("simplification_pairs", []))
                new_acts.extend(data.get("adaptation_activities", []))
                new_lex.extend(data.get("lexicon_entries", []))

    # Combine: Adaptation Test Set contains baseline 40 + new activities
    combined_activities = (adapt_base if isinstance(adapt_base, list) else adapt_base.get("records", [])) + new_acts
    combined_pairs = (simp_base if isinstance(simp_base, list) else simp_base.get("records", [])) + new_pairs
    combined_lexicons = (lex_base if isinstance(lex_base, list) else lex_base.get("records", [])) + new_lex

    # 3. Build group-aware candidate splits
    splitter = SplitBuilder(seed=args.seed)
    eligible_pairs, excluded = splitter.filter_candidate_eligibility(combined_pairs)
    splits = splitter.build_group_aware_splits(eligible_pairs)

    # 4. Generate locked test manifest (IDs and hashes only)
    temp_locked_path = os.path.join(ROOT_DIR, "data", "dataset_expansion", "stage20", "reports", "locked_test_manifest.json")
    locked_manifest = splitter.generate_locked_test_manifest(
        splits["development_candidate_test"],
        temp_locked_path,
        dataset_version=args.output_version
    )

    # 5. Atomic release build
    builder = ReleaseBuilder(root_dir=ROOT_DIR, dataset_version=args.output_version, seed=args.seed)
    staged = builder.build_release_staging(
        adaptation_activities=combined_activities,
        simplification_pairs=combined_pairs,
        splits=splits,
        lexicon_entries=combined_lexicons,
        locked_test_manifest=locked_manifest
    )

    print(f"Staging build complete: {staged['staging_dir']}")
    print(f"  - Total Activities in Release: {len(combined_activities)}")
    print(f"  - Total Pairs in Release:      {len(combined_pairs)}")
    print(f"  - Total Lexicon in Release:    {len(combined_lexicons)}")

    # 6. Publish
    published = builder.publish_release(dry_run=args.dry_run)
    print(f"Publish status: {published['status']}")
    if not args.dry_run:
        print(f"  - SHA-256 Manifest: {published['manifest_path']}")
        print(f"  - Reproducibility:  {published['reproducibility_path']}")
    print("=" * 60)

if __name__ == "__main__":
    main()
