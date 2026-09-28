"""
Stage 21 Raw Linguistic Feature Extractor Module
Computes surface, lexical, syntactic, and protected features across parsed sentence records.
"""
import re
from typing import List, Dict, Any, Set
from app.nlp_preprocessing.schemas import (
    SentenceRecord,
    SurfaceFeatures,
    LexicalFeatures,
    SyntacticFeatures,
    ProtectedMeaningFeatures,
    LinguisticFeatureSet
)
from app.nlp_preprocessing.protected_elements import ProtectedElementExtractor

class FeatureExtractor:
    def __init__(self, long_word_char_threshold: int = 7, internal_lexicon_words: Set[str] = None):
        self.long_word_threshold = long_word_char_threshold
        self.internal_lexicon_words = internal_lexicon_words or set()
        self.protected_extractor = ProtectedElementExtractor()

    def extract_features(
        self,
        sentences: List[SentenceRecord],
        protected_meaning_units: List[str] = None,
        lexicon_repository: Dict[str, Any] = None
    ) -> LinguisticFeatureSet:
        all_tokens = [tok for s in sentences for tok in s.tokens]
        word_tokens = [t for t in all_tokens if not t.is_punct and re.search(r"[a-zA-Z]", t.text)]
        
        # 1. Surface Features
        total_chars = sum(len(t.text) for t in all_tokens)
        token_count = len(all_tokens)
        word_count = len(word_tokens)
        sentence_count = max(1, len(sentences))
        punct_count = sum(1 for t in all_tokens if t.is_punct)
        
        avg_word_len = round((sum(len(t.text) for t in word_tokens) / max(1, word_count)), 2)
        avg_sent_len = round((token_count / sentence_count), 2)
        
        unique_tokens = len(set(t.lemma for t in word_tokens))
        ttr = round((unique_tokens / max(1, word_count)), 3)
        
        total_syllables = sum(t.syllable_count for t in word_tokens)
        avg_syllables_per_word = round((total_syllables / max(1, word_count)), 2)
        long_words = sum(1 for t in word_tokens if len(t.text) >= self.long_word_threshold)

        surface = SurfaceFeatures(
            char_count=total_chars,
            token_count=token_count,
            word_count=word_count,
            sentence_count=sentence_count,
            punct_count=punct_count,
            avg_word_length=avg_word_len,
            avg_sentence_length=avg_sent_len,
            unique_token_count=unique_tokens,
            type_token_ratio=ttr,
            syllable_count=total_syllables,
            avg_syllables_per_word=avg_syllables_per_word,
            long_word_count=long_words
        )

        # 2. Lexical Features
        nouns = sum(1 for t in all_tokens if t.pos in ["NOUN", "PROPN"])
        verbs = sum(1 for t in all_tokens if t.pos in ["VERB", "AUX"])
        adjs = sum(1 for t in all_tokens if t.pos == "ADJ")
        advs = sum(1 for t in all_tokens if t.pos == "ADV")
        pronouns = sum(1 for t in all_tokens if t.pos == "PRON")
        preps = sum(1 for t in all_tokens if t.pos in ["ADP", "PREP"])
        
        content_words = nouns + verbs + adjs + advs
        function_words = max(0, word_count - content_words)
        
        finite_verbs = sum(1 for t in all_tokens if t.tag in ["VBD", "VBZ", "VBP", "MD"])
        aux_verbs = sum(1 for t in all_tokens if t.pos == "AUX")
        
        # Internal lexicon matching
        lex_matches = []
        difficult_words = []
        tier_counts = {"easy": 0, "medium": 0, "hard": 0}
        
        for t in word_tokens:
            w_lem = t.lemma.lower()
            if w_lem in self.internal_lexicon_words:
                lex_matches.append(w_lem)
            if len(t.text) >= 8 or t.syllable_count >= 3:
                difficult_words.append(t.text)
                
        lex_matches = sorted(list(set(lex_matches)))
        difficult_words = sorted(list(set(difficult_words)))
        out_of_lex_count = max(0, word_count - len(lex_matches))

        lexical = LexicalFeatures(
            content_word_count=content_words,
            function_word_count=function_words,
            noun_count=nouns,
            verb_count=verbs,
            adj_count=adjs,
            adv_count=advs,
            pronoun_count=pronouns,
            prep_count=preps,
            finite_verb_count=finite_verbs,
            auxiliary_verb_count=aux_verbs,
            out_of_lexicon_count=out_of_lex_count,
            internal_lexicon_tier_counts=tier_counts,
            internal_lexicon_matches=lex_matches,
            difficult_candidate_words=difficult_words
        )

        # 3. Syntactic Features
        roots = sum(1 for t in all_tokens if t.dependency == "ROOT")
        clauses = sum(1 for t in all_tokens if t.dependency in ["advcl", "relcl", "ccomp", "xcomp"])
        sub_conjs = sum(1 for t in all_tokens if t.pos == "SCONJ" or t.dependency == "mark")
        passive = any(t.dependency in ["nsubjpass", "auxpass"] for t in all_tokens)
        coords = sum(1 for t in all_tokens if t.dependency in ["conj", "cc"])
        
        # Estimate max and avg dependency depth based on distance to head
        depths = [abs(t.index - t.head_index) for t in all_tokens if not t.is_punct]
        max_depth = max(depths) if depths else 1
        avg_depth = round(sum(depths) / max(1, len(depths)), 2) if depths else 1.0
        
        # Imperative vs Fragment detection
        first_word = word_tokens[0] if word_tokens else None
        imperative = (first_word is not None and first_word.pos == "VERB" and first_word.tag == "VB")
        fragment = (verbs == 0 or word_count < 3)

        syntactic = SyntacticFeatures(
            max_dependency_depth=max_depth,
            avg_dependency_depth=avg_depth,
            clause_count=clauses,
            subordinate_conjunction_count=sub_conjs,
            passive_voice_detected=passive,
            coordination_count=coords,
            avg_noun_phrase_length=round(nouns / max(1, roots), 2),
            svo_triplets_available=(nouns >= 2 and verbs >= 1),
            root_count=roots,
            parse_failure_count=0,
            fragment_detected=fragment,
            imperative_detected=imperative
        )

        # 4. Protected Elements
        protected_feats = self.protected_extractor.extract_features(sentences, protected_meaning_units or [])

        return LinguisticFeatureSet(
            surface=surface,
            lexical=lexical,
            syntactic=syntactic,
            protected_elements=protected_feats
        )
