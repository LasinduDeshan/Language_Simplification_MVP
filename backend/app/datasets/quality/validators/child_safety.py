"""Child safety and protected answer leakage validator."""
import uuid
import re
from typing import List, Dict, Any
from app.datasets.quality.enums import RuleSeverity, QualityDimension
from app.datasets.quality.schemas import QualityRuleResultV1
from app.datasets.quality.validators.base import BaseValidator

# Inappropriate words filter for ages 4-8
INAPPROPRIATE_TERMS = {
    "violence", "weapon", "kill", "die", "death", "blood", "murder", "gun", "knife",
    "swear", "curse", "drug", "alcohol", "beer", "wine", "smoke", "gamble"
}

FORBIDDEN_CHILD_VIEW_KEYS = {
    "protected_answer", "acceptable_answers", "scoring_rubric",
    "evaluation_notes", "teacher_notes", "rubric", "answer_key", "internal_diagnostics"
}


class ChildSafetyValidator(BaseValidator):
    """Validates that child-safe views never expose protected evaluation metadata and contain safe content."""

    validator_name = "child_safety_validator"
    validator_version = "1.0.0"

    def validate(self, record: Dict[str, Any], run_id: str = "adhoc_run") -> List[QualityRuleResultV1]:
        results: List[QualityRuleResultV1] = []
        record_id = record.get("activity_id") or record.get("pair_id") or record.get("entry_id") or "UNKNOWN_RECORD"
        dataset_layer = record.get("dataset_layer", "adaptation_test_set")

        # 1. SAFE-LEAK-001: Protected answer leakage check
        leaked_keys = []
        if "child_view" in record:
            child_view = record["child_view"]
            for key in FORBIDDEN_CHILD_VIEW_KEYS:
                if key in child_view and child_view[key]:
                    leaked_keys.append(key)
        
        leak_passed = len(leaked_keys) == 0
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="SAFE-LEAK-001",
            validator_name=self.validator_name,
            dimension=QualityDimension.SAFETY_ANSWER_BOUNDARY,
            severity=RuleSeverity.CRITICAL,
            passed=leak_passed,
            threshold="zero_leakage",
            message="Zero protected evaluation fields in child view." if leak_passed else f"Critical leakage: Protected fields {leaked_keys} found in child view.",
            recommended_action=None if leak_passed else "Purge protected answer keys from child serialization view immediately."
        ))

        # 2. SAFE-TEXT-002: Inappropriate content scanner
        all_text = " ".join([
            str(record.get("instruction", "")),
            str(record.get("original_text", "")),
            str(record.get("simplified_text", "")),
            str(record.get("explanation", "")),
            str(record.get("example_sentence", ""))
        ]).lower()

        found_terms = [t for t in INAPPROPRIATE_TERMS if re.search(r'\b' + re.escape(t) + r'\b', all_text)]
        content_passed = len(found_terms) == 0
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="SAFE-TEXT-002",
            validator_name=self.validator_name,
            dimension=QualityDimension.SAFETY_ANSWER_BOUNDARY,
            severity=RuleSeverity.ERROR,
            passed=content_passed,
            threshold="zero_inappropriate_terms",
            message="Text content is child-friendly." if content_passed else f"Potentially inappropriate terms detected: {found_terms}.",
            recommended_action=None if content_passed else "Review text content and replace inappropriate terms with child-friendly phrasing."
        ))

        return results
