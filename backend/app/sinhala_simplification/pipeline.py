"""
Stage 33 — End-to-End Sinhala Simplification Pipeline.
Orchestrates protected span detection, rule applicability matching, candidate generation,
two-stage candidate resolution, trace recording, and governed audit ledgers.
"""

from typing import Dict, List, Optional, Tuple

from app.sinhala_simplification.candidate_selector import CandidateSelector
from app.sinhala_simplification.enums import RuleType
from app.sinhala_simplification.lexical_rules import LexicalRuleEngine
from app.sinhala_simplification.phrase_rules import PhraseRuleEngine
from app.sinhala_simplification.protected_spans import ProtectedSpanDetector
from app.sinhala_simplification.rule_registry import GovernedRuleDefinition, RuleRegistry
from app.sinhala_simplification.schemas import (
    FinalRewriteRecord,
    ProtectedSpan,
    RewriteCandidate,
    RewriteRequest,
    RuleAttempt,
    TransformationOperation,
)
from app.sinhala_simplification.sentence_splitter import SentenceSplitterEngine
from app.sinhala_simplification.syntactic_rules import SyntacticRuleEngine


class SimplificationPipeline:
    """
    Governed pipeline executing deterministic Sinhala simplification rules.
    """

    def __init__(self, registry: Optional[RuleRegistry] = None):
        self.registry = registry or RuleRegistry()
        self.rules_map: Dict[str, GovernedRuleDefinition] = {}
        self.detector = ProtectedSpanDetector()
        self.lexical_engine = LexicalRuleEngine()
        self.phrase_engine = PhraseRuleEngine()
        self.sentence_engine = SentenceSplitterEngine()
        self.syntactic_engine = SyntacticRuleEngine()
        self.selector = CandidateSelector()

        self._attempt_counter = 1
        self._candidate_counter = 1
        self._output_counter = 1

    def initialize(self):
        """Loads and binds the rule registry and external protected payloads."""
        self.rules_map = self.registry.load_registry()

    def process_request(
        self,
        request: RewriteRequest,
        source_text: str,
    ) -> Tuple[FinalRewriteRecord, List[RuleAttempt], List[RewriteCandidate], List[TransformationOperation]]:
        """
        Executes end-to-end simplification on a single request.
        """
        if not self.rules_map:
            self.initialize()

        # Step 1: Detect meaning-critical protected spans
        protected_spans = self.detector.detect_spans(source_text)

        attempts: List[RuleAttempt] = []
        generated_candidates: List[RewriteCandidate] = []

        # Step 2: Evaluate each active governed rule
        for rid, rule_def in self.rules_map.items():
            rtype = rule_def.rule_type
            if rtype == RuleType.LEXICAL_SUBSTITUTION:
                res = self.lexical_engine.evaluate_rule(
                    rule_def, source_text, request.request_id, protected_spans,
                    self._attempt_counter, self._candidate_counter
                )
            elif rtype == RuleType.PHRASE_SUBSTITUTION:
                res = self.phrase_engine.evaluate_rule(
                    rule_def, source_text, request.request_id, protected_spans,
                    self._attempt_counter, self._candidate_counter
                )
            elif rtype == RuleType.SENTENCE_SPLIT:
                res = self.sentence_engine.evaluate_rule(
                    rule_def, source_text, request.request_id, protected_spans,
                    self._attempt_counter, self._candidate_counter
                )
            elif rtype == RuleType.CONSERVATIVE_SYNTACTIC:
                res = self.syntactic_engine.evaluate_rule(
                    rule_def, source_text, request.request_id, protected_spans,
                    self._attempt_counter, self._candidate_counter
                )
            else:
                continue

            for att, cand in res:
                attempts.append(att)
                self._attempt_counter += 1
                if cand:
                    generated_candidates.append(cand)
                    self._candidate_counter += 1

        # Step 3: Candidate Selection and Governed Fallback
        final_record, all_candidates = self.selector.select_candidate(
            request, source_text, generated_candidates, protected_spans,
            self.rules_map, self._output_counter
        )
        self._output_counter += 1

        # Step 4: Collect all operations from candidates
        all_operations: List[TransformationOperation] = []
        for cand in all_candidates:
            all_operations.extend(cand.operations)

        return final_record, attempts, all_candidates, all_operations
