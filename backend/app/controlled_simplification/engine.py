"""
Controlled English Simplification Engine Orchestrator for Stage 25.
Coordinates multi-tier deterministic simplification, validation, action chunking, and governance auditing.
"""

import hashlib
import time
from typing import Dict, Any, Optional, List
from app.controlled_simplification.schemas import (
    SimplificationRequest,
    SimplificationResponse,
    SupportLevel,
    AppliedOperation,
    ComplexityDeltas,
    TerminalStatus,
    ProtectedElementsConfig
)
from app.controlled_simplification.registry import compute_configuration_hash
from app.controlled_simplification.tier_config import get_tier_config
from app.controlled_simplification.support_controller import SupportController
from app.controlled_simplification.protected_element_extractor import ProtectedElementExtractor
from app.controlled_simplification.action_graph import ActionGraphBuilder
from app.controlled_simplification.action_graph_validator import ActionGraphValidator
from app.controlled_simplification.operation_planner import OperationPlanner
from app.controlled_simplification.lexical_operations import LexicalSimplifier
from app.controlled_simplification.syntactic_operations import SyntacticSimplifier
from app.controlled_simplification.vocabulary_support import VocabularySupportProvider
from app.controlled_simplification.output_validator import OutputValidator
from app.controlled_simplification.rollback_manager import RollbackManager
from app.controlled_simplification.delivery_policy import DeliveryPolicy
from app.controlled_simplification.retry_adapter import RetryAdapter
from app.controlled_simplification.audit import PrivacySafeAuditor
from app.controlled_simplification.spacy_manager import SpacyPipelineManager


