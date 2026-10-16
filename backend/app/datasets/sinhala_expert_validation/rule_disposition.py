"""
Stage 34 — Rule Disposition and Backlog Service
Synthesizes expert findings into governed rule-level dispositions and a versioned correction backlog.
Reconciles Level 7 accounting.
"""

from typing import Any, Dict, List, Optional
from .enums import RuleDisposition
from .schemas import RuleDispositionRecord


class RuleDispositionService:
    def __init__(self):
        self._rules: Dict[str, RuleDispositionRecord] = {}

    def record_disposition(self, record: RuleDispositionRecord) -> RuleDispositionRecord:
        self._rules[record.rule_id] = record
        return record

    def get_disposition(self, rule_id: str) -> Optional[RuleDispositionRecord]:
        return self._rules.get(rule_id)

    def list_dispositions(self) -> List[RuleDispositionRecord]:
        return list(self._rules.values())

    def reconcile_rule_accounting(self) -> Dict[str, int]:
        """Level 7 Accounting: EvaluatedRules = SupportedForResearch + SupportedWithConstraints + RevisionRequired + Rejected + InsufficientEvidence + UnresolvedDisagreement + Unaccounted"""
        total = len(self._rules)
        supported_res = sum(
            1 for r in self._rules.values() if r.disposition == RuleDisposition.SUPPORTED_FOR_FURTHER_RESEARCH
        )
        supported_con = sum(
            1 for r in self._rules.values() if r.disposition == RuleDisposition.SUPPORTED_WITH_CONSTRAINTS
        )
        revision = sum(1 for r in self._rules.values() if r.disposition == RuleDisposition.REVISION_REQUIRED)
        rejected = sum(
            1 for r in self._rules.values() if r.disposition == RuleDisposition.REJECT_RULE_OR_OUTPUT_PATTERN
        )
        insufficient = sum(
            1 for r in self._rules.values() if r.disposition == RuleDisposition.INSUFFICIENT_EXPERT_EVIDENCE
        )
        unresolved = sum(
            1 for r in self._rules.values() if r.disposition == RuleDisposition.UNRESOLVED_EXPERT_DISAGREEMENT
        )

        unaccounted = total - (
            supported_res + supported_con + revision + rejected + insufficient + unresolved
        )

        return {
            "total_rules": total,
            "supported_for_further_research": supported_res,
            "supported_with_constraints": supported_con,
            "revision_required": revision,
            "rejected": rejected,
            "insufficient_expert_evidence": insufficient,
            "unresolved_expert_disagreement": unresolved,
            "unaccounted": unaccounted,
        }
