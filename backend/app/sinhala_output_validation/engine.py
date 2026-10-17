"""
Stage 36 Candidate Disposition Router and Governed Fallback Engine.
Implements 9-tier fixed precedence disposition assignment and bounded fail-closed fallback ladder.
"""

from datetime import datetime, timezone
import hashlib
from typing import Any, Callable, Dict, List, Optional, Tuple

from app.sinhala_output_validation.schemas import (
    AutomatedValidationStatus,
    CandidateDisposition,
    CandidateEnvelope,
    ExecutionMode,
    ExecutionOutcome,
    FallbackStep,
    FallbackTransitionType,
    ProviderCondition,
    RequestFinalOutcome,
    RequestTrace,
    SeverityLevel,
    ValidationResult,
    ValidatorFinding,
)
from app.sinhala_output_validation.validators.registry import ValidatorPipeline


def _get_enum_str(val: Any) -> str:
    if hasattr(val, "value"):
        return str(val.value)
    return str(val) if val is not None else ""


def determine_candidate_disposition(
    findings: List[ValidatorFinding],
    is_unchanged: bool
) -> CandidateDisposition:
    """
    Evaluates findings in strict 9-tier fixed precedence order:
    1. REJECTED_CONFIGURATION_OR_PROVENANCE
    2. REJECTED_INVALID_UNICODE
    3. REJECTED_PROTECTED_SPAN_VIOLATION
    4. REJECTED_NUMERICAL_OR_POLARITY_DRIFT
    5. REJECTED_UNSUPPORTED_INSERTION
    6. REJECTED_CRITICAL_SEMANTIC_RISK
    7. MANUAL_REVIEW_REQUIRED
    8. VALID_UNCHANGED_NO_SIMPLIFICATION
    9. ACCEPTED_TECHNICAL_RESEARCH_CANDIDATE
    """
    critical_findings = [f for f in findings if _get_enum_str(f.severity) == SeverityLevel.CRITICAL.value]
    review_findings = [f for f in findings if _get_enum_str(f.severity) == SeverityLevel.REVIEW.value]

    # Rank 1: REJECTED_CONFIGURATION_OR_PROVENANCE
    for f in critical_findings:
        if f.reason_code == "REJ_CONF_PROVENANCE_INVALID":
            return CandidateDisposition.REJECTED_CONFIGURATION_OR_PROVENANCE

    # Rank 2: REJECTED_INVALID_UNICODE
    for f in critical_findings:
        if f.reason_code in ("REJ_INVALID_UNICODE", "REJ_NON_SINHALA_SCRIPT"):
            return CandidateDisposition.REJECTED_INVALID_UNICODE

    # Rank 3: REJECTED_PROTECTED_SPAN_VIOLATION
    for f in critical_findings:
        if f.reason_code == "REJ_PROTECTED_SPAN_VIOLATION":
            return CandidateDisposition.REJECTED_PROTECTED_SPAN_VIOLATION

    # Rank 4: REJECTED_NUMERICAL_OR_POLARITY_DRIFT
    for f in critical_findings:
        if f.reason_code == "REJ_NUMERICAL_OR_POLARITY_DRIFT":
            return CandidateDisposition.REJECTED_NUMERICAL_OR_POLARITY_DRIFT

    # Rank 5: REJECTED_UNSUPPORTED_INSERTION
    for f in critical_findings:
        if f.reason_code == "REJ_UNSUPPORTED_INSERTION":
            return CandidateDisposition.REJECTED_UNSUPPORTED_INSERTION

    # Rank 6: REJECTED_CRITICAL_SEMANTIC_RISK
    for f in critical_findings:
        if f.reason_code == "REJ_CRITICAL_SEMANTIC_RISK":
            return CandidateDisposition.REJECTED_CRITICAL_SEMANTIC_RISK

    # Any other unclassified critical finding defaults to semantic/operational risk
    if critical_findings:
        return CandidateDisposition.REJECTED_CRITICAL_SEMANTIC_RISK

    # Rank 7: MANUAL_REVIEW_REQUIRED
    if review_findings:
        return CandidateDisposition.MANUAL_REVIEW_REQUIRED

    # Rank 8: VALID_UNCHANGED_NO_SIMPLIFICATION
    if is_unchanged:
        return CandidateDisposition.VALID_UNCHANGED_NO_SIMPLIFICATION

    # Rank 9: ACCEPTED_TECHNICAL_RESEARCH_CANDIDATE
    return CandidateDisposition.ACCEPTED_TECHNICAL_RESEARCH_CANDIDATE


