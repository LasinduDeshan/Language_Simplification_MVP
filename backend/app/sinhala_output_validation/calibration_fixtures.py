"""
Development-only calibration fixtures for Stage 36 Sinhala Output Validation Pipeline.
Pre-declared fixtures used exclusively for calibrating validator thresholds and disposition boundaries.
These fixtures are segregated from the final evaluation fixtures.
"""

from typing import Any, Dict, List
from app.sinhala_output_validation.schemas import CandidateDisposition

DEVELOPMENT_CALIBRATION_FIXTURES: List[Dict[str, Any]] = [
    {
        "fixture_id": "DEV_FIX_01_VALID_SIMPLE",
        "description": "Standard valid simplification preserving meaning and numbers",
        "source_text": "2023 වසරේදී මහනුවර දිස්ත්‍රික්කයේ පාසල් සිසුන් සඳහා නොමිලේ ක්‍රීඩා උපකරණ බෙදා දුන්නේය.",
        "candidate_text": "2023 වසරේදී මහනුවර දිස්ත්‍රික්කයේ පාසල් ළමුන්ට නොමිලේ ක්‍රීඩා බඩු දුන්නා.",
        "context": {
            "declared_protected_spans": [{"text": "මහනුවර"}],
        },
        "expected_disposition": CandidateDisposition.ACCEPTED_TECHNICAL_RESEARCH_CANDIDATE,
    },
    {
        "fixture_id": "DEV_FIX_02_VALID_UNCHANGED",
        "description": "Candidate identical to source text (no simplification performed)",
        "source_text": "පොකුණේ ලස්සන මල් පිපී ඇත.",
        "candidate_text": "පොකුණේ ලස්සන මල් පිපී ඇත.",
        "context": {},
        "expected_disposition": CandidateDisposition.VALID_UNCHANGED_NO_SIMPLIFICATION,
    },
    {
        "fixture_id": "DEV_FIX_03_UNICODE_MOJIBAKE",
        "description": "Candidate containing Unicode replacement character (mojibake)",
        "source_text": "ගුරුවරයා පන්තියට පැමිණියේය.",
        "candidate_text": "ගුරුවරයා පන්තියට \uFFFD ආවා.",
        "context": {},
        "expected_disposition": CandidateDisposition.REJECTED_INVALID_UNICODE,
    },
    {
        "fixture_id": "DEV_FIX_04_CONTROL_CHARS",
        "description": "Candidate containing illegal non-printable control characters",
        "source_text": "ළමයා පොත කියවයි.",
        "candidate_text": "ළමයා\x00 පොත කියවයි.",
        "context": {},
        "expected_disposition": CandidateDisposition.REJECTED_INVALID_UNICODE,
    },
    {
        "fixture_id": "DEV_FIX_05_NON_SINHALA",
        "description": "Candidate with dominant foreign Latin script",
        "source_text": "අද දින පාසල වසා ඇත.",
        "candidate_text": "The school is closed today due to bad weather.",
        "context": {},
        "expected_disposition": CandidateDisposition.REJECTED_INVALID_UNICODE,
    },
    {
        "fixture_id": "DEV_FIX_06_DECLARED_SPAN",
        "description": "Missing declared protected span",
        "source_text": "මාර්ටින් වික්‍රමසිංහ සූරීන් විසින් කොග්ගල ගම්මානය පිළිබඳ නවකතා රචනා කරන ලදී.",
        "candidate_text": "කතුවරයෙක් ගම ගැන පොත් ලිව්වා.",
        "context": {
            "declared_protected_spans": [{"text": "මාර්ටින් වික්‍රමසිංහ"}],
        },
        "expected_disposition": CandidateDisposition.REJECTED_PROTECTED_SPAN_VIOLATION,
    },
    {
        "fixture_id": "DEV_FIX_07_NUMERIC_SPAN",
        "description": "Missing or altered deterministic numeric value",
        "source_text": "ගම්මානයේ පවුල් 350ක් ජීවත් වෙති.",
        "candidate_text": "ගම්මානයේ පවුල් බොහෝ දෙනෙක් ඉන්නවා.",
        "context": {},
        "expected_disposition": CandidateDisposition.REJECTED_PROTECTED_SPAN_VIOLATION,
    },
    {
        "fixture_id": "DEV_FIX_08_POLARITY_NEG_TO_POS",
        "description": "Polarity inversion from negative to positive",
        "source_text": "අද දිනයේ වැසි ඇද හැලුණේ නැත.",
        "candidate_text": "අද දිනයේ වැසි ඇද හැළුණි.",
        "context": {},
        "expected_disposition": CandidateDisposition.REJECTED_NUMERICAL_OR_POLARITY_DRIFT,
    },
    {
        "fixture_id": "DEV_FIX_09_POLARITY_POS_TO_NEG",
        "description": "Polarity inversion from positive to negative",
        "source_text": "ඔහු තරගයෙන් ජයග්‍රහණය කළේය.",
        "candidate_text": "ඔහු තරගයෙන් ජයග්‍රහණය කළේ නැත.",
        "context": {},
        "expected_disposition": CandidateDisposition.REJECTED_NUMERICAL_OR_POLARITY_DRIFT,
    },
    {
        "fixture_id": "DEV_FIX_10_HALLUCINATION",
        "description": "Excessive insertion of novel ungrounded content tokens",
        "source_text": "සමනලයා මල මත ලැගුම් ගත්තේය.",
        "candidate_text": "කර්මාන්තශාලාවේ නිෂ්පාදන ධාරිතාව වැඩි කිරීම සඳහා නව යන්ත්‍රෝපකරණ සවි කෙරිණි.",
        "context": {},
        "expected_disposition": CandidateDisposition.REJECTED_UNSUPPORTED_INSERTION,
    },
    {
        "fixture_id": "DEV_FIX_11_SEMANTIC_DRIFT",
        "description": "Severe semantic truncation risk (under 20% length ratio without novel tokens)",
        "source_text": "සූර්යයා පෙරදිගින් උදා වී මුළු ලෝකයටම අවශ්‍ය ආලෝකය සහ උණුසුම ලබා දෙයි.",
        "candidate_text": "සූර්යයා",
        "context": {},
        "expected_disposition": CandidateDisposition.REJECTED_CRITICAL_SEMANTIC_RISK,
    },
    {
        "fixture_id": "DEV_FIX_12_VIRAMA_CORRUPT",
        "description": "Orthographic corruption with illegal double virama",
        "source_text": "ළමයා පාසල් යයි.",
        "candidate_text": "ළමයා පාසල\u0DCA\u0DCA යයි.",
        "context": {},
        "expected_disposition": CandidateDisposition.REJECTED_INVALID_UNICODE,
    },
    {
        "fixture_id": "DEV_FIX_13_INFERRED_SPAN",
        "description": "Inferred entity mutated, routing to manual review",
        "source_text": "පොළොන්නරුව දිස්ත්‍රික්කයේ ගොවිතැන් කටයුතු සිදු කෙරේ.",
        "candidate_text": "එම ප්‍රදේශයේ ගොවිතැන් කටයුතු සිදු වේ.",
        "context": {
            "inferred_protected_spans": [{"text": "පොළොන්නරුව"}],
        },
        "expected_disposition": CandidateDisposition.MANUAL_REVIEW_REQUIRED,
    },
    {
        "fixture_id": "DEV_FIX_14_UNBALANCED_BRACKETS",
        "description": "Unbalanced brackets routing to manual review",
        "source_text": "ගාල්ල (ඓතිහාසික බලකොටුව පිහිටි නගරය) දකුණු පළාතේ පිහිටා ඇත.",
        "candidate_text": "ගාල්ල (ඓතිහාසික නගරය දකුණු පළාතේ ඇත.",
        "context": {},
        "expected_disposition": CandidateDisposition.MANUAL_REVIEW_REQUIRED,
    },
]
