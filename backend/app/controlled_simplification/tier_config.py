"""
Support-tier configuration parameters for Mild, Moderate, and Strong simplification.
"""

from typing import Dict, Any
from pydantic import BaseModel
from app.controlled_simplification.schemas import SupportLevel


class TierConfiguration(BaseModel):
    support_level: SupportLevel
    name: str
    difficult_word_age_offset: int  # Replace if word target_age > content_age + offset
    max_clause_words: int
    split_compound_length_threshold: int
    enable_passive_conversion: bool
    enable_nominalization_unpacking: bool
    enable_step_numbering_multi_action: bool
    repeat_explicit_subjects: bool
    vocabulary_explanation_policy: str  # none | top_difficult | selected | all_complex
    target_fkgl_reduction: float


# Governed parameters for each support tier
TIER_CONFIGURATIONS: Dict[SupportLevel, TierConfiguration] = {
    SupportLevel.MILD: TierConfiguration(
        support_level=SupportLevel.MILD,
        name="Mild Support",
        difficult_word_age_offset=2,
        max_clause_words=15,
        split_compound_length_threshold=18,
        enable_passive_conversion=True,
        enable_nominalization_unpacking=False,
        enable_step_numbering_multi_action=False,
        repeat_explicit_subjects=False,
        vocabulary_explanation_policy="top_difficult",
        target_fkgl_reduction=0.5
    ),
    SupportLevel.MODERATE: TierConfiguration(
        support_level=SupportLevel.MODERATE,
        name="Moderate Support",
        difficult_word_age_offset=0,
        max_clause_words=10,
        split_compound_length_threshold=12,
        enable_passive_conversion=True,
        enable_nominalization_unpacking=True,
        enable_step_numbering_multi_action=True,
        repeat_explicit_subjects=True,
        vocabulary_explanation_policy="selected",
        target_fkgl_reduction=1.2
    ),
    SupportLevel.STRONG: TierConfiguration(
        support_level=SupportLevel.STRONG,
        name="Strong Support",
        difficult_word_age_offset=-1,
        max_clause_words=7,
        split_compound_length_threshold=8,
        enable_passive_conversion=True,
        enable_nominalization_unpacking=True,
        enable_step_numbering_multi_action=True,
        repeat_explicit_subjects=True,
        vocabulary_explanation_policy="all_complex",
        target_fkgl_reduction=2.0
    ),
}


def get_tier_config(level: SupportLevel) -> TierConfiguration:
    """Retrieve governed configuration for a support level."""
    return TIER_CONFIGURATIONS.get(level, TIER_CONFIGURATIONS[SupportLevel.MODERATE])
