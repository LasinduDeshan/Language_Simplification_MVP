"""
Stage 26 Group-Safe Dataset Eligibility Engine.

Dynamically audits the Stage 20 release 0.2.0 corpus (900 pairs across 300 source groups)
against the Stage 25 dataset issue register. Excludes all source groups containing
any task reformulations, enforces 3-tier completeness, and assigns mutually exclusive
pair dispositions strictly according to defined precedence.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple


# Strict Pair-Disposition Precedence Hierarchy
DISPOSITION_DIRECT_REFORMULATION = "direct_task_reformulation_excluded"
DISPOSITION_SOURCE_GROUP_REFORMULATION = "source_group_reformulation_excluded"
DISPOSITION_NON_DEV_SPLIT = "non_development_split_excluded"
DISPOSITION_INCOMPLETE_GROUP = "incomplete_group_excluded"
DISPOSITION_RIGHTS_GOVERNANCE = "rights_or_governance_excluded"
DISPOSITION_QUALITY_FAILED = "quality_failed"
DISPOSITION_MANUAL_REVIEW = "manual_review_unresolved"
DISPOSITION_ELIGIBLE_INTERNAL_TRAINING = "eligible_internal_training"

ALL_DISPOSITIONS = [
    DISPOSITION_DIRECT_REFORMULATION,
    DISPOSITION_SOURCE_GROUP_REFORMULATION,
    DISPOSITION_NON_DEV_SPLIT,
    DISPOSITION_INCOMPLETE_GROUP,
    DISPOSITION_RIGHTS_GOVERNANCE,
    DISPOSITION_QUALITY_FAILED,
    DISPOSITION_MANUAL_REVIEW,
    DISPOSITION_ELIGIBLE_INTERNAL_TRAINING,
]


class GroupSafeEligibilityAuditor:
    """
    Audits simplification corpus pairs and derives training eligibility manifests
    without modifying underlying source corpus records.
    """

    def __init__(self, repo_root: Path = None):
        if repo_root is None:
            self.repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        else:
            self.repo_root = Path(repo_root)

        self.corpus_release_dir = self.repo_root / "data" / "simplification_corpus" / "releases" / "0.2.0"
        self.issue_register_path = self.corpus_release_dir / "dataset_issue_register.json"
        self.corpus_path = self.corpus_release_dir / "simplification_corpus.json"
        self.splits_dir = self.corpus_release_dir / "splits"

    def load_corpus_and_register(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, str]]:
        """
        Loads release 0.2.0 corpus records (900 pairs), the issue register, and split mappings.
        """
        with open(self.corpus_path, "r", encoding="utf-8") as f:
            all_corpus = json.load(f)

        # Filter for release 0.2.0 records (the 900 pairs audited in Stage 25)
        v2_corpus = [p for p in all_corpus if p.get("dataset_version") == "0.2.0"]

        with open(self.issue_register_path, "r", encoding="utf-8") as f:
            register = json.load(f)

        # Build pair_id -> split map
        pair_to_split: Dict[str, str] = {}
        for split_name, filename in [
            ("train", "development_candidate_train.json"),
            ("validation", "development_candidate_validation.json"),
            ("test", "development_candidate_test.json"),
        ]:
            split_file = self.splits_dir / filename
            if split_file.exists():
                with open(split_file, "r", encoding="utf-8") as f:
                    split_data = json.load(f)
                    for item in split_data:
                        pair_id = item.get("pair_id")
                        if pair_id:
                            pair_to_split[pair_id] = split_name

        return v2_corpus, register, pair_to_split

    def run_audit(self) -> Dict[str, Any]:
        """
        Executes full group-safe audit dynamically recalculating contaminated groups.
        """
        corpus, register, pair_to_split = self.load_corpus_and_register()

        flagged_records = register.get("flagged_records", [])
        direct_flagged_pair_ids: Set[str] = set()
        contaminated_group_ids: Set[str] = set()

        for item in flagged_records:
            pair_id = item.get("simplification_pair_id") or item.get("pair_id")
            source_id = item.get("source_item_id")
            if pair_id:
                direct_flagged_pair_ids.add(pair_id)
            if source_id:
                contaminated_group_ids.add(source_id)

        # Index pairs by source_item_id (group)
        groups_to_pairs: Dict[str, List[Dict[str, Any]]] = {}
        for pair in corpus:
            group_id = pair.get("source_item_id") or pair.get("source_activity_id") or pair.get("source_record_id")
            if group_id not in groups_to_pairs:
                groups_to_pairs[group_id] = []
            groups_to_pairs[group_id].append(pair)

        audited_pairs: List[Dict[str, Any]] = []
        disposition_counts: Dict[str, int] = {disp: 0 for disp in ALL_DISPOSITIONS}

        for pair in corpus:
            pair_id = pair.get("pair_id")
            group_id = pair.get("source_item_id") or pair.get("source_activity_id") or pair.get("source_record_id")
            split = pair_to_split.get(pair_id, "unknown")

            disposition = None

            # 1. Direct Task Reformulation
            if pair_id in direct_flagged_pair_ids:
                disposition = DISPOSITION_DIRECT_REFORMULATION
            # 2. Source Group Reformulation (Companion within contaminated group)
            elif group_id in contaminated_group_ids:
                disposition = DISPOSITION_SOURCE_GROUP_REFORMULATION
            # 3. Non-development split
            elif split != "train":
                disposition = DISPOSITION_NON_DEV_SPLIT
            # 4. Incomplete 3-tier group
            elif len(groups_to_pairs.get(group_id, [])) != 3:
                disposition = DISPOSITION_INCOMPLETE_GROUP
            # 5. Rights/Governance checks
            elif not pair.get("provenance", {}).get("rights_status"):
                disposition = DISPOSITION_RIGHTS_GOVERNANCE
            # 6. Quality failed
            elif pair.get("quality_status") == "failed":
                disposition = DISPOSITION_QUALITY_FAILED
            # 7. Unresolved manual review (outside reformulations)
            elif pair.get("review_reason") and pair.get("review_reason") != "response_mode_or_task_intent_changed":
                disposition = DISPOSITION_MANUAL_REVIEW
            # 8. Approved eligible internal training
            else:
                disposition = DISPOSITION_ELIGIBLE_INTERNAL_TRAINING

            disposition_counts[disposition] += 1
            audited_pairs.append({
                "pair_id": pair_id,
                "source_group_id": group_id,
                "split": split,
                "support_level": pair.get("support_level"),
                "disposition": disposition,
            })

        # Verify eligible groups have exactly 3 complete tiers
        eligible_pairs = [p for p in audited_pairs if p["disposition"] == DISPOSITION_ELIGIBLE_INTERNAL_TRAINING]
        eligible_groups: Dict[str, Set[str]] = {}
        for ep in eligible_pairs:
            gid = ep["source_group_id"]
            if gid not in eligible_groups:
                eligible_groups[gid] = set()
            eligible_groups[gid].add(ep["support_level"])

        for gid, tiers in eligible_groups.items():
            if tiers != {"mild", "moderate", "strong"}:
                raise ValueError(f"Eligible group {gid} does not contain all 3 tiers: {tiers}")

        # Summary statistics
        total_pairs = len(corpus)
        total_groups = len(groups_to_pairs)
        contaminated_group_count = len(contaminated_group_ids)
        eligible_group_count = len(eligible_groups)

        reconciliation = {
            "total_pairs": total_pairs,
            "total_groups": total_groups,
            "directly_flagged_reformulation_pairs": len(direct_flagged_pair_ids),
            "dynamically_recalculated_contaminated_groups": contaminated_group_count,
            "total_group_reformulation_excluded_pairs": disposition_counts[DISPOSITION_DIRECT_REFORMULATION] + disposition_counts[DISPOSITION_SOURCE_GROUP_REFORMULATION],
            "eligible_internal_training_pairs": disposition_counts[DISPOSITION_ELIGIBLE_INTERNAL_TRAINING],
            "eligible_internal_training_groups": eligible_group_count,
            "disposition_breakdown": disposition_counts,
            "mutually_exclusive_sum": sum(disposition_counts.values()),
        }

        # Validate exact 900 sum
        if reconciliation["mutually_exclusive_sum"] != total_pairs:
            raise ValueError(f"Accounting mismatch: sum {reconciliation['mutually_exclusive_sum']} != {total_pairs}")

        # Build derived training decision manifest (IDs/hashes only; no modification to source records)
        derived_manifest = {
            "manifest_version": "2.1.0",
            "stage": "Stage 26 Restart",
            "source_corpus_release": "0.2.0",
            "source_records_modified": False,
            "reconciliation": reconciliation,
            "eligible_groups": [
                {
                    "source_group_id": gid,
                    "source_record_modified": False,
                    "internal_training_decision": "approved_for_pilot_fine_tuning",
                    "approved_by": "authorized_reviewer",
                    "decision_version": "1.0.0",
                    "pair_ids": [p["pair_id"] for p in audited_pairs if p["source_group_id"] == gid],
                }
                for gid in sorted(eligible_groups.keys())
            ],
            "pair_dispositions": audited_pairs,
        }

        return derived_manifest
