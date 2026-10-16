"""
Stage 33 — Protected-Span and Meaning-Critical Detector.
Identifies meaning-critical elements that must not be altered without allowlisted rules.
Acknowledges that automated detection is conservative and incomplete for Sinhala.
"""

import re
from typing import List, Pattern, Set

from app.sinhala_simplification.enums import ProtectedSpanCategory
from app.sinhala_simplification.schemas import CodePointSpan, ProtectedSpan


# Stage 32 governed review-required vocabulary items
STAGE32_REVIEW_VOCABULARY: Set[str] = {
    "අනතුරු",
    "නිරෝගී",
    "රෝග",
    "ක්‍රියාකාරිත්වය",
    "කාබන්ඩයොක්සයිඩ්",
    "ප්‍රජාතන්ත්‍රවාදී",
    "ප්‍රතිශක්තිකරණයටද",
    "ප්‍රභාසංස්ලේෂණය",
    "සරච්චන්ද්‍රයන්ගේ",
}

# Negation markers
NEGATION_MARKERS: Set[str] = {
    "නැත",
    "නො",
    "නෙවෙයි",
    "නොවේ",
    "නැතැයි",
    "නැහැ",
    "නොමැත",
}

# Modality and condition markers
MODALITY_MARKERS: Set[str] = {
    "හැකිය",
    "යුතුය",
    "යුතු",
    "නම්",
    "බැවින්",
    "හෙයින්",
    "ඇතැම්විට",
    "හැකි",
}

# Month names for date detection
SINHALA_MONTHS: Set[str] = {
    "ජනවාරි", "පෙබරවාරි", "මාර්තු", "අප්‍රේල්", "මැයි", "ජූනි",
    "ජූලි", "අගෝස්තු", "සැප්තැම්බර්", "ඔක්තෝබර්", "නොවැම්බර්", "දෙසැම්බර්",
}

# Units of measurement
MEASUREMENT_UNITS: Set[str] = {
    "කිලෝග්‍රෑම්", "මීටර්", "සෙන්ටිමීටර්", "මිලිමීටර්", "ලීටර්",
    "මිලිලීටර්", "කිලෝමීටර්", "ග්‍රෑම්", "පැය", "මිනිත්තු", "තත්පර",
}

# Currencies
CURRENCY_MARKERS: Set[str] = {
    "රුපියල්", "රු.", "ඩොලර්", "$", "Rs.", "LKR", "USD"
}

# Spelled numbers
SPELLED_NUMBERS: Set[str] = {
    "එක", "දෙක", "තුන", "හතර", "පහ", "හය", "හත", "අට", "නවය", "දහය",
    "විස්ස", "තිහ", "හතළිහ", "පනහ", "හැට", "හැත්තෑව", "අසූව", "අනූව",
    "සියය", "දහස", "ලක්ෂය", "මිලියනය", "බිලියනය",
}

# Regex patterns
RE_NUMBER = re.compile(r"\b\d+(?:[.,]\d+)*(?:%| percent)?\b")
RE_URL = re.compile(r"https?://[^\s]+|www\.[^\s]+")
RE_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
RE_QUOTATION = re.compile(r'“[^”]*”|"[^"]*"|‘[^’]*’')
RE_PARENTHETICAL = re.compile(r"\([^)]*\)")
RE_MIXED_SCRIPT = re.compile(r"\b[A-Za-z0-9_#-]+\b")


