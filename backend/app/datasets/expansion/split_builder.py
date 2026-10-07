"""
Stage 20 Group-Aware Split Builder and Candidate Eligibility Gate Module
Enforces candidate eligibility, assigns deterministic group-aware 70/15/15 splits,
and generates the locked test manifest with access protection hashes.
"""
import os
import json
import random
import hashlib
from datetime import datetime
from collections import defaultdict
from typing import Dict, Any, List, Set, Tuple

class SplitBuilder:
    def __init__(self, seed: int = 42, target_ratios: Tuple[float, float, float] = (0.70, 0.15, 0.15), tolerance: float = 0.03):
        self.seed = seed
        self.target_ratios = target_ratios
        self.tolerance = tolerance

    def filter_candidate_eligibility(self, records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Applies the 7-condition Candidate Eligibility Check.
        Returns: (eligible_records, excluded_records)
        """
        eligible = []
        excluded = []

        for r in records:
            # 1. Schema valid
            schema_valid = r.get("schema_version") is not None
            # 2. Quality check passed
            quality_status = r.get("quality_status", "automatic_check_passed")
            quality_passed = quality_status in ["automatic_check_passed", "passed", "valid", "draft"]
            # 3. Rights permitted
            rights = r.get("provenance", {}).get("rights_status", "internal_team_owned") if isinstance(r.get("provenance"), dict) else "internal_team_owned"
            rights_permitted = rights in ["internal_team_owned", "permitted", "team_authored"]
            # 4. Provenance complete
            prov = r.get("provenance")
            prov_complete = bool(prov and (isinstance(prov, dict) and prov.get("created_by") and prov.get("batch_id")))
            # 5. Duplicate status
            dup_status = r.get("duplicate_status", "unique")
            is_unique = dup_status in ["unique", "unique_or_reviewed", None]
            # 6. Unresolved review
            unresolved = r.get("unresolved_review", False)
            # 7. Critical failure
            crit_fail = r.get("critical_failure", False)

            if (schema_valid and quality_passed and rights_permitted and prov_complete and is_unique and not unresolved and not crit_fail):
                eligible.append(r)
            else:
                excluded.append({
                    "record_id": r.get("pair_id") or r.get("source_item_id") or r.get("activity_id"),
                    "reason": "Failed 7-condition candidate eligibility check",
                    "record": r
                })

        return eligible, excluded

    def build_group_aware_splits(self, eligible_records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Partitions records into development_candidate_train (70%), val (15%), test (15%)
        ensuring all records for a source group remain strictly co-located.
        """
        # Group records by source item / group ID
        groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for r in eligible_records:
            gid = r.get("source_item_id") or r.get("activity_id") or r.get("source_activity_id") or r.get("original_text")
            groups[gid].append(r)

        group_keys = list(groups.keys())
        
        # Deterministic shuffle
        rng = random.Random(self.seed)
        rng.shuffle(group_keys)

        total_records = len(eligible_records)
        target_train = int(total_records * self.target_ratios[0])
        target_val = int(total_records * self.target_ratios[1])

        train_records = []
        val_records = []
        test_records = []

        curr_train_count = 0
        curr_val_count = 0

        for gid in group_keys:
            recs = groups[gid]
            count = len(recs)

            if curr_train_count + count <= target_train or (curr_train_count < target_train and curr_val_count >= target_val):
                train_records.extend(recs)
                curr_train_count += count
            elif curr_val_count + count <= target_val:
                val_records.extend(recs)
                curr_val_count += count
            else:
                test_records.extend(recs)

        return {
            "development_candidate_train": train_records,
            "development_candidate_validation": val_records,
            "development_candidate_test": test_records
        }

    def generate_locked_test_manifest(self, test_records: List[Dict[str, Any]], output_path: str, dataset_version: str = "0.2.0") -> Dict[str, Any]:
        """
        Generates the locked test manifest containing ONLY IDs, group IDs, and SHA-256 hashes.
        Strictly excludes raw text or answers.
        """
        manifest_entries = []
        for r in test_records:
            rec_id = r.get("pair_id") or r.get("source_item_id") or r.get("activity_id")
            gid = r.get("source_item_id") or r.get("activity_id")
            # Compute hash of content
            content_str = json.dumps(r, sort_keys=True)
            chash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()

            manifest_entries.append({
                "record_id": rec_id,
                "source_group_id": gid,
                "content_hash_sha256": chash
            })

        locked_manifest = {
            "manifest_type": "locked_test_manifest",
            "dataset_version": dataset_version,
            "split_version": "1.0.0",
            "creation_seed": self.seed,
            "creation_timestamp": datetime.utcnow().isoformat() + "Z",
            "total_test_records": len(manifest_entries),
            "records": manifest_entries
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(locked_manifest, f, indent=2)

        return locked_manifest
