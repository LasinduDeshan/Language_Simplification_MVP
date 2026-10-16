"""
Stage 33 — Sentence Splitting Engine with Constrained Subject Recovery.
Splits compound sentences at allowlisted conjunction markers.
Subject insertion into a second clause is permitted ONLY when the exact subject
is copied verbatim from an unambiguous source span; ambiguous cases route to review.
"""

import hashlib
import re
from typing import List, Optional, Tuple

from app.sinhala_simplification.enums import (
    CandidateTerminalStatus,
    MappingStatus,
    OperationType,
    RuleAttemptTerminalStatus,
)
from app.sinhala_simplification.rule_registry import GovernedRuleDefinition
from app.sinhala_simplification.schemas import (
    CodePointSpan,
    ProtectedSpan,
    RewriteCandidate,
    RuleAttempt,
    TransformationOperation,
)


def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class SentenceSplitterEngine:
    """
    Evaluates sentence splitting rules with strict subject recovery constraints.
    """

    def evaluate_rule(
        self,
        rule: GovernedRuleDefinition,
        text: str,
        request_id: str,
        protected_spans: List[ProtectedSpan],
        attempt_counter: int,
        candidate_counter: int,
    ) -> List[Tuple[RuleAttempt, Optional[RewriteCandidate]]]:
        results: List[Tuple[RuleAttempt, Optional[RewriteCandidate]]] = []
        conjunction = rule.source_pattern.strip()

        # Find coordination conjunction surrounded by whitespace
        regex = re.compile(rf"\s+{re.escape(conjunction)}\s+")
        matches = list(regex.finditer(text))

        if not matches:
            attempt = RuleAttempt(
                attempt_id=f"SI-RULE-ATTEMPT-{attempt_counter:06d}",
                request_id=request_id,
                rule_id=rule.rule_id,
                rule_version=rule.rule_version,
                terminal_status=RuleAttemptTerminalStatus.NOT_APPLICABLE,
                reason_codes=["NO_COORDINATION_MARKER"],
                source_spans=[],
                candidate_id=None
            )
            results.append((attempt, None))
            return results

        for m in matches:
            start, end = m.start(), m.end()
            source_span = CodePointSpan(start_code_point=start, end_code_point=end, text=m.group())

            clause1 = text[:start].strip()
            clause2 = text[end:].strip()

            candidate_id = f"SI-CAND-{candidate_counter:06d}"
            candidate_counter += 1

            # Check incomplete clause or ambiguous subject
            clause1_words = clause1.split()
            clause2_words = clause2.split()
            first_subject = clause1_words[0] if clause1_words else None
            has_explicit_subject = len(clause2_words) > 0 and not clause2_words[0].endswith("යි")

            before_flag = m.group()
            if len(clause1_words) < 3 or len(clause2_words) < 3:
                before_flag = f"{m.group()} [INCOMPLETE_CLAUSE_STRUCTURE]"
            elif not has_explicit_subject and not first_subject:
                before_flag = f"{m.group()} [AMBIGUOUS_SUBJECT_RECOVERY]"

            # Deterministic split text: clause 1 ending with full stop, space, then clause 2
            punct = "." if not clause1.endswith(".") else ""
            new_text = f"{clause1}{punct} {clause2}"

            op = TransformationOperation(
                operation_id=f"SI-OP-{candidate_counter:06d}",
                operation_type=OperationType.SPLIT,
                rule_id=rule.rule_id,
                raw_source_spans=[source_span],
                normalized_source_spans=[source_span],
                output_spans=[CodePointSpan(start_code_point=len(clause1), end_code_point=len(clause1) + 2, text=f"{punct} ")],
                mapping_status=MappingStatus.NON_LOCAL,
                mapping_exact=False,
                before_hash_internal=compute_sha256(before_flag),
                after_hash_internal=compute_sha256(f"{punct} "),
                before_text_internal=before_flag,
                after_text_internal=f"{punct} "
            )

            candidate = RewriteCandidate(
                candidate_id=candidate_id,
                request_id=request_id,
                rule_id=rule.rule_id,
                candidate_text_internal=new_text,
                candidate_sha256_internal=compute_sha256(new_text),
                operations=[op],
                applied_rule_ids=[rule.rule_id],
                guard_results={},
                all_guards_passed=False,
                terminal_status=CandidateTerminalStatus.NOT_SELECTED_LOWER_RANK
            )

            attempt = RuleAttempt(
                attempt_id=f"SI-RULE-ATTEMPT-{attempt_counter:06d}",
                request_id=request_id,
                rule_id=rule.rule_id,
                rule_version=rule.rule_version,
                terminal_status=RuleAttemptTerminalStatus.CANDIDATE_GENERATED,
                reason_codes=[],
                source_spans=[source_span],
                candidate_id=candidate_id
            )
            attempt_counter += 1
            results.append((attempt, candidate))

        return results
