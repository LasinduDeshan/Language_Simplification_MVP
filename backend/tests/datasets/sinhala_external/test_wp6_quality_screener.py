"""
Unit tests for Stage 31 Quality and Privacy Screening engine.
"""

import pytest
from app.datasets.sinhala_external.quality_screener import (
    QualityAndPrivacyScreener,
    Stage31Disposition,
)

@pytest.fixture
def screener():
    return QualityAndPrivacyScreener(
        min_token_count=3,
        max_token_count=400,
        min_sinhala_script_ratio=0.50
    )

def test_screener_accepts_clean_sinhala_prose(screener):
    text = "ශ්‍රී ලංකාවේ ඉතිහාසය ඉතා දීර්ඝ වන අතර එය විවිධ සංස්කෘතීන්ගෙන් පෝෂණය වී ඇත."
    res = screener.screen_text(text, stage30_disposition="PASSED", token_count=12)
    assert res.disposition == Stage31Disposition.ACCEPTED_PILOT_CANDIDATE
    assert res.is_quarantined is False
    assert len(res.quality_flags) == 0

def test_screener_detects_email_privacy(screener):
    text = "වැඩිදුර විස්තර සඳහා info@example.gov.lk වෙත විද්‍යුත් තැපෑලක් යොමු කරන්න."
    res = screener.screen_text(text, stage30_disposition="PASSED", token_count=10)
    assert res.disposition == Stage31Disposition.REJECTED_PRIVACY
    assert res.reason_code == "CONFIRMED_PERSONAL_OR_PRIVATE_DATA"
    assert "PII_EMAIL_DETECTED" in res.quality_flags
    assert res.is_quarantined is True

def test_screener_detects_phone_number(screener):
    text = "හදිසි ඇමතුම් සඳහා 0771234567 අංකය අමතන්න."
    res = screener.screen_text(text, stage30_disposition="PASSED", token_count=7)
    assert res.disposition == Stage31Disposition.REJECTED_PRIVACY
    assert "PII_PHONE_DETECTED" in res.quality_flags
    assert res.is_quarantined is True

def test_screener_detects_nic(screener):
    text = "අයදුම්කරුගේ ජාතික හැඳුනුම්පත් අංකය 199012345678 වේ."
    res = screener.screen_text(text, stage30_disposition="PASSED", token_count=6)
    assert res.disposition == Stage31Disposition.REJECTED_PRIVACY
    assert "PII_NIC_DETECTED" in res.quality_flags

def test_screener_detects_security_token(screener):
    text = "Internal token: ghp_123456789012345678901234567890123456 do not share."
    res = screener.screen_text(text, stage30_disposition="PASSED", token_count=8)
    assert res.disposition == Stage31Disposition.REJECTED_SECURITY
    assert res.reason_code == "CREDENTIAL_OR_API_KEY_DETECTED"
    assert res.is_quarantined is True

def test_screener_rejects_too_short(screener):
    text = "හලෝ"
    res = screener.screen_text(text, stage30_disposition="PASSED", token_count=1)
    assert res.disposition == Stage31Disposition.REJECTED_QUALITY
    assert res.reason_code == "TOKEN_COUNT_BELOW_MINIMUM"
    assert "TOO_SHORT" in res.quality_flags

def test_screener_rejects_excessive_repetition(screener):
    text = "ඔව් ඔව් ඔව් ඔව් ඔව් ඔව් මෙය සත්‍යයකි."
    res = screener.screen_text(text, stage30_disposition="PASSED", token_count=7)
    assert res.disposition == Stage31Disposition.REJECTED_QUALITY
    assert res.reason_code == "EXCESSIVE_TOKEN_REPETITION"
    assert "EXCESSIVE_REPETITION" in res.quality_flags

def test_precedence_order_security_over_privacy(screener):
    # Text with BOTH security secret and email address
    text = "User info@example.com used token ghp_123456789012345678901234567890123456."
    res = screener.screen_text(text, stage30_disposition="PASSED", token_count=6)
    # Security has higher precedence
    assert res.disposition == Stage31Disposition.REJECTED_SECURITY
