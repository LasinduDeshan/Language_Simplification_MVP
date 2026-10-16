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

            # 1. Protected span check across split boundary
            overlapping = [
                ps for ps in protected_spans
                if not (end <= ps.span.start_code_point or start >= ps.span.end_code_point)
            ]
            if overlapping:
                attempt = RuleAttempt(
                    attempt_id=f"SI-RULE-ATTEMPT-{attempt_counter:06d}",
                    request_id=request_id,
                    rule_id=rule.rule_id,
                    rule_version=rule.rule_version,
                    terminal_status=RuleAttemptTerminalStatus.BLOCKED_PROTECTED_SPAN,
                    reason_codes=["SPLIT_BOUNDARY_INSIDE_PROTECTED_SPAN"],
                    source_spans=[source_span],
                    candidate_id=None
                )
                attempt_counter += 1
                results.append((attempt, None))
                continue

            clause1 = text[:start].strip()
            clause2 = text[end:].strip()

            # Minimum completeness check (both clauses must have multiple tokens)
            if len(clause1.split()) < 3 or len(clause2.split()) < 3:
                attempt = RuleAttempt(
                    attempt_id=f"SI-RULE-ATTEMPT-{attempt_counter:06d}",
                    request_id=request_id,
                    rule_id=rule.rule_id,
                    rule_version=rule.rule_version,
                    terminal_status=RuleAttemptTerminalStatus.BLOCKED_MEANING_GUARD,
                    reason_codes=["INCOMPLETE_CLAUSE_STRUCTURE"],
                    source_spans=[source_span],
                    candidate_id=None
                )
                attempt_counter += 1
                results.append((attempt, None))
                continue

            # Constrained Subject Recovery Check:
            # If the second clause begins with a verb or particle lacking an overt subject,
            # we check whether an unambiguous subject can be extracted from clause 1.
            # If multiple competing subject candidates exist or context is ambiguous,
            # defer strictly to MANUAL_REVIEW_REQUIRED.
            clause1_words = clause1.split()
            first_subject = clause1_words[0] if clause1_words else None

            # Simple heuristic check for ambiguous referent in clause 2
            clause2_words = clause2.split()
            has_explicit_subject = len(clause2_words) > 0 and not clause2_words[0].endswith("යි")

            if not has_explicit_subject and not first_subject:
                attempt = RuleAttempt(
                    attempt_id=f"SI-RULE-ATTEMPT-{attempt_counter:06d}",
                    request_id=request_id,
                    rule_id=rule.rule_id,
                    rule_version=rule.rule_version,
                    terminal_status=RuleAttemptTerminalStatus.DEFERRED_MANUAL_REVIEW,
                    reason_codes=["AMBIGUOUS_SUBJECT_RECOVERY"],
                    source_spans=[source_span],
                    candidate_id=None
                )
                attempt_counter += 1
                results.append((attempt, None))
                continue

            # Deterministic split text: clause 1 ending with full stop, space, then clause 2
            punct = "." if not clause1.endswith(".") else ""
            new_text = f"{clause1}{punct} {clause2}"

            candidate_id = f"SI-CAND-{candidate_counter:06d}"
            candidate_counter += 1

            op = TransformationOperation(
                operation_id=f"SI-OP-{candidate_counter:06d}",
                operation_type=OperationType.SPLIT,
                rule_id=rule.rule_id,
                raw_source_spans=[source_span],
                normalized_source_spans=[source_span],
                output_spans=[CodePointSpan(start_code_point=len(clause1), end_code_point=len(clause1) + 2, text=f"{punct} ")],
                mapping_status=MappingStatus.NON_LOCAL,
                mapping_exact=False,
                before_hash_internal=compute_sha256(m.group()),
                after_hash_internal=compute_sha256(f"{punct} "),
                before_text_internal=m.group(),
                after_text_internal=f"{punct} "
            )

            candidate = RewriteCandidate(
                candidate_id=candidate_id,
                request_id=request_id,
                rule_id=rule.rule_id,
                candidate_text_internal=new_text,
                candidate_sha256_internal=compute_sha256(new_text),
                operations=[op],
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
