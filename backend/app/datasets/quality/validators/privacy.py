"""Privacy, PII scanner, and interaction export allowlist validator."""
import uuid
import re
from typing import List, Dict, Any
from app.datasets.quality.enums import RuleSeverity, QualityDimension
from app.datasets.quality.schemas import QualityRuleResultV1
from app.datasets.quality.validators.base import BaseValidator

# Regexes for PII detection
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_REGEX = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')

FORBIDDEN_INTERACTION_FIELDS = {
    "learner_name", "first_name", "last_name", "email", "phone", "address",
    "parent_name", "therapist_name", "raw_screening_notes", "unrestricted_notes",
    "password_hash", "auth_token", "api_key"
}


class PrivacyValidator(BaseValidator):
    """Validates interaction export allowlist, PII exclusion, and immutable screening snapshot."""

    validator_name = "privacy_validator"
    validator_version = "1.0.0"

    def validate(self, record: Dict[str, Any], run_id: str = "adhoc_run") -> List[QualityRuleResultV1]:
        results: List[QualityRuleResultV1] = []
        record_id = record.get("interaction_id") or record.get("export_id") or record.get("record_id") or "UNKNOWN_RECORD"
        dataset_layer = "interaction_exports"

        # 1. PRIV-ALLOW-001: Forbidden field scanner
        found_forbidden = [k for k in FORBIDDEN_INTERACTION_FIELDS if k in record and record[k]]
        allowlist_passed = len(found_forbidden) == 0
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="PRIV-ALLOW-001",
            validator_name=self.validator_name,
            dimension=QualityDimension.SAFETY_ANSWER_BOUNDARY,
            severity=RuleSeverity.CRITICAL,
            passed=allowlist_passed,
            threshold="strict_allowlist",
            message="No forbidden personal fields present in export." if allowlist_passed else f"Critical privacy leak: Forbidden fields {found_forbidden} detected.",
            recommended_action=None if allowlist_passed else "Quarantine export immediately and purge un-allowlisted personal data."
        ))

        # 2. PRIV-PII-002: PII regex scanner in text content fields
        id_keys = {"interaction_id", "record_id", "activity_id", "run_id", "schema_version", "dataset_version", "created_at", "validated_at", "completed_at"}
        text_values = []
        for k, v in record.items():
            if k not in id_keys and isinstance(v, str):
                text_values.append(v)
            elif isinstance(v, dict):
                text_values.extend([str(sub_v) for sub_k, sub_v in v.items() if sub_k not in id_keys and isinstance(sub_v, str)])

        combined_text = " ".join(text_values)
        found_emails = EMAIL_REGEX.findall(combined_text)
        found_phones = PHONE_REGEX.findall(combined_text)
        pii_passed = len(found_emails) == 0 and len(found_phones) == 0
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="PRIV-PII-002",
            validator_name=self.validator_name,
            dimension=QualityDimension.SAFETY_ANSWER_BOUNDARY,
            severity=RuleSeverity.CRITICAL,
            passed=pii_passed,
            threshold="zero_pii_patterns",
            message="Zero PII regex patterns detected." if pii_passed else f"Critical PII pattern detected: emails={found_emails}, phones={found_phones}.",
            recommended_action=None if pii_passed else "Quarantine export and redact PII patterns."
        ))

        # 3. PRIV-RISK-003: Screening risk read-only snapshot verification
        risk_level = record.get("screening_risk_level")
        risk_passed = True
        if risk_level is not None and risk_level not in ("low", "moderate", "high", "unknown"):
            risk_passed = False

        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="PRIV-RISK-003",
            validator_name=self.validator_name,
            dimension=QualityDimension.METADATA_INTEGRITY,
            severity=RuleSeverity.CRITICAL,
            passed=risk_passed,
            threshold="valid_c1_snapshot",
            message="Screening risk level conforms to Component 1 read-only contract." if risk_passed else f"Invalid screening risk '{risk_level}'.",
            recommended_action=None if risk_passed else "Ensure screening risk is an immutable snapshot from Component 1."
        ))

        # 4. PRIV-C4-004: Component 4 trend contract
        trend = record.get("trend") or record.get("preliminary_trend")
        c4_passed = True
        if trend and "longitudinal_diagnosis" in str(trend).lower():
            c4_passed = False

        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="PRIV-C4-004",
            validator_name=self.validator_name,
            dimension=QualityDimension.SAFETY_ANSWER_BOUNDARY,
            severity=RuleSeverity.CRITICAL,
            passed=c4_passed,
            threshold="local_preliminary_only",
            message="Export adheres to Component 4 local preliminary trend boundary." if c4_passed else "Export claims longitudinal clinical diagnosis, violating Component 3/4 boundary.",
            recommended_action=None if c4_passed else "Use local_preliminary_trend only."
        ))

        return results
