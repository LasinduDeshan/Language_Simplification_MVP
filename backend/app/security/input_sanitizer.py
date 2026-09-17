import unicodedata
import re

MAX_TRANSCRIPT_LENGTH = 300
MAX_TEXT_INPUT_LENGTH = 1000

def sanitize_text(text: str, max_length: int = MAX_TEXT_INPUT_LENGTH) -> str:
    """
    Sanitizes user and simulated text input:
    - Normalizes Unicode (NFKC)
    - Strips non-printable and control characters
    - Truncates to maximum allowed length
    - Strips dangerous HTML tags
    """
    if not text:
        return ""
    
    # 1. Unicode normalization
    normalized = unicodedata.normalize("NFKC", text)
    
    # 2. Remove control characters (except newline, tab)
    cleaned = "".join(ch for ch in normalized if unicodedata.category(ch)[0] != "C" or ch in "\n\t ")
    
    # 3. Strip basic HTML tags
    no_html = re.sub(r"<[^>]*>", "", cleaned)
    
    # 4. Truncate
    truncated = no_html.strip()[:max_length]
    
    return truncated
