"""
Adaptation Decision Service — Risk-Informed and Performance-Adaptive Instruction Correction
Component: Component 3 — AI/NLP-Based Language Simplification
Target languages: English (en) and Sinhala (si, si-LK)

Principle:
- Component 1: Produces experimental screening-support signal.
- Component 4: Recommends initial support level based on risk, history, and developmental metrics.
- Component 3: Converts recommendation into English or Sinhala instruction and validates output.
- Risk influences the initial support starting point.
- Later attempts respond strictly to observed performance and error evidence.
- Minimal safe instructions declare governed reuse rather than unnecessary text churn.
"""

import json
import os
import unicodedata
from typing import Dict, Any, Optional, List

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "personalization", "risk_support_map.json")

DEFAULT_LADDER = [
    "ORIGINAL_BASELINE",
    "MILD_SUPPORT",
    "MODERATE_SUPPORT",
    "STRONG_SCAFFOLD",
    "STRONG_DECOMPOSED_STEP",
    "UNCHANGED_REUSE"
]

DEFAULT_INITIAL_MAP = {
    "LOW": "ORIGINAL_BASELINE",
    "MODERATE": "MILD_SUPPORT",
    "HIGH": "STRONG_SCAFFOLD"
}

def normalize_text_nfc(text: Optional[str]) -> str:
    """Normalize text using Unicode NFC format for reliable linguistic comparison."""
    if not text:
        return ""
    return unicodedata.normalize("NFC", text.strip())


