"""
Stage 21 Conservative Cleaner Module
Performs safe whitespace normalization and control character filtering with an audit log.
"""
import re
from typing import Tuple, List, Dict, Any

class ConservativeCleaner:
    def __init__(self):
        # Allowable characters: printable ASCII, basic Latin punctuation, common Unicode letters, standard linebreaks (\n)
        self.control_char_pattern = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")

    def clean(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Cleans text conservatively:
        - Detects and removes control characters while recording audit entries
        - Normalizes repeated horizontal whitespace without destroying multi-step line breaks (\\n)
        - Trims leading and trailing edge whitespace
        """
        if not text:
            return "", []

        audit_log = []
        
        # 1. Audit and remove unsupported control characters
        cleaned_chars = []
        for idx, ch in enumerate(text):
            if self.control_char_pattern.match(ch):
                audit_log.append({
                    "action": "removed_control_character",
                    "char_code": ord(ch),
                    "original_char_index": idx
                })
            else:
                cleaned_chars.append(ch)
                
        cleaned_text = "".join(cleaned_chars)

        # 2. Normalize horizontal whitespace within lines (preserve \n for step numbering)
        lines = cleaned_text.split("\n")
        normalized_lines = []
        for line in lines:
            norm_line = re.sub(r"[ \t]+", " ", line).strip()
            normalized_lines.append(norm_line)

        final_text = "\n".join(normalized_lines).strip()
        return final_text, audit_log
