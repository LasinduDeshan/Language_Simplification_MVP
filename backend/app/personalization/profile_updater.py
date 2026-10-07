from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import LearnerProfile, Task, ActivitySession, Attempt

class LearnerProfileUpdater:
    """
    Stage 12 Educational Performance Profile Update Engine.
    
    Responsibility Boundaries:
    1. Updates ONLY the primary educational domain targeted by the activity
       (vocabulary, grammar, comprehension, or instruction_following).
    2. NEVER mutates screening_risk_level (owned as a read-only snapshot from Component 1).
    3. Calculates recommended_support_level (mild, moderate, strong) for educational scaffolding.
    4. Increments domain-specific evidence counters.
    5. Produces reproducible calculation snapshots for auditability.
    """

    DIFFICULTY_MULTIPLIERS = {
        "easy": 1.0,
        "medium": 1.2,
        "hard": 1.5
    }

    def _determine_target_domain(self, category: str) -> str:
        cat = (category or "vocabulary").lower()
        if cat in ["grammar", "syntax", "gram"]:
            return "grammar"
        elif cat in ["comprehension", "comp"]:
            return "comprehension"
        elif cat in ["sentence_and_instruction", "instruction", "instruction_following", "inst"]:
            return "instruction_following"
        else:
            return "vocabulary"

    def update_profile_after_session(
        self,
        db: Session,
        learner: LearnerProfile,
        task: Task,
        session_final_outcome: str,
        attempt_number: int,
        grammar_errors_count: int = 0,
        assistance_level: str = "independent",
        adult_confirmed: bool = True
    ) -> Dict[str, Any]:
        """
        Calculates and applies pedagogical deltas to a learner's educational performance profile.
        Requires adult_confirmed == True for valid score updates.
        """
        if not adult_confirmed:
            raise ValueError("Cannot update learner performance score without adult confirmation.")

        target_domain = self._determine_target_domain(task.category)

        # Store before state
        screening_risk = getattr(learner, "screening_risk_level", None) or getattr(learner, "risk_support_level", "moderate")
        before_state = {
            "vocabulary_score": round(learner.vocabulary_score, 1),
            "grammar_score": round(learner.grammar_score, 1),
            "comprehension_score": round(learner.comprehension_score, 1),
            "instruction_following_score": round(learner.instruction_following_score, 1),
            "screening_risk_level": screening_risk,
            "recommended_support_level": getattr(learner, "recommended_support_level", "moderate"),
            "risk_support_level": learner.risk_support_level,
            "english_level": learner.english_level
        }

        # 1. Base Delta calculation
        if session_final_outcome == "success":
            if attempt_number == 1 and assistance_level == "independent":
                base_delta = 5.0
            elif attempt_number == 2:
                base_delta = 3.0
            elif attempt_number == 3:
                base_delta = 1.5
            else:
                base_delta = 2.0
        elif session_final_outcome in ["completed_with_adult_support", "adult_support"]:
            base_delta = 2.0
        elif session_final_outcome in ["adult_support_required", "escalation"]:
            base_delta = -2.5
        elif session_final_outcome == "partial":
            base_delta = 0.5
        else:
            base_delta = -1.0

        # 2. Difficulty multiplier
        diff = (task.base_difficulty or "medium").lower()
        multiplier = self.DIFFICULTY_MULTIPLIERS.get(diff, 1.2)
        net_delta = base_delta * multiplier

        # 3. Domain-specific bonus/penalty
        syntax_adjustment = 0.0
        if target_domain == "grammar":
            if session_final_outcome == "success" and grammar_errors_count == 0:
                syntax_adjustment = 1.0
            elif grammar_errors_count >= 2:
                syntax_adjustment = -1.0
        
        final_domain_delta = round(net_delta + syntax_adjustment, 1)

        # 4. Evidence counts before & after
        ev_before = 0
        if target_domain == "vocabulary":
            ev_before = learner.vocabulary_evidence_count or 0
            learner.vocabulary_score = round(max(0.0, min(100.0, learner.vocabulary_score + final_domain_delta)), 1)
            learner.vocabulary_evidence_count = ev_before + 1
        elif target_domain == "grammar":
            ev_before = learner.grammar_evidence_count or 0
            learner.grammar_score = round(max(0.0, min(100.0, learner.grammar_score + final_domain_delta)), 1)
            learner.grammar_evidence_count = ev_before + 1
        elif target_domain == "comprehension":
            ev_before = learner.comprehension_evidence_count or 0
            learner.comprehension_score = round(max(0.0, min(100.0, learner.comprehension_score + final_domain_delta)), 1)
            learner.comprehension_evidence_count = ev_before + 1
        elif target_domain == "instruction_following":
            ev_before = learner.instruction_evidence_count or 0
            learner.instruction_following_score = round(max(0.0, min(100.0, learner.instruction_following_score + final_domain_delta)), 1)
            learner.instruction_evidence_count = ev_before + 1

        ev_after = ev_before + 1

        # 5. Composite Learning Support Index (for educational scaffolding)
        cli = round(
            (0.30 * learner.vocabulary_score) +
            (0.30 * learner.grammar_score) +
            (0.20 * learner.comprehension_score) +
            (0.20 * learner.instruction_following_score),
            1
        )

        # 6. Recalculate RECOMMENDED SUPPORT LEVEL (independent of screening risk!)
        target_score = getattr(learner, f"{target_domain if target_domain != 'instruction_following' else 'instruction_following'}_score", 50.0)
        if cli < 48.0 or target_score < 40.0:
            new_support = "strong"
        elif cli >= 70.0 and target_score >= 65.0:
            new_support = "mild"
        else:
            new_support = "moderate"

        # 7. English level recommendation
        if cli < 48.0:
            new_english = "emerging"
        elif cli < 68.0:
            new_english = "developing"
        else:
            new_english = "proficient"

        # 8. PERSIST: Note that screening_risk_level is NEVER modified by activity completion
        learner.recommended_support_level = new_support
        learner.english_level = new_english
        learner.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(learner)

        after_state = {
            "vocabulary_score": round(learner.vocabulary_score, 1),
            "grammar_score": round(learner.grammar_score, 1),
            "comprehension_score": round(learner.comprehension_score, 1),
            "instruction_following_score": round(learner.instruction_following_score, 1),
            "screening_risk_level": screening_risk,
            "recommended_support_level": learner.recommended_support_level,
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

        calculation_snapshot = {
            "scoring_version": "1.0",
            "target_domain": target_domain,
            "session_final_outcome": session_final_outcome,
            "attempt_number": attempt_number,
            "assistance_level": assistance_level,
            "base_delta": base_delta,
            "difficulty_multiplier": multiplier,
            "syntax_adjustment": syntax_adjustment,
            "final_domain_delta": final_domain_delta,
            "evidence_count_before": ev_before,
            "evidence_count_after": ev_after,
            "timestamp": datetime.utcnow().isoformat()
        }

        return {
            "learner_id": learner.id,
            "learner_code": learner.learner_code,
            "target_domain": target_domain,
            "evidence_count_before": ev_before,
            "evidence_count_after": ev_after,
            "before": before_state,
            "after": after_state,
            "deltas": deltas,
            "risk_changed": False,  # Strictly False: activity evaluation never changes DLD screening risk
            "calculation_snapshot": calculation_snapshot,
            "reason": f"Activity in domain '{target_domain}' completed with {session_final_outcome} at attempt {attempt_number}"
        }

profile_updater = LearnerProfileUpdater()
