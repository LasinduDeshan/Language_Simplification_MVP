"""
Stage 36 Validators V4 and V5: Polarity/Numerical Drift and Unsupported Insertion/Hallucination Risk Gates.
"""

import re
from typing import Any, Dict, List, Set

from app.sinhala_output_validation.schemas import (
    CandidateEnvelope,
    EvidenceClass,
    SeverityLevel,
    ValidatorFinding,
)
from app.sinhala_output_validation.validators.base import BaseValidator

# Standard Sinhala negation markers and prefixes
SINHALA_NEGATION_MARKERS = {
    "නැත", "නැහැ", "නැති", "නොවේ", "නොමැත", "එපා", "නොහැක", "බැහැ", "නොවෙයි", "නොවන", "නෑ", "නැතුව"
}
SINHALA_NEGATION_PREFIX = "නො"

NUMERIC_TOKEN_REGEX = re.compile(r"\d+(?:[\.,]\d+)?")


def extract_negation_signals(text: str) -> bool:
    """
    Returns True if any explicit Sinhala negation marker or prefix is present.
    """
    words = re.findall(r"[\u0D80-\u0DFF]+", text)
    for word in words:
        if word in SINHALA_NEGATION_MARKERS:
            return True
        if word.startswith(SINHALA_NEGATION_PREFIX) and len(word) > len(SINHALA_NEGATION_PREFIX) + 1:
            return True
    return False


def extract_numbers(text: str) -> Set[str]:
    return set(NUMERIC_TOKEN_REGEX.findall(text))


class ValidatorV4PolarityNumerical(BaseValidator):
    """
    V4: Detects polarity inversion (negation flips) and unauthorized numerical mutations.
    """

    def __init__(self):
        super().__init__(validator_id="V4_POLARITY_NUMERICAL", version="1.0.0")

    def validate(
        self,
        source_text: str,
        candidate_text: str,
        envelope: CandidateEnvelope,
        context: Dict[str, Any],
    ) -> List[ValidatorFinding]:
        findings = []

        # 1. Negation / Polarity Flip Check
        src_neg = extract_negation_signals(source_text)
        cand_neg = extract_negation_signals(candidate_text)

        if src_neg != cand_neg:
            flip_desc = "negative-to-positive" if src_neg else "positive-to-negative"
            findings.append(
                ValidatorFinding(
                    finding_id=f"fnd_{envelope.candidate_id}_v4_polarity",
                    validator_id=self.validator_id,
                    validator_version=self.version,
                    severity=SeverityLevel.CRITICAL,
                    reason_code="REJ_NUMERICAL_OR_POLARITY_DRIFT",
                    evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                    public_summary=f"Detected polarity inversion ({flip_desc}) between source and candidate",
                )
            )

        # 2. Numerical Drift Check (Novel numbers inserted into candidate)
        src_nums = extract_numbers(source_text)
        cand_nums = extract_numbers(candidate_text)

        unsupported_nums = cand_nums - src_nums
        if unsupported_nums:
            findings.append(
                ValidatorFinding(
                    finding_id=f"fnd_{envelope.candidate_id}_v4_novel_num",
                    validator_id=self.validator_id,
                    validator_version=self.version,
                    severity=SeverityLevel.CRITICAL,
                    reason_code="REJ_NUMERICAL_OR_POLARITY_DRIFT",
                    evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                    public_summary=f"Candidate introduces unsupported numerical quantities: {sorted(list(unsupported_nums))}",
                )
            )

        return findings


class ValidatorV5OmissionInsertion(BaseValidator):
    """
    V5: Detects unsupported insertions (hallucinations) and excessive lexical divergence.
    """

    def __init__(self, max_novel_token_ratio: float = 0.65):
        super().__init__(validator_id="V5_OMISSION_INSERTION", version="1.0.0")
        self.max_novel_token_ratio = max_novel_token_ratio

    def validate(
        self,
        source_text: str,
        candidate_text: str,
        envelope: CandidateEnvelope,
        context: Dict[str, Any],
    ) -> List[ValidatorFinding]:
        findings = []

        src_words = set(re.findall(r"[\u0D80-\u0DFF]+", source_text))
        cand_words = re.findall(r"[\u0D80-\u0DFF]+", candidate_text)

        if not cand_words:
            return findings

        # Check novel token ratio with pedagogical scaffolding and inflection tolerance
        allowed_words = set(src_words)
        is_scaffolding = (
            context.get("strategy_code") in ("STRONG_DECOMPOSED_STEP", "STRONG_SCAFFOLD")
            or str(envelope.execution_mode) in ("DETERMINISTIC_COPY", "ExecutionMode.DETERMINISTIC_COPY")
            or context.get("allow_governed_scaffolding", False)
        )
        if is_scaffolding:
            GOVERNED_PEDAGOGICAL_VOCABULARY = {
                "පින්තූර", "පින්තූරය", "පින්තූරවල", "දෙක", "බලන්න", "තෝරන්න", "අහන්න",
                "දේ", "එකක්", "එකිනෙක", "හොඳින්", "අල්ලන්න", "සොයන්න", "කරන",
                "කුමක්ද", "නම", "වෙනස්", "වන", "රූපය", "කෑමට", "ගන්නා", "හැඩතල",
                "උපදෙස්වල", "කියන", "හැඩය", "සඳහා", "භාවිත",
                "පළමුව", "කවුද", "කියා", "එය", "දැන්", "ඉතිරි", "කොටසෙන්", "ඒ", "අය", "දෙය"
            }
            allowed_words.update(GOVERNED_PEDAGOGICAL_VOCABULARY)
            if "scaffolding_vocabulary" in context:
                allowed_words.update(context["scaffolding_vocabulary"])

        def is_word_allowed(w: str) -> bool:
            if w in allowed_words:
                return True
            for sw in src_words:
                if (len(sw) >= 3 and w.startswith(sw)) or (len(w) >= 3 and sw.startswith(w)):
                    return True
            return False

        novel_tokens = [w for w in cand_words if not is_word_allowed(w)]
        novel_ratio = len(novel_tokens) / len(cand_words)

        if novel_ratio > self.max_novel_token_ratio:

            findings.append(
                ValidatorFinding(
                    finding_id=f"fnd_{envelope.candidate_id}_v5_hallucination",
                    validator_id=self.validator_id,
                    validator_version=self.version,
                    severity=SeverityLevel.CRITICAL,
                    reason_code="REJ_UNSUPPORTED_INSERTION",
                    evidence_class=EvidenceClass.GOVERNED_HEURISTIC,
                    public_summary=f"Novel token ratio {novel_ratio:.2f} exceeds threshold {self.max_novel_token_ratio:.2f} (hallucination risk)",
                )
            )
        elif novel_ratio > 0.45:
            # Advisory / Review warning
            findings.append(
                ValidatorFinding(
                    finding_id=f"fnd_{envelope.candidate_id}_v5_lexical_warn",
                    validator_id=self.validator_id,
                    validator_version=self.version,
                    severity=SeverityLevel.WARNING,
                    reason_code="WARN_HIGH_LEXICAL_DIVERGENCE",
                    evidence_class=EvidenceClass.GOVERNED_HEURISTIC,
                    public_summary=f"High lexical divergence ratio {novel_ratio:.2f}; expert review suggested",
                )
            )

        return findings
