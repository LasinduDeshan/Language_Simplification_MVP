"""
Stage 33 — Phrase-Level Simplification Rule Engine.
Evaluates multi-token idiom and phrase substitutions using longest-match-first precedence.
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


class PhraseRuleEngine:
    """
    Evaluates multi-token phrase substitutions with longest-match-first priority.
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
        pattern = rule.source_pattern
        target = rule.target_template

        escaped_pat = re.escape(pattern)
        regex = re.compile(rf"(?<![\u0D80-\u0DFF]){escaped_pat}(?![\u0D80-\u0DFF])")

        matches = list(regex.finditer(text))
        if not matches:
            attempt = RuleAttempt(
                attempt_id=f"SI-RULE-ATTEMPT-{attempt_counter:06d}",
                request_id=request_id,
                rule_id=rule.rule_id,
                rule_version=rule.rule_version,
                terminal_status=RuleAttemptTerminalStatus.NOT_APPLICABLE,
                reason_codes=["NO_PHRASE_MATCH"],
                source_spans=[],
                candidate_id=None
            )
            results.append((attempt, None))
            return results

        for m in matches:
            start, end = m.start(), m.end()
            source_span = CodePointSpan(start_code_point=start, end_code_point=end, text=m.group())

            # Check protected spans
            overlapping_protected = [
                ps for ps in protected_spans
                if not (end <= ps.span.start_code_point or start >= ps.span.end_code_point)
            ]
            if overlapping_protected and not any(ps.allowlist_override for ps in overlapping_protected):
                attempt = RuleAttempt(
                    attempt_id=f"SI-RULE-ATTEMPT-{attempt_counter:06d}",
                    request_id=request_id,
                    rule_id=rule.rule_id,
                    rule_version=rule.rule_version,
                    terminal_status=RuleAttemptTerminalStatus.BLOCKED_PROTECTED_SPAN,
                    reason_codes=[f"OVERLAPS_{ps.category.value}" for ps in overlapping_protected],
                    source_spans=[source_span],
                    candidate_id=None
                )
                attempt_counter += 1
                results.append((attempt, None))
                continue

            candidate_id = f"SI-CAND-{candidate_counter:06d}"
            candidate_counter += 1

            new_text = text[:start] + target + text[end:]
            output_span = CodePointSpan(
                start_code_point=start,
                end_code_point=start + len(target),
                text=target
            )

            op = TransformationOperation(
                operation_id=f"SI-OP-{candidate_counter:06d}",
                operation_type=OperationType.REPLACE,
                rule_id=rule.rule_id,
                raw_source_spans=[source_span],
                normalized_source_spans=[source_span],
                output_spans=[output_span],
                mapping_status=MappingStatus.MANY_TO_ONE,
                mapping_exact=True,
                before_hash_internal=compute_sha256(m.group()),
                after_hash_internal=compute_sha256(target),
                before_text_internal=m.group(),
                after_text_internal=target
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
