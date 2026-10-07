"""
Operation planner that dynamically schedules simplification operations based on target support tier.
"""

from typing import List
from app.controlled_simplification.schemas import (
    AppliedOperation,
    SupportLevel,
    ActionGraph,
    EffectiveProtectionContext
)
from app.controlled_simplification.tier_config import TierConfiguration, get_tier_config


class OperationPlanner:
    """
    Formulates a deterministic sequence of simplification operations tailored to the target support tier.
    """

    def plan_operations(
        self,
        tier_config: TierConfiguration,
        action_graph: ActionGraph,
        effective_protections: EffectiveProtectionContext,
        word_count: int
    ) -> List[AppliedOperation]:
        """
        Produce ordered list of operations to be executed for this request.
        """
        operations: List[AppliedOperation] = []

        # 1. Temporal unrolling (if temporal inversion detected in ActionGraph)
        if action_graph.has_temporal_inversion:
            operations.append(AppliedOperation(
                rule_id="ACT_TEMPORAL_UNROLL",
                type="action_graph",
                description="Reorder chronological sequence"
            ))

        # 2. Syntactic Voice Transformation
        if tier_config.enable_passive_conversion:
            operations.append(AppliedOperation(
                rule_id="SYN_PASSIVE_TO_ACTIVE",
                type="syntactic",
                description="Convert passive voice to active voice"
            ))

        # 3. Nominalization Unpacking (Moderate and Strong)
        if tier_config.enable_nominalization_unpacking:
            operations.append(AppliedOperation(
                rule_id="SYN_NOMINALIZATION_UNPACK",
                type="syntactic",
                description="Unpack nominalizations into simple verbs"
            ))

        # 4. Clause Splitting
        if word_count >= tier_config.split_compound_length_threshold or action_graph.is_multi_step:
            operations.append(AppliedOperation(
                rule_id="SYN_CLAUSE_SPLIT",
                type="syntactic",
                description="Split complex and compound clauses"
            ))
            if tier_config.repeat_explicit_subjects:
                operations.append(AppliedOperation(
                    rule_id="SYN_EXPLICIT_SUBJECT",
                    type="syntactic",
                    description="Re-insert explicit subjects in split clauses"
                ))

        # 5. Lexical Substitution
        operations.append(AppliedOperation(
            rule_id="LEX_SUB_AGE_APPROPRIATE",
            type="lexical",
            description=f"Age-calibrated lexical substitution (offset {tier_config.difficult_word_age_offset})"
        ))

        # 6. Morphological Surface Repair
        operations.append(AppliedOperation(
            rule_id="LEX_MORPH_REPAIR",
            type="lexical",
            description="Repair agreement and morphological inflections"
        ))

        # 7. Action Graph Step Numbering (for multi-step instructions)
        if tier_config.enable_step_numbering_multi_action and action_graph.is_multi_step:
            operations.append(AppliedOperation(
                rule_id="ACT_NUMBERED_STEPS",
                type="action_graph",
                description="Format multi-step actions into numbered atomic lines"
            ))

        # 8. Vocabulary Support Definitions
        if tier_config.vocabulary_explanation_policy != "none":
            operations.append(AppliedOperation(
                rule_id="VOCAB_DEF_ATTACH",
                type="vocabulary_support",
                description=f"Attach vocabulary support definitions ({tier_config.vocabulary_explanation_policy})"
            ))

        return operations
