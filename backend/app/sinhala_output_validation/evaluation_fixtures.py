"""
Governed evaluation fixtures for Stage 36 final pipeline evaluation (WP8).
Comprises 16 comprehensive fixtures covering all primary selection, fallback ladder,
and safe abstention trajectories.
"""

from typing import Any, Callable, Dict, List, Optional
from app.sinhala_output_validation.schemas import RequestFinalOutcome

GOVERNED_FINAL_EVALUATION_FIXTURES: List[Dict[str, Any]] = [
    {
        "fixture_id": "EVAL_01_VALID_PRIMARY",
        "description": "Valid primary simplification preserving meaning and numbers",
        "source_text": "2024 වසරේදී ශ්‍රී ලංකාවේ පාසල් දරුවන් සඳහා නව පෙළපොත් නොමිලේ බෙදා දෙන ලදී.",
        "primary_text": "2024 වසරේදී ශ්‍රී ලංකාවේ පාසල් ළමුන්ට අලුත් පොත් නොමිලේ දුන්නා.",
        "context": {
            "declared_protected_spans": [{"text": "ශ්‍රී ලංකාවේ"}],
        },
        "rule_simplifier": None,
        "primary_envelope_override": {},
        "expected_final_outcome": RequestFinalOutcome.PRIMARY_CANDIDATE_SELECTED,
    },
    {
        "fixture_id": "EVAL_02_VALID_UNCHANGED",
        "description": "Candidate identical to source text routed to unchanged research baseline",
        "source_text": "පොකුණේ ලස්සන නෙළුම් මල් පිපී ඇත.",
        "primary_text": "පොකුණේ ලස්සන නෙළුම් මල් පිපී ඇත.",
        "context": {},
        "rule_simplifier": None,
        "primary_envelope_override": {},
        "expected_final_outcome": RequestFinalOutcome.UNCHANGED_SOURCE_SELECTED_FOR_RESEARCH_ONLY,
    },
    {
        "fixture_id": "EVAL_03_NUMERIC_VIOLATION_FALLBACK_C0",
        "description": "Primary mutates number 500, fallback to C0 which preserves 500",
        "source_text": "පාසලේ සිසුන් 500ක් ඉගෙනුම ලබති.",
        "primary_text": "පාසලේ සිසුන් බොහෝ දෙනෙක් ඉගෙන ගනිති.",  # 500 omitted
        "context": {},
        "rule_simplifier": lambda s: "පාසලේ සිසුන් 500ක් ඉගෙන ගන්නවා.",
        "primary_envelope_override": {},
        "expected_final_outcome": RequestFinalOutcome.RULE_FALLBACK_SELECTED,
    },
    {
        "fixture_id": "EVAL_04_DECLARED_SPAN_FALLBACK_C0",
        "description": "Primary drops declared protected proper noun, fallback to C0",
        "source_text": "මහාචාර්ය සෙනරත් පරණවිතාන මහතා සීගිරිය පිළිබඳ පර්යේෂණ කළේය.",
        "primary_text": "විද්වතෙක් සීගිරිය ගැන කරුණු සෙව්වා.",  # drops "සෙනරත් පරණවිතාන"
        "context": {
            "declared_protected_spans": [{"text": "සෙනරත් පරණවිතාන"}],
        },
        "rule_simplifier": lambda s: "මහාචාර්ය සෙනරත් පරණවිතාන මහතා සීගිරිය ගැන කරුණු සෙව්වා.",
        "primary_envelope_override": {},
        "expected_final_outcome": RequestFinalOutcome.RULE_FALLBACK_SELECTED,
    },
    {
        "fixture_id": "EVAL_05_POLARITY_INVERSION_FALLBACK_C0",
        "description": "Primary inverts polarity, fallback to C0 which preserves negation",
        "source_text": "ඔහු ඊයේ පාසල් ගියේ නැත.",
        "primary_text": "ඔහු ඊයේ පාසල් ගියේය.",  # negation flipped
        "context": {},
        "rule_simplifier": lambda s: "ඔහු ඊයේ පාසල් ගියේ නෑ.",
        "primary_envelope_override": {},
        "expected_final_outcome": RequestFinalOutcome.RULE_FALLBACK_SELECTED,
    },
    {
        "fixture_id": "EVAL_06_HALLUCINATION_FALLBACK_C0",
        "description": "Primary hallucinates ungrounded content, fallback to C0",
        "source_text": "කුරුල්ලා ගසේ අත්තක වාඩි විය.",
        "primary_text": "විදුහල්පතිතුමා කාර්යාලයේ වැදගත් ලිපිගොනු පරීක්ෂා කරමින් සිටියි.",
        "context": {},
        "rule_simplifier": lambda s: "කුරුල්ලා ගසේ අත්තක වාඩි වුණා.",
        "primary_envelope_override": {},
        "expected_final_outcome": RequestFinalOutcome.RULE_FALLBACK_SELECTED,
    },
    {
        "fixture_id": "EVAL_07_INFERRED_SPAN_MANUAL_REVIEW",
        "description": "Primary alters inferred entity span, routing to manual review queue",
        "source_text": "අනුරාධපුර නගරයේ පෞරාණික නටබුන් පිහිටා ඇත.",
        "primary_text": "පැරණි නගරයේ නටබුන් පිහිටා තිබේ.",
        "context": {
            "inferred_protected_spans": [{"text": "අනුරාධපුර"}],
        },
        "rule_simplifier": None,
        "primary_envelope_override": {},
        "expected_final_outcome": RequestFinalOutcome.MANUAL_REVIEW_NO_OUTPUT,
    },
    {
        "fixture_id": "EVAL_08_UNBALANCED_BRACKETS_MANUAL_REVIEW",
        "description": "Primary contains unbalanced brackets, routing to manual review queue",
        "source_text": "කොළඹ (ප්‍රධාන වාණිජ නගරය) වේ.",
        "primary_text": "කොළඹ (ප්‍රධාන නගරය වේ.",
        "context": {},
        "rule_simplifier": None,
        "primary_envelope_override": {},
        "expected_final_outcome": RequestFinalOutcome.MANUAL_REVIEW_NO_OUTPUT,
    },
    {
        "fixture_id": "EVAL_09_CORRUPT_UNICODE_TERMINAL_REJECT",
        "description": "Source itself has corrupted Unicode mojibake, resulting in terminal abstention",
        "source_text": "පාසලට \uFFFD ගියා",
        "primary_text": "පාසලට \uFFFD පැමිණියා",
        "context": {},
        "rule_simplifier": lambda s: s,
        "primary_envelope_override": {},
        "expected_final_outcome": RequestFinalOutcome.REJECTED_NO_OUTPUT,
    },
    {
        "fixture_id": "EVAL_10_DOUBLE_VIRAMA_FALLBACK_C0",
        "description": "Primary has orthographic double virama corruption, fallback to C0",
        "source_text": "ගුරුවරයා පාසලට පැමිණියේය.",
        "primary_text": "ගුරු\u0DCA\u0DCAවරයා පාසලට ආවා.",
        "context": {},
        "rule_simplifier": lambda s: "ගුරුවරයා පාසලට ආවා.",
        "primary_envelope_override": {},
        "expected_final_outcome": RequestFinalOutcome.RULE_FALLBACK_SELECTED,
    },
    {
        "fixture_id": "EVAL_11_TRUNCATION_FALLBACK_C0",
        "description": "Primary suffers severe truncation (<0.20 length), fallback to C0",
        "source_text": "මෙම ව්‍යාපෘතිය මගින් ග්‍රාමීය දරුවන්ට අවශ්‍ය පාසල් උපකරණ සහ පොත්පත් නොමිලේ ලබා දීමට කටයුතු සැලසුම් කර ඇත.",
        "primary_text": "පොත්",
        "context": {},
        "rule_simplifier": lambda s: "මේ ව්‍යාපෘතියෙන් ගමේ ළමුන්ට පොත්පත් නොමිලේ දෙනවා.",
        "primary_envelope_override": {},
        "expected_final_outcome": RequestFinalOutcome.RULE_FALLBACK_SELECTED,
    },
    {
        "fixture_id": "EVAL_12_C0_ALSO_FAILS_FALLBACK_UNCHANGED",
        "description": "Primary and C0 both mutate number 12, falling back to unchanged source",
        "source_text": "2024 වසරේ ශ්‍රී ලංකාවේ ප්‍රධාන සංවර්ධන ව්‍යාපෘති 12ක් ක්‍රියාත්මක කෙරේ.",
        "primary_text": "2024 වසරේ ප්‍රධාන ව්‍යාපෘති 5ක් කෙරේ.",   # mutates 12 to 5
        "context": {},
        "rule_simplifier": lambda s: "2024 වසරේ ප්‍රධාන ව්‍යාපෘති 20ක් කෙරේ.",  # mutates 12 to 20
        "primary_envelope_override": {},
        "expected_final_outcome": RequestFinalOutcome.UNCHANGED_SOURCE_SELECTED_FOR_RESEARCH_ONLY,
    },
    {
        "fixture_id": "EVAL_13_COMPLEX_HISTORICAL_PRIMARY",
        "description": "Complex historical sentence with preserved proper noun, primary accepted",
        "source_text": "ක්‍රිස්තු පූර්ව තෙවන සියවසේදී මහින්දාගමනය ශ්‍රී ලංකාවට සිදු විය.",
        "primary_text": "ක්‍රිස්තු පූර්ව තෙවන සියවසේදී මහින්දාගමනය ලංකාවට සිද්ධ වුණා.",
        "context": {
            "declared_protected_spans": [{"text": "මහින්දාගමනය"}],
        },
        "rule_simplifier": None,
        "primary_envelope_override": {},
        "expected_final_outcome": RequestFinalOutcome.PRIMARY_CANDIDATE_SELECTED,
    },
    {
        "fixture_id": "EVAL_14_SCIENCE_TEXT_NUMBERS_PRESERVED",
        "description": "Science text with temperature quantity preserved, primary accepted",
        "source_text": "ජලය සෙල්සියස් අංශක 100 දී වාෂ්ප බවට පත් වේ.",
        "primary_text": "වතුර සෙල්සියස් අංශක 100 දී වාෂ්ප වෙනවා.",
        "context": {},
        "rule_simplifier": None,
        "primary_envelope_override": {},
        "expected_final_outcome": RequestFinalOutcome.PRIMARY_CANDIDATE_SELECTED,
    },
    {
        "fixture_id": "EVAL_15_PROVENANCE_FAIL_FALLBACK_C0",
        "description": "Primary has invalid generation config hash, fallback to C0",
        "source_text": "ළමයි පාසල් යති.",
        "primary_text": "ළමයි පාසල් යනවා.",
        "context": {},
        "rule_simplifier": lambda s: "ළමයි පාසල් යනවා.",
        "primary_envelope_override": {
            "generation_configuration_hash": "unfrozen_mismatched_config_hash_0000"
        },
        "expected_final_outcome": RequestFinalOutcome.RULE_FALLBACK_SELECTED,
    },
    {
        "fixture_id": "EVAL_16_TOTAL_SOURCE_CORRUPTION_ABSTAIN",
        "description": "Source has non-printable control characters, terminating in safe abstention",
        "source_text": "පාසල\x00\x01\x02",
        "primary_text": "පාසල\x00\x01\x02",
        "context": {},
        "rule_simplifier": lambda s: s,
        "primary_envelope_override": {},
        "expected_final_outcome": RequestFinalOutcome.REJECTED_NO_OUTPUT,
    },
]
