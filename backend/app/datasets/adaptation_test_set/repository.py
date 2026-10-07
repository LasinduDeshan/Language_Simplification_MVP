import os
import json
from typing import List, Dict, Any, Optional, Union
from app.datasets.common.draft_models import DraftAdaptationRecord
from app.datasets.adaptation_test_set.schemas import AdaptationRecordV1, ChildSafeActivityView
from app.datasets.common.permissions import filter_child_safe_activity
from app.datasets.common.paths import (
    ADAPTATION_C3_LOCAL_SAMPLES_DIR, ADAPTATION_RELEASE_DIR, LEGACY_APPLICATION_TASKS
)

class AdaptationTestSetRepository:
    """
    Repository interface for accessing Adaptation Test Set activities.
    Supports DATASET_SCHEMA_MODE='v1' (default) and 'stage13_compat'.
    Component 3 owns this test set for development and evaluation.
    Component 3 does NOT own the production Activity Bank.
    """
    def __init__(self, data_file: Optional[str] = None):
        schema_mode = os.environ.get("DATASET_SCHEMA_MODE", "v1")
        if data_file is None:
            if schema_mode == "stage13_compat":
                c3_file = os.path.join(ADAPTATION_C3_LOCAL_SAMPLES_DIR, "c3_local_tasks.json")
                data_file = c3_file if os.path.exists(c3_file) else LEGACY_APPLICATION_TASKS
            else:
                v1_file = os.path.join(ADAPTATION_RELEASE_DIR, "0.1.0", "adaptation_test_set.json")
                if os.path.exists(v1_file):
                    data_file = v1_file
                else:
                    c3_file = os.path.join(ADAPTATION_C3_LOCAL_SAMPLES_DIR, "c3_local_tasks.json")
                    data_file = c3_file if os.path.exists(c3_file) else LEGACY_APPLICATION_TASKS

        self.data_file = data_file
        self.schema_mode = schema_mode
        self._cache: Optional[List[Union[AdaptationRecordV1, DraftAdaptationRecord]]] = None

    def _load_records(self) -> List[Union[AdaptationRecordV1, DraftAdaptationRecord]]:
        if self._cache is not None:
            return self._cache

        if not os.path.exists(self.data_file):
            self._cache = []
            return self._cache

        with open(self.data_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        records = []
        for item in raw_data:
            if self.schema_mode == "stage13_compat" or "schema_version" not in item:
                # Stage 13 draft compatibility
                if "activity_id" in item:
                    records.append(DraftAdaptationRecord(**item))
                else:
                    act_id = f"C3-EN-{item.get('task_code', 'TASK')}"
                    rec = DraftAdaptationRecord(
                        activity_id=act_id,
                        legacy_task_code=item.get("task_code"),
                        activity_owner="component_3",
                        language=item.get("language", "en"),
                        primary_domain=item.get("category", "vocabulary"),
                        activity_type=item.get("task_type", "standard"),
                        target_skill=item.get("target_skill"),
                        age_min=item.get("minimum_age", 4),
                        age_max=item.get("maximum_age", 8),
                        base_difficulty=item.get("base_difficulty", "medium"),
                        original_instruction=item.get("original_instruction", ""),
                        child_friendly_instruction=item.get("child_friendly_instruction"),
                        stimulus=item.get("stimulus"),
                        prompt=item.get("prompt"),
                        options=item.get("options"),
                        passage=item.get("passage"),
                        protected_answer=item.get("acceptable_answers", [""])[0] if item.get("acceptable_answers") else None,
                        acceptable_answers=item.get("acceptable_answers", []),
                        expected_concepts=item.get("expected_concepts", []),
                        support_versions=item.get("support_versions")
                    )
                    records.append(rec)
            else:
                # V1 Schema
                records.append(AdaptationRecordV1(**item))

        self._cache = records
        return self._cache

    def get_all_activities(self) -> List[Union[AdaptationRecordV1, DraftAdaptationRecord]]:
        return self._load_records()

    def get_child_activity(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns a sanitized child-safe view: protected answers and internal metadata
        are strictly stripped out before presentation to children.
        """
        for rec in self._load_records():
            legacy_code = getattr(rec, "legacy_task_code", None)
            if rec.activity_id == activity_id or legacy_code == activity_id:
                data = rec.model_dump(mode="json")
                return filter_child_safe_activity(data)
        return None

    def get_full_activity_record(self, activity_id: str) -> Optional[Union[AdaptationRecordV1, DraftAdaptationRecord]]:
        """
        Internal full representation intended only for authorized adult/evaluator services.
        """
        for rec in self._load_records():
            legacy_code = getattr(rec, "legacy_task_code", None)
            if rec.activity_id == activity_id or legacy_code == activity_id:
                return rec
        return None

    def reload(self):
        self._cache = None
