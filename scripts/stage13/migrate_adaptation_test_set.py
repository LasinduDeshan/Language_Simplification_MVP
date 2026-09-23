import os
import sys
import json
import shutil
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from app.datasets.common.draft_models import DraftAdaptationRecord, MigrationMappingRecord, MigrationDisposition
from app.datasets.common.paths import (
    ADAPTATION_TEST_SET_DIR, ADAPTATION_C1_SAMPLES_DIR, ADAPTATION_C2_AR_SAMPLES_DIR,
    ADAPTATION_C3_LOCAL_SAMPLES_DIR, ADAPTATION_ID_MAPPINGS_DIR, LEXICONS_EN_DIR,
    LEGACY_APPLICATION_TASKS, LEGACY_VOCABULARY
)

def migrate_adaptation_test_set():
    print("=== STARTING ADAPTATION TEST SET MIGRATION ===")
    
    temp_dir = os.path.join(ADAPTATION_TEST_SET_DIR, ".tmp_staging")
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(ADAPTATION_C1_SAMPLES_DIR, exist_ok=True)
    os.makedirs(ADAPTATION_C2_AR_SAMPLES_DIR, exist_ok=True)
    os.makedirs(ADAPTATION_C3_LOCAL_SAMPLES_DIR, exist_ok=True)
    os.makedirs(ADAPTATION_ID_MAPPINGS_DIR, exist_ok=True)
    os.makedirs(LEXICONS_EN_DIR, exist_ok=True)

    mappings = []
    rejections = []
    migrated_tasks = []

    # 1. Migrate Local Tasks (Component 3 Local Samples)
    if os.path.exists(LEGACY_APPLICATION_TASKS):
        with open(LEGACY_APPLICATION_TASKS, "r", encoding="utf-8") as f:
            legacy_tasks = json.load(f)

        print(f"Reading {len(legacy_tasks)} seed tasks from {LEGACY_APPLICATION_TASKS}")

        for task in legacy_tasks:
            try:
                task_code = task.get("task_code")
                target_id = f"C3-EN-{task_code}"
                
                # Determine protected answer
                prot_ans = None
                if task.get("acceptable_answers"):
                    prot_ans = task["acceptable_answers"][0]
                elif task.get("expected_sequence"):
                    prot_ans = " ".join(task["expected_sequence"])

                draft_rec = DraftAdaptationRecord(
                    activity_id=target_id,
                    legacy_task_code=task_code,
                    activity_owner="component_3",
                    language=task.get("language", "en"),
                    primary_domain=task.get("category", "vocabulary"),
                    activity_type=task.get("task_type", "standard"),
                    target_skill=task.get("target_skill"),
                    age_min=task.get("minimum_age", 4),
                    age_max=task.get("maximum_age", 8),
                    base_difficulty=task.get("base_difficulty", "medium"),
                    original_instruction=task.get("original_instruction", ""),
                    child_friendly_instruction=task.get("child_friendly_instruction"),
                    stimulus=task.get("stimulus"),
                    prompt=task.get("prompt"),
                    options=task.get("options"),
                    passage=task.get("passage"),
                    protected_answer=prot_ans,
                    protected_elements=task.get("vocabulary_targets", []) + task.get("grammar_targets", []),
                    acceptable_answers=task.get("acceptable_answers", []),
                    expected_concepts=task.get("expected_concepts", []),
                    adaptation_policy="instruction_only",
                    allowed_transformations=["simplify_instruction", "add_audio", "present_visual_cues"],
                    forbidden_transformations=["change_stimulus", "expose_answer", "change_target_skill"],
                    support_versions=task.get("support_versions"),
                    is_simulated=True,
                    research_eligible=False
                )
                
                migrated_tasks.append(draft_rec.model_dump(mode="json"))

                mappings.append(MigrationMappingRecord(
                    source_path="data/application_tasks/seed_tasks.json",
                    source_id=task_code,
                    target_layer="adaptation_test_set/en/component3_local_samples",
                    target_id=target_id,
                    disposition=MigrationDisposition.MIGRATED,
                    notes=f"Domain: {task.get('category')}, Skill: {task.get('target_skill')}"
                ).model_dump(mode="json"))

            except Exception as e:
                rejections.append({
                    "source_id": task.get("task_code", "UNKNOWN"),
                    "reason": str(e)
                })

    # Write staging file
    temp_target = os.path.join(temp_dir, "c3_local_tasks.json")
    with open(temp_target, "w", encoding="utf-8") as f:
        json.dump(migrated_tasks, f, indent=2)

    # 2. Atomic Publication for c3_local_tasks
    final_target = os.path.join(ADAPTATION_C3_LOCAL_SAMPLES_DIR, "c3_local_tasks.json")
    shutil.copyfile(temp_target, final_target)
    print(f"Atomically published {len(migrated_tasks)} tasks to {final_target}")

    # 3. Copy Component 1 fixtures
    src_c1 = os.path.join(BASE_DIR, "data", "integration_fixtures", "component1_inputs")
    if os.path.exists(src_c1):
        for fname in os.listdir(src_c1):
            if fname.endswith(".json"):
                shutil.copyfile(os.path.join(src_c1, fname), os.path.join(ADAPTATION_C1_SAMPLES_DIR, fname))
                mappings.append(MigrationMappingRecord(
                    source_path=f"data/integration_fixtures/component1_inputs/{fname}",
                    source_id=fname.replace(".json", ""),
                    target_layer="adaptation_test_set/en/component1_samples",
                    target_id=fname.replace(".json", ""),
                    disposition=MigrationDisposition.MIGRATED,
                    notes="Simulated Component 1 screening fixture"
                ).model_dump(mode="json"))

    # 4. Copy Component 2 AR fixtures
    src_c2 = os.path.join(BASE_DIR, "data", "integration_fixtures", "component2_ar_expected")
    if os.path.exists(src_c2):
        for fname in os.listdir(src_c2):
            if fname.endswith(".json"):
                shutil.copyfile(os.path.join(src_c2, fname), os.path.join(ADAPTATION_C2_AR_SAMPLES_DIR, fname))
                mappings.append(MigrationMappingRecord(
                    source_path=f"data/integration_fixtures/component2_ar_expected/{fname}",
                    source_id=fname.replace(".json", ""),
                    target_layer="adaptation_test_set/en/component2_ar_samples",
                    target_id=fname.replace(".json", ""),
                    disposition=MigrationDisposition.MIGRATED,
                    notes="Simulated Component 2 AR output fixture"
                ).model_dump(mode="json"))

    # 5. Copy vocabulary dictionary to lexicons/en
    if os.path.exists(LEGACY_VOCABULARY):
        lexicon_target = os.path.join(LEXICONS_EN_DIR, "tiered_vocabulary_lexicon.json")
        shutil.copyfile(LEGACY_VOCABULARY, lexicon_target)
        print(f"Copied vocabulary lexicon to {lexicon_target}")

    # 6. Save ID Mappings & Rejection Reports
    mapping_file = os.path.join(ADAPTATION_ID_MAPPINGS_DIR, "task_id_mappings.json")
    with open(mapping_file, "w", encoding="utf-8") as f:
        json.dump(mappings, f, indent=2)

    if rejections:
        rej_file = os.path.join(ADAPTATION_ID_MAPPINGS_DIR, "rejections_report.json")
        with open(rej_file, "w", encoding="utf-8") as f:
            json.dump(rejections, f, indent=2)

    # Clean up temp staging
    shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"Migration complete: {len(migrated_tasks)} tasks migrated, {len(rejections)} rejected.")
    return len(migrated_tasks), len(rejections)

if __name__ == "__main__":
    migrate_adaptation_test_set()
