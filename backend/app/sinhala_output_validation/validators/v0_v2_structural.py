"""
Stage 36 Validators V0, V1, V2: Envelope/Provenance, Unicode/Script, and Structural Consistency Gates.
"""

import re
import unicodedata
from typing import Any, Dict, List

from app.sinhala_output_validation.schemas import (
    CandidateEnvelope,
    EvidenceClass,
    ExecutionMode,
    ProviderCondition,
    SeverityLevel,
    ValidatorFinding,
)
from app.sinhala_output_validation.validators.base import BaseValidator

# Sinhala Unicode block: U+0D80 to U+0DFF
SINHALA_BLOCK_START = 0x0D80
SINHALA_BLOCK_END = 0x0DFF

# Forbidden control character regex (control chars except newline, tab, carriage return)
CONTROL_CHAR_REGEX = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]")


class ValidatorV0EnvelopeProvenance(BaseValidator):
    """
    V0: Validates envelope integrity, cryptographic hashes, execution mode compatibility,
    and external processing rights.
    """

    def __init__(self):
        super().__init__(validator_id="V0_ENVELOPE_PROVENANCE", version="1.0.0")

    def validate(
        self,
        source_text: str,
        candidate_text: str,
        envelope: CandidateEnvelope,
        context: Dict[str, Any],
    ) -> List[ValidatorFinding]:
        findings = []

        # Check external processing authorization for real external providers
        if (
            envelope.execution_mode == ExecutionMode.REAL_PROVIDER.value
            and envelope.provider_condition == ProviderCondition.C1_GEMINI_EXPERIMENTAL.value
            and not envelope.external_processing_authorized
        ):
            findings.append(
                ValidatorFinding(
                    finding_id=f"fnd_{envelope.candidate_id}_v0_unauth_ext",
                    validator_id=self.validator_id,
                    validator_version=self.version,
                    severity=SeverityLevel.CRITICAL,
                    reason_code="REJ_CONF_PROVENANCE_INVALID",
                    evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                    public_summary="External processing authorization missing for external provider execution",
                )
            )

        # Check generation configuration hash
        if not envelope.generation_configuration_hash or len(envelope.generation_configuration_hash) < 16:
            findings.append(
                ValidatorFinding(
                    finding_id=f"fnd_{envelope.candidate_id}_v0_bad_hash",
                    validator_id=self.validator_id,
                    validator_version=self.version,
                    severity=SeverityLevel.CRITICAL,
                    reason_code="REJ_CONF_PROVENANCE_INVALID",
                    evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                    public_summary="Generation configuration hash missing or invalid",
                )
            )
        elif (
            context.get("expected_configuration_hash")
            and envelope.generation_configuration_hash != context["expected_configuration_hash"]
        ):
            findings.append(
                ValidatorFinding(
                    finding_id=f"fnd_{envelope.candidate_id}_v0_mismatch_hash",
                    validator_id=self.validator_id,
                    validator_version=self.version,
                    severity=SeverityLevel.CRITICAL,
                    reason_code="REJ_CONF_PROVENANCE_INVALID",
                    evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                    public_summary=f"Generation configuration hash mismatch: expected {context['expected_configuration_hash']}",
                )
            )

        return findings


