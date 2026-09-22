from typing import Dict, Any, Optional, List
from app.database.models import LearnerProfile, Task

class PersonalizationController:
    """
    Deterministic Personalization Controller for English Adaptive Language Support.
    Evaluates learner risk profiles, task-specific developmental skill scores,
    and initial-level-dependent retry scaffolding matrices.
    """

    def calculate_initial_support(
        self,
        learner: LearnerProfile,
        task: Optional[Task] = None
    ) -> Dict[str, Any]:
        """
        Determines the deterministic initial support level for Attempt 1.
        
        Rules:
        - High risk -> Strong
        - Moderate risk -> Moderate
        - Low risk -> Mild
        - Relevant skill score < 40 -> Upgrade to Strong
        - Relevant skill score 40-59 -> At least Moderate
        - Relevant skill score >= 60 -> Retain risk-based baseline
        - Task minimum age > Learner age -> Flag age mismatch
        """
        reason_codes = []

        # 1. Baseline risk level
        risk = (learner.risk_support_level or "moderate").lower()
        if risk == "high":
            base_support = "strong"
            reason_codes.append("risk_level_high")
        elif risk == "low":
            base_support = "mild"
            reason_codes.append("risk_level_low")
        else:
            base_support = "moderate"
            reason_codes.append("risk_level_moderate")

        # 2. Determine relevant skill score from task category
        category = getattr(task, "category", "vocabulary") if task else "vocabulary"
        relevant_score = 50.0
        score_name = "general"

        if category == "vocabulary":
            relevant_score = learner.vocabulary_score
            score_name = "vocabulary"
        elif category == "grammar":
            relevant_score = learner.grammar_score
            score_name = "grammar"
        elif category == "comprehension":
            relevant_score = learner.comprehension_score
            score_name = "comprehension"
        elif category == "sentence_and_instruction":
            relevant_score = learner.comprehension_score
            score_name = "comprehension"
            # Secondary check on grammar for instruction tasks
            if learner.grammar_score < 40.0:
                reason_codes.append("secondary_grammar_score_below_40")
                base_support = "strong"

        # 3. Score-based adjustments
        if relevant_score < 40.0:
            base_support = "strong"
            reason_codes.append(f"{score_name}_score_below_40")
        elif 40.0 <= relevant_score < 60.0:
            if base_support == "mild":
                base_support = "moderate"
                reason_codes.append(f"{score_name}_score_40_to_59_upgrade_to_moderate")
        else:
            reason_codes.append(f"{score_name}_score_60_or_above_retain_baseline")

        # 4. Age suitability check
        if task and hasattr(task, "minimum_age") and task.minimum_age:
            if task.minimum_age > learner.age:
                reason_codes.append("task_above_learner_age_requires_monitoring")

        return {
            "initial_support_level": base_support,
            "support_decision_reasons": reason_codes
        }

    def get_scaffolding_for_attempt(
        self,
        initial_support_level: str,
        target_attempt_number: int
    ) -> Dict[str, Any]:
        """
        Resolves the scaffolding strategy, support level, and assistance level
        based on the initial support level and current attempt number.
        """
        init_level = (initial_support_level or "moderate").lower()
        attempt_num = min(max(target_attempt_number, 1), 3)

        if init_level == "mild":
            if attempt_num == 1:
                return {
                    "support_level": "mild",
                    "adaptation_strategy": "mild_child_friendly",
                    "assistance_level": "independent",
                    "visual_cues": [],
                    "reason_codes": ["attempt_1_mild_baseline"]
                }
            elif attempt_num == 2:
                return {
                    "support_level": "moderate",
                    "adaptation_strategy": "moderate_scaffold",
                    "assistance_level": "prompted",
                    "visual_cues": ["highlight_key_terms"],
                    "reason_codes": ["attempt_2_mild_to_moderate_escalation"]
                }
            else:
                return {
                    "support_level": "strong",
                    "adaptation_strategy": "strong_scaffold",
                    "assistance_level": "visually_supported",
                    "visual_cues": ["binary_choice_focus", "highlight_key_terms"],
                    "reason_codes": ["attempt_3_mild_to_strong_escalation"]
                }

        elif init_level == "moderate":
            if attempt_num == 1:
                return {
                    "support_level": "moderate",
                    "adaptation_strategy": "moderate_child_friendly",
                    "assistance_level": "independent",
                    "visual_cues": ["subtle_focus_glow"],
                    "reason_codes": ["attempt_1_moderate_baseline"]
                }
            elif attempt_num == 2:
                return {
                    "support_level": "strong",
                    "adaptation_strategy": "strong_scaffold",
                    "assistance_level": "prompted",
                    "visual_cues": ["binary_choice_focus", "item_highlight"],
                    "reason_codes": ["attempt_2_moderate_to_strong_escalation"]
                }
            else:
                return {
                    "support_level": "strong",
                    "adaptation_strategy": "strong_decomposed_step",
                    "assistance_level": "visually_supported",
                    "visual_cues": ["step_by_step_pointer", "decomposed_single_action"],
                    "reason_codes": ["attempt_3_moderate_decomposed_step"]
                }

        else:  # Strong initial level
            if attempt_num == 1:
                return {
                    "support_level": "strong",
                    "adaptation_strategy": "strong_child_friendly",
                    "assistance_level": "independent",
                    "visual_cues": ["high_contrast_pointer", "simplified_visual"],
                    "reason_codes": ["attempt_1_strong_baseline"]
                }
            elif attempt_num == 2:
                return {
                    "support_level": "strong",
                    "adaptation_strategy": "strong_visual_cue",
                    "assistance_level": "prompted",
                    "visual_cues": ["visual_example_callout", "isolated_target_frame"],
                    "reason_codes": ["attempt_2_strong_visual_example_cue"]
                }
            else:
                return {
                    "support_level": "strong",
                    "adaptation_strategy": "strong_adult_modelling",
                    "assistance_level": "modelled",
                    "visual_cues": ["adult_modelling_prompt", "one_step_demonstration"],
                    "reason_codes": ["attempt_3_strong_adult_modelling"]
                }

    # Backward compatibility method
    def determine_support_level(
        self,
        learner: LearnerProfile,
        target_attempt_number: int,
        previous_observations: Optional[List[Dict[str, Any]]] = None,
        component_4_recommendation: Optional[str] = None
    ) -> Dict[str, Any]:
        init_res = self.calculate_initial_support(learner)
        scaffolding = self.get_scaffolding_for_attempt(
            initial_support_level=init_res["initial_support_level"],
            target_attempt_number=target_attempt_number
        )
        legacy_reasons = []
        risk = (learner.risk_support_level or "moderate").lower()
        if risk == "high":
            legacy_reasons.append("base_risk_high")
        elif risk == "low":
            legacy_reasons.append("base_risk_low")
        else:
            legacy_reasons.append("base_risk_moderate")

        if (learner.vocabulary_score or 50) < 45:
            legacy_reasons.append("low_vocabulary_score")
        if (learner.grammar_score or 50) < 45:
            legacy_reasons.append("low_grammar_score")
        if (learner.english_level or "").lower() == "emerging":
            legacy_reasons.append("english_level_emerging")

        if target_attempt_number == 2:
            legacy_reasons.append("attempt_2_retry_escalation")
        elif target_attempt_number == 3:
            legacy_reasons.append("attempt_3_maximum_support")

        return {
            "support_level": scaffolding["support_level"],
            "base_support": init_res["initial_support_level"],
            "target_attempt_number": target_attempt_number,
            "adaptation_strategy": scaffolding["adaptation_strategy"],
            "assistance_level": scaffolding["assistance_level"],
            "reason_codes": list(set(init_res["support_decision_reasons"] + scaffolding["reason_codes"] + legacy_reasons))
        }

personalization_controller = PersonalizationController()
