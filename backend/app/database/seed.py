import os
import json
from datetime import datetime
from app.database.db import SessionLocal, engine, Base
from app.database.models import (
    LearnerProfile, Task, ActivityAsset, ActivityQuestion, ActivitySession,
    Attempt, QuestionResponse, PerformancePattern, ExperimentRun, Adaptation,
    ValidationResult, LanguageObservation, IntegrationEvent, ExpertEvaluation
)
from app.services.adaptation_service import adaptation_service
from app.services.experiment_service import experiment_service

BASE_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data"))

def seed_database(reset: bool = True):
    print("Initializing database tables...")
    if reset:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Learner Profiles
        learners_file = os.path.join(BASE_DATA_DIR, "learner_profiles", "seed_learners.json")
        if os.path.exists(learners_file):
            with open(learners_file, "r", encoding="utf-8") as f:
                learners_data = json.load(f)
            
            for l_data in learners_data:
                learner = LearnerProfile(
                    learner_code=l_data["learner_code"],
                    age=l_data["age"],
                    grade=l_data.get("grade"),
                    risk_support_level=l_data["risk_support_level"],
                    vocabulary_score=l_data["vocabulary_score"],
                    grammar_score=l_data["grammar_score"],
                    comprehension_score=l_data["comprehension_score"],
                    instruction_following_score=l_data["instruction_following_score"],
                    english_level=l_data["english_level"],
                    preferred_language=l_data.get("preferred_language", "en")
                )
                db.add(learner)
            db.commit()
            print("Seeded learner profiles successfully.")

        # 2. Seed Tasks, Assets, and Questions
        tasks_file = os.path.join(BASE_DATA_DIR, "application_tasks", "seed_tasks.json")
        if os.path.exists(tasks_file):
            with open(tasks_file, "r", encoding="utf-8") as f:
                tasks_data = json.load(f)

            for t_data in tasks_data:
                task = Task(
                    task_code=t_data["task_code"],
                    title=t_data["title"],
                    category=t_data.get("category", "vocabulary"),
                    task_type=t_data.get("category", "vocabulary"),
                    subskill=t_data.get("subskill"),
                    target_skill=t_data.get("target_skill"),
                    language=t_data.get("language", "en"),
                    learning_objective=t_data["learning_objective"],
                    child_friendly_instruction=t_data.get("child_friendly_instruction"),
                    original_instruction=t_data["original_instruction"],
                    minimum_age=t_data.get("minimum_age", 4),
                    maximum_age=t_data.get("maximum_age", 8),
                    base_difficulty=t_data.get("base_difficulty", "medium"),
                    delivery_modes=t_data.get("delivery_modes", ["standard"]),
                    response_modes=t_data.get("response_modes", ["manual_transcript", "multiple_choice"]),
                    stimulus=t_data.get("stimulus", {}),
                    prompt=t_data.get("prompt"),
                    options=t_data.get("options", []),
                    passage=t_data.get("passage"),
                    expected_concepts=t_data.get("expected_concepts", []),
                    acceptable_answers=t_data.get("acceptable_answers", []),
                    expected_sequence=t_data.get("expected_sequence", []),
                    protected_answers=t_data.get("protected_answers", {}),
                    answer_presentation_policy=t_data.get("answer_presentation_policy", {}),
                    support_versions=t_data.get("support_versions", {}),
                    follow_up_for_strong=t_data.get("follow_up_for_strong"),
                    vocabulary_targets=t_data.get("vocabulary_targets", []),
                    grammar_targets=t_data.get("grammar_targets", []),
                    ar_metadata=t_data.get("ar_metadata", {}),
                    is_active=t_data.get("is_active", True)
                )
                db.add(task)
                db.flush()

                # Seed assets if any
                for a_data in t_data.get("assets", []):
                    db.add(ActivityAsset(
                        task_id=task.id,
                        asset_type=a_data.get("asset_type", "image"),
                        asset_key=a_data["asset_key"],
                        file_path_or_url=a_data["file_path_or_url"],
                        alt_text=a_data["alt_text"],
                        display_order=a_data.get("display_order", 1),
                        asset_source=a_data.get("asset_source", "Project team"),
                        asset_creator=a_data.get("asset_creator", "Project team"),
                        license_type=a_data.get("license_type", "Original project asset"),
                        license_url=a_data.get("license_url"),
                        permission_status=a_data.get("permission_status", "Approved for project use"),
                        attribution_text=a_data.get("attribution_text", "Created for Language Simplification MVP")
                    ))

                # Seed questions if any
                for q_data in t_data.get("questions", []):
                    db.add(ActivityQuestion(
                        task_id=task.id,
                        question_order=q_data["question_order"],
                        question_text=q_data["question_text"],
                        response_mode=q_data.get("response_mode", "manual_transcript"),
                        options=q_data.get("options", []),
                        acceptable_answers=q_data.get("acceptable_answers", []),
                        expected_concepts=q_data.get("expected_concepts", [])
                    ))

            db.commit()
            print("Seeded 30 application tasks and related assets successfully.")

        # 3. Seed Performance Patterns
        scenarios_file = os.path.join(BASE_DATA_DIR, "development_scenarios", "seed_scenarios.json")
        if os.path.exists(scenarios_file):
            with open(scenarios_file, "r", encoding="utf-8") as f:
                scenarios_data = json.load(f)

            for sc in scenarios_data:
                l_code = sc["learner"]["learner_code"]
                learner = db.query(LearnerProfile).filter(LearnerProfile.learner_code == l_code).first()
                if learner:
                    comp4 = sc.get("simulated_component_4", {})
                    for p_code in comp4.get("repeated_grammar_patterns", []):
                        db.add(PerformancePattern(
                            learner_id=learner.id,
                            pattern_type="grammar",
                            pattern_code=p_code,
                            frequency=2,
                            confidence=0.85,
                            successful_support=comp4.get("successful_support", "sentence_starter"),
                            recommended_support=comp4.get("recommended_support", "moderate"),
                            source="manual_input_session"
                        ))
                    for v_code in comp4.get("repeated_vocabulary_issues", []):
                        db.add(PerformancePattern(
                            learner_id=learner.id,
                            pattern_type="vocabulary",
                            pattern_code=v_code,
                            frequency=2,
                            confidence=0.85,
                            successful_support=comp4.get("successful_support", "picture_cue"),
                            recommended_support=comp4.get("recommended_support", "moderate"),
                            source="manual_input_session"
                        ))
            db.commit()
            print("Seeded performance patterns successfully.")

        # 4. Seed Benchmark Expert Evaluations using rule mode
        sample_tasks = db.query(Task).limit(3).all()
        sample_learner = db.query(LearnerProfile).first()

        if sample_tasks and sample_learner:
            benchmark_evaluators = [
                ("SLP-EXPERT-01", 5, 5, 5, 4, 5, "Exemplary child-friendly adaptation. Highly accessible for DLD."),
                ("EDUCATOR-EXPERT-02", 4, 5, 4, 5, 4, "Clear single-action instructions suitable for early childhood classroom."),
                ("RESEARCHER-EXPERT-03", 5, 4, 5, 4, 4, "Vocabulary substitution aligned with CEFR pre-A1. Safe length.")
            ]

            for i, t in enumerate(sample_tasks):
                exp = ExperimentRun(
                    learner_id=sample_learner.id,
                    task_id=t.id,
                    generation_mode="rule",
                    status="active"
                )
                db.add(exp)
                db.flush()

                ad = adaptation_service.create_initial_adaptation(db, exp, generation_mode="rule")

                for ev_code, age_sc, clar_sc, gram_sc, mean_sc, pers_sc, comm in benchmark_evaluators:
                    db.add(ExpertEvaluation(
                        adaptation_id=ad.id,
                        evaluator_code=ev_code,
                        age_appropriateness=age_sc,
                        clarity=clar_sc,
                        grammar_correctness=gram_sc,
                        meaning_preservation=mean_sc,
                        personalization_suitability=pers_sc,
                        comments=comm
                    ))
            db.commit()
            print("Seeded benchmark expert evaluations successfully.")

        print("Database seeding completed.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