class ValidatorV1UnicodeScript(BaseValidator):
    """
    V1: Unicode serialization, NFC compatibility and script-validation gate.
    Verifies NFC compatibility, script constraints (Sinhala block), and prohibits
    non-printable control characters and encoding corruption without silently rewriting provider output.
    Original candidate bytes and characters are immutably preserved.
    """

    def __init__(self, min_sinhala_ratio: float = 0.50):
        super().__init__(validator_id="V1_UNICODE_SCRIPT", version="1.0.0")
        self.min_sinhala_ratio = min_sinhala_ratio

    def validate(
        self,
        source_text: str,
        candidate_text: str,
        envelope: CandidateEnvelope,
        context: Dict[str, Any],
    ) -> List[ValidatorFinding]:
        findings = []

        # Check NFC normalization
        normalized = unicodedata.normalize("NFC", candidate_text)
        if normalized != candidate_text:
            findings.append(
                ValidatorFinding(
                    finding_id=f"fnd_{envelope.candidate_id}_v1_nfc",
                    validator_id=self.validator_id,
                    validator_version=self.version,
                    severity=SeverityLevel.CRITICAL,
                    reason_code="REJ_INVALID_UNICODE",
                    evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                    public_summary="Candidate text is not in canonical Unicode NFC normalized form",
                )
            )

        # Check for illegal control characters
        if CONTROL_CHAR_REGEX.search(candidate_text):
            findings.append(
                ValidatorFinding(
                    finding_id=f"fnd_{envelope.candidate_id}_v1_ctrl",
                    validator_id=self.validator_id,
                    validator_version=self.version,
                    severity=SeverityLevel.CRITICAL,
                    reason_code="REJ_INVALID_UNICODE",
                    evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                    public_summary="Candidate text contains illegal non-printable control characters",
                )
            )

        # Check for unicode replacement character \uFFFD (mojibake)
        if "\uFFFD" in candidate_text:
            findings.append(
                ValidatorFinding(
                    finding_id=f"fnd_{envelope.candidate_id}_v1_mojibake",
                    validator_id=self.validator_id,
                    validator_version=self.version,
                    severity=SeverityLevel.CRITICAL,
                    reason_code="REJ_INVALID_UNICODE",
                    evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                    public_summary="Candidate text contains Unicode replacement character (encoding corruption)",
                )
            )

        # Script ratio check: ratio of Sinhala characters among all alphabetic characters
        sinhala_count = 0
        alpha_count = 0
        for char in candidate_text:
            code = ord(char)
            if SINHALA_BLOCK_START <= code <= SINHALA_BLOCK_END:
                sinhala_count += 1
                alpha_count += 1
            elif char.isalpha():
                alpha_count += 1

        if alpha_count > 0:
            ratio = sinhala_count / alpha_count
            if ratio < self.min_sinhala_ratio:
                findings.append(
                    ValidatorFinding(
                        finding_id=f"fnd_{envelope.candidate_id}_v1_script_ratio",
                        validator_id=self.validator_id,
                        validator_version=self.version,
                        severity=SeverityLevel.CRITICAL,
                        reason_code="REJ_INVALID_UNICODE",
                        evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                        public_summary=f"Sinhala script ratio {ratio:.2f} is below minimum required {self.min_sinhala_ratio:.2f}",
                    )
                )

        return findings


class ValidatorV2StructureLength(BaseValidator):
    """
    V2: Validates structural consistency, non-empty content, and length expansion/compression bounds.
    """

    def __init__(self, min_length_ratio: float = 0.20, max_length_ratio: float = 3.0):
        super().__init__(validator_id="V2_STRUCTURE_LENGTH", version="1.0.0")
        self.min_length_ratio = min_length_ratio
        self.max_length_ratio = max_length_ratio

    def validate(
        self,
        source_text: str,
        candidate_text: str,
        envelope: CandidateEnvelope,
        context: Dict[str, Any],
    ) -> List[ValidatorFinding]:
        findings = []

        # Check non-empty
        stripped_cand = candidate_text.strip()
        if not stripped_cand:
            findings.append(
                ValidatorFinding(
                    finding_id=f"fnd_{envelope.candidate_id}_v2_empty",
                    validator_id=self.validator_id,
                    validator_version=self.version,
                    severity=SeverityLevel.CRITICAL,
                    reason_code="REJ_CRITICAL_SEMANTIC_RISK",
                    evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                    public_summary="Candidate text is empty or contains only whitespace",
                )
            )
            return findings

        # Check unchanged source candidate
        if candidate_text.strip() == source_text.strip():
            findings.append(
                ValidatorFinding(
                    finding_id=f"fnd_{envelope.candidate_id}_v2_unchanged",
                    validator_id=self.validator_id,
                    validator_version=self.version,
                    severity=SeverityLevel.DIAGNOSTIC,
                    reason_code="DIAG_UNCHANGED_SOURCE",
                    evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                    public_summary="Candidate text is identical to source text (no simplification performed)",
                )
            )

        # Character length ratio
        src_len = len(source_text.strip())
        cand_len = len(stripped_cand)

        if src_len > 0:
            char_ratio = cand_len / src_len
            if char_ratio < self.min_length_ratio:
                findings.append(
                    ValidatorFinding(
                        finding_id=f"fnd_{envelope.candidate_id}_v2_truncated",
                        validator_id=self.validator_id,
                        validator_version=self.version,
                        severity=SeverityLevel.CRITICAL,
                        reason_code="REJ_CRITICAL_SEMANTIC_RISK",
                        evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                        public_summary=f"Candidate length ratio {char_ratio:.2f} indicates severe truncation (< {self.min_length_ratio:.2f})",
                    )
                )
            elif char_ratio > self.max_length_ratio:
                findings.append(
                    ValidatorFinding(
                        finding_id=f"fnd_{envelope.candidate_id}_v2_exploded",
                        validator_id=self.validator_id,
                        validator_version=self.version,
                        severity=SeverityLevel.CRITICAL,
                        reason_code="REJ_CRITICAL_SEMANTIC_RISK",
                        evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                        public_summary=f"Candidate length ratio {char_ratio:.2f} indicates excessive length explosion (> {self.max_length_ratio:.2f})",
                    )
                )

        return findings
