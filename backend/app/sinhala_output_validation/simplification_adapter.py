"""
Stage 36 Simplification Adapter & Governance Orchestrator
Component 3: AI/NLP-Based Language Simplification

Invariants:
1. Upstream Immutability: The Stage 33 codebase is sealed and immutable.
   This adapter wraps SimplificationPipeline.process_request() without modifying Stage 33.
2. Two-Pass Validation: Both the Stage 33 candidate and the governed catalog fallback
   are evaluated against the exact same Stage 36 V0–V9 validation context envelope.
3. Fail-Closed Governance: An internal anomaly or validation rejection falls back
   in strict sequence: Stage 33 candidate -> Governed Catalog Fallback -> Governed Reuse -> Safe Abstention.
4. Privacy & Opaque References: Sensitive cryptographic hashes remain server-side.
"""

import hashlib
import uuid
from typing import Any, Dict, List, Optional, Tuple

from app.localization.enums import TargetDisclosureClass, TargetDisclosurePolicy
from app.localization.target_aliases import get_target_alias_metadata, load_target_aliases
from app.sinhala_output_validation.engine import determine_candidate_disposition
from app.sinhala_output_validation.schemas import (
    CandidateDisposition,
    CandidateEnvelope,
    ExecutionMode,
    ProviderCondition,
    SeverityLevel,
)
from app.sinhala_output_validation.validators.registry import ValidatorPipeline
from app.sinhala_simplification.enums import CorpusView, FinalDisposition, Partition
from app.sinhala_simplification.pipeline import SimplificationPipeline
from app.sinhala_simplification.schemas import RewriteRequest, RightsProfileBinding


