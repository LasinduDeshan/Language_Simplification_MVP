"""
Quality, Privacy, and Scope Screening Engine for Stage 31 Sinhala External Records.
Implements fail-closed privacy detection, text quality metrics, and strict terminal disposition routing.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

class Stage31Disposition(str, Enum):
    REJECTED_RIGHTS = "REJECTED_RIGHTS"
    REJECTED_SECURITY = "REJECTED_SECURITY"
    REJECTED_PRIVACY = "REJECTED_PRIVACY"
    REJECTED_INVALID_UNICODE = "REJECTED_INVALID_UNICODE"
    QUARANTINED_SOURCE_ERROR = "QUARANTINED_SOURCE_ERROR"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    EXCLUDED_NON_SINHALA = "EXCLUDED_NON_SINHALA"
    EXCLUDED_DUPLICATE = "EXCLUDED_DUPLICATE"
    EXCLUDED_OUT_OF_SCOPE = "EXCLUDED_OUT_OF_SCOPE"
    REJECTED_QUALITY = "REJECTED_QUALITY"
    ACCEPTED_PILOT_CANDIDATE = "ACCEPTED_PILOT_CANDIDATE"

@dataclass(frozen=True)
class ScreeningResult:
    disposition: Stage31Disposition
    reason_code: Optional[str]
    quality_flags: List[str]
    is_quarantined: bool

# Regex patterns for privacy and security screening
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_PATTERN = re.compile(r'(?:\+94|0)(?:7[0-9]|11|2[1-8]|3[1-8]|4[1-7]|5[1-7]|6[3-7]|8[1-3])[0-9]{7}\b')
SL_NIC_PATTERN = re.compile(r'\b(?:19|20)?\d{9}[vVxX]|\b\d{12}\b')
TOKEN_PATTERN = re.compile(r'\b(?:ghp_[a-zA-Z0-9]{36}|bearer\s+[a-zA-Z0-9_\-\.]{20,}|api[_\-]?key\s*[:=]\s*["\']?[a-zA-Z0-9_\-]{16,})\b', re.IGNORECASE)

class QualityAndPrivacyScreener:
    """Evaluates preprocessed Sinhala documents against quality, privacy, and scope invariants."""

    def __init__(
        self,
        min_token_count: int = 3,
        max_token_count: int = 400,
        min_sinhala_script_ratio: float = 0.50
    ):
        self.min_token_count = min_token_count
        self.max_token_count = max_token_count
        self.min_sinhala_script_ratio = min_sinhala_script_ratio

    def screen_text(
        self,
        text: str,
        stage30_disposition: str,
        token_count: int,
        is_rights_approved: bool = True
    ) -> ScreeningResult:
        flags: List[str] = []

        # 1. Rights gate (First-matching order)
        if not is_rights_approved:
            return ScreeningResult(
                disposition=Stage31Disposition.REJECTED_RIGHTS,
                reason_code="SOURCE_RIGHTS_NOT_APPROVED",
                quality_flags=["RIGHTS_BLOCKED"],
                is_quarantined=False
            )

        # 2. Security screening (Credentials, API keys, private tokens)
        if TOKEN_PATTERN.search(text):
            flags.append("SECURITY_SECRET_PRESENT")
            return ScreeningResult(
                disposition=Stage31Disposition.REJECTED_SECURITY,
                reason_code="CREDENTIAL_OR_API_KEY_DETECTED",
                quality_flags=flags,
                is_quarantined=True
            )

        # 3. Privacy screening (PII: Emails, Phone numbers, NICs)
        if EMAIL_PATTERN.search(text):
            flags.append("PII_EMAIL_DETECTED")
        if PHONE_PATTERN.search(text):
            flags.append("PII_PHONE_DETECTED")
        if SL_NIC_PATTERN.search(text):
            flags.append("PII_NIC_DETECTED")

        if any(f.startswith("PII_") for f in flags):
            return ScreeningResult(
                disposition=Stage31Disposition.REJECTED_PRIVACY,
                reason_code="CONFIRMED_PERSONAL_OR_PRIVATE_DATA",
                quality_flags=flags,
                is_quarantined=True
            )

        # 4. Stage 30 Unicode validation passthrough
        if stage30_disposition == "REJECTED_INVALID_UNICODE":
            flags.append("UNICODE_CORRUPTION")
            return ScreeningResult(
                disposition=Stage31Disposition.REJECTED_INVALID_UNICODE,
                reason_code="STAGE30_INVALID_UNICODE",
                quality_flags=flags,
                is_quarantined=True
            )

        if stage30_disposition == "MANUAL_REVIEW_REQUIRED":
            flags.append("STAGE30_REVIEW_REQUIRED")
            return ScreeningResult(
                disposition=Stage31Disposition.MANUAL_REVIEW_REQUIRED,
                reason_code="STAGE30_MANUAL_REVIEW_TRIGGERED",
                quality_flags=flags,
                is_quarantined=True
            )

        if stage30_disposition == "EXCLUDED_NON_SINHALA":
            flags.append("NON_SINHALA_SCRIPT")
            return ScreeningResult(
                disposition=Stage31Disposition.EXCLUDED_NON_SINHALA,
                reason_code="STAGE30_SCRIPT_THRESHOLD_NOT_MET",
                quality_flags=flags,
                is_quarantined=False
            )

        # 5. Length checks
        if token_count < self.min_token_count:
            flags.append("TOO_SHORT")
            return ScreeningResult(
                disposition=Stage31Disposition.REJECTED_QUALITY,
                reason_code="TOKEN_COUNT_BELOW_MINIMUM",
                quality_flags=flags,
                is_quarantined=False
            )

        if token_count > self.max_token_count:
            flags.append("TOO_LONG")
            return ScreeningResult(
                disposition=Stage31Disposition.REJECTED_QUALITY,
                reason_code="TOKEN_COUNT_EXCEEDS_MAXIMUM",
                quality_flags=flags,
                is_quarantined=False
            )

        # 6. Repetition check (Same word repeated 5+ times consecutively)
        words = text.split()
        max_rep = 1
        curr_rep = 1
        for i in range(1, len(words)):
            if words[i] == words[i-1]:
                curr_rep += 1
                max_rep = max(max_rep, curr_rep)
            else:
                curr_rep = 1
        if max_rep >= 5:
            flags.append("EXCESSIVE_REPETITION")
            return ScreeningResult(
                disposition=Stage31Disposition.REJECTED_QUALITY,
                reason_code="EXCESSIVE_TOKEN_REPETITION",
                quality_flags=flags,
                is_quarantined=False
            )

        # 7. Passed all gates -> Accepted pilot candidate
        return ScreeningResult(
            disposition=Stage31Disposition.ACCEPTED_PILOT_CANDIDATE,
            reason_code=None,
            quality_flags=flags,
            is_quarantined=False
        )
