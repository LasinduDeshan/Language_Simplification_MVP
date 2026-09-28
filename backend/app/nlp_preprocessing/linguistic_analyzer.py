"""
Stage 21 Linguistic Analyzer & Syntactic Parser Module
Integrates spaCy en_core_web_sm to extract sentences, tokens, POS tags, dependencies, and character offsets.
"""
import re
import spacy
from typing import List, Dict, Any, Tuple
from app.nlp_preprocessing.schemas import SentenceRecord, TokenRecord

class LinguisticAnalyzer:
    def __init__(self, spacy_model_name: str = "en_core_web_sm"):
        self.spacy_model_name = spacy_model_name
        self.nlp = spacy.load(spacy_model_name)

    @staticmethod
    def count_syllables(word: str) -> int:
        """Estimates syllable count using English vowel cluster rules."""
        w = word.lower().strip()
        if not w or not re.search(r"[a-z]", w):
            return 1
        if len(w) <= 3:
            return 1
            
        w = re.sub(r"(?:[^laeiouy]|ed|es|e)$", "", w)
        w = re.sub(r"^y", "", w)
        vowel_clusters = re.findall(r"[aeiouy]{1,2}", w)
        return max(1, len(vowel_clusters))

    def analyze(self, normalized_text: str, original_text: str, offset_map: List[int], record_id: str) -> List[SentenceRecord]:
        if not normalized_text:
            return []

        doc = self.nlp(normalized_text)
        sentences: List[SentenceRecord] = []
        token_counter = 0

        for sent_idx, sent in enumerate(doc.sents):
            raw_sent_text = sent.text
            if not raw_sent_text.strip():
                continue

            l_strip = len(raw_sent_text) - len(raw_sent_text.lstrip())
            r_strip = len(raw_sent_text) - len(raw_sent_text.rstrip())
            sent_norm_start = sent.start_char + l_strip
            sent_norm_end = sent.end_char - r_strip
            sent_text = normalized_text[sent_norm_start:sent_norm_end]

            # Map to original character offsets
            sent_orig_start = offset_map[sent_norm_start] if sent_norm_start < len(offset_map) else sent_norm_start
            sent_orig_end = offset_map[min(sent_norm_end - 1, len(offset_map) - 1)] + 1 if sent_norm_end <= len(offset_map) and sent_norm_end > 0 else sent_norm_end

            tokens: List[TokenRecord] = []
            for tok in sent:
                tok_text = tok.text
                if not tok_text:
                    continue

                tok_norm_start = tok.idx
                tok_norm_end = tok.idx + len(tok_text)

                tok_orig_start = offset_map[tok_norm_start] if tok_norm_start < len(offset_map) else tok_norm_start
                tok_orig_end = offset_map[min(tok_norm_end - 1, len(offset_map) - 1)] + 1 if tok_norm_end <= len(offset_map) and tok_norm_end > 0 else tok_norm_end

                syllables = self.count_syllables(tok_text)
                
                # Head index relative to sentence or doc
                head_idx = tok.head.i - sent.start

                tok_rec = TokenRecord(
                    index=token_counter,
                    text=tok_text,
                    lemma=tok.lemma_.lower() if tok.lemma_ else tok_text.lower(),
                    pos=tok.pos_,
                    tag=tok.tag_,
                    dependency=tok.dep_,
                    head_index=max(0, head_idx),
                    is_stop=tok.is_stop,
                    is_punct=tok.is_punct,
                    is_num=tok.like_num or tok.pos_ == "NUM",
                    syllable_count=syllables,
                    original_start_char=tok_orig_start,
                    original_end_char=tok_orig_end,
                    normalized_start_char=tok_norm_start,
                    normalized_end_char=tok_norm_end
                )
                tokens.append(tok_rec)
                token_counter += 1

            sent_rec = SentenceRecord(
                sentence_id=f"{record_id}-S{sent_idx+1:02d}",
                sentence_index=sent_idx,
                text=sent_text,
                original_start_char=sent_orig_start,
                original_end_char=sent_orig_end,
                normalized_start_char=sent_norm_start,
                normalized_end_char=sent_norm_end,
                tokens=tokens
            )
            sentences.append(sent_rec)

        return sentences