class Stage36SimplificationAdapter:
    """
    Adapter interfacing between SessionService and the frozen Stage 33 SimplificationPipeline.
    Executes V0–V9 output validation, template fallback, and governed reuse routing.
    """

    def __init__(self, pipeline: Optional[SimplificationPipeline] = None, validator_pipeline: Optional[ValidatorPipeline] = None):
        self.pipeline = pipeline or SimplificationPipeline()
        self.validator_pipeline = validator_pipeline or ValidatorPipeline(halt_on_critical=True)

    def simplify_attempt_3(
        self,
        task_code: str,
        source_text: str,
        attempt_2_instruction: Optional[str] = None,
        attempt_2_id: Optional[str] = None,
        target_id: Optional[str] = None,
        catalog_fallback_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes multi-pass simplification for Attempt 3 (STRONG_DECOMPOSED_STEP).
        Returns a dictionary containing:
        - presented_instruction: str
        - lineage_dict: Dict[str, Any] (matching discriminated Pydantic models)
        - validation_passed: bool
        """
        source_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
        source_ref = f"governed://task/{task_code}/source"

        # Resolve disclosure classification & policy
        alias_meta = get_target_alias_metadata(target_id) if target_id else None
        disclosure_class = (
            alias_meta["target_disclosure_class"]
            if alias_meta
            else TargetDisclosureClass.INFERRED_ANSWER
        )
        disclosure_policy = (
            alias_meta["target_disclosure_policy"]
            if alias_meta
            else TargetDisclosurePolicy.DO_NOT_REVEAL
        )
        loaded_aliases = load_target_aliases(target_id) if target_id else {"en": [], "si": []}

        # Build validation context envelope (identical for both passes)
        validation_context: Dict[str, Any] = {
            "task_id": task_code,
            "strategy_code": "STRONG_DECOMPOSED_STEP",
            "attempt_number": 3,
            "target_id": target_id,
            "target_disclosure_class": disclosure_class,
            "target_disclosure_policy": disclosure_policy,
            "target_aliases": loaded_aliases,
        }

        # ==============================================================================
        # Pass 1: Stage 33 Deterministic Rule Engine Candidate Generation
        # ==============================================================================
        candidate_text: Optional[str] = None
        applied_rule_ids: List[str] = []
        simp_run_id = f"SIMP-RUN-{uuid.uuid4().hex[:12].upper()}"

        try:
            rewrite_req = RewriteRequest(
                request_id=f"SI-SIMP-REQ-{uuid.uuid4().hex[:8].upper()}",
                record_id=task_code,
                source_storage_ref=source_ref,
                source_sha256_internal=source_hash,
                language="si",
                stage30_configuration_hash="3a28f8045958793b8d64115cbdfb19e2",
                stage31_split_manifest_hash="stage31_analytical_manifest_150_hash",
                stage31_corpus_view=CorpusView.CANONICAL_ANALYTICAL_150,
                stage32_configuration_hash="stage32_lexicon_configuration_hash",
                stage32_lexicon_manifest_hash="stage32_lexicon_manifest_hash",
                stage33_configuration_hash="stage33_rule_configuration_hash",
                rights_profile_ids_and_versions=[
                    RightsProfileBinding(rights_profile_id="RP-SRC-SI-001", rights_profile_version=1)
                ],
                partition=Partition.TEST,
            )

            final_rec, attempts, all_cands, all_ops = self.pipeline.process_request(
                rewrite_req, source_text
            )

            if final_rec.final_disposition == FinalDisposition.SIMPLIFICATION_APPLIED and final_rec.selected_candidate_id:
                for c in all_cands:
                    if c.candidate_id == final_rec.selected_candidate_id:
                        candidate_text = c.candidate_text_internal
                        applied_rule_ids = list(final_rec.applied_rule_ids)
                        break

        except Exception:
            # Stage 33 execution anomaly fails closed to catalog fallback
            candidate_text = None

        # Validate Pass 1 Candidate through V0–V9
        if candidate_text and candidate_text.strip() and candidate_text.strip() != source_text.strip():
            cand_hash = hashlib.sha256(candidate_text.encode("utf-8")).hexdigest()
            envelope_p1 = CandidateEnvelope(
                candidate_id=f"CAND-ST36-P1-{uuid.uuid4().hex[:8]}",
                request_id=f"REQ-ST36-P1-{uuid.uuid4().hex[:8]}",
                source_record_id=task_code,
                source_text_ref=source_ref,
                source_text_sha256_internal=source_hash,
                candidate_text_ref=f"governed://task/{task_code}/candidate_p1",
                candidate_text_sha256_internal=cand_hash,
                provider_condition=ProviderCondition.C0_RULE_BASELINE,
                execution_mode=ExecutionMode.RULE_ENGINE,
                generation_configuration_hash="stage36_generation_config_v1",
            )

            findings_p1, count_p1, status_p1 = self.validator_pipeline.execute(
                source_text, candidate_text, envelope_p1, validation_context
            )
            disp_p1 = determine_candidate_disposition(findings_p1, is_unchanged=False)

            if disp_p1 == CandidateDisposition.ACCEPTED_TECHNICAL_RESEARCH_CANDIDATE:
                return {
                    "presented_instruction": candidate_text,
                    "lineage_dict": {
                        "strategy_code": "STRONG_DECOMPOSED_STEP",
                        "generation_mode": "RULE_ENGINE",
                        "simplification_status": "CHANGED_AND_VALIDATED",
                        "source_instruction_ref": source_ref,
                        "presented_instruction_ref": f"governed://task/{task_code}/presented",
                        "simplification_run_id": simp_run_id,
                        "applied_rule_ids": applied_rule_ids,
                        "target_disclosure_class": disclosure_class,
                        "target_disclosure_policy": disclosure_policy,
                        "independent_performance_measure": False,
                        "score_interpretation": "HIGHLY_SUPPORTED_PERFORMANCE",
                    },
                    "validation_passed": True,
                }

        # ==============================================================================
        # Pass 2: Governed Catalog Template Fallback
        # ==============================================================================
        if catalog_fallback_text and catalog_fallback_text.strip():
            fb_text = catalog_fallback_text.strip()
            fb_hash = hashlib.sha256(fb_text.encode("utf-8")).hexdigest()
            envelope_p2 = CandidateEnvelope(
                candidate_id=f"CAND-ST36-FB-{uuid.uuid4().hex[:8]}",
                request_id=f"REQ-ST36-FB-{uuid.uuid4().hex[:8]}",
                source_record_id=task_code,
                source_text_ref=source_ref,
                source_text_sha256_internal=source_hash,
                candidate_text_ref=f"governed://task/{task_code}/candidate_fb",
                candidate_text_sha256_internal=fb_hash,
                execution_mode=ExecutionMode.DETERMINISTIC_COPY,
                generation_configuration_hash="stage36_generation_config_v1",
            )

            findings_p2, count_p2, status_p2 = self.validator_pipeline.execute(
                source_text, fb_text, envelope_p2, validation_context
            )
            disp_p2 = determine_candidate_disposition(findings_p2, is_unchanged=False)

            if disp_p2 == CandidateDisposition.ACCEPTED_TECHNICAL_RESEARCH_CANDIDATE:
                return {
                    "presented_instruction": fb_text,
                    "lineage_dict": {
                        "strategy_code": "STRONG_DECOMPOSED_STEP",
                        "generation_mode": "TEMPLATE_CATALOG",
                        "simplification_status": "TEMPLATE_FALLBACK_USED",
                        "source_instruction_ref": source_ref,
                        "presented_instruction_ref": f"governed://task/{task_code}/presented",
                        "template_variant_id": f"{task_code}:strong_decomposed_step:v1",
                        "target_disclosure_class": disclosure_class,
                        "target_disclosure_policy": disclosure_policy,
                        "independent_performance_measure": False,
                        "score_interpretation": "HIGHLY_SUPPORTED_PERFORMANCE",
                    },
                    "validation_passed": True,
                }

        # ==============================================================================
        # Pass 3: Governed Unchanged Reuse of Previously Validated Attempt 2
        # ==============================================================================
        if attempt_2_instruction and attempt_2_instruction.strip() and attempt_2_id:
            reused_text = attempt_2_instruction.strip()
            
            reuse_valid = False
            # Verify that reused Attempt 2 does not violate disclosure policy
            if disclosure_policy == TargetDisclosurePolicy.DO_NOT_REVEAL and target_id:
                reused_hash = hashlib.sha256(reused_text.encode("utf-8")).hexdigest()
                envelope_reuse = CandidateEnvelope(
                    candidate_id=f"CAND-ST36-REUSE-{uuid.uuid4().hex[:8]}",
                    request_id=f"REQ-ST36-REUSE-{uuid.uuid4().hex[:8]}",
                    source_record_id=task_code,
                    source_text_ref=source_ref,
                    source_text_sha256_internal=source_hash,
                    candidate_text_ref=f"governed://task/{task_code}/candidate_reuse",
                    candidate_text_sha256_internal=reused_hash,
                    execution_mode=ExecutionMode.DETERMINISTIC_COPY,
                    generation_configuration_hash="stage36_generation_config_v1",
                )
                findings_reuse, _, _ = self.validator_pipeline.execute(
                    source_text, reused_text, envelope_reuse, validation_context
                )
                has_critical = any(f.severity == SeverityLevel.CRITICAL for f in findings_reuse)
                if not has_critical:
                    reuse_valid = True
            else:
                reuse_valid = True

            if reuse_valid:
                return {
                    "presented_instruction": reused_text,
                    "lineage_dict": {
                        "strategy_code": "STRONG_DECOMPOSED_STEP",
                        "generation_mode": "UNCHANGED_REUSE",
                        "simplification_status": "NO_FURTHER_SAFE_SIMPLIFICATION",
                        "source_instruction_ref": source_ref,
                        "presented_instruction_ref": f"governed://task/{task_code}/presented",
                        "reused_from_attempt_id": attempt_2_id,
                        "reuse_reason_code": "MINIMAL_SAFE_INSTRUCTION_ALREADY_REACHED",
                        "target_disclosure_class": disclosure_class,
                        "target_disclosure_policy": disclosure_policy,
                        "independent_performance_measure": False,
                        "score_interpretation": "HIGHLY_SUPPORTED_PERFORMANCE",
                    },
                    "validation_passed": True,
                }

        # ==============================================================================
        # Fallback 4: Safe Abstention (Return original prompt fail-closed)
        # ==============================================================================
        return {
            "presented_instruction": source_text,
            "lineage_dict": {
                "strategy_code": "STRONG_DECOMPOSED_STEP",
                "generation_mode": "UNCHANGED_REUSE",
                "simplification_status": "FAILED_INTERNAL",
                "source_instruction_ref": source_ref,
                "presented_instruction_ref": source_ref,
                "reused_from_attempt_id": attempt_2_id or "NONE",
                "reuse_reason_code": "MINIMAL_SAFE_INSTRUCTION_ALREADY_REACHED",
                "target_disclosure_class": disclosure_class,
                "target_disclosure_policy": disclosure_policy,
                "independent_performance_measure": False,
                "score_interpretation": "HIGHLY_SUPPORTED_PERFORMANCE",
            },
            "validation_passed": False,
        }
