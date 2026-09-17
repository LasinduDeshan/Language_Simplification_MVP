import os
import json
from datetime import datetime
from app.database.db import SessionLocal, engine, Base
from app.database.models import LearnerProfile, Task, PerformancePattern

BASE_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data"))

def seed_database():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Learner Profiles
        learners_file = os.path.join(BASE_DATA_DIR, "learner_profiles", "seed_learners.json")
        if os.path.exists(learners_file):
            with open(learners_file, "r", encoding="utf-8") as f:
                learners_data = json.load(f)
            
            for l_data in learners_data:
                existing = db.query(LearnerProfile).filter(LearnerProfile.learner_code == l_data["learner_code"]).first()
                if not existing:
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
            print(f"Seeded learner profiles successfully.")

        # 2. Seed Tasks
        tasks_file = os.path.join(BASE_DATA_DIR, "application_tasks", "seed_tasks.json")
        if os.path.exists(tasks_file):
            with open(tasks_file, "r", encoding="utf-8") as f:
                tasks_data = json.load(f)

            for t_data in tasks_data:
                existing = db.query(Task).filter(Task.task_code == t_data["task_code"]).first()
                if not existing:
                    task = Task(
                        task_code=t_data["task_code"],
                        title=t_data["title"],
                        task_type=t_data["task_type"],
                        language=t_data.get("language", "en"),
                        learning_objective=t_data["learning_objective"],
                        original_instruction=t_data["original_instruction"],
                        minimum_age=t_data.get("minimum_age", 4),
                        maximum_age=t_data.get("maximum_age", 8),
                        base_difficulty=t_data.get("base_difficulty", "medium"),
                        expected_concepts=t_data.get("expected_concepts", []),
                        acceptable_answers=t_data.get("acceptable_answers", []),
                        protected_answers=t_data.get("protected_answers", {}),
                        answer_presentation_policy=t_data.get("answer_presentation_policy", {}),
                        vocabulary_targets=t_data.get("vocabulary_targets", []),
                        grammar_targets=t_data.get("grammar_targets", []),
                        ar_metadata=t_data.get("ar_metadata", {}),
                        is_active=t_data.get("is_active", True)
                    )
                    db.add(task)
            db.commit()
            print(f"Seeded application tasks successfully.")

        # 3. Seed Performance Patterns for Learners from Scenarios
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
                        exists = db.query(PerformancePattern).filter(
                            PerformancePattern.learner_id == learner.id,
                            PerformancePattern.pattern_code == p_code
                        ).first()
                        if not exists:
                            db.add(PerformancePattern(
                                learner_id=learner.id,
                                pattern_type="grammar",
                                pattern_code=p_code,
                                frequency=2,
                                confidence=0.85,
                                successful_support=comp4.get("successful_support", "sentence_starter"),
                                recommended_support=comp4.get("recommended_support", "moderate"),
                                source="simulator_component_4"
                            ))
                    for v_code in comp4.get("repeated_vocabulary_issues", []):
                        exists = db.query(PerformancePattern).filter(
                            PerformancePattern.learner_id == learner.id,
                            PerformancePattern.pattern_code == v_code
                        ).first()
                        if not exists:
                            db.add(PerformancePattern(
                                learner_id=learner.id,
                                pattern_type="vocabulary",
                                pattern_code=v_code,
                                frequency=2,
                                confidence=0.85,
                                successful_support=comp4.get("successful_support", "picture_cue"),
                                recommended_support=comp4.get("recommended_support", "moderate"),
                                source="simulator_component_4"
                            ))
            db.commit()
            print("Seeded baseline performance patterns successfully.")

        print("Database seeding completed.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
