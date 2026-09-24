"""Validator registry managing layer-specific and common validators."""
from typing import Dict, List, Any
from app.datasets.quality.validators.base import BaseValidator
from app.datasets.quality.validators.common import CommonRecordValidator
from app.datasets.quality.validators.child_safety import ChildSafetyValidator
from app.datasets.quality.validators.privacy import PrivacyValidator
from app.datasets.quality.validators.adaptation import AdaptationValidator
from app.datasets.quality.validators.simplification import SimplificationValidator
from app.datasets.quality.validators.lexicon import LexiconValidator
from app.datasets.quality.validators.linguistic import LinguisticValidator
from app.datasets.quality.validators.interaction_export import InteractionExportValidator
from app.datasets.quality.schemas import QualityRuleResultV1


class QualityValidatorRegistry:
    """Registry coordinating validators based on dataset layer."""

    def __init__(self):
        self.common_validator = CommonRecordValidator()
        self.child_safety_validator = ChildSafetyValidator()
        self.privacy_validator = PrivacyValidator()
        self.adaptation_validator = AdaptationValidator()
        self.simplification_validator = SimplificationValidator()
        self.lexicon_validator = LexiconValidator()
        self.linguistic_validator = LinguisticValidator()
        self.interaction_validator = InteractionExportValidator()

    def get_validators_for_layer(self, dataset_layer: str, enable_nlp: bool = True) -> List[BaseValidator]:
        """Returns ordered list of validators for a given dataset layer."""
        validators: List[BaseValidator] = [self.common_validator, self.child_safety_validator]

        if dataset_layer == "adaptation_test_set":
            validators.append(self.adaptation_validator)
            if enable_nlp:
                validators.append(self.linguistic_validator)
        elif dataset_layer == "simplification_corpus":
            validators.append(self.simplification_validator)
            if enable_nlp:
                validators.append(self.linguistic_validator)
        elif dataset_layer == "lexicons":
            validators.append(self.lexicon_validator)
        elif dataset_layer == "interaction_exports":
            validators = [self.interaction_validator]

        return validators

    def validate_record(
        self,
        record: Dict[str, Any],
        dataset_layer: str,
        run_id: str = "adhoc_run",
        enable_nlp: bool = True
    ) -> List[QualityRuleResultV1]:
        """Runs all applicable validators on a single record dictionary."""
        # Ensure dataset_layer is set on record for validators
        record_copy = dict(record)
        record_copy["dataset_layer"] = dataset_layer
        
        validators = self.get_validators_for_layer(dataset_layer, enable_nlp=enable_nlp)
        results: List[QualityRuleResultV1] = []
        for val in validators:
            val_results = val.validate(record_copy, run_id=run_id)
            results.extend(val_results)
        return results
