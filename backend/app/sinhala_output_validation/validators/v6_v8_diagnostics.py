"""
Stage 36 Validators V6, V7, V8: Semantic Proxy, Grammaticality/Orthography, and Simplification Gain Diagnostics.
"""

import re
from typing import Any, Dict, List

from app.sinhala_output_validation.schemas import (
    CandidateEnvelope,
    EvidenceClass,
    SeverityLevel,
    ValidatorFinding,
)
from app.sinhala_output_validation.validators.base import BaseValidator

# Virama (Hal kirima) in Sinhala: U+0DCA
VIRAMA = "\u0DCA"
CONSECUTIVE_VIRAMA_REGEX = re.compile(rf"{VIRAMA}{{2,}}")

# Dependent vowel signs in Sinhala: U+0DCF to U+0DDF, plus U+0DF2, U+0DF3
DEPENDENT_VOWELS = set(chr(c) for c in range(0x0DCF, 0x0DE0)) | {"\u0DF2", "\u0DF3"}


def compute_char_ngram_jaccard(text1: str, text2: str, n: int = 3) -> float:
    """
    Computes character n-gram Jaccard similarity as an automated semantic proxy.
    """
    if not text1 or not text2:
        return 0.0

    ngrams1 = {text1[i:i+n] for i in range(max(0, len(text1) - n + 1))}
    ngrams2 = {text2[i:i+n] for i in range(max(0, len(text2) - n + 1))}

    if not ngrams1 or not ngrams2:
        return 1.0 if text1 == text2 else 0.0

    intersection = ngrams1 & ngrams2
    union = ngrams1 | ngrams2
    return len(intersection) / len(union)


class ValidatorV6SemanticProxy(BaseValidator):
    """
    V6: Semantic-risk proxy diagnostic.
    Evaluates coarse semantic-risk proxy using character n-gram Jaccard overlap to catch catastrophic divergence.
    This metric serves strictly as an automated diagnostic risk indicator; it cannot override a hard gate failure
    or independently establish semantic equivalence.
    """

    def __init__(self, min_similarity_threshold: float = 0.20):
        super().__init__(validator_id="V6_SEMANTIC_PROXY", version="1.0.0")
        self.min_similarity_threshold = min_similarity_threshold

    def validate(
        self,
        source_text: str,
        candidate_text: str,
        envelope: CandidateEnvelope,
        context: Dict[str, Any],
    ) -> List[ValidatorFinding]:
        findings = []

        similarity = compute_char_ngram_jaccard(source_text, candidate_text, n=3)
        context["diagnostic_metrics"] = context.get("diagnostic_metrics", {})
        context["diagnostic_metrics"]["semantic_similarity_proxy"] = round(similarity, 4)

        if similarity < self.min_similarity_threshold:
            findings.append(
                ValidatorFinding(
                    finding_id=f"fnd_{envelope.candidate_id}_v6_drift",
                    validator_id=self.validator_id,
                    validator_version=self.version,
                    severity=SeverityLevel.CRITICAL,
                    reason_code="REJ_CRITICAL_SEMANTIC_RISK",
                    evidence_class=EvidenceClass.AUTOMATED_PROXY,
                    public_summary=f"Semantic similarity proxy {similarity:.2f} indicates critical semantic drift (< {self.min_similarity_threshold:.2f})",
                )
            )

        return findings


