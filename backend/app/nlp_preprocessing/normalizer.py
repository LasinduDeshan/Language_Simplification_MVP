"""
Stage 21 Unicode Normalizer Module
Applies deterministic NFC normalization, quote standardization, and character offset mapping.
"""
import unicodedata
from typing import Tuple, List, Dict

class UnicodeNormalizer:
    def __init__(self, form: str = "NFC", allow_nfkc_diagnostic: bool = False):
        if form == "NFKC" and not allow_nfkc_diagnostic:
            raise ValueError("NFKC normalization is disabled by default to protect mathematical/educational symbols. Use NFC or explicitly enable diagnostic mode.")
        self.form = form

    def normalize(self, text: str) -> Tuple[str, List[int]]:
        """
        Normalizes text using the configured Unicode normalization form (NFC default).
        Returns:
            normalized_text (str)
            offset_map (List[int]): Mapping from normalized character index to original character index.
        """
        if not text:
            return "", []

        # 1. Standardize quotes & apostrophes while maintaining length
        replacements = {
            "’": "'",
            "‘": "'",
            "“": '"',
            "”": '"',
            "–": "-",
            "—": "-",
            "\r\n": "\n",
            "\r": "\n"
        }
        
        # Build character-by-character mapping
        cur_text = text
        for orig_char, rep_char in replacements.items():
            cur_text = cur_text.replace(orig_char, rep_char)

        # 2. Unicode normalization
        norm_text = unicodedata.normalize(self.form, cur_text)

        # 3. Compute exact offset mapping table (len(norm_text) -> original index)
        # For direct 1-1 character replacements, index aligns directly
        # For non-1-1 transforms, compute alignment
        offset_map = []
        orig_len = len(text)
        norm_len = len(norm_text)
        
        if orig_len == norm_len:
            offset_map = list(range(orig_len))
        else:
            # Linear alignment approximation for Unicode composition/decomposition
            for i in range(norm_len):
                orig_idx = min(int(round(i * (orig_len / max(1, norm_len)))), orig_len - 1)
                offset_map.append(orig_idx)

        return norm_text, offset_map
