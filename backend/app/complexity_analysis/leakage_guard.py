"""Group-aware and text-hash anti-leakage verification module for Stage 22."""

from typing import Any, Dict, List, Set, Tuple


class LeakageGuard:
    """Verifies that splits maintain zero group-level, text-hash, or locked-test leakage."""

    @staticmethod
    def check_group_leakage(
        train_records: List[Dict[str, Any]],
        val_records: List[Dict[str, Any]],
    ) -> Tuple[bool, Set[str]]:
        """Verifies 0 overlap in source_group_id between train and val records."""
        train_groups = {
            r.get("source_group_id") or r.get("parent_record_id")
            for r in train_records
            if r.get("source_group_id") or r.get("parent_record_id")
        }
        val_groups = {
            r.get("source_group_id") or r.get("parent_record_id")
            for r in val_records
            if r.get("source_group_id") or r.get("parent_record_id")
        }

        overlapping = train_groups.intersection(val_groups)
        return len(overlapping) == 0, overlapping

    @staticmethod
    def check_hash_leakage(
        train_records: List[Dict[str, Any]],
        val_records: List[Dict[str, Any]],
    ) -> Tuple[bool, Set[str]]:
        """Verifies 0 overlap in exact normalized text_hash between train and val records."""
        train_hashes = {
            r["text_hash"]
            for r in train_records
            if "text_hash" in r and r["text_hash"] != "LOCKED_TEST_HASH"
        }
        val_hashes = {
            r["text_hash"]
            for r in val_records
            if "text_hash" in r and r["text_hash"] != "LOCKED_TEST_HASH"
        }

        overlapping = train_hashes.intersection(val_hashes)
        return len(overlapping) == 0, overlapping

    @staticmethod
    def check_locked_test_quarantine(
        records: List[Dict[str, Any]],
    ) -> Tuple[bool, List[str]]:
        """Verifies that no record in the provided list contains locked test items."""
        violations = []
        for r in records:
            if r.get("dataset_split") == "development_candidate_test":
                violations.append(f"Locked test instance present: {r.get('text_instance_id')}")
            if r.get("text_hash") == "LOCKED_TEST_HASH":
                violations.append(f"Locked test hash present: {r.get('text_instance_id')}")
        return len(violations) == 0, violations