class ValidatorV7GrammaticalityProxy(BaseValidator):
    """
    V7: Validates Sinhala orthographic rules, virama consistency, and punctuation balance.
    """

    def __init__(self):
        super().__init__(validator_id="V7_GRAMMATICALITY_PROXY", version="1.0.0")

    def validate(
        self,
        source_text: str,
        candidate_text: str,
        envelope: CandidateEnvelope,
        context: Dict[str, Any],
    ) -> List[ValidatorFinding]:
        findings = []

        # 1. Consecutive Virama signs (Orthographic Corruption)
        if CONSECUTIVE_VIRAMA_REGEX.search(candidate_text):
            findings.append(
                ValidatorFinding(
                    finding_id=f"fnd_{envelope.candidate_id}_v7_virama",
                    validator_id=self.validator_id,
                    validator_version=self.version,
                    severity=SeverityLevel.CRITICAL,
                    reason_code="REJ_INVALID_UNICODE",
                    evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                    public_summary="Candidate contains illegal consecutive virama (hal-kirima) signs",
                )
            )

        # 2. Leading dependent vowel signs without preceding consonant
        if candidate_text and candidate_text[0] in DEPENDENT_VOWELS:
            findings.append(
                ValidatorFinding(
                    finding_id=f"fnd_{envelope.candidate_id}_v7_orphan_vowel",
                    validator_id=self.validator_id,
                    validator_version=self.version,
                    severity=SeverityLevel.CRITICAL,
                    reason_code="REJ_INVALID_UNICODE",
                    evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                    public_summary="Candidate begins with an orphaned dependent vowel sign",
                )
            )

        # 3. Unbalanced brackets / quotes
        bracket_pairs = {"(": ")", "[": "]", "{": "}"}
        counts = {b: 0 for b in bracket_pairs}
        for char in candidate_text:
            if char in bracket_pairs:
                counts[char] += 1
            elif char in bracket_pairs.values():
                for k, v in bracket_pairs.items():
                    if v == char and counts[k] > 0:
                        counts[k] -= 1

        unbalanced = sum(counts.values())
        if unbalanced > 0:
            findings.append(
                ValidatorFinding(
                    finding_id=f"fnd_{envelope.candidate_id}_v7_bracket",
                    validator_id=self.validator_id,
                    validator_version=self.version,
                    severity=SeverityLevel.REVIEW,
                    reason_code="REV_FLUENCY_ANOMALY",
                    evidence_class=EvidenceClass.GOVERNED_HEURISTIC,
                    public_summary="Candidate text contains unbalanced brackets or delimiters",
                )
            )

        return findings


class ValidatorV8SimplificationGain(BaseValidator):
    """
    V8: Evaluates readability and simplification gain proxies (word length, syllable count reduction).
    Never rejects on its own; records diagnostic telemetry.
    """

    def __init__(self):
        super().__init__(validator_id="V8_SIMPLIFICATION_GAIN", version="1.0.0")

    def validate(
        self,
        source_text: str,
        candidate_text: str,
        envelope: CandidateEnvelope,
        context: Dict[str, Any],
    ) -> List[ValidatorFinding]:
        findings = []

        src_words = [w for w in re.findall(r"[\u0D80-\u0DFF]+", source_text) if w]
        cand_words = [w for w in re.findall(r"[\u0D80-\u0DFF]+", candidate_text) if w]

        src_avg_len = sum(len(w) for w in src_words) / max(1, len(src_words))
        cand_avg_len = sum(len(w) for w in cand_words) / max(1, len(cand_words))

        # Simplification gain: reduction in average word length
        avg_word_reduction = round(src_avg_len - cand_avg_len, 3)

        context["diagnostic_metrics"] = context.get("diagnostic_metrics", {})
        context["diagnostic_metrics"]["src_avg_word_length"] = round(src_avg_len, 2)
        context["diagnostic_metrics"]["cand_avg_word_length"] = round(cand_avg_len, 2)
        context["diagnostic_metrics"]["simplification_gain_proxy"] = avg_word_reduction

        findings.append(
            ValidatorFinding(
                finding_id=f"fnd_{envelope.candidate_id}_v8_diag",
                validator_id=self.validator_id,
                validator_version=self.version,
                severity=SeverityLevel.DIAGNOSTIC,
                reason_code="DIAG_SIMPLIFICATION_METRICS",
                evidence_class=EvidenceClass.AUTOMATED_PROXY,
                public_summary=f"Simplification metrics: word length reduction={avg_word_reduction:.2f}",
            )
        )

        return findings
