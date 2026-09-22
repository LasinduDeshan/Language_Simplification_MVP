from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import LearnerProfile, Task, ActivitySession, Attempt

class LearnerProfileUpdater:
    """
    Dynamic Learner Profile Evolution & Risk Recalibration Engine.
    Adjusts vocabulary_score, grammar_score, comprehension_score, instruction_following_score,
    and dynamically transitions risk_support_level (high <-> moderate <-> low) and english_level
    based on task performance, attempt counts, and linguistic observations.
    """

    # Category attribution weights
    CATEGORY_WEIGHTS = {
        "vocabulary": {"vocab": 0.60, "gram": 0.10, "comp": 0.15, "inst": 0.15},
        "grammar": {"vocab": 0.10, "gram": 0.60, "comp": 0.15, "inst": 0.15},
        "comprehension": {"vocab": 0.15, "gram": 0.15, "comp": 0.50, "inst": 0.20},
        "sentence_and_instruction": {"vocab": 0.15, "gram": 0.15, "comp": 0.20, "inst": 0.50},
    }

    # Difficulty multiplier
    DIFFICULTY_MULTIPLIERS = {
        "easy": 1.0,
        "medium": 1.2,
        "hard": 1.5
    }

    def update_profile_after_session(
        self,
        db: Session,
        learner: LearnerProfile,
        task: Task,
        session_final_outcome: str,
        attempt_number: int,
        grammar_errors_count: int = 0,
        assistance_level: str = "independent"
    ) -> Dict[str, Any]:
        """
        Calculates and applies pedagogical deltas to a learner's profile
        based on the completed activity session.
        """
        # Store previous state for change tracking
        before_state = {
            "vocabulary_score": round(learner.vocabulary_score, 1),
            "grammar_score": round(learner.grammar_score, 1),
            "comprehension_score": round(learner.comprehension_score, 1),
            "instruction_following_score": round(learner.instruction_following_score, 1),
            "risk_support_level": learner.risk_support_level,
            "english_level": learner.english_level
        }

        # 1. Determine Base Delta (Δ_base)
        if session_final_outcome == "success":
            if attempt_number == 1 and assistance_level == "independent":
                base_delta = 5.0
            elif attempt_number == 2:
                base_delta = 3.0
            elif attempt_number == 3:
                base_delta = 1.5
            else:
                base_delta = 2.0
        elif session_final_outcome in ["adult_support_required", "adult_support"]:
            # Escalation penalty: Struggled across 3 attempts
            base_delta = -2.5
        elif session_final_outcome == "partial":
            base_delta = 0.5
        else:
            base_delta = -1.0

        # 2. Apply Difficulty Multiplier
        diff = (task.base_difficulty or "medium").lower()
        multiplier = self.DIFFICULTY_MULTIPLIERS.get(diff, 1.2)
        net_delta = base_delta * multiplier

        # 3. Apply Category Attribution Weights
        cat = (task.category or "vocabulary").lower()
        weights = self.CATEGORY_WEIGHTS.get(cat, self.CATEGORY_WEIGHTS["vocabulary"])

        delta_vocab = net_delta * weights["vocab"]
        delta_gram = net_delta * weights["gram"]
        delta_comp = net_delta * weights["comp"]
        delta_inst = net_delta * weights["inst"]

        # 4. Linguistic Error Bonuses & Penalties
        if session_final_outcome == "success" and grammar_errors_count == 0:
            delta_gram += 1.0  # Clean syntax bonus
        elif grammar_errors_count >= 2:
            delta_gram -= 1.0  # Persistent DLD error pattern impact

        # 5. Apply and Clamp Scores [0.0, 100.0]
        learner.vocabulary_score = round(max(0.0, min(100.0, learner.vocabulary_score + delta_vocab)), 1)
        learner.grammar_score = round(max(0.0, min(100.0, learner.grammar_score + delta_gram)), 1)
        learner.comprehension_score = round(max(0.0, min(100.0, learner.comprehension_score + delta_comp)), 1)
        learner.instruction_following_score = round(max(0.0, min(100.0, learner.instruction_following_score + delta_inst)), 1)

        # 6. Recalculate Composite Language Index (CLI)
        cli = round(
            (0.30 * learner.vocabulary_score) +
            (0.30 * learner.grammar_score) +
            (0.20 * learner.comprehension_score) +
            (0.20 * learner.instruction_following_score),
            1
        )

        # 7. Recalibrate Risk Support Level
        # High Risk: CLI < 48.0 OR min(Vocab, Gram) < 38.0
        # Moderate Risk: 48.0 <= CLI < 68.0 AND both >= 38.0
        # Low Risk: CLI >= 68.0 AND both >= 60.0
        min_core = min(learner.vocabulary_score, learner.grammar_score)
        if cli < 48.0 or min_core < 38.0:
            new_risk = "high"
        elif cli >= 68.0 and min_core >= 60.0:
            new_risk = "low"
        else:
            new_risk = "moderate"

        # 8. Recalibrate English Level
        if cli < 48.0:
            new_english = "emerging"
        elif cli < 68.0:
            new_english = "developing"
        else:
            new_english = "proficient"

        risk_changed = (new_risk != learner.risk_support_level)
        learner.risk_support_level = new_risk
        learner.english_level = new_english
        learner.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(learner)

        after_state = {
            "vocabulary_score": round(learner.vocabulary_score, 1),
            "grammar_score": round(learner.grammar_score, 1),
            "comprehension_score": round(learner.comprehension_score, 1),
            "instruction_following_score": round(learner.instruction_following_score, 1),
            "risk_support_level": learner.risk_support_level,
            "english_level": learner.english_level,
            "composite_language_index": cli
        }

        deltas = {
            "vocabulary": round(after_state["vocabulary_score"] - before_state["vocabulary_score"], 1),
            "grammar": round(after_state["grammar_score"] - before_state["grammar_score"], 1),
            "comprehension": round(after_state["comprehension_score"] - before_state["comprehension_score"], 1),
            "instruction": round(after_state["instruction_following_score"] - before_state["instruction_following_score"], 1)
        }

        return {
            "learner_id": learner.id,
            "learner_code": learner.learner_code,
            "before": before_state,
            "after": after_state,
            "deltas": deltas,
            "risk_changed": risk_changed,
            "reason": f"Session completed with {session_final_outcome} at attempt {attempt_number}"
        }

profile_updater = LearnerProfileUpdater()
