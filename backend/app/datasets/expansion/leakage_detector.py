"""
Stage 20 Leakage Detector Module
Verifies group-aware split containment and enforces strict isolation of the Adaptation Test Set.
"""
from typing import Dict, Any, List, Set

class LeakageDetector:
    def __init__(self, adaptation_test_ids: Set[str] = None):
        self.adaptation_test_ids = adaptation_test_ids or set()

    def check_split_containment(self, splits: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Verifies that all pairs for any given source_item_id or source_group_id reside in only one split.
        """
        group_to_split: Dict[str, str] = {}
        leakage_violations: List[Dict[str, Any]] = []

        for split_name, records in splits.items():
            for r in records:
                group_id = r.get("source_item_id") or r.get("activity_id") or r.get("source_activity_id") or r.get("original_text")
                if not group_id:
                    continue

                if group_id in group_to_split and group_to_split[group_id] != split_name:
                    leakage_violations.append({
                        "group_id": group_id,
                        "primary_split": group_to_split[group_id],
                        "leaked_split": split_name,
                        "record_id": r.get("pair_id") or r.get("activity_id")
                    })
                else:
                    group_to_split[group_id] = split_name

        # Check Adaptation Test Set isolation from training splits
        adaptation_leakage: List[Dict[str, Any]] = []
        train_records = splits.get("development_candidate_train", [])
        for r in train_records:
            act_id = r.get("activity_id") or r.get("source_activity_id")
            if act_id and act_id in self.adaptation_test_ids:
                adaptation_leakage.append({
                    "activity_id": act_id,
                    "split": "development_candidate_train",
                    "reason": "Adaptation Test Set activity leaked into training split"
                })

        is_clean = (len(leakage_violations) == 0 and len(adaptation_leakage) == 0)

        return {
            "is_clean": is_clean,
            "group_leakage_violations": leakage_violations,
            "adaptation_test_leakage": adaptation_leakage,
            "total_groups_isolated": len(group_to_split),
            "status": "passed" if is_clean else "failed"
        }
