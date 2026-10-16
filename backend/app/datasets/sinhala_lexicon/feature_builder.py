"""
Feature Builder for Stage 32 Sinhala Lexicon Candidates.
Computes multi-dimensional structural, frequency, and dispersion metrics.
Maintains feature independence without collapsing dimensions into ad-hoc composite scores.
"""

import math
import unicodedata
from typing import Dict, List, Tuple

from app.sinhala_preprocessing.graphemes import segment_graphemes
from app.sinhala_preprocessing.script_analyzer import is_sinhala_cp
from app.datasets.sinhala_lexicon.parity_analyzer import ParityAnalyzer

class LexiconFeatureBuilder:
    """Extracts independent structural and corpus evidence features for candidate entries."""

    def __init__(self, parity_analyzer: ParityAnalyzer = None):
        self.parity_analyzer = parity_analyzer or ParityAnalyzer()

    def build_entry_features(
        self,
        surface: str,
        canonical_freq: int,
        canonical_doc_freq: int,
        source_freq_dist: Dict[str, int],
        eligible_source_count: int
    ) -> dict:
        """Computes all independent features for a candidate entry."""
        graphemes = segment_graphemes(surface)
        grapheme_count = len(graphemes)
        code_point_count = len(surface)
        utf8_byte_count = len(surface.encode("utf-8"))

        # Grapheme character inventory analysis
        has_joiner = ("\u200D" in surface) or ("\u200C" in surface)
        vowel_sign_count = 0
        consonant_count = 0

        for ch in surface:
            cp = ord(ch)
            if 0x0D85 <= cp <= 0x0D96:
                # Independent vowels
                vowel_sign_count += 1
            elif 0x0DCF <= cp <= 0x0DF3:
                # Dependent vowel signs
                vowel_sign_count += 1
            elif 0x0D9A <= cp <= 0x0DC6:
                # Consonants
                consonant_count += 1

        # Syllable proxy: heuristic counting non-virama consonants plus independent vowels
        syllable_proxy = max(1, len([g for g in graphemes if "\u0DCA" not in g]))

        # Source dispersion
        dispersion = self.parity_analyzer.compute_bounded_source_dispersion(
            source_freq_dist=source_freq_dist,
            eligible_source_count=eligible_source_count
        )

        return {
            "utf8_byte_count": utf8_byte_count,
            "code_point_count": code_point_count,
            "grapheme_count": grapheme_count,
            "consonant_count": consonant_count,
            "vowel_sign_count": vowel_sign_count,
            "has_joiner": has_joiner,
            "syllable_proxy_count": syllable_proxy,
            "canonical_frequency": canonical_freq,
            "canonical_document_frequency": canonical_doc_freq,
            "eligible_source_count": eligible_source_count,
            "observed_source_count": len(source_freq_dist),
            "source_dispersion": dispersion
        }
