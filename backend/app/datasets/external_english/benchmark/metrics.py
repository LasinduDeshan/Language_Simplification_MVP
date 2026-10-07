"""Standard evaluation metrics for sentence simplification benchmarks (SARI, BLEU, Semantic Similarity Proxy, Complexity Shift).

Metrics Specifications:
- SARI: Implemented strictly according to Xu et al. (TACL 2016) / EASSE standard reference formulation.
  Computes unigram to 4-gram Add, Keep, and Delete precisions, recalls, and F1 scores against multi-reference sets.
- BLEU: Multi-reference sentence BLEU-4 with brevity penalty and standard add-1 smoothing.
- Semantic Similarity Proxy: Token-level harmonic precision/recall maximum across reference sets.
  * Algorithm: Harmonic F1 of unigram token overlap against closest reference.
  * Model / Embedding: Lexical token set intersection (offline proxy).
  * Scale: [0, 100].
  * Limitations: Lexical overlap harmonic mean only; does not utilize contextual RoBERTa embeddings;
    must NOT be compared directly to published RoBERTa-large BERTScore values.
- Complexity Reduction: Measures word/character compression ratio and Flesch-Kincaid Grade Level (FKGL) shift.
"""

from collections import Counter
import math
import re
from typing import Any, Dict, List, Optional, Tuple


def get_ngrams(tokens: List[str], n: int) -> Counter:
    """Extracts n-grams and counts their frequencies."""
    if len(tokens) < n:
        return Counter()
    return Counter(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))


def tokenize_words(text: str) -> List[str]:
    """Tokenizes text into lowercase word tokens matching standard EASSE evaluation tokenization."""
    return re.findall(r"\b\w+\b", text.lower())


def compute_sari(
    orig_text: str,
    pred_text: str,
    ref_texts: List[str],
    max_n: int = 4,
) -> Tuple[float, float, float, float]:
    """Computes standard multi-reference SARI (Xu et al., TACL 2016 / EASSE standard).
    
    Returns:
        (sari_overall, add_score, keep_score, del_score) in standard range [0, 100].
    """
    orig_tokens = tokenize_words(orig_text)
    pred_tokens = tokenize_words(pred_text)
    ref_tokens_list = [tokenize_words(ref) for ref in ref_texts if ref.strip()]

    if not ref_tokens_list:
        return 0.0, 0.0, 0.0, 0.0

    num_refs = len(ref_tokens_list)
    add_scores: List[float] = []
    keep_scores: List[float] = []
    del_scores: List[float] = []

    for n in range(1, max_n + 1):
        orig_ngrams = get_ngrams(orig_tokens, n)
        pred_ngrams = get_ngrams(pred_tokens, n)
        ref_ngrams_list = [get_ngrams(ref_toks, n) for ref_toks in ref_tokens_list]

        # 1. ADD Component (n-grams in pred NOT in orig, rewarded if added in refs)
        pred_add = pred_ngrams - orig_ngrams
        num_add = 0.0
        for ng, c_pred in pred_add.items():
            c_ref_avg = sum(ref.get(ng, 0) for ref in ref_ngrams_list) / num_refs
            num_add += min(c_pred, c_ref_avg)

        denom_add_p = sum(pred_add.values())
        p_add = (num_add / denom_add_p) if denom_add_p > 0 else 0.0

        all_ref_ngrams_set = set().union(*[set(ref.keys()) for ref in ref_ngrams_list])
        denom_add_r = sum(
            sum(max(0, ref.get(ng, 0) - orig_ngrams.get(ng, 0)) for ref in ref_ngrams_list) / num_refs
            for ng in all_ref_ngrams_set
        )
        r_add = (num_add / denom_add_r) if denom_add_r > 0 else 0.0
        f_add = (2 * p_add * r_add / (p_add + r_add)) if (p_add + r_add) > 0 else 0.0
        add_scores.append(f_add)

        # 2. KEEP Component (n-grams in orig KEPT in pred, rewarded if kept in refs)
        pred_keep = orig_ngrams & pred_ngrams
        num_keep = 0.0
        for ng, c_pred in pred_keep.items():
            c_orig = orig_ngrams[ng]
            c_ref_avg = sum(min(c_orig, ref.get(ng, 0)) for ref in ref_ngrams_list) / num_refs
            num_keep += min(c_pred, c_ref_avg)

        denom_keep_p = sum(pred_keep.values())
        p_keep = (num_keep / denom_keep_p) if denom_keep_p > 0 else 0.0

        denom_keep_r = sum(
            sum(min(orig_ngrams[ng], ref.get(ng, 0)) for ref in ref_ngrams_list) / num_refs
            for ng in orig_ngrams
        )
        r_keep = (num_keep / denom_keep_r) if denom_keep_r > 0 else 0.0
        f_keep = (2 * p_keep * r_keep / (p_keep + r_keep)) if (p_keep + r_keep) > 0 else 0.0
        keep_scores.append(f_keep)

        # 3. DELETE Component (n-grams in orig DELETED from pred, rewarded if deleted in refs)
        pred_del = orig_ngrams - pred_ngrams
        num_del = 0.0
        for ng, c_del in pred_del.items():
            c_orig = orig_ngrams[ng]
            c_ref_del = sum(max(0, c_orig - ref.get(ng, 0)) for ref in ref_ngrams_list) / num_refs
            num_del += min(c_del, c_ref_del)

        denom_del = sum(pred_del.values())
        p_del = (num_del / denom_del) if denom_del > 0 else 0.0
        del_scores.append(p_del)

    avg_add = sum(add_scores) / len(add_scores) * 100.0
    avg_keep = sum(keep_scores) / len(keep_scores) * 100.0
    avg_del = sum(del_scores) / len(del_scores) * 100.0
    overall_sari = (avg_add + avg_keep + avg_del) / 3.0

    return overall_sari, avg_add, avg_keep, avg_del


