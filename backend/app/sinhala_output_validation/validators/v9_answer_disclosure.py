"""
Stage 36 Output Validation — Validator V9: Assessment Answer-Disclosure Gate & Decomposed Step Complexity.
Prevents instruction simplification from leaking answers to children in inference-based activities.
Employs frozen Stage 30 grapheme-safe tokenization and Unicode NFC normalization (no regex word boundaries).
"""

import unicodedata
from typing import Any, Dict, List, Set

from app.localization.enums import TargetDisclosurePolicy
from app.localization.target_aliases import load_target_aliases
from app.sinhala_output_validation.schemas import (
    CandidateEnvelope,
    EvidenceClass,
    SeverityLevel,
    TextSpan,
    ValidatorFinding,
)
from app.sinhala_output_validation.validators.base import BaseValidator
from app.sinhala_preprocessing.tokenizer import tokenize_text

# Common Sinhala grammatical case / inflectional suffixes
SINHALA_INFLECTION_SUFFIXES = (
    "ට",      # Dative (e.g. පැන්සලට)
    "ෙන්",    # Instrumental / Ablative (e.g. පැන්සලෙන්, පොතෙන්)
    "න්",     # Plural / Instrumental
    "ගේ",     # Genitive (e.g. පූසාගේ)
    "ක්",     # Indefinite (e.g. පැන්සලක්, පොතක්)
    "ක",      # Indefinite stem (e.g. පොතක)
    "ගෙන්",   # Ablative animate (e.g. පූසාගෙන්)
    "ල",      # Plural animate
    "වල්",    # Plural inanimate
    "ටත්",    # Dative + emphatic (e.g. පැන්සලටත්)
)


class ValidatorV9AnswerDisclosureGate(BaseValidator):
    """
    Validator V9: Evaluates answer leakage against protected target aliases
    and verifies per-step complexity bounds for decomposed instructions.
    """

    def __init__(self, version: str = "1.0.0"):
        super().__init__(validator_id="V9_ANSWER_DISCLOSURE", version=version)

    def validate(
        self,
        source_text: str,
        candidate_text: str,
        envelope: CandidateEnvelope,
        context: Dict[str, Any],
    ) -> List[ValidatorFinding]:
        findings: List[ValidatorFinding] = []

        if not candidate_text:
            return findings

        norm_candidate = unicodedata.normalize("NFC", candidate_text)

        # 1. Answer Disclosure Evaluation
        disclosure_policy = context.get("target_disclosure_policy")
        if disclosure_policy is None:
            disclosure_policy = TargetDisclosurePolicy.DO_NOT_REVEAL

        # Only enforce disclosure gate when policy is DO_NOT_REVEAL
        if disclosure_policy != TargetDisclosurePolicy.MAY_REPEAT_TASK_TARGET:
            target_aliases = context.get("target_aliases")
            target_id = context.get("target_id")

            if not target_aliases and target_id:
                target_aliases = load_target_aliases(target_id)

            if target_aliases:
                # Assemble normalized set of prohibited alias stems
                prohibited_stems: Set[str] = set()
                for locale_key in ("si", "en"):
                    for alias in target_aliases.get(locale_key, []):
                        clean_alias = unicodedata.normalize("NFC", alias.strip().lower())
                        if clean_alias:
                            prohibited_stems.add(clean_alias)

                # Grapheme-safe tokenization of candidate
                tokens = tokenize_text(norm_candidate)

                for tok in tokens:
                    tok_surface = tok.surface.strip().lower()
                    if not tok_surface:
                        continue

                    # Direct match
                    is_match = tok_surface in prohibited_stems

                    # Suffix-stripped stem matching for Sinhala inflections
                    if not is_match:
                        for sfx in SINHALA_INFLECTION_SUFFIXES:
                            if tok_surface.endswith(sfx):
                                stem = tok_surface[: -len(sfx)]
                                if stem in prohibited_stems:
                                    is_match = True
                                    break

                    if is_match:
                        findings.append(
                            ValidatorFinding(
                                finding_id=f"FIND-V9-DISCLOSURE-{len(findings)+1:03d}",
                                validator_id=self.validator_id,
                                validator_version=self.version,
                                severity=SeverityLevel.CRITICAL,
                                reason_code="REJ_ANSWER_DISCLOSURE_DETECTED",
                                evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
                                candidate_spans=[
                                    TextSpan(
                                        start=tok.start_code_point,
                                        end=tok.end_code_point,
                                    )
                                ],
                                public_summary="Candidate instruction discloses protected task answer target.",
                            )
                        )

        # 2. Per-Step Complexity Check (for Attempt 3 / STRONG_DECOMPOSED_STEP)
        strategy = context.get("strategy_code") or context.get("strategy")
        attempt_number = context.get("attempt_number", 1)

        if strategy == "STRONG_DECOMPOSED_STEP" or attempt_number == 3:
            # Split into sub-steps by sentence terminators
            steps = [s.strip() for s in norm_candidate.replace("\n", ".").split(".") if s.strip()]
            
            # Bound 1: Maximum 2 decomposed sub-steps
            if len(steps) > 2:
                findings.append(
                    ValidatorFinding(
                        finding_id=f"FIND-V9-COMPLEXITY-STEPS-{len(findings)+1:03d}",
                        validator_id=self.validator_id,
                        validator_version=self.version,
                        severity=SeverityLevel.REVIEW,
                        reason_code="DIAG_DECOMPOSED_TOO_MANY_STEPS",
                        evidence_class=EvidenceClass.GOVERNED_HEURISTIC,
                        public_summary="Decomposed instruction exceeds maximum allowable sub-step count (max 2).",
                    )
                )

            # Bound 2: Maximum 8 words per sub-step
            for idx, step in enumerate(steps):
                step_tokens = tokenize_text(step)
                word_tokens = [t for t in step_tokens if "WORD" in str(t.token_type)]
                if len(word_tokens) > 8:
                    findings.append(
                        ValidatorFinding(
                            finding_id=f"FIND-V9-COMPLEXITY-WORDS-{idx+1:02d}",
                            validator_id=self.validator_id,
                            validator_version=self.version,
                            severity=SeverityLevel.REVIEW,
                            reason_code="DIAG_DECOMPOSED_STEP_WORD_LIMIT_EXCEEDED",
                            evidence_class=EvidenceClass.GOVERNED_HEURISTIC,
                            public_summary=f"Sub-step {idx+1} exceeds maximum allowable word count (max 8 words).",
                        )
                    )

        return findings
