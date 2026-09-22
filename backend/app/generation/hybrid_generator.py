from typing import Dict, Any, Optional, List
from app.generation.base import BaseInstructionGenerator
from app.generation.llm_generator import llm_generator
from app.generation.rule_generator import rule_generator
from app.validation.validator import adaptation_validator
from app.database.models import Task, LearnerProfile, Attempt

class HybridInstructionGenerator(BaseInstructionGenerator):
    """
    Hybrid instruction generator.
    Attempts LLM generation first, passes candidate through AdaptationValidator.
    If LLM output passes: returns hybrid LLM output.
    If LLM output fails (e.g. answer leakage, excessive word length):
    automatically falls back to deterministic RuleGenerator, preserving the
    rejected candidate for auditability.
    """

    def generate(
        self,
        task: Task,
        learner: LearnerProfile,
        target_attempt_number: int,
        support_level: str,
        previous_attempt: Optional[Attempt] = None,
        previous_observations: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        # 1. Try LLM Generation
        try:
            llm_candidate = llm_generator.generate(
                task=task,
                learner=learner,
                target_attempt_number=target_attempt_number,
                support_level=support_level,
                previous_attempt=previous_attempt,
                previous_observations=previous_observations
            )
        except Exception as e:
            print(f"[HybridGenerator] LLM generation failed with exception ({e}); triggering safe rule fallback.")
            llm_candidate = None

        # 2. Validate Candidate via AdaptationValidator
        if llm_candidate:
            val_eval = adaptation_validator.validate_candidate(task, llm_candidate, learner)
            if val_eval["status"] == "approved":
                llm_candidate["generation_method"] = "hybrid"
                llm_candidate["reason_codes"] = list(dict.fromkeys(
                    llm_candidate.get("reason_codes", []) + ["hybrid_llm_verified_safe"]
                ))
                return llm_candidate
            else:
                # LLM Candidate was REJECTED by validator
                # Generate safe deterministic rule fallback
                rule_fallback = rule_generator.generate(
                    task=task,
                    learner=learner,
                    target_attempt_number=target_attempt_number,
                    support_level=support_level,
                    previous_attempt=previous_attempt,
                    previous_observations=previous_observations
                )
                rule_fallback["generation_method"] = "fallback"
                rule_fallback["provider"] = "rule_fallback"
                rule_fallback["model_name"] = "hybrid_safe_fallback"
                rule_fallback["reason_codes"] = list(dict.fromkeys(
                    rule_fallback.get("reason_codes", []) + [
                        "hybrid_llm_candidate_rejected",
                        "safe_rule_fallback_activated"
                    ]
                ))
                # Attach rejected candidate metadata for multi-sequence persistence
                rule_fallback["rejected_candidate"] = llm_candidate
                rule_fallback["rejection_reasons"] = val_eval["failure_reasons"]
                return rule_fallback

        # If LLM threw exception, fallback to rule
        rule_fallback = rule_generator.generate(
            task=task,
            learner=learner,
            target_attempt_number=target_attempt_number,
            support_level=support_level,
            previous_attempt=previous_attempt,
            previous_observations=previous_observations
        )
        rule_fallback["generation_method"] = "fallback"
        rule_fallback["reason_codes"] = list(dict.fromkeys(
            rule_fallback.get("reason_codes", []) + ["llm_exception_rule_fallback"]
        ))
        return rule_fallback

hybrid_generator = HybridInstructionGenerator()