def validate_candidate(
    source_text: str,
    candidate_text: str,
    envelope: CandidateEnvelope,
    context: Dict[str, Any],
    configuration_hash: str = "stage36-unfrozen-dev",
    pipeline: Optional[ValidatorPipeline] = None,
) -> ValidationResult:
    """
    Execute full validation on a candidate envelope and assign terminal disposition.
    """
    pipeline = pipeline or ValidatorPipeline()
    result_id = f"valres_{envelope.candidate_id}"

    try:
        findings, completed_count, auto_status = pipeline.execute(
            source_text=source_text,
            candidate_text=candidate_text,
            envelope=envelope,
            context=context,
        )

        is_unchanged = (candidate_text.strip() == source_text.strip())
        disposition = determine_candidate_disposition(findings, is_unchanged)

        critical_passed = disposition in (
            CandidateDisposition.ACCEPTED_TECHNICAL_RESEARCH_CANDIDATE,
            CandidateDisposition.VALID_UNCHANGED_NO_SIMPLIFICATION,
            CandidateDisposition.MANUAL_REVIEW_REQUIRED,
        )
        fallback_required = disposition not in (
            CandidateDisposition.ACCEPTED_TECHNICAL_RESEARCH_CANDIDATE,
            CandidateDisposition.VALID_UNCHANGED_NO_SIMPLIFICATION,
        )

        return ValidationResult(
            validation_result_id=result_id,
            candidate_id=envelope.candidate_id,
            configuration_hash=configuration_hash,
            execution_outcome=ExecutionOutcome.COMPLETED,
            candidate_disposition=disposition,
            automated_validation_status=auto_status,
            completed_validator_count=completed_count,
            expected_validator_count=len(pipeline.validators),
            critical_gate_passed=critical_passed,
            fallback_required=fallback_required,
            findings=findings,
            diagnostic_metrics=context.get("diagnostic_metrics", {}),
            selected_output_ref=envelope.candidate_text_ref if critical_passed else None,
            selected_output_origin=(
                envelope.provider_condition.value
                if hasattr(envelope.provider_condition, "value")
                else str(envelope.provider_condition)
            ) if critical_passed else None,
            approved_for_child_delivery=False,
            approved_for_unsupervised_child_delivery=False,
            requires_expert_review=True,
        )

    except Exception as e:
        # Fail-closed internal error handling
        return ValidationResult(
            validation_result_id=result_id,
            candidate_id=envelope.candidate_id,
            configuration_hash=configuration_hash,
            execution_outcome=ExecutionOutcome.FAILED_INTERNAL,
            candidate_disposition=None,
            automated_validation_status=AutomatedValidationStatus.FAILED_INTERNAL,
            completed_validator_count=0,
            expected_validator_count=len(pipeline.validators),
            critical_gate_passed=False,
            fallback_required=True,
            findings=[],
            diagnostic_metrics={},
            selected_output_ref=None,
            selected_output_origin=None,
            approved_for_child_delivery=False,
            approved_for_unsupervised_child_delivery=False,
            requires_expert_review=True,
        )


