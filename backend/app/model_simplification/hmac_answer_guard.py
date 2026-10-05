"""
Stage 26: Server-Side HMAC Answer Non-Disclosure Guard.
Guarantees answer leakage detection on low-entropy tokens (e.g. 'cat', 'red', '3')
using keyed HMAC and normalized local string matching.
"""

import hmac
import hashlib
import os
import re
from typing import List, Optional, Tuple


class HmacAnswerGuard:
    """
    Manages server-side answer boundary verification.
    The secret key is loaded from environment / secret storage and only its key version is logged.
    """
    def __init__(self, key_version: str = "v1.0.0", secret_key: Optional[bytes] = None):
        self.key_version = key_version
        self._secret_key = secret_key or os.environ.get("HMAC_ANSWER_SECRET_KEY", "stage26_dev_hmac_secret_key").encode("utf-8")

    def compute_answer_hmac(self, answer_text: str) -> str:
        """Computes keyed HMAC-SHA256 of normalized answer text."""
        norm = answer_text.strip().lower()
        h = hmac.new(self._secret_key, norm.encode("utf-8"), hashlib.sha256)
        return f"hmac:{self.key_version}:{h.hexdigest()}"

    def check_leakage(self, candidate_text: str, protected_answers: List[str]) -> Tuple[bool, List[str]]:
        """
        Checks candidate output text against protected answers.
        Returns (is_leaked, list_of_leaked_answers).
        """
        leaked = []
        cand_norm = candidate_text.lower()
        cand_tokens = set(re.findall(r"\b\w+\b", cand_norm))

        for ans in protected_answers:
            if not ans:
                continue
            ans_norm = ans.strip().lower()
            
            # 1. Exact Substring match
            if ans_norm in cand_norm:
                leaked.append(ans)
                continue
            
            # 2. Token Set match
            ans_tokens = set(re.findall(r"\b\w+\b", ans_norm))
            if ans_tokens and ans_tokens.issubset(cand_tokens):
                leaked.append(ans)

        return (len(leaked) > 0, leaked)
