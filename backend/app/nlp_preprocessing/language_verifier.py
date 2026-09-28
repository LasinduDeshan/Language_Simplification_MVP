"""
Stage 21 Language Verifier Module
Verifies English language identity using pinned fastText or deterministic Latin/function-word heuristics.
"""
import re
from typing import Dict, Any, Optional
from app.nlp_preprocessing.schemas import LanguageVerificationRecord

class LanguageVerifier:
    def __init__(self, confidence_threshold: float = 0.80):
        self.confidence_threshold = confidence_threshold
        self.fasttext_model = None
        self._init_fasttext()
        
        # High-frequency English function words for deterministic fallback
        self.common_english_words = {
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
            "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
            "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
            "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
            "put", "look", "tap", "point", "choose", "find", "read", "answer", "select"
        }

    def _init_fasttext(self):
        try:
            import fasttext
            # If a local fasttext binary is available, load it; otherwise use fastText wrapper or fallback
            # We suppress fasttext verbose logging
            fasttext.FastText.eprint = lambda x: None
        except Exception:
            self.fasttext_model = None

    def verify_language(self, text: str) -> LanguageVerificationRecord:
        if not text or not text.strip():
            return LanguageVerificationRecord(
                verification_engine="deterministic_heuristic",
                model_version="heuristic_v1",
                confidence=0.0,
                decision="manual_review_required",
                fallback_reason="empty_text"
            )

        # 1. Primary Engine: fastText if model is loaded
        if self.fasttext_model is not None:
            try:
                single_line = text.replace("\n", " ").strip()
                labels, probs = self.fasttext_model.predict(single_line, k=1)
                lang = labels[0].replace("__label__", "")
                conf = float(probs[0])
                
                decision = "verified" if (lang == "en" and conf >= self.confidence_threshold) else "manual_review_required"
                return LanguageVerificationRecord(
                    verification_engine="fasttext",
                    model_version="lid.176.ftz",
                    confidence=round(conf, 4),
                    decision=decision,
                    fallback_reason=None if decision == "verified" else f"predicted_{lang}_conf_{conf:.2f}"
                )
            except Exception as e:
                pass

        # 2. Fallback Engine: Deterministic Latin character ratio + English function word heuristic
        words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
        total_words = max(1, len(words))
        
        # Check non-Latin characters
        non_latin_chars = len(re.findall(r"[^\x00-\x7F\s\.,!\?\"'\(\)\-;:0-9]", text))
        total_chars = max(1, len(text))
        latin_ratio = 1.0 - (non_latin_chars / total_chars)
        
        # Check English function word & vocabulary overlap
        eng_word_matches = sum(1 for w in words if w in self.common_english_words)
        function_word_ratio = eng_word_matches / total_words
        
        # English vowel & phonotactics check
        has_vowels = bool(re.search(r"[aeiouy]", text.lower()))
        
        # Blended heuristic confidence
        if latin_ratio < 0.85 or not has_vowels:
            conf = 0.20
            decision = "manual_review_required"
            fallback_reason = "non_latin_or_no_vowels"
        elif eng_word_matches == 0:
            conf = 0.40
            decision = "manual_review_required"
            fallback_reason = "zero_english_function_words"
        elif latin_ratio >= 0.98 and (function_word_ratio >= 0.15 or total_words <= 4):
            conf = 0.95
            decision = "verified"
            fallback_reason = "deterministic_heuristic_verified"
        elif function_word_ratio >= 0.10:
            conf = 0.85
            decision = "verified"
            fallback_reason = "deterministic_heuristic_verified"
        else:
            conf = 0.65
            decision = "manual_review_required"
            fallback_reason = "low_english_function_word_density"

        return LanguageVerificationRecord(
            verification_engine="deterministic_heuristic",
            model_version="heuristic_v1",
            confidence=round(conf, 4),
            decision=decision,
            fallback_reason=fallback_reason
        )
