"""De-identified interaction export dataset quality validator."""
from typing import List, Dict, Any
from app.datasets.quality.schemas import QualityRuleResultV1
from app.datasets.quality.validators.base import BaseValidator
from app.datasets.quality.validators.privacy import PrivacyValidator


class InteractionExportValidator(BaseValidator):
    """Validates de-identified interaction records for privacy compliance, allowlists, and contract adherence."""

    validator_name = "interaction_export_validator"
    validator_version = "1.0.0"

    def __init__(self):
        self.privacy_validator = PrivacyValidator()

    def validate(self, record: Dict[str, Any], run_id: str = "adhoc_run") -> List[QualityRuleResultV1]:
        return self.privacy_validator.validate(record, run_id=run_id)
