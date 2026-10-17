"""
Comprehensive unit tests for Stage 36 Validators (V0-V8) and Governed Fallback Engine.
"""

import hashlib
import pytest

from app.sinhala_output_validation.engine import (
    GovernedFallbackOrchestrator,
    determine_candidate_disposition,
    validate_candidate,
)
from app.sinhala_output_validation.schemas import (
    AutomatedValidationStatus,
    CandidateDisposition,
    CandidateEnvelope,
    EvidenceClass,
    ExecutionMode,
    ExecutionOutcome,
    ProviderCondition,
    RequestFinalOutcome,
    SeverityLevel,
    ValidatorFinding,
)
from app.sinhala_output_validation.validators.v0_v2_structural import (
    ValidatorV0EnvelopeProvenance,
    ValidatorV1UnicodeScript,
    ValidatorV2StructureLength,
)
from app.sinhala_output_validation.validators.v3_protected_spans import ValidatorV3ProtectedSpans
from app.sinhala_output_validation.validators.v4_v5_semantic_fidelity import (
    ValidatorV4PolarityNumerical,
    ValidatorV5OmissionInsertion,
)
from app.sinhala_output_validation.validators.v6_v8_diagnostics import (
    ValidatorV6SemanticProxy,
    ValidatorV7GrammaticalityProxy,
    ValidatorV8SimplificationGain,
)


@pytest.fixture
def base_envelope():
    return CandidateEnvelope(
        candidate_id="cand_test_01",
        request_id="req_test_01",
        source_record_id="rec_test_01",
        source_text_ref="protected://sources/rec_01.txt",
        source_text_sha256_internal="a" * 64,
        candidate_text_ref="protected://candidates/cand_01.txt",
        candidate_text_sha256_internal="b" * 64,
        provider_condition=ProviderCondition.C0_RULE_BASELINE,
        execution_mode=ExecutionMode.RULE_ENGINE,
        generation_configuration_hash="cfg_hash_1234567890",
        external_processing_authorized=False,
    )


class TestValidatorsV0V2:
    def test_v0_valid_envelope(self, base_envelope):
        v0 = ValidatorV0EnvelopeProvenance()
        findings = v0.validate("මූලාශ්‍රය", "ප්‍රතිදානය", base_envelope, {})
        assert len(findings) == 0

    def test_v0_invalid_config_hash(self, base_envelope):
        v0 = ValidatorV0EnvelopeProvenance()
        bad_envelope = base_envelope.model_copy(update={"generation_configuration_hash": "short"})
        findings = v0.validate("මූලාශ්‍රය", "ප්‍රතිදානය", bad_envelope, {})
        assert len(findings) == 1
        assert findings[0].reason_code == "REJ_CONF_PROVENANCE_INVALID"

    def test_v1_valid_sinhala(self, base_envelope):
        v1 = ValidatorV1UnicodeScript()
        findings = v1.validate("ගුරුවරයා පාසලට පැමිණියේය.", "ගුරුවරයා ආවා.", base_envelope, {})
        assert len(findings) == 0

    def test_v1_mojibake_rejection(self, base_envelope):
        v1 = ValidatorV1UnicodeScript()
        findings = v1.validate("ගුරුවරයා", "ගුරුවරයා \uFFFD ආවා", base_envelope, {})
        assert any(f.reason_code == "REJ_INVALID_UNICODE" for f in findings)

    def test_v1_illegal_control_char(self, base_envelope):
        v1 = ValidatorV1UnicodeScript()
        findings = v1.validate("ගුරුවරයා", "ගුරුවරයා\x00ආවා", base_envelope, {})
        assert any(f.reason_code == "REJ_INVALID_UNICODE" for f in findings)

    def test_v1_non_sinhala_script_dominance(self, base_envelope):
        v1 = ValidatorV1UnicodeScript(min_sinhala_ratio=0.5)
        findings = v1.validate("ගුරුවරයා", "The teacher came to the school today.", base_envelope, {})
        assert any(f.reason_code == "REJ_INVALID_UNICODE" for f in findings)

    def test_v2_empty_candidate(self, base_envelope):
        v2 = ValidatorV2StructureLength()
        findings = v2.validate("ගුරුවරයා පැමිණියේය.", "   ", base_envelope, {})
        assert any(f.reason_code == "REJ_CRITICAL_SEMANTIC_RISK" for f in findings)

    def test_v2_excessive_truncation(self, base_envelope):
        v2 = ValidatorV2StructureLength(min_length_ratio=0.20)
        long_source = "මෙය ඉතා දිගු සිංහල වාක්‍යයක් වන අතර ළමුන් සඳහා සරල කළ යුතු වේ." * 5
        findings = v2.validate(long_source, "කෙටි", base_envelope, {})
        assert any(f.reason_code == "REJ_CRITICAL_SEMANTIC_RISK" for f in findings)


