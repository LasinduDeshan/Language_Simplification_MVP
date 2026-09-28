"""
Stage 21 Preprocessing Execution Script
Ingests Stage 20 governed release 0.2.0 and generates versioned preprocessed linguistic representations & features.
Target Release: data/preprocessed_features/en/source-0.2.0/pipeline-1.0.0/
"""
import os
import sys
import json
import csv
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Set

# Add backend to sys.path
backend_path = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.nlp_preprocessing.config import PreprocessingConfig
from app.nlp_preprocessing.version import PIPELINE_VERSION, SCHEMA_VERSION, SOURCE_DATASET_VERSION, MODEL_METADATA
from app.nlp_preprocessing.schemas import (
    TextInstance,
    SourceItemAdapter,
    SimplificationPairAdapter,
    AdaptationActivityAdapter,
    LexiconEntryAdapter
)
from app.nlp_preprocessing.pipeline import NLPPreprocessingPipeline
from app.nlp_preprocessing.accounting import PreprocessingAccounting

def load_stage20_data(repo_root: Path):
    # 1. Simplification Pairs
    corpus_path = repo_root / "data" / "simplification_corpus" / "releases" / "0.2.0" / "simplification_corpus.json"
    with open(corpus_path, "r", encoding="utf-8") as f:
        pairs = json.load(f)
        
    # Split map for pairs
    splits_dir = repo_root / "data" / "simplification_corpus" / "releases" / "0.2.0" / "splits"
    train_ids = set()
    val_ids = set()
    test_ids = set()
    if (splits_dir / "development_candidate_train.json").exists():
        with open(splits_dir / "development_candidate_train.json", "r", encoding="utf-8") as f:
            train_ids = {p["pair_id"] for p in json.load(f)}
    if (splits_dir / "development_candidate_validation.json").exists():
        with open(splits_dir / "development_candidate_validation.json", "r", encoding="utf-8") as f:
            val_ids = {p["pair_id"] for p in json.load(f)}
    if (splits_dir / "development_candidate_test.json").exists():
        with open(splits_dir / "development_candidate_test.json", "r", encoding="utf-8") as f:
            test_ids = {p["pair_id"] for p in json.load(f)}

    for p in pairs:
        pid = p["pair_id"]
        if pid in test_ids:
            p["dataset_split"] = "development_candidate_test"
        elif pid in val_ids:
            p["dataset_split"] = "development_candidate_validation"
        else:
            p["dataset_split"] = "development_candidate_train"

    # 2. Adaptation Activities
    act_path = repo_root / "data" / "adaptation_test_set" / "releases" / "0.2.0" / "adaptation_test_set.json"
    with open(act_path, "r", encoding="utf-8") as f:
        activities = json.load(f)

    # 3. Lexicon Entries
    lex_path = repo_root / "data" / "lexicons" / "en" / "releases" / "0.2.0" / "lexicon_repository.json"
    with open(lex_path, "r", encoding="utf-8") as f:
        lex_data = json.load(f)
        lexicons = lex_data if isinstance(lex_data, list) else lex_data.get("entries", [])

    # 4. Source Items (Collect all unique source items across batches)
    batches_dir = repo_root / "data" / "dataset_expansion" / "stage20" / "authoring_batches"
    source_items_dict = {}
    if batches_dir.exists():
        for b_file in sorted(batches_dir.glob("*.json")):
            with open(b_file, "r", encoding="utf-8") as f:
                b_data = json.load(f)
                for item in b_data.get("source_items", []):
                    sid = item.get("source_item_id") or item.get("item_id")
                    if sid:
                        source_items_dict[sid] = item
    
    source_items = list(source_items_dict.values())
    
    return source_items, pairs, activities, lexicons

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    print(f"=== Stage 21 NLP Preprocessing Execution (Source v{SOURCE_DATASET_VERSION} -> Pipeline v{PIPELINE_VERSION}) ===")

    # 1. Load Raw Dataset Entities
    source_items, pairs, activities, lexicons = load_stage20_data(repo_root)
    print(f"Loaded Source Entities:")
    print(f"  - Source Items: {len(source_items)}")
    print(f"  - Simplification Pairs: {len(pairs)}")
    print(f"  - Adaptation Activities: {len(activities)}")
    print(f"  - Lexicon Entries: {len(lexicons)}")

    # Internal lexicon set for matcher
    internal_lex_words = {entry.get("word", "").lower() for entry in lexicons if entry.get("word")}

    # 2. Extract Canonical Text Instances
    text_instances: List[TextInstance] = []
    parent_mappings: List[Dict[str, Any]] = []

    for item in source_items:
        instances = SourceItemAdapter.extract_text_instances(item)
        for inst in instances:
            text_instances.append(inst)
            parent_mappings.append({
                "parent_record_id": inst.parent_record_id,
                "parent_record_type": inst.parent_record_type,
                "text_instance_id": inst.text_instance_id,
                "text_role": inst.text_role,
                "dataset_split": inst.dataset_split
            })

    for pair in pairs:
        instances = SimplificationPairAdapter.extract_text_instances(pair)
        for inst in instances:
            text_instances.append(inst)
            parent_mappings.append({
                "parent_record_id": inst.parent_record_id,
                "parent_record_type": inst.parent_record_type,
                "text_instance_id": inst.text_instance_id,
                "text_role": inst.text_role,
                "dataset_split": inst.dataset_split
            })

    for act in activities:
        instances = AdaptationActivityAdapter.extract_text_instances(act)
        for inst in instances:
            text_instances.append(inst)
            parent_mappings.append({
                "parent_record_id": inst.parent_record_id,
                "parent_record_type": inst.parent_record_type,
                "text_instance_id": inst.text_instance_id,
                "text_role": inst.text_role,
                "dataset_split": inst.dataset_split
            })

    for lex in lexicons:
        instances = LexiconEntryAdapter.extract_text_instances(lex)
        for inst in instances:
            text_instances.append(inst)
            parent_mappings.append({
                "parent_record_id": inst.parent_record_id,
                "parent_record_type": inst.parent_record_type,
                "text_instance_id": inst.text_instance_id,
                "text_role": inst.text_role,
                "dataset_split": inst.dataset_split
            })

    print(f"Extracted {len(text_instances)} total canonical TextInstance objects.")

    # 3. Initialize Pipeline (Mode A: Development Candidate Release)
    config = PreprocessingConfig(allow_locked_test=False)
    cache_dir = repo_root / "data" / "preprocessed_features" / "en" / f"source-{SOURCE_DATASET_VERSION}" / f"pipeline-{PIPELINE_VERSION}" / ".cache"
    pipeline = NLPPreprocessingPipeline(config=config, cache_dir=str(cache_dir), internal_lexicon_words=internal_lex_words)

    # 4. Process all text instances
    print("Processing text instances through NLP Preprocessing Pipeline...")
    processed_records = pipeline.process_batch(text_instances)

    # 5. Prepare Release Directory
    release_dir = repo_root / "data" / "preprocessed_features" / "en" / f"source-{SOURCE_DATASET_VERSION}" / f"pipeline-{PIPELINE_VERSION}"
    release_dir.mkdir(parents=True, exist_ok=True)
    protected_test_dir = release_dir / "protected_test"
    protected_test_dir.mkdir(parents=True, exist_ok=True)

    # 6. Save JSONL records
    records_jsonl_path = release_dir / "preprocessed_records.jsonl"
    with open(records_jsonl_path, "w", encoding="utf-8") as f:
        for rec in processed_records:
            f.write(rec.model_dump_json() + "\n")

    # 7. Save Parent-to-Text Mappings
    mappings_path = release_dir / "parent_to_text_mappings.json"
    with open(mappings_path, "w", encoding="utf-8") as f:
        json.dump(parent_mappings, f, indent=2)

    # 8. Save Tabular Features CSV
    features_csv_path = release_dir / "linguistic_features.csv"
    with open(features_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "text_instance_id", "parent_record_id", "parent_record_type", "text_role", "dataset_split",
            "processing_status", "char_count", "token_count", "word_count", "sentence_count",
            "avg_word_length", "avg_sentence_length", "type_token_ratio", "syllable_count",
            "long_word_count", "noun_count", "verb_count", "adj_count", "adv_count",
            "max_dependency_depth", "avg_dependency_depth", "clause_count", "passive_voice",
            "negation_count", "quantity_count", "text_hash", "feature_hash", "record_hash"
        ])
        for rec in processed_records:
            s = rec.features.surface
            l = rec.features.lexical
            syn = rec.features.syntactic
            prot = rec.features.protected_elements
            writer.writerow([
                rec.text_instance_id, rec.parent_record_id, rec.parent_record_type, rec.text_role, rec.dataset_split,
                rec.processing_status, s.char_count, s.token_count, s.word_count, s.sentence_count,
                s.avg_word_length, s.avg_sentence_length, s.type_token_ratio, s.syllable_count,
                s.long_word_count, l.noun_count, l.verb_count, l.adj_count, l.adv_count,
                syn.max_dependency_depth, syn.avg_dependency_depth, syn.clause_count, syn.passive_voice_detected,
                len(prot.negation_markers), len(prot.quantity_numbers),
                rec.text_hash, rec.feature_hash, rec.record_hash
            ])

    # 9. Save Locked Test Manifest (Protected isolation, 0 raw text)
    locked_records = [r for r in processed_records if r.dataset_split == "development_candidate_test"]
    locked_manifest = {
        "release_version": PIPELINE_VERSION,
        "source_dataset_version": SOURCE_DATASET_VERSION,
        "total_locked_records": len(locked_records),
        "quarantined_from_development": True,
        "items": [
            {
                "text_instance_id": r.text_instance_id,
                "parent_record_id": r.parent_record_id,
                "parent_record_type": r.parent_record_type,
                "text_role": r.text_role,
                "text_hash": r.text_hash,
                "record_hash": r.record_hash,
                "processing_status": r.processing_status
            }
            for r in locked_records
        ]
    }
    with open(protected_test_dir / "locked_test_manifest.json", "w", encoding="utf-8") as f:
        json.dump(locked_manifest, f, indent=2)

    # 10. Accounting & Zero-Loss Reconciliation
    accounting = PreprocessingAccounting()
    summary = accounting.reconcile(text_instances, processed_records, parent_mappings)
    accounting_csv_path = release_dir / "reconciliation_report.csv"
    accounting.generate_csv_report(summary, str(accounting_csv_path))

    # 11. Release Manifest
    manifest = {
        "pipeline_version": PIPELINE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "source_dataset_version": SOURCE_DATASET_VERSION,
        "target_language": "en",
        "target_age_group": "4-8",
        "models": MODEL_METADATA,
        "summary": summary,
        "files": {
            "records_jsonl": "preprocessed_records.jsonl",
            "parent_mappings": "parent_to_text_mappings.json",
            "features_csv": "linguistic_features.csv",
            "reconciliation_csv": "reconciliation_report.csv",
            "locked_test_manifest": "protected_test/locked_test_manifest.json"
        }
    }
    with open(release_dir / "dataset_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("\n=== Preprocessing Completed Successfully ===")
    print(f"Total Text Instances: {summary['raw_text_instance_count']}")
    print(f"Unique Normalized Texts: {summary['unique_normalized_text_count']}")
    print(f"Duplicates Cached/Mapped: {summary['duplicate_text_instance_count']}")
    print(f"Primary Pipeline Success: {summary['success_count']}")
    print(f"Fallback Success: {summary['fallback_success_count']}")
    print(f"Manual Review Required: {summary['manual_review_count']}")
    print(f"Skipped Locked Test Items: {summary['skipped_locked_test_count']}")
    print(f"Failed Records: {summary['failed_count']}")
    print(f"Unaccounted Records: {summary['unaccounted_records']} (Zero Loss: {summary['is_zero_loss']})")
    print(f"Artifacts written to: {release_dir}")

if __name__ == "__main__":
    main()
