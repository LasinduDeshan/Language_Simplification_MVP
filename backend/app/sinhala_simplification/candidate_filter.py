"""
Stage 33 — Stage 1: Candidate Eligibility Filter.
Evaluates mandatory semantic, lexical, structural, and Unicode guards on each candidate.
Eliminates any candidate that violates meaning invariants.
"""

from typing import Dict, List, Tuple

from app.sinhala_simplification.enums import (
    CandidateTerminalStatus,
    GuardType,
    MappingStatus,
    ProtectedSpanCategory,
)
from app.sinhala_simplification.protected_spans import (
    CURRENCY_MARKERS,
    MEASUREMENT_UNITS,
    MODALITY_MARKERS,
    NEGATION_MARKERS,
    RE_NUMBER,
    RE_QUOTATION,
)
from app.sinhala_simplification.schemas import GuardResult, ProtectedSpan, RewriteCandidate


class CandidateEligibilityFilter:
    """
    Stage 1 filter: rigorously verifies that proposed rewrite candidates preserve
    all configured meaning elements, Unicode invariants, and trace contracts.
    """

    def filter_candidates(
        self,
        candidates: List[RewriteCandidate],
        source_text: str,
        protected_spans: List[ProtectedSpan],
    ) -> Tuple[List[RewriteCandidate], List[RewriteCandidate]]:
        """
        Splits candidates into (eligible_candidates, eliminated_candidates).
        Updates guard_results and terminal_status on each candidate.
        """
        eligible: List[RewriteCandidate] = []
        eliminated: List[RewriteCandidate] = []

        for cand in candidates:
            cand_text = cand.candidate_text_internal or ""
            guards: Dict[str, GuardResult] = {}
            passed_all = True
            terminal_status = CandidateTerminalStatus.NOT_SELECTED_LOWER_RANK

            # 0. Atomic Single-Rule Policy Check (Must have exactly 1 applied rule)
            rule_ids = cand.applied_rule_ids or ([cand.rule_id] if cand.rule_id else [])
            if len(rule_ids) > 1 or len(cand.operations) > 1:
                guards["ATOMIC_RULE_POLICY"] = GuardResult(
                    guard_type=GuardType.MEANING_CRITICAL_SCOPE_CHECK,
                    passed=False,
                    reason_codes=["VIOLATED_ATOMIC_RULE_POLICY", "MULTI_RULE_COMPOSITION_PROHIBITED"],
                    violation_details="Candidates containing more than one applied transformation rule are rejected before guard evaluation"
                )
                cand_copy = cand.model_copy(update={
                    "guard_results": guards,
                    "all_guards_passed": False,
                    "terminal_status": CandidateTerminalStatus.BLOCKED_MEANING_GUARD
                })
                eliminated.append(cand_copy)
                continue

            # 1. Unicode Replacement Character Guard (U+FFFD)
            if "\uFFFD" in cand_text:
                guards[GuardType.UNICODE_REPLACEMENT_CHAR_CHECK.value] = GuardResult(
                    guard_type=GuardType.UNICODE_REPLACEMENT_CHAR_CHECK,
                    passed=False,
                    reason_codes=["INTRODUCED_REPLACEMENT_CHARACTER"],
                    violation_details="Text contains U+FFFD"
                )
                passed_all = False
                terminal_status = CandidateTerminalStatus.BLOCKED_MEANING_GUARD
            else:
                guards[GuardType.UNICODE_REPLACEMENT_CHAR_CHECK.value] = GuardResult(
                    guard_type=GuardType.UNICODE_REPLACEMENT_CHAR_CHECK,
                    passed=True,
                    reason_codes=[]
                )

            # 2. Number Preservation Guard
            src_nums = sorted(RE_NUMBER.findall(source_text))
            cand_nums = sorted(RE_NUMBER.findall(cand_text))
            if src_nums != cand_nums:
                guards[GuardType.NUMBER_PRESERVATION.value] = GuardResult(
                    guard_type=GuardType.NUMBER_PRESERVATION,
                    passed=False,
                    reason_codes=["NUMBER_MISMATCH"],
                    violation_details=f"Source numbers {src_nums} != Candidate numbers {cand_nums}"
                )
                passed_all = False
                terminal_status = CandidateTerminalStatus.BLOCKED_MEANING_GUARD
            else:
                guards[GuardType.NUMBER_PRESERVATION.value] = GuardResult(
                    guard_type=GuardType.NUMBER_PRESERVATION,
                    passed=True,
                    reason_codes=[]
                )

            # 3. Negation Preservation & Negation Scope Guard
            src_neg = [neg for neg in NEGATION_MARKERS if neg in source_text]
            cand_neg = [neg for neg in NEGATION_MARKERS if neg in cand_text]
            if src_neg != cand_neg:
                guards[GuardType.NEGATION_PRESERVATION.value] = GuardResult(
                    guard_type=GuardType.NEGATION_PRESERVATION,
                    passed=False,
                    reason_codes=["NEGATION_MISMATCH"],
                    violation_details=f"Source negation {src_neg} != Candidate negation {cand_neg}"
                )
                passed_all = False
                terminal_status = CandidateTerminalStatus.BLOCKED_MEANING_GUARD
            else:
                # Check negation scope: whether candidate modified text followed immediately by a negation marker
                in_neg_scope = False
                for op in cand.operations:
                    for raw_s in op.raw_source_spans:
                        subsequent = source_text[raw_s.end_code_point:raw_s.end_code_point + 30]
                        if any(neg in subsequent for neg in NEGATION_MARKERS):
                            in_neg_scope = True
                            break
                if in_neg_scope:
                    guards[GuardType.NEGATION_PRESERVATION.value] = GuardResult(
                        guard_type=GuardType.NEGATION_PRESERVATION,
                        passed=False,
                        reason_codes=["WITHIN_NEGATION_SCOPE"],
                        violation_details="Modification occurred within immediate syntactic scope of negation marker"
                    )
                    passed_all = False
                    terminal_status = CandidateTerminalStatus.BLOCKED_MEANING_GUARD
                else:
                    guards[GuardType.NEGATION_PRESERVATION.value] = GuardResult(
                        guard_type=GuardType.NEGATION_PRESERVATION,
                        passed=True,
                        reason_codes=[]
                    )

            # 4. Modality Preservation Guard
            src_mod = [mod for mod in MODALITY_MARKERS if mod in source_text]
            cand_mod = [mod for mod in MODALITY_MARKERS if mod in cand_text]
            if src_mod != cand_mod:
                guards[GuardType.MODALITY_PRESERVATION.value] = GuardResult(
                    guard_type=GuardType.MODALITY_PRESERVATION,
                    passed=False,
                    reason_codes=["MODALITY_MISMATCH"],
                    violation_details=f"Source modality {src_mod} != Candidate modality {cand_mod}"
                )
                passed_all = False
                terminal_status = CandidateTerminalStatus.BLOCKED_MEANING_GUARD
            else:
                guards[GuardType.MODALITY_PRESERVATION.value] = GuardResult(
                    guard_type=GuardType.MODALITY_PRESERVATION,
                    passed=True,
                    reason_codes=[]
                )

            # 5. Quotation Preservation Guard
            src_quotes = RE_QUOTATION.findall(source_text)
            cand_quotes = RE_QUOTATION.findall(cand_text)
            if src_quotes != cand_quotes:
                guards[GuardType.QUOTATION_PRESERVATION.value] = GuardResult(
                    guard_type=GuardType.QUOTATION_PRESERVATION,
                    passed=False,
                    reason_codes=["QUOTATION_MISMATCH"],
                    violation_details="Direct quotation altered or removed"
                )
                passed_all = False
                terminal_status = CandidateTerminalStatus.BLOCKED_MEANING_GUARD
            else:
                guards[GuardType.QUOTATION_PRESERVATION.value] = GuardResult(
                    guard_type=GuardType.QUOTATION_PRESERVATION,
                    passed=True,
                    reason_codes=[]
                )

            # 6. Protected-Span Inviolability Guard
            # Check overlap of operations with protected spans
            span_violated = False
            for op in cand.operations:
                for raw_s in op.raw_source_spans:
                    for ps in protected_spans:
                        if not ps.allowlist_override:
                            # check if interval [raw_s.start, raw_s.end) overlaps [ps.start, ps.end)
                            if not (raw_s.end_code_point <= ps.span.start_code_point or raw_s.start_code_point >= ps.span.end_code_point):
                                guards[GuardType.ENTITY_PRESERVATION.value] = GuardResult(
                                    guard_type=GuardType.ENTITY_PRESERVATION,
                                    passed=False,
                                    reason_codes=[f"OVERLAPS_{ps.category.value}"],
                                    violation_details=f"Operation overlaps protected span '{ps.text}' [{ps.span.start_code_point}, {ps.span.end_code_point})"
                                )
                                passed_all = False
                                span_violated = True
                                terminal_status = CandidateTerminalStatus.BLOCKED_PROTECTED_SPAN
                                break
                    if span_violated:
                        break
                if span_violated:
                    break

            if not span_violated:
                for ps in protected_spans:
                    if not ps.allowlist_override and ps.text not in cand_text:
                        guards[GuardType.ENTITY_PRESERVATION.value] = GuardResult(
                            guard_type=GuardType.ENTITY_PRESERVATION,
                            passed=False,
                            reason_codes=[f"ALTERED_PROTECTED_{ps.category.value}"],
                            violation_details=f"Protected span text '{ps.text}' missing in candidate"
                        )
                        passed_all = False
                        span_violated = True
                        terminal_status = CandidateTerminalStatus.BLOCKED_PROTECTED_SPAN
                        break
            if not span_violated:
                guards[GuardType.ENTITY_PRESERVATION.value] = GuardResult(
                    guard_type=GuardType.ENTITY_PRESERVATION,
                    passed=True,
                    reason_codes=[]
                )

            # 7. Unmapped Trace Guard
            for op in cand.operations:
                if op.mapping_status == MappingStatus.UNMAPPED:
                    guards[GuardType.MEANING_CRITICAL_SCOPE_CHECK.value] = GuardResult(
                        guard_type=GuardType.MEANING_CRITICAL_SCOPE_CHECK,
                        passed=False,
                        reason_codes=["UNMAPPED_TRACE_BLOCKED"],
                        violation_details="Operation contains unmapped trace and is not routed to manual review"
                    )
                    passed_all = False
                    terminal_status = CandidateTerminalStatus.BLOCKED_MEANING_GUARD
                    break

            # 8. Structural & Subject Recovery Guard (for sentence splits)
            # If candidate was flagged for ambiguous subject recovery or incomplete clause
            for op in cand.operations:
                if "AMBIGUOUS_SUBJECT_RECOVERY" in op.before_text_internal:
                    passed_all = False
                    terminal_status = CandidateTerminalStatus.DEFERRED_MANUAL_REVIEW
                    break
                if "INCOMPLETE_CLAUSE_STRUCTURE" in op.before_text_internal:
                    passed_all = False
                    terminal_status = CandidateTerminalStatus.BLOCKED_MEANING_GUARD
                    break

            # Update candidate copy
            updated_cand = RewriteCandidate(
                candidate_id=cand.candidate_id,
                request_id=cand.request_id,
                rule_id=cand.rule_id,
                candidate_text_internal=cand.candidate_text_internal,
                candidate_sha256_internal=cand.candidate_sha256_internal,
                operations=cand.operations,
                guard_results=guards,
                all_guards_passed=passed_all,
                terminal_status=terminal_status
            )

            if passed_all:
                eligible.append(updated_cand)
            else:
                eliminated.append(updated_cand)

        return eligible, eliminated
