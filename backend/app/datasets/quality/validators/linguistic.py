"""NLP-assisted linguistic complexity and feature extraction validator."""
import re
import uuid
from typing import List, Dict, Any, Tuple
from app.datasets.quality.enums import RuleSeverity, QualityDimension
from app.datasets.quality.schemas import QualityRuleResultV1
from app.datasets.quality.validators.base import BaseValidator
from app.datasets.quality.thresholds import (
    MAX_RECOMMENDED_ASL_TOKENS,
    MAX_ALLOWABLE_ASL_TOKENS,
    COMPRESSION_RATIO_MIN_WARN,
    COMPRESSION_RATIO_MAX_WARN,
    COMPRESSION_RATIO_MIN_ERR,
    COMPRESSION_RATIO_MAX_ERR
)


def count_syllables_heuristic(word: str) -> int:
    """Deterministic English syllable counter heuristic."""
    word = word.lower().strip()
    if not word or not word.isalpha():
        return 1
    if len(word) <= 3:
        return 1
    # Count vowel groups
    vowels = "aeiouy"
    count = 0
    prev_is_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel
    if word.endswith("e") and not word.endswith("le") and count > 1:
        count -= 1
    return max(1, count)


def extract_linguistic_features(text: str) -> Dict[str, Any]:
    """Extracts deterministic linguistic features for child-friendly simplification analysis."""
    clean_text = text.strip()
    sentences = [s.strip() for s in re.split(r'[.!?]+', clean_text) if s.strip()]
    tokens = re.findall(r'\b\w+\b', clean_text)
    
    num_sentences = max(1, len(sentences))
    num_tokens = len(tokens)
    asl = num_tokens / num_sentences if num_sentences > 0 else 0.0
    
    syllables = [count_syllables_heuristic(t) for t in tokens]
    avg_syllables = sum(syllables) / num_tokens if num_tokens > 0 else 1.0
    complex_words = sum(1 for s in syllables if s >= 3)
    complex_word_ratio = complex_words / num_tokens if num_tokens > 0 else 0.0
    
    # Repetition ratio
    unique_tokens = len(set(t.lower() for t in tokens))
    repetition_ratio = 1.0 - (unique_tokens / num_tokens) if num_tokens > 0 else 0.0

    return {
        "num_sentences": num_sentences,
        "num_tokens": num_tokens,
        "asl": round(asl, 2),
        "avg_syllables_per_word": round(avg_syllables, 2),
        "complex_word_ratio": round(complex_word_ratio, 2),
        "repetition_ratio": round(repetition_ratio, 2)
    }


class LinguisticValidator(BaseValidator):
    """Evaluates Average Sentence Length, compression, repetition, and linguistic proxies."""

    validator_name = "linguistic_validator"
    validator_version = "1.0.0"

    def validate(self, record: Dict[str, Any], run_id: str = "adhoc_run") -> List[QualityRuleResultV1]:
        results: List[QualityRuleResultV1] = []
        record_id = record.get("pair_id") or record.get("activity_id") or "UNKNOWN_RECORD"
        dataset_layer = record.get("dataset_layer", "simplification_corpus")

        orig_text = str(record.get("original_text", "") or record.get("instruction", "")).strip()
        simp_text = str(record.get("simplified_text", "") or record.get("mild_scaffold", "") or orig_text).strip()

        orig_feat = extract_linguistic_features(orig_text)
        simp_feat = extract_linguistic_features(simp_text)

        # 1. SIMP-ASL-006: Average Sentence Length Check
        asl = simp_feat["asl"]
        if asl > MAX_ALLOWABLE_ASL_TOKENS:
            asl_severity = RuleSeverity.ERROR
            asl_passed = False
            asl_msg = f"Average sentence length ({asl} tokens) exceeds maximum allowable limit ({MAX_ALLOWABLE_ASL_TOKENS})."
        elif asl > MAX_RECOMMENDED_ASL_TOKENS:
            asl_severity = RuleSeverity.WARNING
            asl_passed = False
            asl_msg = f"Average sentence length ({asl} tokens) exceeds recommended limit ({MAX_RECOMMENDED_ASL_TOKENS}) for ages 4-8."
        else:
            asl_severity = RuleSeverity.INFO
            asl_passed = True
            asl_msg = f"Average sentence length ({asl} tokens) is appropriate."

        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="SIMP-ASL-006",
            validator_name=self.validator_name,
            dimension=QualityDimension.AGE_APPROPRIATENESS,
            severity=asl_severity if not asl_passed else RuleSeverity.INFO,
            passed=asl_passed,
            score=round(max(0.0, min(100.0, 100.0 - (asl - MAX_RECOMMENDED_ASL_TOKENS) * 10)), 1) if not asl_passed else 100.0,
            threshold=f"ASL <= {MAX_RECOMMENDED_ASL_TOKENS}",
            message=asl_msg,
            recommended_action=None if asl_passed else "Split complex sentences into shorter, child-friendly segments.",
            details=simp_feat
        ))

        # 2. SIMP-COMP-007: Compression ratio check
        orig_len = max(1, len(orig_text.split()))
        simp_len = max(1, len(simp_text.split()))
        ratio = round(simp_len / orig_len, 2)

        if ratio < COMPRESSION_RATIO_MIN_ERR or ratio > COMPRESSION_RATIO_MAX_ERR:
            comp_severity = RuleSeverity.ERROR
            comp_passed = False
            comp_msg = f"Extreme length divergence (ratio={ratio}). Original words={orig_len}, simplified words={simp_len}."
        elif ratio < COMPRESSION_RATIO_MIN_WARN or ratio > COMPRESSION_RATIO_MAX_WARN:
            comp_severity = RuleSeverity.WARNING
            comp_passed = False
            comp_msg = f"Length divergence warning (ratio={ratio}). Original words={orig_len}, simplified words={simp_len}."
        else:
            comp_severity = RuleSeverity.INFO
            comp_passed = True
            comp_msg = f"Compression ratio is well-balanced ({ratio})."

        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="SIMP-COMP-007",
            validator_name=self.validator_name,
            dimension=QualityDimension.SIMPLICITY_IMPROVEMENT,
            severity=comp_severity if not comp_passed else RuleSeverity.INFO,
            passed=comp_passed,
            score=round(ratio, 2),
            threshold=f"{COMPRESSION_RATIO_MIN_WARN} <= ratio <= {COMPRESSION_RATIO_MAX_WARN}",
            message=comp_msg,
            recommended_action=None if comp_passed else "Review text length balance.",
            details={"original_word_count": orig_len, "simplified_word_count": simp_len, "ratio": ratio}
        ))

        # 3. Degeneration / Repetition ratio check
        rep_ratio = simp_feat["repetition_ratio"]
        rep_passed = not (rep_ratio > 0.65 and simp_feat["num_tokens"] > 8)
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="SIMP-REP-008",
            validator_name=self.validator_name,
            dimension=QualityDimension.GRAMMAR_FLUENCY,
            severity=RuleSeverity.ERROR if not rep_passed else RuleSeverity.INFO,
            passed=rep_passed,
            threshold="repetition_ratio <= 0.65",
            message="No repetitive generation detected." if rep_passed else f"High repetition ratio ({rep_ratio}) indicates degenerate output.",
            recommended_action=None if rep_passed else "Regenerate or correct repetitive simplified text.",
            details=simp_feat
        ))

        return results
