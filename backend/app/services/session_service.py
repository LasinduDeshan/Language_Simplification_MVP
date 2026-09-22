from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.database.models import (
    ActivitySession, Attempt, Task, LearnerProfile, LanguageObservation,
    IntegrationEvent, ActivityQuestion, QuestionResponse, TaskResult
)
from app.personalization.controller import personalization_controller
from app.personalization.profile_updater import profile_updater
from app.response_analysis.answer_checker import answer_checker
from app.response_analysis.language_extractor import language_extractor
from app.grammar_analysis.grammar_extractor import grammar_extractor
from app.generation.rule_generator import rule_generator
from app.generation.llm_generator import llm_generator
from app.validation.validator import adaptation_validator
from app.security.input_sanitizer import sanitize_text

class SessionService:
    def create_session(
        self,
        db: Session,
        learner_id: str,
        task_id: str,
        generation_mode: str = "rule",
        created_by: str = "authorized_adult"
    ) -> ActivitySession:
        learner = db.query(LearnerProfile).filter((LearnerProfile.id == learner_id) | (LearnerProfile.learner_code == learner_id)).first()
        if not learner:
            raise ValueError(f"LearnerProfile '{learner_id}' not found")

        task = db.query(Task).filter((Task.id == task_id) | (Task.task_code == task_id)).first()
        if not task:
            raise ValueError(f"Task '{task_id}' not found")

        # 1. Deterministic Initial Support calculation
        init_support_data = personalization_controller.calculate_initial_support(learner, task)
        initial_support = init_support_data["initial_support_level"]
        reasons = init_support_data["support_decision_reasons"]

        # 2. Immutable Learner Profile Snapshot
        profile_snapshot = {
            "learner_code": learner.learner_code,
            "age": learner.age,
            "grade": learner.grade,
            "risk_support_level": learner.risk_support_level,
            "vocabulary_score": learner.vocabulary_score,
            "grammar_score": learner.grammar_score,
            "comprehension_score": learner.comprehension_score,
            "instruction_following_score": learner.instruction_following_score,
            "english_level": learner.english_level,
            "preferred_language": learner.preferred_language
        }

        session = ActivitySession(
            learner_id=learner.id,
            task_id=task.id,
            status="active",
            current_attempt_number=1,
            initial_support_level=initial_support,
            current_support_level=initial_support,
            support_decision_reasons=reasons,
            generation_mode=generation_mode,
            created_by=created_by,
            learner_profile_snapshot=profile_snapshot,
            task_version="1.0",
            adaptation_configuration_version="1.0"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def create_attempt(
        self,
        db: Session,
        session_id: str,
        generation_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        session = db.query(ActivitySession).filter(ActivitySession.id == session_id).first()
        if not session:
            raise ValueError(f"ActivitySession '{session_id}' not found")

        if session.status in ["completed", "completed_with_adult_support", "adult_support_required"]:
            raise ValueError(f"Session is already closed with status '{session.status}'.")

        existing_attempts = db.query(Attempt).filter(Attempt.activity_session_id == session_id).order_by(Attempt.attempt_number).all()
        attempt_number = len(existing_attempts) + 1

        if attempt_number > 3:
            raise ValueError("Maximum 3 attempts limit reached. Cannot create attempt 4.")

        task = session.task
        learner = session.learner
        gen_mode = generation_mode or session.generation_mode

        # 1. Scaffolding progression based on initial support level
        scaffolding = personalization_controller.get_scaffolding_for_attempt(
            initial_support_level=session.initial_support_level,
            target_attempt_number=attempt_number
        )
        support_level = scaffolding["support_level"]
        adaptation_strategy = scaffolding["adaptation_strategy"]
        assistance_level = scaffolding["assistance_level"]
        visual_cues = scaffolding["visual_cues"]

        # 2. Select / Generate exact instruction before child sees it
        presented_instruction = ""
        supportive_message = "You can do it! Take your time."
        generation_method = "curated"
        validation_status = "approved"

        # Check curated support versions in task definition first
        support_versions = task.support_versions or {}
        if support_level in support_versions and support_versions[support_level]:
            presented_instruction = support_versions[support_level]
            generation_method = "curated"
        elif task.child_friendly_instruction:
            presented_instruction = task.child_friendly_instruction
            generation_method = "curated"
        else:
            # Fallback to rule generator
            rule_out = rule_generator.generate(task, learner, attempt_number, support_level)
            presented_instruction = rule_out["child_instruction"]
            supportive_message = rule_out.get("supportive_message", supportive_message)
            generation_method = "rule_based"

        # If LLM requested, attempt generation with deterministic validation & curated fallback
        if gen_mode == "llm":
            try:
                llm_out = llm_generator.generate(task, learner, attempt_number, support_level)
                val_res = adaptation_validator.validate_candidate(task, llm_out, learner)
                if val_res["status"] == "approved":
                    presented_instruction = llm_out["child_instruction"]
                    supportive_message = llm_out.get("supportive_message", supportive_message)
                    generation_method = "llm_generated_rule_validated"
                    validation_status = "approved"
                else:
                    validation_status = "fallback_used"
            except Exception:
                validation_status = "fallback_used"

        # Check for response format adjustments across retries
        response_format_adjusted = False
        original_response_mode = task.response_modes[0] if task.response_modes else "manual_transcript"
        current_response_mode = original_response_mode

        if attempt_number >= 2 and support_level == "strong" and "multiple_choice" in (task.response_modes or []):
            if original_response_mode != "multiple_choice":
                response_format_adjusted = True
                current_response_mode = "multiple_choice"

        # 3. Store exact presented instruction in Attempt record
        attempt = Attempt(
            activity_session_id=session.id,
            attempt_number=attempt_number,
            attempt_status="awaiting_response",
            presented_instruction=presented_instruction,
            instruction_shown=presented_instruction,
            support_level=support_level,
            adaptation_strategy=adaptation_strategy,
            visual_cues=visual_cues,
            vocabulary_cues=task.vocabulary_targets or [],
            generation_method=generation_method,
            validation_status=validation_status,
            response_source="adult_transcribed",
            adult_confirmed=False,
            completion_status="completed",
            assistance_level=assistance_level,
            response_format_adjusted=response_format_adjusted,
            original_response_mode=original_response_mode,
            current_response_mode=current_response_mode,
            target_skill=task.target_skill or task.subskill
        )
        db.add(attempt)
        session.current_attempt_number = attempt_number
        session.current_support_level = support_level
        db.commit()
        db.refresh(attempt)

        child_view = self.get_child_view(db, session_id, attempt.id)

        return {
            "attempt": attempt,
            "child_view": child_view
        }

    def record_response(
        self,
        db: Session,
        attempt_id: str,
        response_source: str = "adult_transcribed",
        manual_transcript: Optional[str] = None,
        selected_option: Optional[str] = None,
        selected_items: Optional[List[str]] = None,
        ordered_items: Optional[List[str]] = None,
        response_time_ms: int = 0,
        completion_status: str = "completed",
        assistance_level: str = "independent",
        adult_notes: Optional[str] = None
    ) -> Attempt:
        attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
        if not attempt:
            raise ValueError(f"Attempt '{attempt_id}' not found")

        clean_transcript = sanitize_text(manual_transcript, max_length=500) if manual_transcript else None

        attempt.response_source = response_source
        attempt.manual_transcript = clean_transcript
        attempt.speech_transcript = clean_transcript
        attempt.speech_confidence = None  # Adult-transcribed responses do not receive artificial confidence
        attempt.selected_option = selected_option
        attempt.selected_items = selected_items or []
        attempt.ordered_items = ordered_items or []
        attempt.response_time_ms = response_time_ms
        attempt.completion_status = completion_status
        attempt.assistance_level = assistance_level
        attempt.adult_notes = adult_notes
        attempt.attempt_status = "response_recorded"

        db.commit()
        db.refresh(attempt)
        return attempt

    def confirm_response(
        self,
        db: Session,
        attempt_id: str,
        confirmed: bool = True,
        manual_transcript: Optional[str] = None
    ) -> Attempt:
        attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
        if not attempt:
            raise ValueError(f"Attempt '{attempt_id}' not found")

        if manual_transcript is not None:
            clean_transcript = sanitize_text(manual_transcript, max_length=500)
            attempt.manual_transcript = clean_transcript
            attempt.speech_transcript = clean_transcript

        attempt.adult_confirmed = confirmed
        attempt.attempt_status = "confirmed"
        db.commit()
        db.refresh(attempt)
        return attempt

    def analyse_attempt(
        self,
        db: Session,
        attempt_id: str
    ) -> Dict[str, Any]:
        attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
        if not attempt:
            raise ValueError(f"Attempt '{attempt_id}' not found")

        if not attempt.adult_confirmed:
            raise ValueError("Cannot analyse unconfirmed response. Adult confirmation of transcript/selection is required.")

        session = attempt.activity_session
        task = session.task
        learner = session.learner

        # Evaluate concept vs target skill
        selected_val = attempt.selected_option or attempt.ordered_items or attempt.selected_items
        eval_res = answer_checker.evaluate_answer(
            task=task,
            transcript=attempt.manual_transcript,
            selected_answer=selected_val,
            completion_status=attempt.completion_status
        )

        concept_result = eval_res["concept_result"]
        target_skill_result = eval_res["target_skill_result"]
        grammar_obs = eval_res["grammar_observations"]
        vocab_obs = eval_res["vocabulary_observations"]
        retry_required = eval_res["retry_required"]
        retry_reason = eval_res["retry_reason"]

        # Store automatic analysis snapshot
        snapshot = {
            "concept_result": concept_result,
            "target_skill_result": target_skill_result,
            "grammar_observations": grammar_obs,
            "vocabulary_observations": vocab_obs,
            "retry_required": retry_required,
            "retry_reason": retry_reason,
            "analysed_at": datetime.utcnow().isoformat()
        }

        attempt.target_skill = eval_res["target_skill"]
        attempt.concept_result = concept_result
        attempt.target_skill_result = target_skill_result
        attempt.grammar_observations = grammar_obs
        attempt.vocabulary_observations = vocab_obs
        attempt.retry_required = retry_required
        attempt.retry_reason = retry_reason
        attempt.automatic_analysis_snapshot = snapshot
        attempt.attempt_status = "analysed"

        # Record observations in database
        for g_obs in grammar_obs:
            db.add(LanguageObservation(
                attempt_id=attempt.id,
                category="grammar",
                observation_code=g_obs,
                evidence=attempt.manual_transcript,
                confidence=1.0,
                confirmed=True,
                child_visible=False
            ))

        db.commit()
        db.refresh(attempt)

        return {
            "attempt_id": attempt.id,
            "concept_result": concept_result,
            "target_skill_result": target_skill_result,
            "grammar_observations": grammar_obs,
            "vocabulary_observations": vocab_obs,
            "retry_required": retry_required,
            "retry_reason": retry_reason,
            "automatic_analysis_snapshot": snapshot
        }

    def review_attempt(
        self,
        db: Session,
        attempt_id: str,
        final_concept_result: str,
        final_target_skill_result: str,
        final_retry_required: bool,
        override_reason: Optional[str] = None,
        reviewed_by_user_id: str = "authorized_adult",
        adult_notes: Optional[str] = None
    ) -> Attempt:
        attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
        if not attempt:
            raise ValueError(f"Attempt '{attempt_id}' not found")

        attempt.final_concept_result = final_concept_result
        attempt.final_target_skill_result = final_target_skill_result
        attempt.final_retry_required = final_retry_required
        attempt.override_reason = override_reason
        attempt.reviewed_by_user_id = reviewed_by_user_id
        attempt.reviewed_at = datetime.utcnow()
        if adult_notes:
            attempt.adult_notes = adult_notes

        db.commit()
        db.refresh(attempt)
        return attempt

    def transition_attempt(
        self,
        db: Session,
        attempt_id: str
    ) -> Dict[str, Any]:
        attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
        if not attempt:
            raise ValueError(f"Attempt '{attempt_id}' not found")

        session = attempt.activity_session
        task = session.task
        learner = session.learner

        # Determine effective outcome
        effective_retry = attempt.final_retry_required if attempt.final_retry_required is not None else attempt.retry_required
        effective_target_result = attempt.final_target_skill_result if attempt.final_target_skill_result is not None else attempt.target_skill_result

        # Independent success evaluation
        is_independent = (attempt.assistance_level == "independent")
        independent_success = (effective_target_result == "correct" and is_independent)
        attempt.independent_success = independent_success
        attempt.attempt_status = "completed"

        session_outcome = None
        next_action = None

        if not effective_retry:
            # Succeeded!
            session.completed_at = datetime.utcnow()
            session.final_outcome = "success"
            session.status = "completed" if is_independent else "completed_with_adult_support"
            session_outcome = session.status
            next_action = "session_completed"

            # Emit Component 4 Analytics Event
            db.add(IntegrationEvent(
                activity_session_id=session.id,
                attempt_id=attempt.id,
                target_component="component_4",
                event_type="session_progress_event",
                payload={
                    "learner_id": learner.learner_code,
                    "task_id": task.task_code,
                    "attempt_number": attempt.attempt_number,
                    "result": effective_target_result,
                    "assistance_level": attempt.assistance_level,
                    "independent_success": independent_success,
                    "status": session.status
                }
            ))
        else:
            # Retry required
            if attempt.attempt_number >= 3:
                # Escalation after attempt 3
                session.completed_at = datetime.utcnow()
                session.final_outcome = "adult_support_required"
                session.status = "adult_support_required"
                session.escalation_required = True
                session_outcome = "adult_support_required"
                next_action = "adult_support_required"

                # Emit Adult Support Required Event
                db.add(IntegrationEvent(
                    activity_session_id=session.id,
                    attempt_id=attempt.id,
                    target_component="component_1",
                    event_type="adult_support_required_event",
                    payload={
                        "learner_id": learner.learner_code,
                        "task_id": task.task_code,
                        "reason": "three_unsuccessful_attempts",
                        "status": "adult_support_required"
                    }
                ))
            else:
                session_outcome = "retry_available"
                next_action = f"create_attempt_{attempt.attempt_number + 1}"

        profile_update = None
        task_result_id = None
        if session.final_outcome in ["success", "completed_with_adult_support", "adult_support_required"]:
            grammar_err_count = len(attempt.grammar_observations or []) if hasattr(attempt, "grammar_observations") else 0

            # Capture score snapshot BEFORE update
            score_before_snap = {
                "vocabulary_score": round(learner.vocabulary_score, 1),
                "grammar_score": round(learner.grammar_score, 1),
                "comprehension_score": round(learner.comprehension_score, 1),
                "instruction_following_score": round(learner.instruction_following_score, 1),
                "risk_support_level": learner.risk_support_level,
                "english_level": learner.english_level
            }

            profile_update = profile_updater.update_profile_after_session(
                db=db,
                learner=learner,
                task=task,
                session_final_outcome=session.final_outcome,
                attempt_number=attempt.attempt_number,
                grammar_errors_count=grammar_err_count,
                assistance_level=attempt.assistance_level or "independent"
            )

            # Build attempt-by-attempt history for the TaskResult record
            all_session_attempts = db.query(Attempt).filter(
                Attempt.activity_session_id == session.id
            ).order_by(Attempt.attempt_number).all()

            attempt_history = []
            for att in all_session_attempts:
                attempt_history.append({
                    "attempt_number": att.attempt_number,
                    "instruction": att.presented_instruction or att.instruction_shown or "",
                    "transcript": att.manual_transcript or att.speech_transcript or "",
                    "selected_option": att.selected_option or "",
                    "concept_result": att.final_concept_result or att.concept_result or "unclear",
                    "target_skill_result": att.final_target_skill_result or att.target_skill_result or "not_applicable",
                    "assistance_level": att.assistance_level or "independent",
                    "response_time_ms": att.response_time_ms or 0,
                    "retry_required": att.final_retry_required if att.final_retry_required is not None else att.retry_required,
                    "grammar_observations": att.grammar_observations or [],
                    "vocabulary_observations": att.vocabulary_observations or []
                })

            # Determine if any attempt was independent
            any_independent = any(
                a.get("assistance_level") == "independent" and a.get("concept_result") == "correct"
                for a in attempt_history
            )

            # Build diagnostic notes
            outcome_label = {
                "success": "independently mastered",
                "completed_with_adult_support": "completed with adult support",
                "adult_support_required": "required adult support after 3 attempts"
            }.get(session.final_outcome, session.final_outcome)
            diagnostic_notes = (
                f"{learner.learner_code} (Age {learner.age}, {score_before_snap['risk_support_level']} risk) "
                f"{outcome_label} the task '{task.title}' ({task.category}, {task.base_difficulty}). "
                f"{len(all_session_attempts)} attempt(s) used. "
                f"Grammar: {score_before_snap['grammar_score']} → {profile_update['after']['grammar_score']} "
                f"(Δ{profile_update['deltas']['grammar']:+.1f}). "
                f"Vocab: {score_before_snap['vocabulary_score']} → {profile_update['after']['vocabulary_score']} "
                f"(Δ{profile_update['deltas']['vocabulary']:+.1f}). "
                f"CLI: {profile_update['after'].get('composite_language_index', '?')}/100. "
                f"Risk level: {score_before_snap['risk_support_level']} → {profile_update['after']['risk_support_level']}."
            )

            # Persist the TaskResult record
            task_result = TaskResult(
                session_id=session.id,
                learner_id=learner.id,
                task_id=task.id,
                learner_code=learner.learner_code,
                learner_age=learner.age,
                task_code=task.task_code,
                task_title=task.title,
                category=task.category or "vocabulary",
                target_skill=task.target_skill,
                difficulty=task.base_difficulty or "medium",
                final_outcome=session.final_outcome,
                attempts_count=len(all_session_attempts),
                independent_success=independent_success,
                score_before=score_before_snap,
                score_after=profile_update["after"],
                score_deltas=profile_update["deltas"],
                risk_before=score_before_snap["risk_support_level"],
                risk_after=profile_update["after"]["risk_support_level"],
                risk_changed=profile_update["risk_changed"],
                composite_language_index=profile_update["after"].get("composite_language_index"),
                attempt_history=attempt_history,
                diagnostic_notes=diagnostic_notes,
                completed_at=session.completed_at or datetime.utcnow()
            )
            db.add(task_result)
            task_result_id = task_result.id

        db.commit()
        db.refresh(session)
        db.refresh(attempt)

        return {
            "session_id": session.id,
            "attempt_id": attempt.id,
            "session_status": session.status,
            "final_outcome": session.final_outcome,
            "next_action": next_action,
            "independent_success": independent_success,
            "profile_update": profile_update,
            "result_id": task_result_id
        }

    def get_child_view(
        self,
        db: Session,
        session_id: str,
        attempt_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Returns a clean, child-safe view payload with NO diagnostic risk scores,
        clinical labels, or research logs.
        """
        session = db.query(ActivitySession).filter(ActivitySession.id == session_id).first()
        if not session:
            raise ValueError(f"ActivitySession '{session_id}' not found")

        task = session.task
        
        # Get active attempt
        if attempt_id:
            attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
        else:
            attempt = db.query(Attempt).filter(Attempt.activity_session_id == session_id).order_by(Attempt.attempt_number.desc()).first()

        presented_inst = attempt.presented_instruction if attempt else (task.child_friendly_instruction or task.original_instruction)
        attempt_num = attempt.attempt_number if attempt else 1

        retry_cue = None
        if attempt_num == 2:
            retry_cue = "Let's try one more time together!"
        elif attempt_num == 3:
            retry_cue = "Almost there! Let's do this step."

        adult_support_message = None
        if session.status == "adult_support_required":
            adult_support_message = "Great effort! Let's ask our teacher or helper to explore this together."

        return {
            "session_id": session.id,
            "attempt_id": attempt.id if attempt else "",
            "attempt_number": attempt_num,
            "presented_instruction": presented_inst,
            "supportive_message": "You are doing great!",
            "stimulus": task.stimulus,
            "prompt": task.prompt,
            "options": task.options,
            "response_modes": task.response_modes or ["manual_transcript"],
            "visual_cues": attempt.visual_cues if attempt else [],
            "audio_available": True,
            "session_status": session.status,
            "retry_cue": retry_cue,
            "adult_support_message": adult_support_message
        }

    def get_session_history(
        self,
        db: Session,
        session_id: str
    ) -> Dict[str, Any]:
        session = db.query(ActivitySession).filter(ActivitySession.id == session_id).first()
        if not session:
            raise ValueError(f"ActivitySession '{session_id}' not found")

        attempts = db.query(Attempt).filter(Attempt.activity_session_id == session_id).order_by(Attempt.attempt_number).all()

        return {
            "session": session,
            "learner": session.learner,
            "task": session.task,
            "attempts": attempts,
            "events": session.integration_events
        }

    def get_task_results(
        self,
        db: Session,
        learner_code: Optional[str] = None,
        category: Optional[str] = None,
        outcome: Optional[str] = None,
        limit: int = 100
    ) -> List[TaskResult]:
        """Query task results with optional filters."""
        q = db.query(TaskResult).order_by(TaskResult.completed_at.desc())
        if learner_code:
            q = q.filter(TaskResult.learner_code == learner_code)
        if category:
            q = q.filter(TaskResult.category == category)
        if outcome:
            q = q.filter(TaskResult.final_outcome == outcome)
        return q.limit(limit).all()

    def get_task_result_by_id(self, db: Session, result_id: str) -> TaskResult:
        """Fetch a single task result by its UUID."""
        result = db.query(TaskResult).filter(TaskResult.id == result_id).first()
        if not result:
            raise ValueError(f"TaskResult '{result_id}' not found")
        return result

    def backfill_task_results(self, db: Session) -> int:
        """
        Backfills TaskResult records for any existing completed ActivitySessions
        that do not yet have a corresponding TaskResult record.
        Returns the count of newly created records.
        """
        terminal_statuses = ["completed", "completed_with_adult_support", "adult_support_required"]
        sessions = db.query(ActivitySession).filter(
            ActivitySession.status.in_(terminal_statuses)
        ).all()

        created = 0
        for session in sessions:
            existing = db.query(TaskResult).filter(TaskResult.session_id == session.id).first()
            if existing:
                continue  # Already has a result record

            learner = session.learner
            task = session.task
            if not learner or not task:
                continue

            attempts = db.query(Attempt).filter(
                Attempt.activity_session_id == session.id
            ).order_by(Attempt.attempt_number).all()

            attempt_history = []
            any_independent_success = False
            for att in attempts:
                eff_result = att.final_target_skill_result or att.target_skill_result or "not_applicable"
                eff_retry = att.final_retry_required if att.final_retry_required is not None else att.retry_required
                is_ind_success = (att.assistance_level == "independent" and eff_result == "correct" and not eff_retry)
                if is_ind_success:
                    any_independent_success = True
                attempt_history.append({
                    "attempt_number": att.attempt_number,
                    "instruction": att.presented_instruction or att.instruction_shown or "",
                    "transcript": att.manual_transcript or att.speech_transcript or "",
                    "selected_option": att.selected_option or "",
                    "concept_result": att.final_concept_result or att.concept_result or "unclear",
                    "target_skill_result": eff_result,
                    "assistance_level": att.assistance_level or "independent",
                    "response_time_ms": att.response_time_ms or 0,
                    "retry_required": eff_retry,
                    "grammar_observations": att.grammar_observations or [],
                    "vocabulary_observations": att.vocabulary_observations or []
                })

            # Use session snapshot if available, else use current learner scores
            snapshot = session.learner_profile_snapshot or {}
            score_before = {
                "vocabulary_score": snapshot.get("vocabulary_score", learner.vocabulary_score),
                "grammar_score": snapshot.get("grammar_score", learner.grammar_score),
                "comprehension_score": snapshot.get("comprehension_score", learner.comprehension_score),
                "instruction_following_score": snapshot.get("instruction_following_score", learner.instruction_following_score),
                "risk_support_level": snapshot.get("risk_support_level", learner.risk_support_level),
                "english_level": snapshot.get("english_level", learner.english_level)
            }
            score_after = {
                "vocabulary_score": learner.vocabulary_score,
                "grammar_score": learner.grammar_score,
                "comprehension_score": learner.comprehension_score,
                "instruction_following_score": learner.instruction_following_score,
                "risk_support_level": learner.risk_support_level,
                "english_level": learner.english_level
            }
            deltas = {
                "vocabulary": round(score_after["vocabulary_score"] - score_before["vocabulary_score"], 1),
                "grammar": round(score_after["grammar_score"] - score_before["grammar_score"], 1),
                "comprehension": round(score_after["comprehension_score"] - score_before["comprehension_score"], 1),
                "instruction": round(score_after["instruction_following_score"] - score_before["instruction_following_score"], 1)
            }

            diagnostic_notes = (
                f"{learner.learner_code} (Age {learner.age}) completed task '{task.title}' "
                f"with outcome: {session.final_outcome}. {len(attempts)} attempt(s). "
                f"Grammar: {score_before['grammar_score']} → {score_after['grammar_score']}. "
                f"[Backfilled record]"
            )

            task_result = TaskResult(
                session_id=session.id,
                learner_id=learner.id,
                task_id=task.id,
                learner_code=learner.learner_code,
                learner_age=learner.age,
                task_code=task.task_code,
                task_title=task.title,
                category=task.category or "vocabulary",
                target_skill=task.target_skill,
                difficulty=task.base_difficulty or "medium",
                final_outcome=session.final_outcome,
                attempts_count=len(attempts),
                independent_success=any_independent_success,
                score_before=score_before,
                score_after=score_after,
                score_deltas=deltas,
                risk_before=score_before["risk_support_level"],
                risk_after=score_after["risk_support_level"],
                risk_changed=(score_before["risk_support_level"] != score_after["risk_support_level"]),
                composite_language_index=None,
                attempt_history=attempt_history,
                diagnostic_notes=diagnostic_notes,
                completed_at=session.completed_at or datetime.utcnow()
            )
            db.add(task_result)
            created += 1

        db.commit()
        return created


session_service = SessionService()
