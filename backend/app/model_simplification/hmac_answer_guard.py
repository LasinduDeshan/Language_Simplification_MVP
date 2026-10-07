"""
Stage 26 HMAC Answer Guard.
Provides local-only answer boundary validation, exact-preservation collision detection,
and answer leakage guards using normalized string matching and keyed HMAC.
Never transmits answers, hashes, or answer IDs to external providers.
"""
import hmac
import hashlib
import re
import unicodedata
from typing import List, Set, Optional, Tuple


class HMACAnswerGuard:
    """
    Local answer boundary guard ensuring zero answer disclosure and zero external hash exposure.
    """

    def __init__(self, secret_key: bytes = b"stage26_local_hmac_answer_guard_secret_2026"):
        self.secret_key = secret_key

    def normalize_token(self, token: str) -> str:
        """
        Normalizes a string for robust matching (lowercase, stripped punctuation, normalized whitespace).
        """
        if not token:
            return ""
        # Unicode normalization
        token = unicodedata.normalize("NFKD", token)
        # Lowercase
        token = token.lower()
        # Remove punctuation
        token = re.sub(r"[^\w\s]", "", token)
        # Collapse whitespace
        return re.sub(r"\s+", " ", token).strip()

    def compute_hmac(self, answer_text: str) -> str:
        """
        Computes keyed HMAC-SHA256 for local verification only.
        """
        normalized = self.normalize_token(answer_text)
        return hmac.new(self.secret_key, normalized.encode("utf-8"), hashlib.sha256).hexdigest()

    def check_protected_element_collision(
        self,
        exact_preservation_terms: List[str],
        protected_answers: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Verifies that no exact-preservation term accidentally collides with an answer token.
        Returns (has_collision, colliding_term).
        """
        norm_answers = {self.normalize_token(ans) for ans in protected_answers if ans}
        # Also split multi-word answers into core tokens
        answer_tokens: Set[str] = set()
        for ans in norm_answers:
            answer_tokens.update(ans.split())

        for term in exact_preservation_terms:
            norm_term = self.normalize_token(term)
            if not norm_term:
                continue
            if norm_term in norm_answers or norm_term in answer_tokens:
                return True, term

        return False, None

    def verify_no_answer_leakage(
        self,
        candidate_text: str,
        protected_answers: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Checks candidate output text to ensure protected answers are not disclosed or given away.
        Returns (is_safe, leaked_answer).
        """
        norm_candidate = self.normalize_token(candidate_text)
        candidate_words = set(norm_candidate.split())

        for ans in protected_answers:
            if not ans:
                continue
            norm_ans = self.normalize_token(ans)
            if not norm_ans:
                continue
            # Check full answer phrase
            if norm_ans in norm_candidate:
                return False, ans
            # If answer is a single key noun/verb, check direct word inclusion
            if len(norm_ans.split()) == 1 and norm_ans in candidate_words:
                return False, ans

        return True, None
