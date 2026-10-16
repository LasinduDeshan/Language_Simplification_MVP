"""
Quality Screener and Router for Stage 32 Lexicon Candidates.
Evaluates proper noun likelihood, OCR/noise flags, mixed-script presence,
structural complexity, and automated semantic review heuristics.
"""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple

from app.datasets.sinhala_lexicon.schemas import ReviewFindingRecord

# Verified clinical, illness, trauma, or danger patterns (applied strictly to semantic roots)
VERIFIED_SENSITIVE_ROOTS = [
    r"අනතුරු",       # accident / danger
    r"අනතුර",       # accident / danger
    r"රෝග",         # disease / illness
    r"නිරෝගී",       # clinical health / disease context
    r"මරණ",         # death
    r"තුවාල",       # injury / trauma
    r"වෛරස",       # virus
    r"පිළිකා",       # cancer
]

# Common Sinhala proper noun prefixes / honorifics that signal potential named entities
PROPER_NOUN_MARKERS = [
    "මහතා", "මිය", "මෙනවිය", "වෙත", "ඇමති", "ජනපති", "හිමි", "නායක"
]

class LexiconQualityRouter:
    """Routes candidates to accepted draft entry, manual review, or exclusion with structured evidence."""

    def __init__(self):
        self.sensitive_regex = re.compile("|".join(VERIFIED_SENSITIVE_ROOTS), re.UNICODE)

    def screen_surface_form(
        self,
        surface: str,
        code_point_count: Optional[int] = None,
        grapheme_count: Optional[int] = None,
        source_record_ids: Optional[List[str]] = None
    ) -> Tuple[List[str], List[ReviewFindingRecord], bool, bool]:
        """
        Screens surface form for quality flags, proper noun indicators, and evidence-based review findings.
        Returns:
            (quality_flags, review_findings, is_proper_noun_candidate, is_sensitive_candidate)
        """
        flags: List[str] = []
        findings: List[ReviewFindingRecord] = []
        is_proper = False
        is_sensitive = False
        src_ids = source_record_ids or []
        cp_count = code_point_count if code_point_count is not None else len(surface)
        g_count = grapheme_count if grapheme_count is not None else len(surface)

        # 1. Evidence-based OCR or character repetition defect
        # Flagged ONLY when genuine anomalies exist (e.g. 3+ identical consecutive characters or corruption)
        if re.search(r"(.)\1\1+", surface):
            flags.append("OCR_OR_REPETITION_FLAG")
            findings.append(ReviewFindingRecord(
                reason_code="OCR_OR_REPETITION_FLAG",
                rule_id="STAGE32-RULE-OCR-REPETITION-ANOMALY-V1",
                trigger_evidence={
                    "observed_metric": "consecutive_identical_code_points",
                    "threshold": ">= 3 identical consecutive code points",
                    "source_record_ids": src_ids
                },
                automated_finding_only=True,
                human_validated=False
            ))

        # 2. Automated semantic review heuristic for potentially sensitive / clinical vocabulary
        # Explicitly qualified as an automated screening heuristic, not a confirmed human safety judgment.
        sensitive_match = self.sensitive_regex.search(surface)
        if sensitive_match or surface == "ලේ":
            matched_text = sensitive_match.group(0) if sensitive_match else surface
            flags.append("POTENTIALLY_SENSITIVE_SEMANTIC_REVIEW")
            is_sensitive = True
            findings.append(ReviewFindingRecord(
                reason_code="POTENTIALLY_SENSITIVE_SEMANTIC_REVIEW",
                rule_id="STAGE32-RULE-SEMANTIC-SENSITIVE-HEURISTIC-V1",
                trigger_evidence={
                    "observed_metric": f"matched_sensitive_pattern:{matched_text}",
                    "threshold": "contains verified clinical, illness, or danger root",
                    "source_record_ids": src_ids
                },
                automated_finding_only=True,
                human_validated=False
            ))

        # 3. Structural complexity and rare form review
        # Words exceeding 14 code points are polysyllabic, scientific, or rare compound forms
        if cp_count >= 15:
            flags.append("COMPLEX_OR_RARE_FORM_REVIEW")
            findings.append(ReviewFindingRecord(
                reason_code="COMPLEX_OR_RARE_FORM_REVIEW",
                rule_id="STAGE32-RULE-STRUCTURAL-COMPLEXITY-V1",
                trigger_evidence={
                    "observed_metric": f"code_point_count={cp_count}, grapheme_count={g_count}",
                    "threshold": "code_point_count >= 15",
                    "source_record_ids": src_ids
                },
                automated_finding_only=True,
                human_validated=False
            ))

        # 4. Check for mixed script or non-Sinhala code points
        sinh_count = 0
        non_sinh_count = 0
        for ch in surface:
            cp = ord(ch)
            if 0x0D80 <= cp <= 0x0DFF or cp in (0x200C, 0x200D):
                sinh_count += 1
            else:
                non_sinh_count += 1

        if non_sinh_count > 0:
            flags.append("MIXED_SCRIPT_PRESENT")
            findings.append(ReviewFindingRecord(
                reason_code="MIXED_SCRIPT_PRESENT",
                rule_id="STAGE32-RULE-MIXED-SCRIPT-V1",
                trigger_evidence={
                    "observed_metric": f"non_sinhala_code_point_count={non_sinh_count}",
                    "threshold": "non_sinhala_code_point_count > 0",
                    "source_record_ids": src_ids
                },
                automated_finding_only=True,
                human_validated=False
            ))

        # 5. Check for lone combining characters at the start of word
        if surface and unicodedata.category(surface[0]).startswith("M"):
            flags.append("LEADING_COMBINING_MARK_ERROR")

        # 6. Proper noun indicators
        for marker in PROPER_NOUN_MARKERS:
            if surface.startswith(marker):
                is_proper = True
                break

        return flags, findings, is_proper, is_sensitive