class GovernedFallbackOrchestrator:
    """
    Orchestrates the bounded fail-closed fallback ladder:
    Primary -> C0 Rule Baseline -> Unchanged Source (Research Only) -> Manual Review / Safe Abstention.
    Maximum depth is bounded at 3 transitions.
    """

    def __init__(
        self,
        configuration_hash: str = "stage36-unfrozen-dev",
        pipeline: Optional[ValidatorPipeline] = None,
    ):
        self.configuration_hash = configuration_hash
        self.pipeline = pipeline or ValidatorPipeline()

    def process_request(
        self,
        request_id: str,
        source_record_id: str,
        source_text: str,
        primary_envelope: CandidateEnvelope,
        primary_candidate_text: str,
        context: Dict[str, Any],
        rule_simplifier: Optional[Callable[[str], str]] = None,
    ) -> Tuple[ValidationResult, RequestTrace]:
        fallback_steps: List[FallbackStep] = []
        created_at = datetime.now(timezone.utc).isoformat()

        context = context.copy()
        if "expected_configuration_hash" not in context:
            context["expected_configuration_hash"] = self.configuration_hash

        # Step 0: Evaluate Primary Candidate
        res_primary = validate_candidate(
            source_text=source_text,
            candidate_text=primary_candidate_text,
            envelope=primary_envelope,
            context=context,
            configuration_hash=self.configuration_hash,
            pipeline=self.pipeline,
        )

        if _get_enum_str(res_primary.candidate_disposition) == CandidateDisposition.ACCEPTED_TECHNICAL_RESEARCH_CANDIDATE.value:
            trace = RequestTrace(
                request_id=request_id,
                source_record_id=source_record_id,
                final_outcome=RequestFinalOutcome.PRIMARY_CANDIDATE_SELECTED,
                primary_candidate_id=primary_envelope.candidate_id,
                selected_candidate_id=primary_envelope.candidate_id,
                total_fallback_transitions=0,
                fallback_steps=[],
                created_at=created_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
            )
            return res_primary, trace

        if _get_enum_str(res_primary.candidate_disposition) == CandidateDisposition.VALID_UNCHANGED_NO_SIMPLIFICATION.value:
            trace = RequestTrace(
                request_id=request_id,
                source_record_id=source_record_id,
                final_outcome=RequestFinalOutcome.UNCHANGED_SOURCE_SELECTED_FOR_RESEARCH_ONLY,
                primary_candidate_id=primary_envelope.candidate_id,
                selected_candidate_id=primary_envelope.candidate_id,
                total_fallback_transitions=0,
                fallback_steps=[],
                created_at=created_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
            )
            return res_primary, trace

        if _get_enum_str(res_primary.candidate_disposition) == CandidateDisposition.MANUAL_REVIEW_REQUIRED.value:
            fallback_steps.append(
                FallbackStep(
                    step_number=1,
                    transition_type=FallbackTransitionType.TO_MANUAL_REVIEW_NO_OUTPUT,
                    from_candidate_id=primary_envelope.candidate_id,
                    to_candidate_id=None,
                    triggering_reason_code="MANUAL_REVIEW_REQUIRED",
                )
            )
            trace = RequestTrace(
                request_id=request_id,
                source_record_id=source_record_id,
                final_outcome=RequestFinalOutcome.MANUAL_REVIEW_NO_OUTPUT,
                primary_candidate_id=primary_envelope.candidate_id,
                selected_candidate_id=None,
                total_fallback_transitions=1,
                fallback_steps=fallback_steps,
                created_at=created_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
            )
            return res_primary, trace

        # Fallback Level 1: Transition to C0 Rule Baseline
        triggering_code = (
            res_primary.findings[0].reason_code
            if res_primary.findings
            else (_get_enum_str(res_primary.candidate_disposition) if res_primary.candidate_disposition else "FAILED_INTERNAL")
        )
        c0_candidate_id = f"cand_{primary_envelope.candidate_id}_c0"
        fallback_steps.append(
            FallbackStep(
                step_number=len(fallback_steps) + 1,
                transition_type=FallbackTransitionType.TO_RULE_BASELINE,
                from_candidate_id=primary_envelope.candidate_id,
                to_candidate_id=c0_candidate_id,
                triggering_reason_code=triggering_code,
            )
        )

        c0_text = rule_simplifier(source_text) if rule_simplifier else source_text
        c0_hash = hashlib.sha256(c0_text.encode("utf-8")).hexdigest()

        c0_envelope = CandidateEnvelope(
            candidate_id=c0_candidate_id,
            request_id=request_id,
            parent_candidate_id=primary_envelope.candidate_id,
            fallback_depth=1,
            fallback_reason_code=triggering_code,
            source_record_id=source_record_id,
            source_text_ref=primary_envelope.source_text_ref,
            source_text_sha256_internal=primary_envelope.source_text_sha256_internal,
            candidate_text_ref=f"protected://candidates/{c0_candidate_id}.txt",
            candidate_text_sha256_internal=c0_hash,
            provider_condition=ProviderCondition.C0_RULE_BASELINE,
            execution_mode=ExecutionMode.RULE_ENGINE,
            generation_configuration_hash=self.configuration_hash,
            external_processing_authorized=False,
            simulation_only=primary_envelope.simulation_only,
        )

        res_c0 = validate_candidate(
            source_text=source_text,
            candidate_text=c0_text,
            envelope=c0_envelope,
            context=context.copy(),
            configuration_hash=self.configuration_hash,
            pipeline=self.pipeline,
        )

        if _get_enum_str(res_c0.candidate_disposition) in (
            CandidateDisposition.ACCEPTED_TECHNICAL_RESEARCH_CANDIDATE.value,
            CandidateDisposition.VALID_UNCHANGED_NO_SIMPLIFICATION.value,
        ):
            trace = RequestTrace(
                request_id=request_id,
                source_record_id=source_record_id,
                final_outcome=RequestFinalOutcome.RULE_FALLBACK_SELECTED,
                primary_candidate_id=primary_envelope.candidate_id,
                selected_candidate_id=c0_candidate_id,
                total_fallback_transitions=len(fallback_steps),
                fallback_steps=fallback_steps,
                created_at=created_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
            )
            return res_c0, trace

        # Fallback Level 2: Transition to Unchanged Source (Research-Only Baseline)
        unchanged_candidate_id = f"cand_{primary_envelope.candidate_id}_unchanged"
        c0_trigger = (
            res_c0.findings[0].reason_code
            if res_c0.findings
            else (_get_enum_str(res_c0.candidate_disposition) if res_c0.candidate_disposition else "C0_REJECTED")
        )
        fallback_steps.append(
            FallbackStep(
                step_number=len(fallback_steps) + 1,
                transition_type=FallbackTransitionType.TO_UNCHANGED_SOURCE,
                from_candidate_id=c0_candidate_id,
                to_candidate_id=unchanged_candidate_id,
                triggering_reason_code=c0_trigger,
            )
        )

        src_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
        unchanged_envelope = CandidateEnvelope(
            candidate_id=unchanged_candidate_id,
            request_id=request_id,
            parent_candidate_id=c0_candidate_id,
            fallback_depth=2,
            fallback_reason_code=c0_trigger,
            source_record_id=source_record_id,
            source_text_ref=primary_envelope.source_text_ref,
            source_text_sha256_internal=primary_envelope.source_text_sha256_internal,
            candidate_text_ref=f"protected://candidates/{unchanged_candidate_id}.txt",
            candidate_text_sha256_internal=src_hash,
            provider_condition=ProviderCondition.C0_RULE_BASELINE,
            execution_mode=ExecutionMode.RULE_ENGINE,
            generation_configuration_hash=self.configuration_hash,
            external_processing_authorized=False,
            simulation_only=primary_envelope.simulation_only,
        )

        res_unchanged = validate_candidate(
            source_text=source_text,
            candidate_text=source_text,
            envelope=unchanged_envelope,
            context=context.copy(),
            configuration_hash=self.configuration_hash,
            pipeline=self.pipeline,
        )

        if _get_enum_str(res_unchanged.candidate_disposition) in (
            CandidateDisposition.VALID_UNCHANGED_NO_SIMPLIFICATION.value,
            CandidateDisposition.ACCEPTED_TECHNICAL_RESEARCH_CANDIDATE.value,
        ):
            trace = RequestTrace(
                request_id=request_id,
                source_record_id=source_record_id,
                final_outcome=RequestFinalOutcome.UNCHANGED_SOURCE_SELECTED_FOR_RESEARCH_ONLY,
                primary_candidate_id=primary_envelope.candidate_id,
                selected_candidate_id=unchanged_candidate_id,
                total_fallback_transitions=len(fallback_steps),
                fallback_steps=fallback_steps,
                created_at=created_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
            )
            return res_unchanged, trace

        # Fallback Level 3: Safe Abstention (Terminal Abstention - No Output)
        abstain_trigger = (
            res_unchanged.findings[0].reason_code
            if res_unchanged.findings
            else (_get_enum_str(res_unchanged.candidate_disposition) if res_unchanged.candidate_disposition else "UNCHANGED_FAILED")
        )
        fallback_steps.append(
            FallbackStep(
                step_number=len(fallback_steps) + 1,
                transition_type=FallbackTransitionType.TO_REJECTED_NO_OUTPUT,
                from_candidate_id=unchanged_candidate_id,
                to_candidate_id=None,
                triggering_reason_code=abstain_trigger,
            )
        )

        trace = RequestTrace(
            request_id=request_id,
            source_record_id=source_record_id,
            final_outcome=RequestFinalOutcome.REJECTED_NO_OUTPUT,
            primary_candidate_id=primary_envelope.candidate_id,
            selected_candidate_id=None,
            total_fallback_transitions=len(fallback_steps),
            fallback_steps=fallback_steps,
            created_at=created_at,
            completed_at=datetime.now(timezone.utc).isoformat(),
        )
        return res_unchanged, trace
