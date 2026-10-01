"""
Progressive retry and scaffolding adapter.
Escalates educational support across successive attempts without modifying clinical profiles.
"""

from typing import Tuple, Dict, Any
from app.controlled_simplification.schemas import (
    SupportLevel,
    SupportLevelSource,
    ScaffoldingMetadata,
    LearnerProfileContext
)


class RetryAdapter:
    """
    Manages progressive scaffolding escalation across successive task attempts.
    """

    @staticmethod
    def get_scaffolding_metadata(
        attempt_number: int,
        applied_tier: SupportLevel
    ) -> ScaffoldingMetadata:
        """
        Determines hint flags and adult escalation status based on attempt count.
        """
        if attempt_number <= 1:
            return ScaffoldingMetadata(
                attempt_number=1,
                visual_hint_flag=False,
                audio_hint_flag=False,
                requires_adult_escalation=False
            )
        elif attempt_number == 2:
            return ScaffoldingMetadata(
                attempt_number=2,
                visual_hint_flag=True,
                audio_hint_flag=False,
                requires_adult_escalation=False
            )
        elif attempt_number == 3:
            return ScaffoldingMetadata(
                attempt_number=3,
                visual_hint_flag=True,
                audio_hint_flag=True,
                requires_adult_escalation=False
            )
        else:
            # 4 or more attempts: halt automated escalation and request adult support
            return ScaffoldingMetadata(
                attempt_number=attempt_number,
                visual_hint_flag=True,
                audio_hint_flag=True,
                requires_adult_escalation=True
            )