class ProtectedSpanDetector:
    """
    Conservative detector for meaning-critical spans in Sinhala text.
    All detected spans are immutable half-open code-point intervals [start, end).
    """

    DETECTOR_VERSION = 1

    def detect_spans(self, text: str) -> List[ProtectedSpan]:
        """
        Analyzes normalized text and returns all identified protected spans.
        """
        spans: List[ProtectedSpan] = []
        counter = 1

        # 1. URL and Email identifiers
        for m in RE_URL.finditer(text):
            spans.append(self._create_span(counter, ProtectedSpanCategory.IDENTIFIER_CODE_URL, m.start(), m.end(), m.group(), "DET-URL-001"))
            counter += 1
        for m in RE_EMAIL.finditer(text):
            spans.append(self._create_span(counter, ProtectedSpanCategory.IDENTIFIER_CODE_URL, m.start(), m.end(), m.group(), "DET-EMAIL-001"))
            counter += 1

        # 2. Quotations and direct speech
        for m in RE_QUOTATION.finditer(text):
            spans.append(self._create_span(counter, ProtectedSpanCategory.QUOTATION_DIRECT_SPEECH, m.start(), m.end(), m.group(), "DET-QUOTE-001"))
            counter += 1

        # 3. Parentheticals and citations
        for m in RE_PARENTHETICAL.finditer(text):
            spans.append(self._create_span(counter, ProtectedSpanCategory.PARENTHETICAL_REFERENCE, m.start(), m.end(), m.group(), "DET-PAREN-001"))
            counter += 1

        # 4. Numbers and percentages
        for m in RE_NUMBER.finditer(text):
            spans.append(self._create_span(counter, ProtectedSpanCategory.NUMBER_NUMERIC, m.start(), m.end(), m.group(), "DET-NUM-001"))
            counter += 1

        # 5. Mixed-script terms
        for m in RE_MIXED_SCRIPT.finditer(text):
            # Avoid re-adding numbers or URLs already matched
            s, e = m.start(), m.end()
            if not any(ps.span.start_code_point <= s and e <= ps.span.end_code_point for ps in spans):
                spans.append(self._create_span(counter, ProtectedSpanCategory.MIXED_SCRIPT_TERM, s, e, m.group(), "DET-SCRIPT-001"))
                counter += 1

        # Token-based scanning for lexical keywords and meaning markers
        words = list(re.finditer(r"\S+", text))
        for wm in words:
            word = wm.group()
            s, e = wm.start(), wm.end()
            clean_word = word.strip(".,;:!?()[]\"'“”‘’")
            if not clean_word:
                continue

            rel_s = word.find(clean_word)
            clean_s = s + rel_s
            clean_e = clean_s + len(clean_word)

            # Check if already within an existing span
            if any(ps.span.start_code_point <= clean_s and clean_e <= ps.span.end_code_point for ps in spans):
                continue

            # Stage 32 review-required vocabulary
            if clean_word in STAGE32_REVIEW_VOCABULARY:
                spans.append(self._create_span(counter, ProtectedSpanCategory.STAGE32_REVIEW_REQUIRED_VOCABULARY, clean_s, clean_e, clean_word, "DET-STG32-001"))
                counter += 1
            # Negation markers
            elif clean_word in NEGATION_MARKERS:
                spans.append(self._create_span(counter, ProtectedSpanCategory.NEGATION_MARKER, clean_s, clean_e, clean_word, "DET-NEG-001"))
                counter += 1
            # Modality and condition
            elif clean_word in MODALITY_MARKERS:
                spans.append(self._create_span(counter, ProtectedSpanCategory.MODALITY_CONDITION, clean_s, clean_e, clean_word, "DET-MOD-001"))
                counter += 1
            # Spelled numbers
            elif clean_word in SPELLED_NUMBERS:
                spans.append(self._create_span(counter, ProtectedSpanCategory.NUMBER_NUMERIC, clean_s, clean_e, clean_word, "DET-NUM-SPELL-001"))
                counter += 1
            # Months / dates
            elif clean_word in SINHALA_MONTHS:
                spans.append(self._create_span(counter, ProtectedSpanCategory.DATE_TIME, clean_s, clean_e, clean_word, "DET-DATE-001"))
                counter += 1
            # Measurement units
            elif clean_word in MEASUREMENT_UNITS:
                spans.append(self._create_span(counter, ProtectedSpanCategory.UNIT_MEASUREMENT, clean_s, clean_e, clean_word, "DET-UNIT-001"))
                counter += 1
            # Currencies
            elif clean_word in CURRENCY_MARKERS:
                spans.append(self._create_span(counter, ProtectedSpanCategory.CURRENCY, clean_s, clean_e, clean_word, "DET-CURR-001"))
                counter += 1

        # Sort spans by start_code_point
        return sorted(spans, key=lambda x: (x.span.start_code_point, x.span.end_code_point))

    def _create_span(
        self,
        index: int,
        category: ProtectedSpanCategory,
        start: int,
        end: int,
        text: str,
        detector_rule_id: str
    ) -> ProtectedSpan:
        return ProtectedSpan(
            span_id=f"PROT-SPAN-{index:06d}",
            category=category,
            span=CodePointSpan(start_code_point=start, end_code_point=end, text=text),
            text=text,
            detector_rule_id=detector_rule_id,
            detector_version=self.DETECTOR_VERSION,
            confidence=1.0,
            allowlist_override=False
        )
