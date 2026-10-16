"""
Stage 32 Corpus Contract Verifier (WP0)
Reconciles Stage 31 authoritative corpus artifacts:
- canonical_analytical_corpus.jsonl (150 records)
- pilot_corpus.jsonl (180 records)
- corpus_metadata.json
- duplicate clustering and cluster-normalized weight sums
Generates authoritative data/sinhala_lexicon/ledgers/corpus_identity_ledger.json.
"""

import collections
import hashlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CANONICAL_PATH = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "canonical_analytical_corpus.jsonl"
PROVENANCE_PATH = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "pilot_corpus.jsonl"
METADATA_PATH = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "corpus_metadata.json"
LEDGER_DIR = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers"
IDENTITY_LEDGER_PATH = LEDGER_DIR / "corpus_identity_ledger.json"

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def verify_corpus_contract():
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)

    print("--- Verifying Stage 31 Corpus Contract for Stage 32 Ingestion ---")

    # 1. Load canonical records
    canonical_records = []
    canonical_ids = set()
    with open(CANONICAL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            canonical_records.append(rec)
            canonical_ids.add(rec["record_id"])

    assert len(canonical_records) == 150, f"Expected 150 canonical records, got {len(canonical_records)}"
    assert len(canonical_ids) == 150, "Duplicate record_id found in canonical analytical corpus"
    print(f"  [OK] Canonical analytical corpus: {len(canonical_records)} unique records")

    # 2. Load provenance records
    provenance_records = []
    provenance_ids = set()
    canonical_to_provenance_map = collections.defaultdict(list)
    cluster_weights = collections.defaultdict(list)

    with open(PROVENANCE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            provenance_records.append(rec)
            provenance_ids.add(rec["record_id"])
            c_id = rec.get("canonical_record_id")
            assert c_id in canonical_ids, f"Provenance record {rec['record_id']} references unknown canonical_id {c_id}"
            canonical_to_provenance_map[c_id].append(rec["record_id"])
            cluster_weights[c_id].append(float(rec.get("exact_duplicate_weight", 1.0)))

    assert len(provenance_records) == 180, f"Expected 180 provenance records, got {len(provenance_records)}"
    assert len(provenance_ids) == 180, "Duplicate record_id found in provenance corpus"
    print(f"  [OK] Provenance-preserving corpus: {len(provenance_records)} unique records")

    # 3. Verify duplicate weights sum and parity preconditions
    total_provenance_weight = 0.0
    invalid_weights = 0
    mapping_failures = 0

    for c_id in canonical_ids:
        members = canonical_to_provenance_map[c_id]
        if not members:
            mapping_failures += 1
            continue
        cluster_size = len(members)
        expected_weight = 1.0 / cluster_size
        weights = cluster_weights[c_id]
        for w in weights:
            if abs(w - expected_weight) > 1e-6:
                invalid_weights += 1
            total_provenance_weight += w

    print(f"  [OK] Sum of provenance weights: {total_provenance_weight:.6f} (Expected: 150.000000, delta: {abs(total_provenance_weight - 150.0):.8f})")
    assert abs(total_provenance_weight - 150.0) < 1e-4, f"Weight sum mismatch: {total_provenance_weight}"
    assert invalid_weights == 0, f"Found {invalid_weights} invalid duplicate weights"
    assert mapping_failures == 0, f"Found {mapping_failures} canonical mapping failures"

    # 4. Read metadata and development predeclaration
    metadata_bytes = METADATA_PATH.read_bytes()
    metadata_sha = hashlib.sha256(metadata_bytes).hexdigest()
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["total_records"] == 180
    assert meta["exact_duplicate_analytical_view"]["unique_exact_text_canonical_records"] == 150
    assert meta["exact_duplicate_analytical_view"]["effective_unweighted_analytical_population"] == 150
    print("  [OK] Corpus metadata exact analytical view matches 150/180")

    # WP0 Development Population Gate
    predecl_path = PROJECT_ROOT / "data" / "sinhala_external" / "registry" / "method_development_predeclaration.json"
    predecl_sha = compute_sha256(predecl_path)
    with open(predecl_path, "r", encoding="utf-8") as f:
        predecl = json.load(f)

    predecl_units = predecl.get("total_predeclared_development_units", 0)
    meta_dev_breakdown = meta.get("development_pool_breakdown", {})
    meta_dev_total = meta_dev_breakdown.get("total_dev_records", 0)
    meta_dev_train = meta_dev_breakdown.get("dev_records_in_train", 0)
    meta_dev_val = meta_dev_breakdown.get("dev_records_in_validation", 0)
    meta_dev_test = meta_dev_breakdown.get("dev_records_in_locked_test", 0)

    prov_dev_records = [r for r in provenance_records if r.get("is_method_development_record")]
    canon_dev_records = [r for r in canonical_records if r.get("is_method_development_record")]

    # WP0 Abort Gate: abort if disagree on development-population membership or counts
    if len(prov_dev_records) != predecl_units or len(prov_dev_records) != meta_dev_total:
        raise ValueError(
            f"WP0 ABORT GATE TRIGGERED: Development counts disagree! "
            f"Predeclaration: {predecl_units}, Metadata: {meta_dev_total}, Pilot Corpus: {len(prov_dev_records)}"
        )
    if meta_dev_val != 0 or meta_dev_test != 0:
        raise ValueError(
            f"WP0 ABORT GATE TRIGGERED: Development records found in eval splits! Val: {meta_dev_val}, Test: {meta_dev_test}"
        )
    for r in prov_dev_records:
        if r.get("split") != "train":
            raise ValueError(f"WP0 ABORT GATE TRIGGERED: Development record {r['record_id']} is in split '{r.get('split')}', expected 'train'!")

    dev_group_ids = sorted(list(set(r["split_group_id"] for r in prov_dev_records)))
    dev_record_ids = [r["record_id"] for r in prov_dev_records]
    print(f"  [OK] WP0 Development Population Gate: {len(prov_dev_records)} units verified exclusively in train split across {len(dev_group_ids)} groups")

    # 5. Build authoritative identity ledger
    canonical_sha = compute_sha256(CANONICAL_PATH)
    provenance_sha = compute_sha256(PROVENANCE_PATH)

    split_counts = collections.Counter(r["split"] for r in canonical_records)
    source_counts = collections.Counter(r["source_id"] for r in canonical_records)

    ledger_data = {
        "ledger_version": "1.0.0",
        "stage": "stage32",
        "corpus_name": "Sinhala Preprocessing and Language Simplification Pilot Corpus",
        "canonical_analytical_population": {
            "record_count": len(canonical_records),
            "file_sha256": canonical_sha,
            "split_distribution": dict(split_counts),
            "source_distribution": dict(source_counts),
            "unweighted_primary_denominator": 150
        },
        "provenance_preserving_population": {
            "record_count": len(provenance_records),
            "file_sha256": provenance_sha,
            "surplus_duplicate_count": len(provenance_records) - len(canonical_records),
            "sum_of_duplicate_weights": round(total_provenance_weight, 6),
            "cluster_count": len(canonical_ids)
        },
        "development_population_audit": {
            "total_predeclared_units": predecl_units,
            "total_provenance_dev_records": len(prov_dev_records),
            "total_canonical_dev_records": len(canon_dev_records),
            "location": "inside_180_record_corpus",
            "outside_corpus_units": 0,
            "split_membership": "train_only",
            "validation_contamination": meta_dev_val,
            "locked_test_contamination": meta_dev_test,
            "distinct_split_groups_count": len(dev_group_ids),
            "split_group_ids": dev_group_ids,
            "record_ids": dev_record_ids,
            "predeclaration_artifact_sha256": predecl_sha,
            "corpus_metadata_sha256": metadata_sha,
            "wp0_abort_gate_status": "PASSED_ZERO_DISCREPANCY"
        },
        "corpus_metadata_sha256": metadata_sha,
        "contract_status": "RECONCILED_AND_VERIFIED",
        "unaccounted_records": 0
    }

    with open(IDENTITY_LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger_data, f, indent=2, ensure_ascii=False)

    print(f"Authoritative corpus identity ledger generated at: {IDENTITY_LEDGER_PATH}")
    print("=== Stage 31 Corpus Contract Verification: PASSED ===")
    return True

if __name__ == "__main__":
    verify_corpus_contract()
