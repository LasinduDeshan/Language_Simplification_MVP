"""
Stage 33 — Stage 2: Deterministic Candidate Ranker.
Ranks strictly among eligible candidates that passed all mandatory Stage 1 guards.
Blocked candidates never participate in ranking.
"""

from typing import Dict, List, Optional, Tuple

from app.sinhala_simplification.enums import CandidateTerminalStatus, RuleType
from app.sinhala_simplification.rule_registry import GovernedRuleDefinition
from app.sinhala_simplification.schemas import RewriteCandidate


class CandidateRanker:
    """
    Stage 2 ranker: applies frozen deterministic precedence among eligible candidates.
    """

    def rank_candidates(
        self,
        eligible_candidates: List[RewriteCandidate],
        rules_map: Dict[str, GovernedRuleDefinition],
        source_text: str,
    ) -> Tuple[Optional[RewriteCandidate], List[RewriteCandidate]]:
        """
        Ranks eligible candidates. Returns (selected_candidate, updated_eligible_candidates).
        """
        if not eligible_candidates:
            return None, []

        def sort_key(cand: RewriteCandidate):
            rule = rules_map.get(cand.rule_id)
            priority = rule.priority if rule else 100
            rtype = rule.rule_type if rule else RuleType.LEXICAL_SUBSTITUTION

            # Criterion 1: Phrase rules preferred over lexical rules (longest match)
            phrase_rank = 0 if rtype == RuleType.PHRASE_SUBSTITUTION else 1

            # Criterion 2: Rule priority descending
            priority_rank = -priority

            # Criterion 3: Fewer operations preferred
            op_count = len(cand.operations)

            # Criterion 4: Lower edit length divergence
            cand_text = cand.candidate_text_internal or ""
            len_divergence = abs(len(cand_text) - len(source_text))

            # Criterion 5: Stable rule ID order
            stable_id = cand.rule_id

            return (phrase_rank, priority_rank, op_count, len_divergence, stable_id)

        sorted_candidates = sorted(eligible_candidates, key=sort_key)

        ranked: List[RewriteCandidate] = []
        selected: Optional[RewriteCandidate] = None

        for idx, cand in enumerate(sorted_candidates):
            if idx == 0:
                terminal_status = CandidateTerminalStatus.SELECTED
                updated = RewriteCandidate(
                    candidate_id=cand.candidate_id,
                    request_id=cand.request_id,
                    rule_id=cand.rule_id,
                    candidate_text_internal=cand.candidate_text_internal,
                    candidate_sha256_internal=cand.candidate_sha256_internal,
                    operations=cand.operations,
                    guard_results=cand.guard_results,
                    all_guards_passed=True,
                    terminal_status=terminal_status
                )
                selected = updated
                ranked.append(updated)
            else:
                terminal_status = CandidateTerminalStatus.NOT_SELECTED_LOWER_RANK
                updated = RewriteCandidate(
                    candidate_id=cand.candidate_id,
                    request_id=cand.request_id,
                    rule_id=cand.rule_id,
                    candidate_text_internal=cand.candidate_text_internal,
                    candidate_sha256_internal=cand.candidate_sha256_internal,
                    operations=cand.operations,
                    guard_results=cand.guard_results,
                    all_guards_passed=True,
                    terminal_status=terminal_status
                )
                ranked.append(updated)

        return selected, ranked
