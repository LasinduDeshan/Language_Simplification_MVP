"""
Stage 34 — Export and Privacy Sanitization Service
Ensures public repository ledgers, exports, and reports contain zero restricted text,
zero reviewer PII, and zero unredacted comments.
"""

from typing import Any, Dict, List


class ExportSanitizer:
    @staticmethod
    def sanitize_annotation(ann: Dict[str, Any]) -> Dict[str, Any]:
        """Removes protected text references and comment bodies from annotation dictionaries."""
        clean = dict(ann)
        clean.pop("protected_comment_ref", None)
        clean.pop("reviewer_notes", None)
        clean.pop("free_text_comment", None)
        return clean

    @staticmethod
    def verify_no_restricted_content(text: str) -> bool:
        """Heuristic check ensuring no raw PII or email patterns are leaked into output."""
        prohibited_indicators = ["@gmail.com", "@yahoo.com", "tel:", "password", "signature"]
        for p in prohibited_indicators:
            if p in text.lower():
                return False
        return True