class TestValidatorV3ProtectedSpans:
    def test_v3_declared_span_preserved(self, base_envelope):
        v3 = ValidatorV3ProtectedSpans()
        source = "කොළඹ නගරය ශ්‍රී ලංකාවේ ප්‍රධාන නගරයයි."
        candidate = "කොළඹ නගරය ප්‍රධාන නගරය වේ."
        context = {"declared_protected_spans": [{"text": "කොළඹ"}]}
        findings = v3.validate(source, candidate, base_envelope, context)
        assert len(findings) == 0

    def test_v3_declared_span_violation(self, base_envelope):
        v3 = ValidatorV3ProtectedSpans()
        source = "කොළඹ නගරය ශ්‍රී ලංකාවේ ප්‍රධාන නගරයයි."
        candidate = "මහනුවර නගරය ප්‍රධාන නගරය වේ."
        context = {"declared_protected_spans": [{"text": "කොළඹ"}]}
        findings = v3.validate(source, candidate, base_envelope, context)
        assert len(findings) == 1
        assert findings[0].reason_code == "REJ_PROTECTED_SPAN_VIOLATION"
        assert findings[0].severity == SeverityLevel.CRITICAL

    def test_v3_deterministic_number_violation(self, base_envelope):
        v3 = ValidatorV3ProtectedSpans()
        source = "පාසලේ සිසුන් 250ක් ඉගෙනුම ලබති."
        candidate = "පාසලේ සිසුන් බොහෝ දෙනෙක් ඉගෙන ගනිති."  # 250 omitted
        findings = v3.validate(source, candidate, base_envelope, {})
        assert any(f.reason_code == "REJ_PROTECTED_SPAN_VIOLATION" for f in findings)

    def test_v3_inferred_span_triggers_review(self, base_envelope):
        v3 = ValidatorV3ProtectedSpans()
        source = "අනුරාධපුර දිස්ත්‍රික්කයේ වැව් පිහිටා ඇත."
        candidate = "එම ප්‍රදේශයේ වැව් ඇත."
        context = {"inferred_protected_spans": [{"text": "අනුරාධපුර"}]}
        findings = v3.validate(source, candidate, base_envelope, context)
        assert any(f.reason_code == "REV_INFERRED_SPAN_ALTERED" and f.severity == SeverityLevel.REVIEW for f in findings)


class TestValidatorsV4V5Fidelity:
    def test_v4_polarity_inversion_detected(self, base_envelope):
        v4 = ValidatorV4PolarityNumerical()
        source = "ඔහු පාසල් ගියේ නැත."
        candidate = "ඔහු පාසල් ගියේය."
        findings = v4.validate(source, candidate, base_envelope, {})
        assert any(f.reason_code == "REJ_NUMERICAL_OR_POLARITY_DRIFT" for f in findings)

    def test_v4_novel_number_insertion(self, base_envelope):
        v4 = ValidatorV4PolarityNumerical()
        source = "පොත් පෙට්ටියේ ඇත."
        candidate = "පොත් 50ක් පෙට්ටියේ ඇත."
        findings = v4.validate(source, candidate, base_envelope, {})
        assert any(f.reason_code == "REJ_NUMERICAL_OR_POLARITY_DRIFT" for f in findings)

    def test_v5_hallucination_insertion(self, base_envelope):
        v5 = ValidatorV5OmissionInsertion(max_novel_token_ratio=0.60)
        source = "ළමයා සෙල්ලම් කරයි."
        candidate = "විදුහල්පතිතුමා කාර්යාලයේ වැදගත් ලිපිගොනු පරීක්ෂා කරමින් සිටියි."
        findings = v5.validate(source, candidate, base_envelope, {})
        assert any(f.reason_code == "REJ_UNSUPPORTED_INSERTION" for f in findings)