class AdaptationDecisionService:
    def __init__(self, config_path: str = CONFIG_PATH):
        self.config_path = config_path
        self._load_config()

    def _load_config(self) -> None:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.mapping_version = data.get("mapping_version", "risk-support-map:v1")
                    self.initial_strategy_by_support = data.get("initial_strategy_by_support", DEFAULT_INITIAL_MAP)
                    self.strategy_ladder = data.get("strategy_ladder", DEFAULT_LADDER)
                    self.expert_validated = data.get("expert_validated", False)
                    return
            except Exception:
                pass
        self.mapping_version = "risk-support-map:v1"
        self.initial_strategy_by_support = DEFAULT_INITIAL_MAP
        self.strategy_ladder = DEFAULT_LADDER
        self.expert_validated = False

    def select_initial_strategy(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determines the Component 3 initial strategy from Component 4 support recommendation.
        Low -> ORIGINAL_BASELINE
        Moderate -> MILD_SUPPORT
        High -> STRONG_SCAFFOLD
        """
        raw_level = (
            recommendation.get("recommended_support_level")
            or recommendation.get("support_level")
            or recommendation.get("risk_support_level")
            or "MODERATE"
        )
        clean_level = str(raw_level).upper().strip()

        # Map mild -> LOW, moderate -> MODERATE, strong -> HIGH
        if clean_level in ["MILD", "LOW"]:
            support_enum = "LOW"
        elif clean_level in ["STRONG", "HIGH", "CRITICAL"]:
            support_enum = "HIGH"
        else:
            support_enum = "MODERATE"

        initial_strategy = self.initial_strategy_by_support.get(support_enum, "MILD_SUPPORT")

        reason_codes = [
            f"INITIAL_SUPPORT_{support_enum}",
            f"STARTING_STRATEGY_{initial_strategy}"
        ]

        if recommendation.get("reason_codes"):
            for rc in recommendation["reason_codes"]:
                if rc not in reason_codes:
                    reason_codes.append(rc)

        return {
            "mapping_version": self.mapping_version,
            "recommended_support_level": support_enum,
            "strategy_code": initial_strategy,
            "adaptation_strategy": initial_strategy.lower(),
            "reason_codes": reason_codes,
            "source_recommendation_id": recommendation.get("source_recommendation_id"),
            "source_screening_result_id": recommendation.get("source_screening_result_id"),
            "expert_validated": self.expert_validated,
            "approved_for_child_delivery": False
        }

    def select_next_strategy(
        self,
        current_attempt: Any,
        response_evidence: Dict[str, Any],
        activity: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculates next strategy based on learner performance, errors, and timing.
        
        State transitions:
        - Correct and timely: Retain or reduce support / activity completed.
        - Correct but slow: Retain current support level.
        - First incorrect response: Increase support by one governed level.
        - Repeated incorrect response: Use decomposed steps and/or visual choices.
        - No response / timeout: Repeat once with additional modality support, or escalate.
        - Minimal safe wording reached: Retain wording and declare governed reuse.
        """
        curr_strategy = (
            getattr(current_attempt, "adaptation_strategy", None)
            or getattr(current_attempt, "strategy_code", None)
            or "ORIGINAL_BASELINE"
        ).upper()

        # Normalize strategy to ladder code
        strat_key = self._normalize_strategy_key(curr_strategy)

        # Extract evidence
        is_correct = bool(response_evidence.get("correct"))
        response_time_ms = int(response_evidence.get("response_time_ms", 0) or 0)
        expected_time_ms = int(response_evidence.get("expected_time_ms", 15000) or 15000)
        is_slow = response_time_ms > expected_time_ms
        is_timeout = bool(response_evidence.get("timeout")) or response_evidence.get("completion_status") in ["no_response", "timeout", "skipped"]
        previous_errors = int(response_evidence.get("previous_errors", 0) or 0)
        total_errors = previous_errors + (0 if is_correct else 1)

        reason_codes: List[str] = []
        additional_support: List[str] = []

        # Current instruction text check for minimal safe wording
        current_instruction = (
            getattr(current_attempt, "presented_instruction", "")
            or getattr(current_attempt, "instruction_shown", "")
            or ""
        )
        is_minimal = self.detect_minimal_safe_instruction(current_instruction, activity)

        # Evaluate transitions
        if is_correct:
            if not is_slow:
                # Correct and timely
                reason_codes.append("CORRECT_AND_TIMELY")
                # When correct, maintain or complete
                next_strat = strat_key
                action = "complete_or_maintain"
            else:
                # Correct but slow
                reason_codes.append("CORRECT_BUT_SLOW_RESPONSE")
                next_strat = strat_key
                action = "maintain"
        elif is_timeout:
            reason_codes.append("TIMEOUT_OR_NO_RESPONSE")
            additional_support.append("EXTENDED_RESPONSE_TIME")
            additional_support.append("AUDIO_PROMPT_REPEAT")
            if is_minimal or strat_key in ["STRONG_SCAFFOLD", "STRONG_DECOMPOSED_STEP"]:
                next_strat = "UNCHANGED_REUSE"
                action = "reuse"
            else:
                next_strat = self._step_ladder(strat_key, step=1)
                action = "escalate"
        else:
            # Incorrect response
            if total_errors >= 2:
                reason_codes.append("REPEATED_INCORRECT_RESPONSE")
                if is_minimal or strat_key in ["STRONG_DECOMPOSED_STEP", "STRONG_SCAFFOLD"]:
                    next_strat = "UNCHANGED_REUSE"
                    action = "reuse"
                    additional_support.extend(["VISUAL_CHOICE_HIGHLIGHTING", "TOUCH_RESPONSE_MODE"])
                else:
                    # Jump directly to decomposed or scaffold
                    if strat_key == "MODERATE_SUPPORT":
                        next_strat = "STRONG_SCAFFOLD"
                    elif strat_key == "STRONG_SCAFFOLD":
                        next_strat = "STRONG_DECOMPOSED_STEP"
                    else:
                        next_strat = self._step_ladder(strat_key, step=2)
                    action = "escalate_decomposed"
            else:
                reason_codes.append("FIRST_INCORRECT_RESPONSE")
                if is_minimal:
                    next_strat = "UNCHANGED_REUSE"
                    action = "reuse"
                    additional_support.extend(["VISUAL_CHOICE_HIGHLIGHTING", "TOUCH_RESPONSE_MODE"])
                else:
                    next_strat = self._step_ladder(strat_key, step=1)
                    action = "escalate"

        # Check minimal safe instruction condition
        reuse_declared = False
        reuse_lineage: Optional[Dict[str, Any]] = None

        if next_strat == "UNCHANGED_REUSE" or (is_minimal and not is_correct and strat_key in ["STRONG_SCAFFOLD", "STRONG_DECOMPOSED_STEP"]):
            next_strat = "UNCHANGED_REUSE"
            reuse_declared = True
            if not additional_support:
                additional_support = ["VISUAL_CHOICE_HIGHLIGHTING", "TOUCH_RESPONSE_MODE"]
            reuse_lineage = self.declare_governed_reuse(
                previous_attempt=current_attempt,
                support_actions=additional_support,
                reason_code="MINIMAL_SAFE_INSTRUCTION_ALREADY_REACHED"
            )

        return {
            "next_strategy_code": next_strat,
            "adaptation_strategy": next_strat.lower(),
            "reason_codes": reason_codes,
            "action": action,
            "reuse_declared": reuse_declared,
            "reuse_lineage": reuse_lineage,
            "additional_support": additional_support,
            "approved_for_child_delivery": False
        }

    def detect_minimal_safe_instruction(
        self,
        instruction: str,
        activity: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Detects whether an instruction text represents a minimal safe wording
        beyond which further textual simplification is counterproductive or impossible.
        Example: "Choose: cat or dog.", "තෝරන්න: පූසා හෝ බල්ලා."
        """
        if not instruction:
            return False
        norm = normalize_text_nfc(instruction).lower()

        # Direct known minimal patterns
        minimal_markers = [
            "choose: cat or dog.",
            "choose: cat or dog",
            "is it a cat or a dog?",
            "touch cat or dog.",
            "තෝරන්න: පූසා හෝ බල්ලා.",
            "මේ පූසෙක්ද බල්ලෙක්ද?",
            "පූසා හෝ බල්ලා තෝරන්න."
        ]
        for marker in minimal_markers:
            if marker in norm:
                return True

        # Short imperative choice check
        if ("choose:" in norm or "touch:" in norm or "තෝරන්න:" in norm) and len(norm.split()) <= 6:
            return True

        return False

    def declare_governed_reuse(
        self,
        previous_attempt: Any,
        support_actions: Optional[List[str]] = None,
        reason_code: str = "MINIMAL_SAFE_INSTRUCTION_ALREADY_REACHED"
    ) -> Dict[str, Any]:
        """
        Emits an explicit governed reuse declaration with non-textual support actions.
        Silent repetition is prohibited.
        """
        prev_id = getattr(previous_attempt, "id", None) or "previous_attempt"
        prev_strategy = (
            getattr(previous_attempt, "adaptation_strategy", None)
            or getattr(previous_attempt, "strategy_code", None)
            or "STRONG_SCAFFOLD"
        ).upper()

        return {
            "simplification_status": "NO_FURTHER_SAFE_SIMPLIFICATION",
            "instruction_changed": False,
            "instruction_reused": True,
            "generation_mode": "UNCHANGED_REUSE",
            "reuse_reason_code": reason_code,
            "reused_from_attempt_id": prev_id,
            "strategy_code": prev_strategy,
            "additional_support": support_actions or [
                "VISUAL_CHOICE_HIGHLIGHTING",
                "TOUCH_RESPONSE_MODE"
            ],
            "approved_for_child_delivery": False
        }

    def _normalize_strategy_key(self, strat: str) -> str:
        s = strat.upper().strip()
        if "ORIGINAL" in s or "BASELINE" in s:
            return "ORIGINAL_BASELINE"
        if "MILD" in s:
            return "MILD_SUPPORT"
        if "MODERATE" in s and "SCAFFOLD" not in s:
            return "MODERATE_SUPPORT"
        if "DECOMPOSED" in s or "STEP" in s:
            return "STRONG_DECOMPOSED_STEP"
        if "STRONG" in s or "SCAFFOLD" in s or "VISUAL_CUE" in s:
            return "STRONG_SCAFFOLD"
        if "REUSE" in s or "UNCHANGED" in s:
            return "UNCHANGED_REUSE"
        return "MODERATE_SUPPORT"

    def _step_ladder(self, current_key: str, step: int = 1) -> str:
        ladder = self.strategy_ladder
        try:
            curr_idx = ladder.index(current_key)
        except ValueError:
            curr_idx = 0
        new_idx = min(curr_idx + step, len(ladder) - 1)
        return ladder[new_idx]


adaptation_decision_service = AdaptationDecisionService()
