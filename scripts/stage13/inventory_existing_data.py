import os
import sys
import json
import csv
import sqlite3

# Add backend directory to path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from app.database.db import SessionLocal
from app.database.models import (
    LearnerProfile, Task, ActivitySession, Attempt, TaskResult,
    Adaptation, ValidationResult, ExpertEvaluation, ExperimentRun,
    LanguageObservation, IntegrationEvent
)

def build_inventory():
    inventory = []

    # 1. Inspect Files in data/
    # application_tasks
    tasks_file = os.path.join(BASE_DIR, "data", "application_tasks", "seed_tasks.json")
    if os.path.exists(tasks_file):
        with open(tasks_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        inventory.append({
            "current_path_or_table": "data/application_tasks/seed_tasks.json",
            "record_count": len(data),
            "current_purpose": "Seed library of learning activities across 4 domains (vocab, grammar, comp, instruction)",
            "data_owner": "component_3",
            "proposed_layer": "adaptation_test_set/en/component3_local_samples",
            "contains_personal_data": "no",
            "contains_raw_response": "no",
            "contains_protected_answer": "yes",
            "is_simulated": "true",
            "research_eligible": "false",
            "source_or_provenance": "team_authored_mvp_v2",
            "migration_action": "transform_and_copy",
            "target_path": "data/adaptation_test_set/en/component3_local_samples/c3_local_tasks.json",
            "validation_notes": "Contains protected answers; child-facing interfaces must mask them"
        })

    # development_scenarios
    scenarios_file = os.path.join(BASE_DIR, "data", "development_scenarios", "seed_scenarios.json")
    if os.path.exists(scenarios_file):
        with open(scenarios_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        inventory.append({
            "current_path_or_table": "data/development_scenarios/seed_scenarios.json",
            "record_count": len(data),
            "current_purpose": "Simulation scenarios coupling learners and tasks for multi-attempt state testing",
            "data_owner": "component_3",
            "proposed_layer": "adaptation_test_set/draft_contracts",
            "contains_personal_data": "no",
            "contains_raw_response": "no",
            "contains_protected_answer": "yes",
            "is_simulated": "true",
            "research_eligible": "false",
            "source_or_provenance": "team_authored_test_scenarios",
            "migration_action": "retain_as_test_fixture",
            "target_path": "data/adaptation_test_set/draft_contracts/development_scenarios.json",
            "validation_notes": "Synthetic testing fixture for developer playground"
        })

    # grammar_test_cases
    grammar_file = os.path.join(BASE_DIR, "data", "grammar_test_cases", "seed_grammar_cases.json")
    if os.path.exists(grammar_file):
        with open(grammar_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        inventory.append({
            "current_path_or_table": "data/grammar_test_cases/seed_grammar_cases.json",
            "record_count": len(data),
            "current_purpose": "Benchmark child transcript grammar evaluation cases with error annotations",
            "data_owner": "component_3",
            "proposed_layer": "simplification_corpus/annotations",
            "contains_personal_data": "no",
            "contains_raw_response": "no",
            "contains_protected_answer": "no",
            "is_simulated": "true",
            "research_eligible": "false",
            "source_or_provenance": "linguistic_expert_rubric",
            "migration_action": "transform_and_copy",
            "target_path": "data/simplification_corpus/annotations/grammar_error_annotations.json",
            "validation_notes": "Annotated grammatical error patterns"
        })

    # learner_profiles
    learners_file = os.path.join(BASE_DIR, "data", "learner_profiles", "seed_learners.json")
    if os.path.exists(learners_file):
        with open(learners_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        inventory.append({
            "current_path_or_table": "data/learner_profiles/seed_learners.json",
            "record_count": len(data),
            "current_purpose": "Seed simulated learner profiles with Component 1 screening risk snapshots",
            "data_owner": "component_1",
            "proposed_layer": "excluded_from_reusable_datasets",
            "contains_personal_data": "pseudonymous_only",
            "contains_raw_response": "no",
            "contains_protected_answer": "no",
            "is_simulated": "true",
            "research_eligible": "false",
            "source_or_provenance": "simulated_component1_profiles",
            "migration_action": "retain_in_database_only",
            "target_path": "backend/app/database/seed.py",
            "validation_notes": "Kept strictly outside public/reusable dataset layers"
        })

    # vocabulary_dictionary
    vocab_file = os.path.join(BASE_DIR, "data", "vocabulary_dictionary", "seed_vocabulary.json")
    if os.path.exists(vocab_file):
        with open(vocab_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        inventory.append({
            "current_path_or_table": "data/vocabulary_dictionary/seed_vocabulary.json",
            "record_count": len(data),
            "current_purpose": "Age-tiered vocabulary simplification substitution lexicon (Tier 1/2)",
            "data_owner": "component_3",
            "proposed_layer": "lexicons/en",
            "contains_personal_data": "no",
            "contains_raw_response": "no",
            "contains_protected_answer": "no",
            "is_simulated": "false",
            "research_eligible": "false",
            "source_or_provenance": "lexical_simplification_dictionary",
            "migration_action": "copy",
            "target_path": "data/lexicons/en/tiered_vocabulary_lexicon.json",
            "validation_notes": "Tiered vocabulary lexicon for word substitution"
        })

    # integration_fixtures (Component 1, Component 2 AR, Component 4)
    c1_fixtures_dir = os.path.join(BASE_DIR, "data", "integration_fixtures", "component1_inputs")
    c1_count = len([f for f in os.listdir(c1_fixtures_dir) if f.endswith(".json")]) if os.path.exists(c1_fixtures_dir) else 0
    inventory.append({
        "current_path_or_table": "data/integration_fixtures/component1_inputs/",
        "record_count": c1_count,
        "current_purpose": "Simulated Component 1 screening profile input contracts",
        "data_owner": "component_1",
        "proposed_layer": "adaptation_test_set/en/component1_samples",
        "contains_personal_data": "pseudonymous_only",
        "contains_raw_response": "no",
        "contains_protected_answer": "no",
        "is_simulated": "true",
        "research_eligible": "false",
        "source_or_provenance": "component1_mock_contracts",
        "migration_action": "copy_and_map",
        "target_path": "data/adaptation_test_set/en/component1_samples/",
        "validation_notes": "Component 1 owned DLD risk screening profiles"
    })

    c2_fixtures_dir = os.path.join(BASE_DIR, "data", "integration_fixtures", "component2_ar_expected")
    c2_count = len([f for f in os.listdir(c2_fixtures_dir) if f.endswith(".json")]) if os.path.exists(c2_fixtures_dir) else 0
    inventory.append({
        "current_path_or_table": "data/integration_fixtures/component2_ar_expected/",
        "record_count": c2_count,
        "current_purpose": "Expected Augmented Reality 3D spatial instruction contracts for Component 2",
        "data_owner": "component_2_ar",
        "proposed_layer": "adaptation_test_set/en/component2_ar_samples",
        "contains_personal_data": "no",
        "contains_raw_response": "no",
        "contains_protected_answer": "no",
        "is_simulated": "true",
        "research_eligible": "false",
        "source_or_provenance": "component2_ar_mock_contracts",
        "migration_action": "copy_and_map",
        "target_path": "data/adaptation_test_set/en/component2_ar_samples/",
        "validation_notes": "Preserves AR 3D object cues and action sequencing"
    })

    # research_exports
    research_dir = os.path.join(BASE_DIR, "data", "research_exports")
    if os.path.exists(research_dir):
        files = [f for f in os.listdir(research_dir) if os.path.isfile(os.path.join(research_dir, f))]
        inventory.append({
            "current_path_or_table": "data/research_exports/",
            "record_count": len(files),
            "current_purpose": "Historical Stage 8/11 research experiment dumps (CSV/JSON/ZIP)",
            "data_owner": "component_3",
            "proposed_layer": "interaction_dataset/deidentified_exports",
            "contains_personal_data": "pseudonymous_only",
            "contains_raw_response": "yes",
            "contains_protected_answer": "yes",
            "is_simulated": "true",
            "research_eligible": "false",
            "source_or_provenance": "historical_evaluation_exports",
            "migration_action": "retain_in_private_storage",
            "target_path": "data/interaction_dataset/deidentified_exports/",
            "validation_notes": "Historical benchmark exports; kept ignored by Git"
        })

    # 2. Inspect Database Tables
    db = SessionLocal()
    try:
        tables = [
            (LearnerProfile, "learner_profiles", "component_1", "excluded_from_reusable_datasets", "pseudonymous_only", "no", "no", "retain_in_database_only", "DB Operational Storage"),
            (Task, "tasks", "component_3", "adaptation_test_set/en/component3_local_samples", "no", "no", "yes", "transform_and_copy", "data/adaptation_test_set/en/component3_local_samples/"),
            (ActivitySession, "activity_sessions", "component_3", "interaction_dataset/private", "pseudonymous_only", "yes", "no", "export_private_snapshot", "data/interaction_dataset/private/"),
            (Attempt, "attempts", "component_3", "interaction_dataset/private", "pseudonymous_only", "yes", "no", "export_private_snapshot", "data/interaction_dataset/private/"),
            (TaskResult, "task_results", "component_3", "interaction_dataset/private", "pseudonymous_only", "yes", "no", "export_private_snapshot", "data/interaction_dataset/private/"),
            (Adaptation, "adaptations", "component_3", "simplification_corpus/en/draft", "no", "no", "no", "extract_simplification_pairs", "data/simplification_corpus/en/draft/"),
            (ValidationResult, "validation_results", "component_3", "simplification_corpus/annotations", "no", "no", "no", "extract_annotations", "data/simplification_corpus/annotations/"),
            (ExpertEvaluation, "expert_evaluations", "component_3", "interaction_dataset/private", "pseudonymous_only", "no", "no", "retain_in_database_only", "DB Operational Storage"),
            (ExperimentRun, "experiment_runs", "component_3", "interaction_dataset/private", "pseudonymous_only", "yes", "no", "retain_in_database_only", "DB Operational Storage"),
            (LanguageObservation, "language_observations", "component_3", "simplification_corpus/annotations", "no", "no", "no", "extract_annotations", "data/simplification_corpus/annotations/"),
            (IntegrationEvent, "integration_events", "component_3", "interaction_dataset/private", "pseudonymous_only", "no", "no", "retain_in_database_only", "DB Operational Storage")
        ]

        for model, t_name, owner, layer, pii, raw_resp, prot_ans, action, target_p in tables:
            cnt = db.query(model).count()
            inventory.append({
                "current_path_or_table": f"db_table:{t_name}",
                "record_count": cnt,
                "current_purpose": f"Relational database storage for {t_name}",
                "data_owner": owner,
                "proposed_layer": layer,
                "contains_personal_data": pii,
                "contains_raw_response": raw_resp,
                "contains_protected_answer": prot_ans,
                "is_simulated": "true",
                "research_eligible": "false",
                "source_or_provenance": "relational_db_sqlite",
                "migration_action": action,
                "target_path": target_p,
                "validation_notes": f"Database table {t_name} is operational source of truth"
            })
    finally:
        db.close()

    # Write to CSV
    csv_file = os.path.join(BASE_DIR, "docs", "stage13_dataset_inventory.csv")
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    
    fieldnames = [
        "current_path_or_table", "record_count", "current_purpose", "data_owner",
        "proposed_layer", "contains_personal_data", "contains_raw_response",
        "contains_protected_answer", "is_simulated", "research_eligible",
        "source_or_provenance", "migration_action", "target_path", "validation_notes"
    ]
    
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(inventory)

    print(f"Successfully generated inventory with {len(inventory)} entries in {csv_file}")
    return inventory

if __name__ == "__main__":
    build_inventory()
