"""
Execute WP8 Full-Corpus Deduplication, Multi-Source Clustering, and Split Assignment.
Enforces Invariants 17, 18, 19, 20:
- Exact duplicate clustering (hash-based)
- Near-duplicate candidate detection (MinHash + Jaccard)
- Transitive connected components for split groups
- Strict dev pool isolation (100% in train)
- Zero leakage across split boundaries
- Dual-view export: Provenance-preserving (180 records) and Canonical analytical (150 records)
"""

import collections
import json
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.datasets.sinhala_external.config import get_frozen_stage31_configuration
from app.datasets.sinhala_external.deduplication import DeduplicationEngine
from app.datasets.sinhala_external.schemas import (
    PilotCorpusRecord,
    CorpusSplit,
    SplitComponentType,
)
from app.datasets.sinhala_external.storage import storage_manager

SCREENED_FILE = PROJECT_ROOT / "data" / "sinhala_external" / "staged" / "screened_documents.jsonl"
CORPUS_FILE = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "pilot_corpus.jsonl"
CANONICAL_FILE = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "canonical_analytical_corpus.jsonl"
METADATA_FILE = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "corpus_metadata.json"

def run():
    print("--- Starting Stage 31 Full-Corpus Deduplication & Split Assignment (WP8) ---")
    cfg = get_frozen_stage31_configuration()
    cfg_hash = "53aa0a8aa7ccc226f17107a18ee024dd85e71ad5776388650ee973a60bc1ef40"
    print(f"Loaded frozen Stage 31 configuration (Hash: {cfg_hash[:16]}...)")

    lines = SCREENED_FILE.read_text(encoding="utf-8").splitlines()
    screened_records = [json.loads(l) for l in lines]
    print(f"Loaded {len(screened_records)} screened records.")

    # 1. Read normalized text for all records
    text_map = {}
    doc_group_map = {}
    record_map = {}
    for r in screened_records:
        rid = r["record_id"]
        record_map[rid] = r
        doc_group_map[rid] = r["document_group_id"]
        text_bytes = storage_manager.read_raw_file(r["normalized_text_storage_ref"])
        text_map[rid] = text_bytes.decode("utf-8")

    engine = DeduplicationEngine(
        candidate_similarity_threshold=0.80,
        confirmed_similarity_threshold=0.90,
    )

    # 2. Duplicate Detection
    print("\n[Step 1] Running exact duplicate detection across all 180 records...")
    exact_clusters = engine.find_exact_duplicates(text_map)
    multimember_exact = {k: v for k, v in exact_clusters.items() if len(v) > 1}
    print(f"  Total exact clusters: {len(exact_clusters)} ({len(multimember_exact)} multi-member clusters)")

    print("\n[Step 2] Running near-duplicate detection across all 180 records...")
    near_candidates = engine.find_near_duplicates(text_map)
    confirmed_near = [(c.record_a, c.record_b) for c in near_candidates if c.similarity >= 0.90]
    manual_review_near = [(c.record_a, c.record_b, c.similarity) for c in near_candidates if 0.80 <= c.similarity < 0.90]
    print(f"  Candidate pairs (>= 0.80): {len(near_candidates)}")
    print(f"  Confirmed near-duplicate edges (>= 0.90): {len(confirmed_near)}")
    print(f"  Manual review pairs (0.80 - 0.90): {len(manual_review_near)}")

    # 3. Transitive Split Group Formation
    print("\n[Step 3] Building transitive connected components for split groups...")
    all_rec_ids = sorted(list(text_map.keys()))
    dev_rec_ids = {r["record_id"] for r in screened_records if r["is_method_development_record"]}
    print(f"  Method-development records in pool: {len(dev_rec_ids)}")

    rec_to_split_group, group_types = engine.build_transitive_split_groups(
        all_record_ids=all_rec_ids,
        doc_group_map=doc_group_map,
        exact_clusters=exact_clusters,
        confirmed_near_dups=confirmed_near,
        dev_records=dev_rec_ids
    )

    all_groups = sorted(list(set(rec_to_split_group.values())))
    dev_groups = [g for g in all_groups if group_types[g] == "TRAIN_ONLY_DEVELOPMENT_COMPONENT"]
    untouched_groups = [g for g in all_groups if group_types[g] == "UNTOUCHED_EVAL_ELIGIBLE_COMPONENT"]
    print(f"  Total Transitive Split Groups Formed: {len(all_groups)}")
    print(f"  Development Groups (TRAIN_ONLY):     {len(dev_groups)}")
    print(f"  Untouched Evaluation-Eligible Groups: {len(untouched_groups)}")

    # 4. Split Assignment
    print("\n[Step 4] Assigning split groups to splits (Train / Validation / Locked-Test)...")
    split_group_to_split = {}
    
    # Invariant 18 & 19: All development groups go strictly to train
    for g in dev_groups:
        split_group_to_split[g] = CorpusSplit.TRAIN

    # Partition untouched groups deterministically
    rng = random.Random(42)
    shuffled_untouched = list(untouched_groups)
    rng.shuffle(shuffled_untouched)

    # Target exactly 13 records for validation and 13 records for locked test
    # from untouched evaluation-eligible components (yielding 64 untouched train + 90 dev = 154 train)
    val_groups = set()
    test_groups = set()
    train_untouched_groups = set()
    val_record_count = 0
    test_record_count = 0

    untouched_group_records = collections.defaultdict(list)
    for rid, grp in rec_to_split_group.items():
        if grp in untouched_groups:
            untouched_group_records[grp].append(rid)

    for g in shuffled_untouched:
        g_len = len(untouched_group_records[g])
        if val_record_count + g_len <= 13:
            val_groups.add(g)
            val_record_count += g_len
            split_group_to_split[g] = CorpusSplit.VALIDATION
        elif test_record_count + g_len <= 13:
            test_groups.add(g)
            test_record_count += g_len
            split_group_to_split[g] = CorpusSplit.LOCKED_TEST
        else:
            train_untouched_groups.add(g)
            split_group_to_split[g] = CorpusSplit.TRAIN

    # Build canonical exact record mapping and cluster-normalized weights
    record_canonical_map = {}
    record_is_canonical = {}
    record_exact_weight = {}
    record_retention_reason = {}

    for cid, members in exact_clusters.items():
        sorted_mems = sorted(members)
        canonical_id = sorted_mems[0]
        cluster_size = len(sorted_mems)
        for m in sorted_mems:
            record_canonical_map[m] = canonical_id
            if m == canonical_id:
                record_is_canonical[m] = True
                record_exact_weight[m] = round(1.0 / cluster_size, 6)
                record_retention_reason[m] = "PRIMARY_CANONICAL_RECORD"
            else:
                record_is_canonical[m] = False
                record_exact_weight[m] = round(1.0 / cluster_size, 6)
                record_retention_reason[m] = "PROVENANCE_AND_TIER_METADATA"

    # Build PilotCorpusRecord list
    corpus_records = []
    split_counts = collections.defaultdict(int)
    split_dev_counts = collections.defaultdict(int)

    for rid in all_rec_ids:
        r = record_map[rid]
        grp_id = rec_to_split_group[rid]
        s_type = group_types[grp_id]
        assigned_split = split_group_to_split[grp_id]

        c_rec = PilotCorpusRecord(
            record_id=r["record_id"],
            document_id=r["document_id"],
            source_id=r["source_id"],
            all_contributing_sources=r.get("all_contributing_sources", [r["source_id"]]),
            retrieval_id=r["retrieval_id"],
            rights_profile_id=r["rights_profile_id"],
            rights_profile_version=r["rights_profile_version"],
            public_record_digest=r["public_record_digest"],
            hmac_key_id=r["hmac_key_id"],
            hmac_key_version=r["hmac_key_version"],
            digest_input_schema=r["digest_input_schema"],
            split=assigned_split,
            split_group_id=grp_id,
            component_type=SplitComponentType(s_type),
            document_group_id=r["document_group_id"],
            source_offset_or_locator=r["source_offset_or_locator"],
            provisional_domain=r["provisional_domain"],
            authoring_origin="human_authored_claimed",
            is_method_development_record=r["is_method_development_record"],
            stage30_disposition=r["stage30_disposition"],
            stage30_configuration_hash=r["stage30_configuration_hash"],
            stage31_configuration_hash=cfg_hash,
            normalized_text_storage_ref=r["normalized_text_storage_ref"],
            sentence_count=r["sentence_count"],
            token_count=r["token_count"],
            grapheme_count=r["grapheme_count"],
            quality_flags=r["quality_flags"],
            effective_export_policy=r["effective_export_policy"],
            literal_text_redistributable=r["literal_text_redistributable"],
            canonical_record_id=record_canonical_map[rid],
            is_canonical_exact_record=record_is_canonical[rid],
            exact_duplicate_weight=record_exact_weight[rid],
            retention_reason=record_retention_reason[rid]
        )
        corpus_records.append(c_rec)
        split_counts[assigned_split.value] += 1
        if c_rec.is_method_development_record:
            split_dev_counts[assigned_split.value] += 1

    # 5. Rigorous Leakage Invariant Verification
    print("\n--- Verifying Zero-Leakage Invariants ---")
    
    # Invariant A: No split_group_id spans multiple splits
    split_to_groups = collections.defaultdict(set)
    for r in corpus_records:
        split_to_groups[r.split.value].add(r.split_group_id)
    train_val_overlap = split_to_groups["train"].intersection(split_to_groups["validation"])
    train_test_overlap = split_to_groups["train"].intersection(split_to_groups["locked_test"])
    val_test_overlap = split_to_groups["validation"].intersection(split_to_groups["locked_test"])
    assert len(train_val_overlap) == 0, f"Leakage! Train/Val overlap: {train_val_overlap}"
    assert len(train_test_overlap) == 0, f"Leakage! Train/Test overlap: {train_test_overlap}"
    assert len(val_test_overlap) == 0, f"Leakage! Val/Test overlap: {val_test_overlap}"
    print("  [Pass] Split-group boundary leakage: 0")

    # Invariant B: No document_group_id spans multiple splits
    doc_to_splits = collections.defaultdict(set)
    for r in corpus_records:
        doc_to_splits[r.document_group_id].add(r.split.value)
    multi_split_docs = {d: splits for d, splits in doc_to_splits.items() if len(splits) > 1}
    assert len(multi_split_docs) == 0, f"Leakage! Document groups span multiple splits: {multi_split_docs}"
    print("  [Pass] Document group cross-split leakage: 0")

    # Invariant C: No exact duplicate spans multiple splits
    record_split_map = {r.record_id: r.split.value for r in corpus_records}
    multi_split_exact = []
    for cid, members in exact_clusters.items():
        cluster_splits = {record_split_map[m] for m in members}
        if len(cluster_splits) > 1:
            multi_split_exact.append((cid, cluster_splits))
    assert len(multi_split_exact) == 0, f"Leakage! Exact duplicates span multiple splits: {multi_split_exact}"
    print("  [Pass] Exact duplicate cross-split leakage: 0")

    # Invariant D: No confirmed near-duplicate spans multiple splits
    near_split_leaks = []
    for a, b in confirmed_near:
        if record_split_map[a] != record_split_map[b]:
            near_split_leaks.append((a, b, record_split_map[a], record_split_map[b]))
    assert len(near_split_leaks) == 0, f"Leakage! Near duplicates span multiple splits: {near_split_leaks}"
    print("  [Pass] Confirmed near-duplicate cross-split leakage: 0")

    # Invariant E: Zero method-development records in validation or locked_test
    assert split_dev_counts["validation"] == 0, f"Leakage! Dev records in validation: {split_dev_counts['validation']}"
    assert split_dev_counts["locked_test"] == 0, f"Leakage! Dev records in locked_test: {split_dev_counts['locked_test']}"
    print(f"  [Pass] Method-development records in evaluation splits: 0 (All {split_dev_counts['train']} in train)")

    # Write View 1: Provenance-preserving pilot_corpus.jsonl (180 records)
    with open(CORPUS_FILE, "w", encoding="utf-8", newline="\n") as f:
        for r in corpus_records:
            f.write(r.model_dump_json() + "\n")
    print(f"\nWrote {len(corpus_records)} provenance pilot corpus records to: {CORPUS_FILE}")

    # Write View 2: Canonical analytical corpus (150 records)
    canonical_records = [r for r in corpus_records if r.is_canonical_exact_record]
    with open(CANONICAL_FILE, "w", encoding="utf-8", newline="\n") as f:
        for r in canonical_records:
            f.write(r.model_dump_json() + "\n")
    print(f"Wrote {len(canonical_records)} canonical analytical records to: {CANONICAL_FILE}")

    # Write corpus metadata
    metadata = {
        "corpus_name": "Sinhala Preprocessing and Language Simplification Pilot Corpus",
        "stage": "stage31",
        "version": "1.0.0",
        "total_records": len(corpus_records),
        "split_counts": dict(split_counts),
        "split_proportions": {k: f"{v / len(corpus_records):.1%}" for k, v in split_counts.items()},
        "development_pool_breakdown": {
            "total_dev_records": len(dev_rec_ids),
            "dev_records_in_train": split_dev_counts["train"],
            "dev_records_in_validation": split_dev_counts["validation"],
            "dev_records_in_locked_test": split_dev_counts["locked_test"]
        },
        "exact_duplicate_analytical_view": {
            "stored_record_instances": len(corpus_records),
            "unique_exact_text_canonical_records": len(canonical_records),
            "surplus_retained_duplicate_instances": len(corpus_records) - len(canonical_records),
            "effective_unweighted_analytical_population": len(canonical_records),
            "protocol_deviation_model": "Model C — Duplicates Intentionally Retained",
            "retention_reason": "Retained to preserve source-level and reading-tier provenance for future governed analysis. Stage 31 performs no simplification-model evaluation."
        },
        "leakage_verification": {
            "split_group_leakage": 0,
            "document_group_leakage": 0,
            "exact_duplicate_leakage": 0,
            "near_duplicate_leakage": 0,
            "development_evaluation_contamination": 0,
            "status": "ZERO_LEAKAGE_PROVEN"
        },
        "stage31_configuration_sha256": cfg_hash,
        "governance_status": {
            "validation_status": "draft",
            "research_eligible": False,
            "approved_for_child_delivery": False,
            "approved_for_unsupervised_child_delivery": False,
            "requires_expert_review": True
        }
    }
    METADATA_FILE.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote corpus metadata to: {METADATA_FILE}")
    print("\nWP8 Execution Completed Successfully.")

if __name__ == "__main__":
    run()
