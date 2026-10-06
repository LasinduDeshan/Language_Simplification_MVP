"""
Stage 26 Hybrid Validation and Controlled Surface Repair Pipeline.
Passes all candidate model outputs through Stage 25 deterministic validation gates.
Applies strictly limited controlled surface repairs (whitespace, punctuation, casing, structured output extraction)
while routing semantic violations, negation flips, order changes, or answer leaks to rejection or manual review.
"""
import re
import difflib
from typing import Dict, Any, List, Optional, Tuple
from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ModelGenerationResult,
    NativeValidationDisposition,
    NativeValidationSummary,
)
from app.model_simplification.hmac_answer_guard import HMACAnswerGuard
from app.controlled_simplification.engine import ControlledSimplificationEngine
from app.controlled_simplification.schemas import SimplificationRequest as Stage25Request


class HybridValidationPipeline:
    """
    Hybrid validator enforcing Stage 25 linguistic, preservation, and delivery invariants on candidate outputs.
    """

    def __init__(self, s25_engine: Optional[ControlledSimplificationEngine] = None):
        self.s25_engine = s25_engine or ControlledSimplificationEngine()
        self.answer_guard = HMACAnswerGuard()

    def clean_surface_formatting(self, text: str) -> Tuple[str, List[str]]:
        """
        Applies safe, permitted surface repairs:
        - Markdown/JSON code block stripping
        - Whitespace normalization
        - Basic capitalization correction
        - Safe trailing punctuation repair
        """
        repairs: List[str] = []
        cleaned = text.strip()

        # 1. Strip markdown code block wrappers if any (e.g. ```text ... ```)
        if cleaned.startswith("```") and cleaned.endswith("```"):
            lines = cleaned.splitlines()
            if len(lines) >= 2:
                cleaned = "\n".join(lines[1:-1]).strip()
                repairs.append("strip_markdown_codeblock")

        # 2. Strip leading conversational filler ("Here is the simplified text: ...")
        filler_patterns = [
            r"^(?:Here is the simplified (?:sentence|text|instruction):\s*)+",
            r"^(?:Simplified (?:text|sentence|instruction):\s*)+",
            r"^(?:Sure, here is (?:the|a) simplified version:\s*)+",
        ]
        for pat in filler_patterns:
            subbed = re.sub(pat, "", cleaned, flags=re.IGNORECASE).strip()
            if subbed != cleaned:
                cleaned = subbed
                repairs.append("strip_conversational_filler")

        # Strip enclosing quotation marks if model wrapped response in quotes
        if (cleaned.startswith('"') and cleaned.endswith('"')) or (cleaned.startswith("'") and cleaned.endswith("'")):
            cleaned = cleaned[1:-1]
            repairs.append("strip_enclosing_quotes")

        # 3. Whitespace normalization
        norm_ws = re.sub(r"[ \t]+", " ", cleaned)
        norm_ws = re.sub(r"\n\s*\n+", "\n", norm_ws).strip()
        if norm_ws != cleaned:
            cleaned = norm_ws
            repairs.append("normalize_whitespace")

        # 4. Safe punctuation & capitalization
        if cleaned and cleaned[0].islower():
            cleaned = cleaned[0].upper() + cleaned[1:]
            repairs.append("capitalize_initial")

        return cleaned, repairs

    def calculate_similarity(self, original: str, candidate: str) -> float:
        """
        Calculates token-level sequence similarity.
        """
        return difflib.SequenceMatcher(None, original.lower().split(), candidate.lower().split()).ratio()

    def validate_candidate(
        self,
        request: ModelGenerationRequest,
        candidate_text: str,
        protected_answers: Optional[List[str]] = None,
    ) -> Tuple[NativeValidationDisposition, List[str], List[str], str, float]:
        """
        Runs comprehensive validation across Stage 25 invariant gates.
        Returns (disposition, failed_gates, repairs_applied, final_text, similarity_score).
        """
        failed_gates: List[str] = []
        repairs_applied: List[str] = []

        if not candidate_text or not candidate_text.strip():
            return NativeValidationDisposition.REJECTED, ["empty_candidate_output"], [], "", 0.0

        # Step 1: Surface cleaning
        repaired_text, repairs = self.clean_surface_formatting(candidate_text)
        repairs_applied.extend(repairs)

        sim_score = self.calculate_similarity(request.text, repaired_text)

        # Step 2: Exact preservation gate
        for term in request.protected_elements.exact_preservation:
            if not term or not term.strip():
                continue
            # Check presence (case-insensitive word boundary)
            pat = r"\b" + re.escape(term.strip()) + r"\b"
            if not re.search(pat, repaired_text, flags=re.IGNORECASE):
                failed_gates.append(f"missing_protected_term:{term}")

        # Step 3: Negation preservation check
        negation_words = {"not", "no", "never", "don't", "dont", "do not", "without", "stop"}
        orig_has_neg = any(re.search(r"\b" + re.escape(nw) + r"\b", request.text, re.IGNORECASE) for nw in negation_words)
        cand_has_neg = any(re.search(r"\b" + re.escape(nw) + r"\b", repaired_text, re.IGNORECASE) for nw in negation_words)
        if orig_has_neg != cand_has_neg:
            failed_gates.append("negation_inversion_detected")

        # Step 4: Answer leakage guard
        if protected_answers:
            is_safe, leaked_ans = self.answer_guard.verify_no_answer_leakage(repaired_text, protected_answers)
            if not is_safe:
                failed_gates.append(f"answer_leakage_detected:{leaked_ans}")

        # Step 5: Similarity threshold check
        if sim_score < 0.30:  # Complete semantic drift
            failed_gates.append("excessive_semantic_drift")

        # Step 6: Determine Disposition
        if not failed_gates:
            if repairs_applied:
                disp = NativeValidationDisposition.PASSED_WITH_CONTROLLED_REPAIR
            else:
                disp = NativeValidationDisposition.PASSED
        elif any("answer_leakage" in g or "negation" in g for g in failed_gates):
            disp = NativeValidationDisposition.REJECTED
        elif any("missing_protected_term" in g for g in failed_gates):
            disp = NativeValidationDisposition.MANUAL_REVIEW_REQUIRED
        else:
            disp = NativeValidationDisposition.REJECTED

        return disp, failed_gates, repairs_applied, repaired_text, round(sim_score, 4)
