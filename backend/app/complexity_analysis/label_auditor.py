"""Label governance, sufficiency gate, and circular leakage audit module."""

from typing import Any, Dict, List, Optional, Set, Tuple
from app.complexity_analysis.schemas import LabelAuditRecord, LabelStatus, DifficultyLabel


class LabelSufficiencyError(Exception):
    """Raised when independently labeled source groups are insufficient for valid CV."""
    pass


class LabelAuditor:
    """Governs label provenance, audits circular leakage, and evaluates label sufficiency."""

    def __init__(self, min_folds_groups: int = 3):
        self.min_folds_groups = min_folds_groups

    def audit_record(
        self,
        text_instance_id: str,
        parent_record_id: str,
        parent_record_type: str,
        source_group_id: str,
        assigned_difficulty: Optional[DifficultyLabel],
        annotator_tier: str,
        provenance_source: str,
        derived_from_rule_heuristic: bool = False,
        reviewer_reference: str = "None (Draft authoring item awaiting expert panel review)",
        reviewer_role: str = "provisional_author",
        annotation_guideline_version: str = "v1.0.0-draft",
        reviewed_at: Optional[str] = None,
        agreement_status: str = "single_author_provisional",
        adjudication_status: str = "pending_expert_adjudication",
    ) -> LabelAuditRecord:
        """Audits a single label and returns an immutable LabelAuditRecord with complete provenance."""
        if not assigned_difficulty or assigned_difficulty not in ("easy", "medium", "hard"):
            label_status: LabelStatus = "missing"
            tier = "none"
        elif derived_from_rule_heuristic:
            label_status = "rule_seeded"
            tier = "heuristic_rule"
        elif annotator_tier == "expert":
            label_status = "expert_verified"
            tier = "expert"
        elif annotator_tier == "reviewer_consensus":
            label_status = "reviewer_consensus"
            tier = "reviewer_consensus"
        elif annotator_tier == "provisional_author":
            label_status = "provisional"
            tier = "provisional_author"
        else:
            label_status = "provisional"
            tier = "provisional_author"

        circular_risk = label_status == "rule_seeded"

        return LabelAuditRecord(
            text_instance_id=text_instance_id,
            parent_record_id=parent_record_id,
            parent_record_type=parent_record_type,
            source_group_id=source_group_id,
            assigned_difficulty=assigned_difficulty,
            label_status=label_status,
            annotator_tier=tier,  # type: ignore
            provenance_source=provenance_source,
            reviewer_reference=reviewer_reference,
            reviewer_role=reviewer_role,
            annotation_guideline_version=annotation_guideline_version,
            reviewed_at=reviewed_at,
            agreement_status=agreement_status,
            adjudication_status=adjudication_status,
            rule_seeded_detected=derived_from_rule_heuristic,
            circular_leakage_risk=circular_risk,
            audit_notes=f"Audited via LabelAuditor (status={label_status})",
        )

    def evaluate_label_sufficiency(
        self,
        records: List[Dict[str, Any]],
        tier_1_only: bool = True,
    ) -> Tuple[bool, int, Dict[DifficultyLabel, int], Optional[str]]:
        """Evaluates whether enough independent source groups exist per class for group-aware CV.

        Returns:
            (is_sufficient, maximum_valid_folds, class_group_counts, message)
        """
        easy_groups: Set[str] = set()
        medium_groups: Set[str] = set()
        hard_groups: Set[str] = set()

        for rec in records:
            if tier_1_only:
                status = rec.get("label_status")
                if status not in ("expert_verified", "reviewer_consensus"):
                    continue

            diff = rec.get("assigned_difficulty") or rec.get("difficulty")
            group_id = rec.get("source_group_id") or rec.get("parent_record_id")

            if not group_id:
                continue

            if diff == "easy":
                easy_groups.add(group_id)
            elif diff == "medium":
                medium_groups.add(group_id)
            elif diff == "hard":
                hard_groups.add(group_id)

        group_counts: Dict[DifficultyLabel, int] = {
            "easy": len(easy_groups),
            "medium": len(medium_groups),
            "hard": len(hard_groups),
        }

        # Check all 3 classes represented
        if group_counts["easy"] == 0 or group_counts["medium"] == 0 or group_counts["hard"] == 0:
            msg = (
                f"Missing class representation in {'Tier 1' if tier_1_only else 'provisional'} labels: "
                f"easy={group_counts['easy']}, medium={group_counts['medium']}, hard={group_counts['hard']}. "
                f"Stage 22 paused for annotation."
            )
            return False, 0, group_counts, msg

        maximum_valid_folds = min(group_counts.values())

        if maximum_valid_folds < self.min_folds_groups:
            msg = (
                f"Insufficient independently labeled groups for {self.min_folds_groups}-fold CV: "
                f"min class-specific source-group count is {maximum_valid_folds} "
                f"(easy={group_counts['easy']}, medium={group_counts['medium']}, hard={group_counts['hard']}). "
                f"Stage 22 paused for annotation."
            )
            return False, maximum_valid_folds, group_counts, msg

        msg = (
            f"Label sufficiency verified ({'Tier 1' if tier_1_only else 'Pilot Level'}): {maximum_valid_folds} valid folds supported "
            f"(easy={group_counts['easy']}, medium={group_counts['medium']}, hard={group_counts['hard']})."
        )
        return True, maximum_valid_folds, group_counts, msg
