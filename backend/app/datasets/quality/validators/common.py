"""Common validators applying across all dataset layers."""
import uuid
from typing import List, Dict, Any
from app.datasets.quality.enums import RuleSeverity, QualityDimension
from app.datasets.quality.schemas import QualityRuleResultV1
from app.datasets.quality.validators.base import BaseValidator
from app.datasets.common.identifiers import is_valid_activity_id, is_valid_pair_id, is_valid_lexicon_id


class CommonRecordValidator(BaseValidator):
    """Validates common metadata, schema versions, identifiers, and language codes."""

    validator_name = "common_record_validator"
    validator_version = "1.0.0"

    def validate(self, record: Dict[str, Any], run_id: str = "adhoc_run") -> List[QualityRuleResultV1]:
        results: List[QualityRuleResultV1] = []
        record_id = record.get("activity_id") or record.get("pair_id") or record.get("entry_id") or record.get("interaction_id") or record.get("record_id") or "UNKNOWN_RECORD"
        dataset_layer = record.get("dataset_layer", "unknown_layer")

        # 1. COMM-SCHEMA-001: Schema version check
        schema_ver = record.get("schema_version")
        schema_passed = schema_ver == "1.0.0"
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="COMM-SCHEMA-001",
            validator_name=self.validator_name,
            dimension=QualityDimension.METADATA_INTEGRITY,
            severity=RuleSeverity.ERROR,
            passed=schema_passed,
            threshold="1.0.0",
            message=f"Schema version is '{schema_ver}'." if schema_passed else f"Invalid schema version '{schema_ver}'. Expected '1.0.0'.",
            recommended_action=None if schema_passed else "Upgrade record to schema version 1.0.0."
        ))

        # 2. COMM-ID-002: Identifier format check
        id_passed = True
        id_msg = f"Valid identifier format '{record_id}'."
        if "activity_id" in record:
            id_passed = is_valid_activity_id(record_id)
        elif "pair_id" in record:
            id_passed = is_valid_pair_id(record_id)
        elif "entry_id" in record:
            id_passed = is_valid_lexicon_id(record_id)
        
        if not id_passed:
            id_msg = f"Invalid identifier format '{record_id}'."

        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="COMM-ID-002",
            validator_name=self.validator_name,
            dimension=QualityDimension.METADATA_INTEGRITY,
            severity=RuleSeverity.ERROR,
            passed=id_passed,
            threshold="valid_prefix_format",
            message=id_msg,
            recommended_action=None if id_passed else "Correct identifier prefix to match governed convention."
        ))

        # 3. COMM-LANG-003: Language code check (English MVP)
        lang = record.get("language")
        lang_passed = lang in ("en", "English", "eng")
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="COMM-LANG-003",
            validator_name=self.validator_name,
            dimension=QualityDimension.METADATA_INTEGRITY,
            severity=RuleSeverity.ERROR,
            passed=lang_passed,
            threshold="en",
            message=f"Language code is '{lang}'." if lang_passed else f"Unexpected language '{lang}'. Expected 'en' for English MVP.",
            recommended_action=None if lang_passed else "Ensure record is classified under English ('en')."
        ))

        # 4. COMM-META-004: Metadata completeness check
        source_meta = record.get("source_metadata") or record.get("source", {})
        gov_meta = record.get("governance", {})
        meta_passed = bool(source_meta and gov_meta)
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="COMM-META-004",
            validator_name=self.validator_name,
            dimension=QualityDimension.METADATA_INTEGRITY,
            severity=RuleSeverity.WARNING,
            passed=meta_passed,
            threshold="complete_blocks",
            message="Source and governance metadata blocks are present." if meta_passed else "Missing source or governance metadata blocks.",
            recommended_action=None if meta_passed else "Populate required source and governance metadata blocks."
        ))

        return results
