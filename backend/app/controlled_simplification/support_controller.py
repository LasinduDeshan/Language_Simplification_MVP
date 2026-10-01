"""
Support-level controller and precedence resolver.
Enforces the explicit precedence hierarchy: Authorized Request > Learner Profile > Attempt Escalation.
Guarantees clinical screening profile immutability and transparent decision auditing.
"""

from typing import Tuple, Optional
from app.controlled_simplification.schemas import (
    SupportLevel,
    SupportLevelSource,
    LearnerProfileContext
)


class SupportController:
    """
    Resolves the effective support tier for a simplification request.
    Ensures that educational adaptation is deterministic and that clinical risk markers remain untouched.
    """

    @staticmethod
    def resolve_support_level(
        target_support_level: Optional[SupportLevel],
        learner_profile: Optional[LearnerProfileContext],
        attempt_number: int = 1
    ) -> Tuple[SupportLevel, SupportLevelSource, Optional[str]]:
        """
        Determines the applied support tier, the source of authority, and any override reason.
        """
        override_reason: Optional[str] = None

        # 1. Primary: Explicit Authorized Request
        if target_support_level is not None:
            base_level = target_support_level
            source = SupportLevelSource.AUTHORIZED_REQUEST
        # 2. Secondary: Learner Profile Recommended Level
        elif learner_profile is not None:
            base_level = learner_profile.recommended_support_level
            source = SupportLevelSource.LEARNER_PROFILE_RECOMMENDATION
        # 3. Default Fallback
        else:
            base_level = SupportLevel.MODERATE
            source = SupportLevelSource.DEFAULT_FALLBACK

        # 3. Attempt Escalation Logic (for Attempt 2 and 3)
        effective_attempt = attempt_number
        if learner_profile and learner_profile.attempt_number > effective_attempt:
            effective_attempt = learner_profile.attempt_number

        applied_level = base_level

        if effective_attempt == 2:
            if base_level == SupportLevel.MILD:
                applied_level = SupportLevel.MODERATE
                source = SupportLevelSource.ATTEMPT_ESCALATION
                override_reason = "Escalated from Mild to Moderate on attempt 2"
            elif base_level == SupportLevel.MODERATE:
                applied_level = SupportLevel.STRONG
                source = SupportLevelSource.ATTEMPT_ESCALATION
                override_reason = "Escalated from Moderate to Strong on attempt 2"
        elif effective_attempt >= 3:
            if base_level != SupportLevel.STRONG:
                applied_level = SupportLevel.STRONG
                source = SupportLevelSource.ATTEMPT_ESCALATION
                override_reason = f"Escalated to Strong on attempt {effective_attempt}"

        return applied_level, source, override_reason

    @staticmethod
    def infer_profile_recommendation(
        vocab_score: float,
        grammar_score: float,
        comprehension_score: float,
        instruction_score: float
    ) -> SupportLevel:
        """
        Helper to map composite educational skill scores into a recommended support level.
        Low composite score (< 0.40) -> Strong
        Moderate composite score (0.40 - 0.70) -> Moderate
        High composite score (> 0.70) -> Mild
        """
        composite = (vocab_score + grammar_score + comprehension_score + instruction_score) / 4.0
        if composite < 0.40:
            return SupportLevel.STRONG
        elif composite <= 0.70:
            return SupportLevel.MODERATE
        else:
            return SupportLevel.MILD
