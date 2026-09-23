import os
import sys
import json
import shutil
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from app.database.db import SessionLocal
from app.database.models import Adaptation
from app.datasets.common.draft_models import DraftSimplificationPair, MigrationMappingRecord, MigrationDisposition
from app.datasets.common.paths import (
    SIMPLIFICATION_CORPUS_DIR, SIMPLIFICATION_DRAFT_DIR, SIMPLIFICATION_ANNOTATIONS_DIR,
    SIMPLIFICATION_ID_MAPPINGS_DIR, LEGACY_APPLICATION_TASKS, LEGACY_GRAMMAR_CASES
)

def migrate_simplification_pairs():
    print("=== STARTING SIMPLIFICATION CORPUS MIGRATION ===")

    temp_dir = os.path.join(SIMPLIFICATION_CORPUS_DIR, ".tmp_staging")
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(SIMPLIFICATION_DRAFT_DIR, exist_ok=True)
    os.makedirs(SIMPLIFICATION_ANNOTATIONS_DIR, exist_ok=True)
    os.makedirs(SIMPLIFICATION_ID_MAPPINGS_DIR, exist_ok=True)

    pairs = []
    mappings = []
    pair_counter = 1

    # 1. Extract sentence pairs from seed_tasks.json
    if os.path.exists(LEGACY_APPLICATION_TASKS):
        with open(LEGACY_APPLICATION_TASKS, "r", encoding="utf-8") as f:
            tasks = json.load(f)

        for task in tasks:
            orig = task.get("original_instruction")
            simp = task.get("child_friendly_instruction")
            task_code = task.get("task_code")

            if orig and simp and orig.strip() != simp.strip():
                pair_id = f"SIMP-EN-{pair_counter:04d}"
                pair_counter += 1

                p = DraftSimplificationPair(
                    pair_id=pair_id,
                    source_activity_id=f"C3-EN-{task_code}",
                    language=task.get("language", "en"),
                    content_type="instruction",
                    original_text=orig,
                    simplified_text=simp,
                    support_level="moderate",
                    age_min=task.get("minimum_age", 4),
                    age_max=task.get("maximum_age", 8),
                    operations=["lexical_substitution", "syntax_simplification"],
                    protected_meaning_units=task.get("vocabulary_targets", []) + task.get("grammar_targets", []),
                    source_type="team_authored",
                    validation_status="draft",
                    research_eligible=False
                )
                pairs.append(p.model_dump(mode="json"))

                mappings.append(MigrationMappingRecord(
                    source_path="data/application_tasks/seed_tasks.json",
                    source_id=f"{task_code}:instruction_pair",
                    target_layer="simplification_corpus/en/draft",
                    target_id=pair_id,
                    disposition=MigrationDisposition.MIGRATED,
                    notes=f"Extracted from task {task_code}"
                ).model_dump(mode="json"))

            # Support versions (mild, moderate, strong)
            sup_versions = task.get("support_versions") or {}
            for level, text in sup_versions.items():
                if orig and text and orig.strip() != text.strip():
                    pair_id = f"SIMP-EN-{pair_counter:04d}"
                    pair_counter += 1

                    p = DraftSimplificationPair(
                        pair_id=pair_id,
                        source_activity_id=f"C3-EN-{task_code}",
                        language=task.get("language", "en"),
                        content_type="instruction",
                        original_text=orig,
                        simplified_text=text,
                        support_level=level if level in ["mild", "moderate", "strong"] else "strong",
                        age_min=task.get("minimum_age", 4),
                        age_max=task.get("maximum_age", 8),
                        operations=["scaffolding", "visual_cues" if level == "strong" else "lexical_substitution"],
                        source_type="team_authored",
                        validation_status="draft",
                        research_eligible=False
                    )
                    pairs.append(p.model_dump(mode="json"))

                    mappings.append(MigrationMappingRecord(
                        source_path="data/application_tasks/seed_tasks.json",
                        source_id=f"{task_code}:support_{level}",
                        target_layer="simplification_corpus/en/draft",
                        target_id=pair_id,
                        disposition=MigrationDisposition.MIGRATED,
                        notes=f"Tiered support variant ({level}) for task {task_code}"
                    ).model_dump(mode="json"))

    # 2. Extract database adaptation pairs if available
    db = SessionLocal()
    try:
        from app.database.models import ActivitySession, ExperimentRun
        db_adaptations = db.query(Adaptation).all()
        for ad in db_adaptations:
            orig = None
            task_code = None
            if ad.activity_session_id:
                sess = db.query(ActivitySession).filter(ActivitySession.id == ad.activity_session_id).first()
                if sess and sess.task:
                    orig = sess.task.original_instruction
                    task_code = sess.task.task_code
            elif ad.experiment_run_id:
                exp = db.query(ExperimentRun).filter(ExperimentRun.id == ad.experiment_run_id).first()
                if exp and exp.task:
                    orig = exp.task.original_instruction
                    task_code = exp.task.task_code

            simp = ad.child_instruction
            if orig and simp and orig.strip() != simp.strip():
                pair_id = f"SIMP-EN-{pair_counter:04d}"
                pair_counter += 1

                p = DraftSimplificationPair(
                    pair_id=pair_id,
                    source_activity_id=task_code,
                    language="en",
                    content_type="instruction",
                    original_text=orig,
                    simplified_text=simp,
                    support_level=ad.support_level or "moderate",
                    age_min=4,
                    age_max=8,
                    operations=[ad.generation_method or "rule_simplification"],
                    source_type="adaptation_engine_generated",
                    validation_status="draft",
                    research_eligible=False
                )
                pairs.append(p.model_dump(mode="json"))
                mappings.append(MigrationMappingRecord(
                    source_path="db_table:adaptations",
                    source_id=ad.id,
                    target_layer="simplification_corpus/en/draft",
                    target_id=pair_id,
                    disposition=MigrationDisposition.MIGRATED,
                    notes=f"Engine adaptation from session {ad.activity_session_id}"
                ).model_dump(mode="json"))
    finally:
        db.close()

    # Write staging file
    temp_target = os.path.join(temp_dir, "draft_pairs.json")
    with open(temp_target, "w", encoding="utf-8") as f:
        json.dump(pairs, f, indent=2)

    # 3. Atomic Publication
    final_target = os.path.join(SIMPLIFICATION_DRAFT_DIR, "draft_pairs.json")
    shutil.copyfile(temp_target, final_target)
    print(f"Atomically published {len(pairs)} simplification pairs to {final_target}")

    # 4. Migrate grammar cases to annotations
    if os.path.exists(LEGACY_GRAMMAR_CASES):
        annot_target = os.path.join(SIMPLIFICATION_ANNOTATIONS_DIR, "grammar_error_annotations.json")
        shutil.copyfile(LEGACY_GRAMMAR_CASES, annot_target)
        print(f"Copied grammar test cases to {annot_target}")

    # 5. Save mappings
    mapping_file = os.path.join(SIMPLIFICATION_ID_MAPPINGS_DIR, "corpus_id_mappings.json")
    with open(mapping_file, "w", encoding="utf-8") as f:
        json.dump(mappings, f, indent=2)

    # Clean up staging
    shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"Simplification Corpus migration complete: {len(pairs)} pairs published.")
    return len(pairs)

if __name__ == "__main__":
    migrate_simplification_pairs()