class TestValidatorsV6V8Diagnostics:
    def test_v7_illegal_consecutive_virama(self, base_envelope):
        v7 = ValidatorV7GrammaticalityProxy()
        candidate = "ගුරු\u0DCA\u0DCAවරයා"  # double virama
        findings = v7.validate("ගුරුවරයා", candidate, base_envelope, {})
        assert any(f.reason_code == "REJ_INVALID_UNICODE" for f in findings)

    def test_v8_simplification_metrics(self, base_envelope):
        v8 = ValidatorV8SimplificationGain()
        context = {}
        findings = v8.validate("විද්‍යාලයීය ශිෂ්‍යයා", "පාසල් ළමයා", base_envelope, context)
        assert len(findings) == 1
        assert "simplification_gain_proxy" in context["diagnostic_metrics"]


class TestEngineAndFallbackOrchestrator:
    def test_precedence_order(self):
        # Create findings of multiple severities and reasons
        f1 = ValidatorFinding(
            finding_id="fnd_001",
            validator_id="V00_PROVENANCE",
            validator_version="1.0",
            severity=SeverityLevel.CRITICAL,
            reason_code="REJ_CONF_PROVENANCE_INVALID",
            evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
            public_summary="provenance error",
        )
        f2 = ValidatorFinding(
            finding_id="fnd_002",
            validator_id="V03_PROTECTED_SPANS",
            validator_version="1.0",
            severity=SeverityLevel.CRITICAL,
            reason_code="REJ_PROTECTED_SPAN_VIOLATION",
            evidence_class=EvidenceClass.AUTHORITATIVE_DETERMINISTIC,
            public_summary="span error",
        )
        disp = determine_candidate_disposition([f2, f1], is_unchanged=False)
        # Provenance (Rank 1) must take precedence over Protected Span (Rank 3)
        assert disp == CandidateDisposition.REJECTED_CONFIGURATION_OR_PROVENANCE

    def test_fallback_ladder_progression_to_rule_baseline(self, base_envelope):
        orchestrator = GovernedFallbackOrchestrator()
        source = "2024 වසරේ පාසලේ ළමුන් 100ක් සිටියහ."
        # Primary candidate mutates number 100 -> 50
        bad_primary = "2024 වසරේ පාසලේ ළමුන් 50ක් සිටියහ."

        # Rule baseline retains 100
        def dummy_rule_simplifier(s: str) -> str:
            return "2024 වසරේ පාසලේ ළමුන් 100ක් හිටියා."

        res, trace = orchestrator.process_request(
            request_id="req_fb_01",
            source_record_id="rec_fb_01",
            source_text=source,
            primary_envelope=base_envelope,
            primary_candidate_text=bad_primary,
            context={},
            rule_simplifier=dummy_rule_simplifier,
        )

        assert trace.final_outcome == RequestFinalOutcome.RULE_FALLBACK_SELECTED
        assert trace.total_fallback_transitions == 1
        assert res.approved_for_child_delivery is False
        assert res.approved_for_unsupervised_child_delivery is False

    def test_fallback_ladder_terminal_safe_abstention(self, base_envelope):
        orchestrator = GovernedFallbackOrchestrator()
        # Source itself contains invalid unicode / mojibake so unchanged candidate also fails
        corrupted_source = "පාසලට \uFFFD ගියා"
        bad_primary = "පාසලට \uFFFD පැමිණියා"

        res, trace = orchestrator.process_request(
            request_id="req_fb_corrupt",
            source_record_id="rec_fb_corrupt",
            source_text=corrupted_source,
            primary_envelope=base_envelope,
            primary_candidate_text=bad_primary,
            context={},
            rule_simplifier=lambda s: s,
        )

        assert trace.final_outcome == RequestFinalOutcome.REJECTED_NO_OUTPUT
        assert trace.total_fallback_transitions == 3
        assert trace.selected_candidate_id is None