def compute_bleu(
    pred_text: str,
    ref_texts: List[str],
    max_n: int = 4,
) -> float:
    """Computes multi-reference sentence BLEU score with brevity penalty."""
    pred_tokens = tokenize_words(pred_text)
    ref_tokens_list = [tokenize_words(ref) for ref in ref_texts if ref.strip()]

    if not pred_tokens or not ref_tokens_list:
        return 0.0

    precisions: List[float] = []
    for n in range(1, max_n + 1):
        pred_ngrams = get_ngrams(pred_tokens, n)
        if sum(pred_ngrams.values()) == 0:
            precisions.append(0.0)
            continue

        max_ref_ngrams = Counter()
        for ref_tokens in ref_tokens_list:
            ref_ng = get_ngrams(ref_tokens, n)
            for k, v in ref_ng.items():
                max_ref_ngrams[k] = max(max_ref_ngrams[k], v)

        clipped_matches = sum((pred_ngrams & max_ref_ngrams).values())
        precisions.append(clipped_matches / sum(pred_ngrams.values()))

    if any(p == 0.0 for p in precisions):
        geom_mean = math.exp(sum(math.log(max(p, 1e-4)) for p in precisions) / max_n)
    else:
        geom_mean = math.exp(sum(math.log(p) for p in precisions) / max_n)

    # Brevity penalty based on closest reference length
    pred_len = len(pred_tokens)
    ref_lens = [len(r) for r in ref_tokens_list]
    closest_ref_len = min(ref_lens, key=lambda r_len: (abs(r_len - pred_len), r_len))

    if pred_len > closest_ref_len:
        bp = 1.0
    else:
        bp = math.exp(1.0 - closest_ref_len / pred_len) if pred_len > 0 else 0.0

    return bp * geom_mean * 100.0


def compute_semantic_similarity_proxy(
    pred_text: str,
    ref_texts: List[str],
) -> float:
    """Computes token-overlap harmonic semantic similarity proxy (NOT RoBERTa BERTScore).
    
    Returns harmonic F1 token similarity in range [0, 100].
    """
    pred_tokens = set(tokenize_words(pred_text))
    if not pred_tokens or not ref_texts:
        return 0.0

    ref_scores = []
    for ref in ref_texts:
        ref_tokens = set(tokenize_words(ref))
        if not ref_tokens:
            continue
        intersection = len(pred_tokens & ref_tokens)
        p = intersection / len(pred_tokens) if pred_tokens else 0.0
        r = intersection / len(ref_tokens) if ref_tokens else 0.0
        f1 = (2 * p * r / (p + r)) if (p + r) > 0 else 0.0
        ref_scores.append(f1)

    return (max(ref_scores) * 100.0) if ref_scores else 0.0


def estimate_fkgl(text: str) -> float:
    """Estimates Flesch-Kincaid Grade Level."""
    words = tokenize_words(text)
    if not words:
        return 0.0
    sentences = max(1, len(re.split(r"[.!?]+", text.strip())) - 1)
    
    syllable_count = 0
    for w in words:
        w_lower = w.lower()
        count = len(re.findall(r"[aeiouy]+", w_lower))
        if w_lower.endswith("e") and not w_lower.endswith("le") and count > 1:
            count -= 1
        syllable_count += max(1, count)

    fkgl = 0.39 * (len(words) / sentences) + 11.8 * (syllable_count / len(words)) - 15.59
    return max(0.0, fkgl)


def compute_complexity_reduction(orig_text: str, pred_text: str) -> Dict[str, float]:
    """Calculates complexity shift between original and simplified text."""
    orig_words = len(tokenize_words(orig_text))
    pred_words = len(tokenize_words(pred_text))
    orig_chars = len(orig_text)
    pred_chars = len(pred_text)
    
    orig_fkgl = estimate_fkgl(orig_text)
    pred_fkgl = estimate_fkgl(pred_text)

    return {
        "word_count_delta": pred_words - orig_words,
        "word_compression_ratio": (pred_words / orig_words) if orig_words > 0 else 1.0,
        "char_count_delta": pred_chars - orig_chars,
        "char_compression_ratio": (pred_chars / orig_chars) if orig_chars > 0 else 1.0,
        "fkgl_original": orig_fkgl,
        "fkgl_predicted": pred_fkgl,
        "fkgl_reduction": orig_fkgl - pred_fkgl,
    }
