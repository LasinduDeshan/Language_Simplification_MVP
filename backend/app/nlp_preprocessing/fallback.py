"""
Stage 21 Fallback Pipeline Module
Provides a deterministic rule-based degraded NLP processing mode when primary model fails.
"""
import re
from typing import List, Tuple, Dict, Any
from app.nlp_preprocessing.schemas import (
    SentenceRecord,
    TokenRecord,
    SurfaceFeatures,
    LexicalFeatures,
    SyntacticFeatures,
    ProtectedMeaningFeatures,
    LinguisticFeatureSet
)

class DeterministicFallbackPipeline:
    @staticmethod
    def count_syllables(word: str) -> int:
        w = word.lower().strip()
        if not w:
            return 1
        if len(w) <= 3:
            return 1
        w = re.sub(r"(?:[^laeiouy]|ed|es|e)$", "", w)
        w = re.sub(r"^y", "", w)
        vowel_clusters = re.findall(r"[aeiouy]{1,2}", w)
        return max(1, len(vowel_clusters))

    def process(self, normalized_text: str, offset_map: List[int], record_id: str, protected_meaning_units: List[str] = None) -> Tuple[List[SentenceRecord], LinguisticFeatureSet]:
        if not normalized_text:
            empty_surface = SurfaceFeatures(
                char_count=0, token_count=0, word_count=0, sentence_count=0,
                punct_count=0, avg_word_length=0.0, avg_sentence_length=0.0,
                unique_token_count=0, type_token_ratio=0.0, syllable_count=0,
                avg_syllables_per_word=0.0, long_word_count=0
            )
            empty_lexical = LexicalFeatures(
                content_word_count=0, function_word_count=0, noun_count=0,
                verb_count=0, adj_count=0, adv_count=0, pronoun_count=0,
                prep_count=0, finite_verb_count=0, auxiliary_verb_count=0,
                out_of_lexicon_count=0, internal_lexicon_tier_counts={},
                internal_lexicon_matches=[], difficult_candidate_words=[]
            )
            empty_syntactic = SyntacticFeatures(
                max_dependency_depth=0, avg_dependency_depth=0.0, clause_count=0,
                subordinate_conjunction_count=0, passive_voice_detected=False,
                coordination_count=0, avg_noun_phrase_length=0.0,
                svo_triplets_available=False, root_count=0, parse_failure_count=0,
                fragment_detected=False, imperative_detected=False
            )
            empty_protected = ProtectedMeaningFeatures(
                negation_markers=[], quantity_numbers=[], named_entities=[],
                spatial_prepositions=[], temporal_connectives=[], action_verbs=[],
                aligned_protected_units=[]
            )
            return [], LinguisticFeatureSet(
                surface=empty_surface,
                lexical=empty_lexical,
                syntactic=empty_syntactic,
                protected_elements=empty_protected
            )

        # Regex sentence split
        raw_sents = [s.strip() for s in re.split(r"(?<=[.!?\n])\s+", normalized_text) if s.strip()]
        if not raw_sents:
            raw_sents = [normalized_text]

        sentences: List[SentenceRecord] = []
        token_counter = 0
        char_ptr = 0

        for sent_idx, sent_str in enumerate(raw_sents):
            s_start = normalized_text.find(sent_str, char_ptr)
            if s_start == -1:
                s_start = char_ptr
            s_end = s_start + len(sent_str)
            char_ptr = s_end

            tokens: List[TokenRecord] = []
            tok_matches = list(re.finditer(r"\b[\w']+\b|[^\w\s]", sent_str))
            
            for m in tok_matches:
                t_str = m.group(0)
                t_start = s_start + m.start()
                t_end = s_start + m.end()

                is_p = bool(re.match(r"^[^\w\s]+$", t_str))
                is_num = bool(re.match(r"^\d+$", t_str))
                syl = self.count_syllables(t_str)

                tok_rec = TokenRecord(
                    index=token_counter,
                    text=t_str,
                    lemma=t_str.lower(),
                    pos="NUM" if is_num else ("PUNCT" if is_p else "NOUN"),
                    tag="CD" if is_num else ("." if is_p else "NN"),
                    dependency="dep",
                    head_index=0,
                    is_stop=False,
                    is_punct=is_p,
                    is_num=is_num,
                    syllable_count=syl,
                    original_start_char=offset_map[t_start] if t_start < len(offset_map) else t_start,
                    original_end_char=offset_map[min(t_end - 1, len(offset_map) - 1)] + 1 if t_end <= len(offset_map) and t_end > 0 else t_end,
                    normalized_start_char=t_start,
                    normalized_end_char=t_end
                )
                tokens.append(tok_rec)
                token_counter += 1

            sent_rec = SentenceRecord(
                sentence_id=f"{record_id}-S{sent_idx+1:02d}",
                sentence_index=sent_idx,
                text=sent_str,
                original_start_char=offset_map[s_start] if s_start < len(offset_map) else s_start,
                original_end_char=offset_map[min(s_end - 1, len(offset_map) - 1)] + 1 if s_end <= len(offset_map) and s_end > 0 else s_end,
                normalized_start_char=s_start,
                normalized_end_char=s_end,
                tokens=tokens
            )
            sentences.append(sent_rec)

        # Basic fallback features
        all_tokens = [t for s in sentences for t in s.tokens]
        words = [t for t in all_tokens if not t.is_punct]
        
        surface = SurfaceFeatures(
            char_count=sum(len(t.text) for t in all_tokens),
            token_count=len(all_tokens),
            word_count=len(words),
            sentence_count=len(sentences),
            punct_count=sum(1 for t in all_tokens if t.is_punct),
            avg_word_length=round(sum(len(t.text) for t in words) / max(1, len(words)), 2),
            avg_sentence_length=round(len(all_tokens) / max(1, len(sentences)), 2),
            unique_token_count=len(set(t.lemma for t in words)),
            type_token_ratio=round(len(set(t.lemma for t in words)) / max(1, len(words)), 3),
            syllable_count=sum(t.syllable_count for t in words),
            avg_syllables_per_word=round(sum(t.syllable_count for t in words) / max(1, len(words)), 2),
            long_word_count=sum(1 for t in words if len(t.text) >= 7)
        )
        lexical = LexicalFeatures(
            content_word_count=len(words),
            function_word_count=0,
            noun_count=len(words),
            verb_count=0,
            adj_count=0,
            adv_count=0,
            pronoun_count=0,
            prep_count=0,
            finite_verb_count=0,
            auxiliary_verb_count=0,
            out_of_lexicon_count=len(words),
            internal_lexicon_tier_counts={},
            internal_lexicon_matches=[],
            difficult_candidate_words=[t.text for t in words if len(t.text) >= 8]
        )
        syntactic = SyntacticFeatures(
            max_dependency_depth=1,
            avg_dependency_depth=1.0,
            clause_count=0,
            subordinate_conjunction_count=0,
            passive_voice_detected=False,
            coordination_count=0,
            avg_noun_phrase_length=1.0,
            svo_triplets_available=False,
            root_count=0,
            parse_failure_count=0,
            fragment_detected=True,
            imperative_detected=False
        )
        protected_feats = ProtectedMeaningFeatures(
            negation_markers=[],
            quantity_numbers=[],
            named_entities=[],
            spatial_prepositions=[],
            temporal_connectives=[],
            action_verbs=[],
            aligned_protected_units=[]
        )

        features = LinguisticFeatureSet(
            surface=surface,
            lexical=lexical,
            syntactic=syntactic,
            protected_elements=protected_feats
        )
        return sentences, features
