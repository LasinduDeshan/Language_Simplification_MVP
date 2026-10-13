"""
Metric Adapter for Stage 28A Preliminary English Model Comparison.
Implements:
1. Multi-reference EASSE-style SARI (Overall, Add F1, Keep F1, Delete precision)
2. Mean Sentence BLEU-4 (sentence-level)
3. Corpus SacreBLEU with explicit signature (corpus-level)
4. Readability FKGL & Delta FKGL
5. Compression ratio & surface statistics
"""
import re
import math
from typing import List, Dict, Any, Tuple
from collections import Counter
import sacrebleu

PINNED_EASSE_SPECIFICATION = {
    "reference_implementation": "Xu et al. (TACL 2016) / EASSE standard reference",
    "pinned_target_version": "0.2.4",
    "tokenization": "lowercase_word_regex_b_w_b",
    "max_ngram": 4,
    "components": ["Add_F1", "Keep_F1", "Delete_Precision"],
    "allowed_tolerance": 1e-4,
}


def tokenize_words(text: str) -> List[str]:
    """Tokenize text into lowercase word tokens."""
    return re.findall(r"\b\w+\b", text.lower())


def get_ngrams(tokens: List[str], n: int) -> Counter:
    if len(tokens) < n:
        return Counter()
    return Counter(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))


def compute_sari_easse_style(
    orig_text: str,
    pred_text: str,
    ref_texts: List[str],
    max_n: int = 4,
) -> Tuple[float, float, float, float]:
    """
    Computes EASSE-style multi-reference SARI.
    Returns: (overall_sari, add_f1, keep_f1, del_precision) on [0, 100] scale.
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

        # 1. ADD Component: n-grams in pred NOT in orig, rewarded if added in refs
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

        # 2. KEEP Component: n-grams in orig KEPT in pred, rewarded if kept in refs
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

        # 3. DELETE Component: deletion precision
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


def count_syllables(word: str) -> int:
    """Heuristic syllable counter for English words."""
    word = word.lower().strip()
    if not word:
        return 0
    if len(word) <= 3:
        return 1
    word = re.sub(r"(?:[^laeiouy]|ed|es|e)$", "", word)
    word = re.sub(r"^y", "", word)
    matches = re.findall(r"[aeiouy]{1,2}", word)
    return max(1, len(matches))


def compute_fkgl(text: str) -> float:
    """Flesch-Kincaid Grade Level formula."""
    words = re.findall(r"\b\w+\b", text)
    if not words:
        return 0.0
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    num_sentences = max(1, len(sentences))
    num_words = len(words)
    num_syllables = sum(count_syllables(w) for w in words)

    fkgl = 0.39 * (num_words / num_sentences) + 11.8 * (num_syllables / num_words) - 15.59
    return max(0.0, round(fkgl, 2))


def compute_sentence_bleu_4(pred_text: str, ref_texts: List[str]) -> float:
    """Sentence-level smoothed BLEU-4 against multiple references."""
    pred_tokens = tokenize_words(pred_text)
    ref_tokens_list = [tokenize_words(ref) for ref in ref_texts if ref.strip()]
    if not pred_tokens or not ref_tokens_list:
        return 0.0

    precisions = []
    for n in range(1, 5):
        pred_ngrams = get_ngrams(pred_tokens, n)
        if sum(pred_ngrams.values()) == 0:
            precisions.append(1.0 / (2 ** n))  # smoothing
            continue

        max_ref_ngrams = Counter()
        for ref_tokens in ref_tokens_list:
            r_ng = get_ngrams(ref_tokens, n)
            for ng, cnt in r_ng.items():
                max_ref_ngrams[ng] = max(max_ref_ngrams[ng], cnt)

        clipped = sum(min(cnt, max_ref_ngrams[ng]) for ng, cnt in pred_ngrams.items())
        total = sum(pred_ngrams.values())
        precisions.append((clipped + 1.0) / (total + 1.0))  # add-1 smoothing

    log_sum = sum(math.log(p) for p in precisions) / 4.0
    geo_mean = math.exp(log_sum)

    # Brevity penalty against closest reference length
    pred_len = len(pred_tokens)
    closest_ref_len = min((len(r) for r in ref_tokens_list), key=lambda r_len: (abs(r_len - pred_len), r_len))
    if pred_len > closest_ref_len:
        bp = 1.0
    elif pred_len == 0:
        bp = 0.0
    else:
        bp = math.exp(1 - closest_ref_len / pred_len)

    return round(bp * geo_mean * 100.0, 2)


def compute_corpus_sacrebleu(
    predictions: List[str],
    references_per_item: List[List[str]],
) -> Tuple[float, str]:
    """
    Computes benchmark-level Corpus SacreBLEU.
    Returns: (corpus_bleu_score, sacrebleu_signature)
    """
    if not predictions:
        return 0.0, ""

    max_refs = max(len(r) for r in references_per_item) if references_per_item else 1
    ref_streams = []
    for r_idx in range(max_refs):
        stream = [r[r_idx] if r_idx < len(r) else r[0] for r in references_per_item]
        ref_streams.append(stream)

    metric = sacrebleu.BLEU()
    bleu_obj = metric.corpus_score(predictions, ref_streams)
    sig = str(metric.get_signature())
    return round(float(bleu_obj.score), 2), sig
