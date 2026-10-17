"""
Validator Registry and Pipeline Executor for Stage 36 Sinhala Output Validation.
Orchestrates validators V0 through V8 in strict sequential order.
"""

from typing import Any, Dict, List, Tuple
from pydantic import ValidationError

from app.sinhala_output_validation.schemas import (
    AutomatedValidationStatus,
    CandidateDisposition,
    CandidateEnvelope,
    ExecutionOutcome,
    SeverityLevel,
    ValidationResult,
    ValidatorFinding,
)
from app.sinhala_output_validation.validators.base import BaseValidator
from app.sinhala_output_validation.validators.v0_v2_structural import (
    ValidatorV0EnvelopeProvenance,
    ValidatorV1UnicodeScript,
    ValidatorV2StructureLength,
)
from app.sinhala_output_validation.validators.v3_protected_spans import ValidatorV3ProtectedSpans
from app.sinhala_output_validation.validators.v4_v5_semantic_fidelity import (
    ValidatorV4PolarityNumerical,
    ValidatorV5OmissionInsertion,
)
from app.sinhala_output_validation.validators.v6_v8_diagnostics import (
    ValidatorV6SemanticProxy,
    ValidatorV7GrammaticalityProxy,
    ValidatorV8SimplificationGain,
)


class ValidatorPipeline:
    """
    Sequential pipeline executing V0 through V8.
    Applies short-circuit fail-closed behavior on critical provenance/Unicode gates if configured,
    or executes all applicable validators to assemble comprehensive diagnostics.
    """

    def __init__(self, halt_on_critical: bool = False):
        self.halt_on_critical = halt_on_critical
        self.validators: List[BaseValidator] = [
            ValidatorV0EnvelopeProvenance(),
            ValidatorV1UnicodeScript(),
            ValidatorV2StructureLength(),
            ValidatorV3ProtectedSpans(),
            ValidatorV4PolarityNumerical(),
            ValidatorV5OmissionInsertion(),
            ValidatorV6SemanticProxy(),
            ValidatorV7GrammaticalityProxy(),
            ValidatorV8SimplificationGain(),
        ]

    def execute(
        self,
        source_text: str,
        candidate_text: str,
        envelope: CandidateEnvelope,
        context: Dict[str, Any],
    ) -> Tuple[List[ValidatorFinding], int, AutomatedValidationStatus]:
        findings: List[ValidatorFinding] = []
        completed_count = 0

        for validator in self.validators:
            try:
                v_findings = validator.validate(source_text, candidate_text, envelope, context)
                findings.extend(v_findings)
                completed_count += 1

                if self.halt_on_critical:
                    has_critical = any(f.severity == SeverityLevel.CRITICAL for f in v_findings)
                    if has_critical:
                        return findings, completed_count, AutomatedValidationStatus.PARTIALLY_COMPLETED

            except Exception as e:
                # Internal validator failure
                raise RuntimeError(f"Validator '{validator.validator_id}' raised unexpected exception: {e}") from e

        status = AutomatedValidationStatus.COMPLETED
        return findings, completed_count, status
