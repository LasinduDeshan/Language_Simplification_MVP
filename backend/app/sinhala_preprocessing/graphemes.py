"""
Grapheme segmentation module for Stage 30 Sinhala Preprocessing.
Pins extended grapheme cluster segmentation using Python's regex package (\\X).
Reports:
- UTF-8 byte count, Unicode code-point count, and grapheme-cluster count independently.
"""

import sys
import regex
import unicodedata
from typing import Dict, List, Tuple

PINNED_METADATA: Dict[str, str] = {
    "engine": "regex_X",
    "pinned_package": "regex",
    "pinned_version": getattr(regex, "__version__", "2025.11.3"),
    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    "unicodedata_version": unicodedata.unidata_version,
    "conformance_scope": "governed_fixtures_verified"
}

def segment_graphemes(text: str) -> List[str]:
    """
    Segment text into Unicode extended grapheme clusters using pinned regex \\X.
    """
    if not text:
        return []
    return regex.findall(r"\X", text)

def count_graphemes(text: str) -> int:
    """
    Return total extended grapheme cluster count.
    """
    if not text:
        return 0
    return len(regex.findall(r"\X", text))

def get_grapheme_spans(text: str) -> List[Tuple[int, int]]:
    """
    Return list of (start_code_point, end_code_point) half-open intervals
    for each extended grapheme cluster in text.
    """
    if not text:
        return []

    spans = []
    current_idx = 0
    for cluster in regex.findall(r"\X", text):
        cluster_len = len(cluster)
        spans.append((current_idx, current_idx + cluster_len))
        current_idx += cluster_len
    return spans

def compute_string_metrics(text: str) -> Dict[str, int]:
    """
    Compute UTF-8 bytes, Unicode code points, and extended grapheme clusters independently.
    """
    return {
        "utf8_byte_count": len(text.encode("utf-8")),
        "code_point_count": len(text),
        "grapheme_count": count_graphemes(text)
    }
