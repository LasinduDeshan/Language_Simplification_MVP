from typing import Dict, Any, Optional, List
from app.database.models import LearnerProfile

class PersonalizationController:
    """
    Deterministic Personalization Controller for English-First Adaptive Language Support.
    Evaluates learner risk profiles, developmental skill scores, and prior attempt outcomes
    to resolve support levels (mild, moderate, strong) and transparent, explainable reason codes.
    """

    def determine_support_level(
        self,
        learner: LearnerProfile,
        target_attempt_number: int,
        previous_observations: Optional[List[Dict[str, Any]]] = None,
        component_4_recommendation: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Determines support intensity and generates explainable reason codes.
        
        Support Levels:
        - mild: Minimal scaffolding, gentle simplification, conversational tone.
        - moderate: Reduced clauses, vocabulary replacement, focused single-step action.
        - strong: Maximum cognitive offloading, 2-choice/picture cues, explicit visual pointing.
        """
        reason_codes = []

        # 1. Component 4 external recommendation (if provided)
        if component_4_recommendation in ["mild", "moderate", "strong"]:
            base_support = component_4_recommendation
            reason_codes.append(f"component_4_recommendation_{component_4_recommendation}")
        else:
            # 2. Risk profile and developmental baseline assessment
            if learner.risk_support_level == "high":
                base_support = "strong"
                reason_codes.append("base_risk_high")
            elif learner.risk_support_level == "moderate":
                base_support = "moderate"
                reason_codes.append("base_risk_moderate")
            else:
                base_support = "mild"
                reason_codes.append("base_risk_low")

            # 3. Domain score overrides
            # Low vocabulary or grammar scores elevate support
            if learner.vocabulary_score < 45.0:
                reason_codes.append(f"low_vocabulary_score_{int(learner.vocabulary_score)}")
                if base_support == "mild":
                    base_support = "moderate"
            if learner.grammar_score < 45.0:
                reason_codes.append(f"low_grammar_score_{int(learner.grammar_score)}")
                if base_support == "mild":
                    base_support = "moderate"
            if learner.comprehension_score < 45.0:
                reason_codes.append(f"low_comprehension_score_{int(learner.comprehension_score)}")
                if base_support == "mild":
                    base_support = "moderate"

            # Emerging English level necessitates at least moderate support
            if learner.english_level == "emerging":
                reason_codes.append("english_level_emerging")
                if base_support == "mild":
                    base_support = "moderate"
            elif learner.english_level == "developing":
                reason_codes.append("english_level_developing")

        # 4. Previous observation feedback (from earlier attempts in current run)
        if previous_observations:
            for obs in previous_observations:
                code = obs.get("observation_code", "")
                if "two_step" in code:
                    reason_codes.append("step_splitting_required_prior_dropoff")
                    if base_support == "mild":
                        base_support = "moderate"
                elif "vocabulary" in code:
                    reason_codes.append("vocabulary_scaffolding_prior_difficulty")
                elif "preposition" in code or "copula" in code:
                    reason_codes.append(f"syntax_scaffold_{code}")

        # 5. Progressive Attempt Escalation
        final_support = base_support
        if target_attempt_number == 1:
            reason_codes.append("attempt_1_initial_instruction")
        elif target_attempt_number == 2:
            reason_codes.append("attempt_2_retry_escalation")
            if base_support == "mild":
                final_support = "moderate"
            else:
                final_support = "strong"
        elif target_attempt_number >= 3:
            reason_codes.append("attempt_3_maximum_support")
            final_support = "strong"

        return {
            "support_level": final_support,
            "base_support": base_support,
            "target_attempt_number": target_attempt_number,
            "reason_codes": reason_codes
        }

personalization_controller = PersonalizationController()