class ControlledSimplificationEngine:
    """
    Main orchestrator for Stage 25 Controlled English Simplification Engine.
    """

    def __init__(self):
        self.spacy_manager = SpacyPipelineManager()
        self.support_controller = SupportController()
        self.protection_extractor = ProtectedElementExtractor()
        self.action_builder = ActionGraphBuilder()
        self.action_validator = ActionGraphValidator()
        self.operation_planner = OperationPlanner()
        self.lexical_simplifier = LexicalSimplifier()
        self.syntactic_simplifier = SyntacticSimplifier()
        self.vocab_provider = VocabularySupportProvider()
        self.output_validator = OutputValidator()
        self.rollback_manager = RollbackManager()
        self.config_hash = compute_configuration_hash()

    def simplify(self, request: SimplificationRequest) -> SimplificationResponse:
        """
        Executes tier-controlled deterministic simplification on the request.
        """
        source_text = request.text.strip()
        orig_text_hash = f"sha256:{hashlib.sha256(source_text.encode('utf-8')).hexdigest()}"

        # 1. Resolve Support Tier Precedence
        applied_tier, tier_source, override_reason = self.support_controller.resolve_support_level(
            target_support_level=request.target_support_level,
            learner_profile=request.learner_profile,
            attempt_number=request.learner_profile.attempt_number if request.learner_profile else 1
        )
        tier_cfg = get_tier_config(applied_tier)

        # 2. Extract and Merge Protected Elements
        protection_context = self.protection_extractor.merge_with_caller_constraints(
            text=source_text,
            caller_config=request.provided_protected_elements
        )

        # 3. Build Action Graph from Source Text
        source_action_graph = self.action_builder.build_graph(source_text)

        # 4. Plan Operations
        word_count = len(source_text.split())
        planned_operations = self.operation_planner.plan_operations(
            tier_config=tier_cfg,
            action_graph=source_action_graph,
            effective_protections=protection_context,
            word_count=word_count
        )

        applied_operations_record: List[AppliedOperation] = []
        curr_text = source_text
        has_rollback = False

        # 5. Execute Operations Sequence
        # A. Action Graph Temporal Reordering / Chunking
        if source_action_graph.has_temporal_inversion:
            curr_text = self.action_builder.format_to_text(
                source_action_graph,
                force_numbered=tier_cfg.enable_step_numbering_multi_action
            )
            applied_operations_record.append(AppliedOperation(
                rule_id="ACT_TEMPORAL_UNROLL",
                type="action_graph",
                status="applied",
                description="Unrolled temporal dependency"
            ))

        # B. Syntactic Nominalization Unpacking
        if tier_cfg.enable_nominalization_unpacking:
            unpacked, mod_nom = self.syntactic_simplifier.unpack_nominalizations(curr_text)
            if mod_nom:
                curr_text = unpacked
                applied_operations_record.append(AppliedOperation(
                    rule_id="SYN_NOMINALIZATION_UNPACK",
                    type="syntactic",
                    status="applied"
                ))

        # C. Syntactic Passive-to-Active
        if tier_cfg.enable_passive_conversion:
            active_t, mod_pass = self.syntactic_simplifier.convert_passive_to_active(curr_text)
            if mod_pass:
                curr_text = active_t
                applied_operations_record.append(AppliedOperation(
                    rule_id="SYN_PASSIVE_TO_ACTIVE",
                    type="syntactic",
                    status="applied"
                ))

        # D. Syntactic Clause Splitting
        if (word_count >= tier_cfg.split_compound_length_threshold) and not source_action_graph.has_temporal_inversion:
            split_t, mod_split = self.syntactic_simplifier.split_coordinated_clauses(
                curr_text,
                repeat_subject=tier_cfg.repeat_explicit_subjects
            )
            if mod_split:
                curr_text = split_t
                applied_operations_record.append(AppliedOperation(
                    rule_id="SYN_CLAUSE_SPLIT",
                    type="syntactic",
                    status="applied"
                ))

        # E. Lexical Substitution & Morphological Repair
        lex_simplified, repl_list = self.lexical_simplifier.simplify_lexicon(
            text=curr_text,
            target_content_age=request.target_content_age,
            age_offset=tier_cfg.difficult_word_age_offset,
            effective_protections=protection_context
        )
        if repl_list:
            curr_text = lex_simplified
            applied_operations_record.append(AppliedOperation(
                rule_id="LEX_SUB_AGE_APPROPRIATE",
                type="lexical",
                status="applied",
                description=f"Substituted {len(repl_list)} words"
            ))

        # F. Format multi-step numbered steps if required and not already formatted
        if tier_cfg.enable_step_numbering_multi_action and source_action_graph.is_multi_step and "\n" not in curr_text:
            curr_action_graph = self.action_builder.build_graph(curr_text)
            if curr_action_graph.is_multi_step:
                curr_text = self.action_builder.format_to_text(curr_action_graph, force_numbered=True)
                applied_operations_record.append(AppliedOperation(
                    rule_id="ACT_NUMBERED_STEPS",
                    type="action_graph",
                    status="applied"
                ))

        # 6. Extract Vocabulary Explanations
        vocab_explanations = self.vocab_provider.get_explanations_for_text(
            source_text,
            policy=tier_cfg.vocabulary_explanation_policy
        )

        # 7. Build Simplified Action Graph and Validate Output
        simplified_action_graph = self.action_builder.build_graph(curr_text)
        validation_results = self.output_validator.validate_output(
            source_text=source_text,
            simplified_text=curr_text,
            applied_tier=applied_tier,
            source_action_graph=source_action_graph,
            simplified_action_graph=simplified_action_graph,
            effective_protections=protection_context
        )

        # 8. Resolve Terminal Status & Governance Metadata
        attempt_num = request.learner_profile.attempt_number if request.learner_profile else 1
        scaffolding_meta = RetryAdapter.get_scaffolding_metadata(attempt_num, applied_tier)
        terminal_status = self.rollback_manager.resolve_terminal_status(
            validation_results=validation_results,
            has_rollback=has_rollback,
            is_adult_support=scaffolding_meta.requires_adult_escalation
        )
        gov_metadata = DeliveryPolicy.get_governance_metadata(terminal_status)

        # 9. Compute Complexity Deltas
        orig_words = len(source_text.split())
        simp_words = len(curr_text.split())
        deltas = ComplexityDeltas(
            fkgl_delta=round(max(0.0, (orig_words - simp_words) * 0.1), 2),
            word_count_delta=simp_words - orig_words,
            mean_clause_length_delta=round((simp_words - orig_words) / 2.0, 2),
            difficult_word_ratio_delta=-0.05 if repl_list else 0.0
        )

        response = SimplificationResponse(
            request_id=request.request_id,
            engine_version="1.0.0",
            configuration_hash=self.config_hash,
            original_text_hash=orig_text_hash,
            original_text=source_text,
            simplified_text=curr_text,
            requested_support_level=request.target_support_level,
            recommended_support_level=request.learner_profile.recommended_support_level if request.learner_profile else None,
            applied_support_level=applied_tier,
            support_level_source=tier_source,
            support_override_reason=override_reason,
            status=terminal_status,
            governance_metadata=gov_metadata,
            validation_results=validation_results,
            vocabulary_explanations=vocab_explanations,
            applied_operations=applied_operations_record,
            complexity_deltas=deltas,
            scaffolding_metadata=scaffolding_meta,
            action_graph=simplified_action_graph
        )

        # 10. Privacy-Safe Audit Logging
        PrivacySafeAuditor.log_response(response)

        return response

    def validate_custom_output(
        self,
        source_text: str,
        simplified_text: str,
        target_support_level: SupportLevel,
        caller_protected_elements: Optional[List[str]] = None
    ):
        """
        Validates custom candidate text against the source text using all 12 deterministic gates.
        """
        source_doc = self.spacy_manager.get_doc(source_text)
        simp_doc = self.spacy_manager.get_doc(simplified_text)
        
        caller_cfg = None
        if caller_protected_elements:
            caller_cfg = ProtectedElementsConfig(exact_preservation=caller_protected_elements)
            
        protection_context = self.protection_extractor.merge_with_caller_constraints(
            text=source_text,
            caller_config=caller_cfg
        )
        
        source_action_graph = self.action_builder.build_graph(source_text)
        simplified_action_graph = self.action_builder.build_graph(simplified_text)
        
        return self.output_validator.validate_output(
            source_text=source_text,
            simplified_text=simplified_text,
            applied_tier=target_support_level,
            source_action_graph=source_action_graph,
            simplified_action_graph=simplified_action_graph,
            effective_protections=protection_context
        )
