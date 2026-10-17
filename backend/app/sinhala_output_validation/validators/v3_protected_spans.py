"""
Stage 36 Validator V3: Three-Tier Protected-Span Integrity and Entailment Gate.
Enforces preservation of Declared, Deterministic, and Inferred spans.
"""

import re
from typing import Any, Dict, List, Set, Tuple

from app.sinhala_output_validation.schemas import (
    CandidateEnvelope,
    EvidenceClass,
    SeverityLevel,
    SpanCategory,
    TextSpan,
    ValidatorFinding,
)
from app.sinhala_output_validation.validators.base import BaseValidator

# Regex for deterministic protected spans: numbers, percentages, currencies, dates
NUMERIC_SPAN_REGEX = re.compile(r"\d+(?:[\.,]\d+)?%?")
URL_REGEX = re.compile(r"https?://[^\s]+|www\.[^\s]+")


class ValidatorV3ProtectedSpans(BaseValidator):
    """
    V3: Enforces exact preservation of protected spans across three tiers:
    1. DECLARED: explicit source annotations (CRITICAL gate)
    2. DETERMINISTIC: numbers, percentages, dates, URLs (CRITICAL gate)
    3. INFERRED: heuristic entity recognizer outputs (REVIEW gate)
    """

    def __init__(self):
        super().__init__(validator_id="V3_PROTECTED_SPANS", version="1.0.0")

    def _extract_deterministic_spans(self, text: str) -> List[Tuple[int, int, str]]:
        spans = []
        for match in NUMERIC_SPAN_REGEX.finditer(text):
            spans.append((match.start(), match.end(), match.group()))
        for match in URL_REGEX.finditer(text):
            spans.append((match.start(), match.end(), match.group()))
        return spans

    def validate(
        self,
        source_text: str,
        candidate_text: str,
        envelope: CandidateEnvelope,
        context: Dict[str, Any],
    ) -> List[ValidatorFinding]:
        findings = []

        # 1. DECLARED Protected Spans (Hard Gate -> CRITICAL)
        declared_spans: List[Dict[str, Any]] = context.get("declared_protected_spans", [])
        for decl in declared_spans:
            target_str = decl.get("text")
            if not target_str:
                start = decl.get("start", 0)
                end = decl.get("end", 0)
                target_str = source_text[start:end]

            if target_str and target_str not in candidate_text:
                start_offset = source_text.find(target_str) if target_str in source_text else decl.get("start", 0)
                end_offset = start_offset + len(target_str) if start_offset >= 0 else decl.get("end", 0)

                findings.append(
                    ValidatorFinding(
                        finding_id=f"fnd_{envelope.candidate_id}_v3_decl_{len(findings)}",
                        validator_id=self.validator_id,
                        validator_version=self.version,
                        severity=SeverityLevel.CRITICAL,
                        reason_code="REJ_PROTECTED_SPAN_VIOLATION",
                        evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                        span_category=SpanCategory.DECLARED_PROTECTED_SPAN,
                        source_spans=[TextSpan(start=max(0, start_offset), end=max(1, end_offset), text=target_str)],
                        candidate_spans=[],
                        mapping_exact=False,
                        public_summary=f"Declared protected span '{target_str}' is missing from candidate output",
                    )
                )

        # 2. DETERMINISTIC Protected Spans (Hard Gate -> CRITICAL)
        deterministic_src_spans = self._extract_deterministic_spans(source_text)
        cand_tokens = set(self._extract_deterministic_spans(candidate_text))
        cand_token_texts = {span[2] for span in cand_tokens}

        for start, end, token in deterministic_src_spans:
            if token not in cand_token_texts:
                findings.append(
                    ValidatorFinding(
                        finding_id=f"fnd_{envelope.candidate_id}_v3_det_{len(findings)}",
                        validator_id=self.validator_id,
                        validator_version=self.version,
                        severity=SeverityLevel.CRITICAL,
                        reason_code="REJ_PROTECTED_SPAN_VIOLATION",
                        evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                        span_category=SpanCategory.DETERMINISTIC_PROTECTED_SPAN,
                        source_spans=[TextSpan(start=start, end=end, text=token)],
                        candidate_spans=[],
                        mapping_exact=False,
                        public_summary=f"Deterministic numeric/factual span '{token}' was altered or omitted",
                    )
                )

        # 3. INFERRED Protected Spans (Soft Gate -> REVIEW)
        inferred_spans: List[Dict[str, Any]] = context.get("inferred_protected_spans", [])
        for inf in inferred_spans:
            target_str = inf.get("text")
            if not target_str:
                start = inf.get("start", 0)
                end = inf.get("end", 0)
                target_str = source_text[start:end]

            if target_str and target_str not in candidate_text:
                start_offset = source_text.find(target_str) if target_str in source_text else inf.get("start", 0)
                end_offset = start_offset + len(target_str) if start_offset >= 0 else inf.get("end", 0)

                findings.append(
                    ValidatorFinding(
                        finding_id=f"fnd_{envelope.candidate_id}_v3_inf_{len(findings)}",
                        validator_id=self.validator_id,
                        validator_version=self.version,
                        severity=SeverityLevel.REVIEW,
                        reason_code="REV_INFERRED_SPAN_ALTERED",
                        evidence_class=EvidenceClass.GOVERNED_HEURISTIC,
                        span_category=SpanCategory.INFERRED_PROTECTED_SPAN,
                        source_spans=[TextSpan(start=max(0, start_offset), end=max(1, end_offset), text=target_str)],
                        candidate_spans=[],
                        mapping_exact=False,
                        public_summary=f"Inferred entity span '{target_str}' altered; expert review recommended",
                    )
                )

        return findings
