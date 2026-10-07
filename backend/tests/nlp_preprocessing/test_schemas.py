"""
Unit tests for Stage 21 Schemas
"""
import pytest
from pydantic import ValidationError
from app.nlp_preprocessing.schemas import (
    TextInstance,
    TokenRecord,
    SentenceRecord,
    SurfaceFeatures,
    LexicalFeatures,
    SyntacticFeatures,
    ProtectedMeaningFeatures,
    LinguisticFeatureSet,
    LanguageVerificationRecord,
    PreprocessedRecord
)

def test_text_instance_validation_success():
    instance = TextInstance(
        text_instance_id="SRC-101__SRC",
        parent_record_id="SRC-101",
        parent_record_type="source_item",
        text_role="source_text",
        text="Put the red ball in the box.",
        language="en",
        source_group_id="SRC-101",
        dataset_split="development_candidate_train",
        protected_meaning_units=["red ball", "box"]
    )
    assert instance.text_instance_id == "SRC-101__SRC"
    assert instance.dataset_split == "development_candidate_train"

def test_text_instance_extra_field_forbid():
    with pytest.raises(ValidationError):
        TextInstance(
            text_instance_id="SRC-101__SRC",
            parent_record_id="SRC-101",
            parent_record_type="source_item",
            text_role="source_text",
            text="Put the red ball in the box.",
            language="en",
            dataset_split="development_candidate_train",
            unknown_arbitrary_field="invalid"
        )

def test_preprocessed_record_validation():
    lang_ver = LanguageVerificationRecord(
        verification_engine="fasttext",
        model_version="lid.176.ftz",
        confidence=0.99,
        decision="verified"
    )
    surf = SurfaceFeatures(
        char_count=28, token_count=7, word_count=7, sentence_count=1, punct_count=1,
        avg_word_length=3.5, avg_sentence_length=7.0, unique_token_count=7, type_token_ratio=1.0,
        syllable_count=7, avg_syllables_per_word=1.0, long_word_count=0
    )
    lex = LexicalFeatures(
        content_word_count=4, function_word_count=3, noun_count=2, verb_count=1, adj_count=1,
        adv_count=0, pronoun_count=0, prep_count=1, finite_verb_count=1, auxiliary_verb_count=0,
        out_of_lexicon_count=0, internal_lexicon_tier_counts={"easy": 3}, internal_lexicon_matches=["ball", "box"],
        difficult_candidate_words=[]
    )
    syn = SyntacticFeatures(
        max_dependency_depth=3, avg_dependency_depth=2.1, clause_count=1, subordinate_conjunction_count=0,
        passive_voice_detected=False, coordination_count=0, avg_noun_phrase_length=2.0, svo_triplets_available=True,
        root_count=1, parse_failure_count=0, fragment_detected=False, imperative_detected=True
    )
    prot = ProtectedMeaningFeatures(
        negation_markers=[], quantity_numbers=[], named_entities=[],
        spatial_prepositions=["in"], temporal_connectives=[], action_verbs=["put"],
        aligned_protected_units=[{"unit": "red ball", "status": "aligned"}]
    )
    feats = LinguisticFeatureSet(surface=surf, lexical=lex, syntactic=syn, protected_elements=prot)
    
    token = TokenRecord(
        index=0, text="Put", lemma="put", pos="VERB", tag="VB", dependency="ROOT", head_index=0,
        is_stop=False, is_punct=False, is_num=False, syllable_count=1,
        original_start_char=0, original_end_char=3, normalized_start_char=0, normalized_end_char=3
    )
    sentence = SentenceRecord(
        sentence_id="SRC-101-S01", sentence_index=0, text="Put the red ball in the box.",
        original_start_char=0, original_end_char=28, normalized_start_char=0, normalized_end_char=28,
        tokens=[token]
    )
    
    record = PreprocessedRecord(
        text_instance_id="SRC-101__SRC",
        parent_record_id="SRC-101",
        parent_record_type="source_item",
        text_role="source_text",
        source_dataset_version="0.2.0",
        pipeline_version="1.0.0",
        schema_version="1.0.0",
        language="en",
        dataset_split="development_candidate_train",
        source_group_id="SRC-101",
        original_text="Put the red ball in the box.",
        normalized_text="Put the red ball in the box.",
        language_verification=lang_ver,
        sentences=[sentence],
        features=feats,
        processing_status="success",
        text_hash="abc123hash",
        feature_hash="feat123hash",
        record_hash="rec123hash"
    )
    assert record.processing_status == "success"
    assert record.features.surface.char_count == 28
