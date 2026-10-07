"""
Stage 21 NLP Preprocessing Schemas and Dataset Adapters
Strict Pydantic v2 data models with extra='forbid'
"""
from typing import Literal, List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field

DatasetSplit = Literal[
    "development_candidate_train",
    "development_candidate_validation",
    "development_candidate_test",
    "adaptation_test",
    "legacy_excluded",
    "unassigned",
]

class TextInstance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    text_instance_id: str
    parent_record_id: str
    parent_record_type: Literal[
        "source_item",
        "simplification_pair",
        "adaptation_activity",
        "lexicon_entry",
    ]
    text_role: Literal[
        "source_text",
        "simplified_text",
        "activity_instruction",
        "activity_prompt",
        "activity_passage",
        "activity_question",
        "lexicon_definition",
        "lexicon_example",
    ]
    text: str
    language: Literal["en"] = "en"
    source_group_id: Optional[str] = None
    dataset_split: DatasetSplit
    protected_meaning_units: List[str] = Field(default_factory=list)
    protected_answer_ref: Optional[str] = None
    protected_answer_hash: Optional[str] = None
    provenance: Dict[str, Any] = Field(default_factory=dict)

# Dataset Adapters
class SourceItemAdapter:
    @staticmethod
    def extract_text_instances(record: Dict[str, Any], default_split: DatasetSplit = "development_candidate_train") -> List[TextInstance]:
        rec_id = record.get("source_item_id") or record.get("item_id") or "UNKNOWN"
        text = record.get("original_text") or record.get("text") or ""
        split = record.get("dataset_split", default_split)
        
        return [
            TextInstance(
                text_instance_id=f"{rec_id}__SRC",
                parent_record_id=rec_id,
                parent_record_type="source_item",
                text_role="source_text",
                text=text,
                language="en",
                source_group_id=rec_id,
                dataset_split=split,
                protected_meaning_units=record.get("protected_meaning_units", []),
                provenance=record.get("provenance", {})
            )
        ]

class SimplificationPairAdapter:
    @staticmethod
    def extract_text_instances(record: Dict[str, Any], default_split: DatasetSplit = "development_candidate_train") -> List[TextInstance]:
        pair_id = record.get("pair_id", "UNKNOWN")
        src_id = record.get("source_item_id", pair_id)
        orig_text = record.get("original_text") or record.get("source_text") or ""
        simp_text = record.get("simplified_text", "")
        split = record.get("dataset_split", default_split)
        prot = record.get("protected_meaning_units", [])
        prov = record.get("provenance", {})
        
        instances = []
        if orig_text:
            instances.append(TextInstance(
                text_instance_id=f"{pair_id}__ORIG",
                parent_record_id=pair_id,
                parent_record_type="simplification_pair",
                text_role="source_text",
                text=orig_text,
                language="en",
                source_group_id=src_id,
                dataset_split=split,
                protected_meaning_units=prot,
                provenance=prov
            ))
        if simp_text:
            instances.append(TextInstance(
                text_instance_id=f"{pair_id}__SIMP",
                parent_record_id=pair_id,
                parent_record_type="simplification_pair",
                text_role="simplified_text",
                text=simp_text,
                language="en",
                source_group_id=src_id,
                dataset_split=split,
                protected_meaning_units=prot,
                provenance=prov
            ))
        return instances

class AdaptationActivityAdapter:
    @staticmethod
    def extract_text_instances(record: Dict[str, Any], default_split: DatasetSplit = "adaptation_test") -> List[TextInstance]:
        act_id = record.get("activity_id", "UNKNOWN")
        src_id = record.get("source_item_id", act_id)
        orig_inst = record.get("original_instruction") or record.get("instruction") or ""
        child_inst = record.get("child_friendly_instruction") or record.get("prompt") or ""
        passage = record.get("passage") or record.get("reading_passage") or ""
        question = record.get("question_text") or record.get("question") or ""
        split = record.get("dataset_split", default_split)
        prov = record.get("provenance", {})
        
        ans_ref = f"{act_id}__ANSWER" if record.get("expected_response") or record.get("protected_answer") or record.get("correct_answer") else None
        
        instances = []
        if orig_inst:
            instances.append(TextInstance(
                text_instance_id=f"{act_id}__INST",
                parent_record_id=act_id,
                parent_record_type="adaptation_activity",
                text_role="activity_instruction",
                text=orig_inst,
                language="en",
                source_group_id=src_id,
                dataset_split=split,
                protected_answer_ref=ans_ref,
                provenance=prov
            ))
        if child_inst:
            instances.append(TextInstance(
                text_instance_id=f"{act_id}__PROMPT",
                parent_record_id=act_id,
                parent_record_type="adaptation_activity",
                text_role="activity_prompt",
                text=child_inst,
                language="en",
                source_group_id=src_id,
                dataset_split=split,
                protected_answer_ref=ans_ref,
                provenance=prov
            ))
        if passage:
            instances.append(TextInstance(
                text_instance_id=f"{act_id}__PASSAGE",
                parent_record_id=act_id,
                parent_record_type="adaptation_activity",
                text_role="activity_passage",
                text=passage,
                language="en",
                source_group_id=src_id,
                dataset_split=split,
                protected_answer_ref=ans_ref,
                provenance=prov
            ))
        if question:
            instances.append(TextInstance(
                text_instance_id=f"{act_id}__QUESTION",
                parent_record_id=act_id,
                parent_record_type="adaptation_activity",
                text_role="activity_question",
                text=question,
                language="en",
                source_group_id=src_id,
                dataset_split=split,
                protected_answer_ref=ans_ref,
                provenance=prov
            ))
        return instances

class LexiconEntryAdapter:
    @staticmethod
    def extract_text_instances(record: Dict[str, Any], default_split: DatasetSplit = "unassigned") -> List[TextInstance]:
        lex_id = record.get("lexicon_id", "UNKNOWN")
        cdef = record.get("child_definition", "")
        ex = record.get("example_sentence", "")
        prov = record.get("provenance", {})
        
        instances = []
        if cdef:
            instances.append(TextInstance(
                text_instance_id=f"{lex_id}__DEF",
                parent_record_id=lex_id,
                parent_record_type="lexicon_entry",
                text_role="lexicon_definition",
                text=cdef,
                language="en",
                source_group_id=None,
                dataset_split=default_split,
                provenance=prov
            ))
        if ex:
            instances.append(TextInstance(
                text_instance_id=f"{lex_id}__EX",
                parent_record_id=lex_id,
                parent_record_type="lexicon_entry",
                text_role="lexicon_example",
                text=ex,
                language="en",
                source_group_id=None,
                dataset_split=default_split,
                provenance=prov
            ))
        return instances


# Linguistic & Feature Models
class TokenRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    index: int
    text: str
    lemma: str
    pos: str
    tag: str
    dependency: str
    head_index: int
    is_stop: bool
    is_punct: bool
    is_num: bool
    syllable_count: int
    original_start_char: int
    original_end_char: int
    normalized_start_char: int
    normalized_end_char: int

class SentenceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    sentence_id: str
    sentence_index: int
    text: str
    original_start_char: int
    original_end_char: int
    normalized_start_char: int
    normalized_end_char: int
    tokens: List[TokenRecord]

class SurfaceFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    char_count: int
    token_count: int
    word_count: int
    sentence_count: int
    punct_count: int
    avg_word_length: float
    avg_sentence_length: float
    unique_token_count: int
    type_token_ratio: float
    syllable_count: int
    avg_syllables_per_word: float
    long_word_count: int

class LexicalFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    content_word_count: int
    function_word_count: int
    noun_count: int
    verb_count: int
    adj_count: int
    adv_count: int
    pronoun_count: int
    prep_count: int
    finite_verb_count: int
    auxiliary_verb_count: int
    out_of_lexicon_count: int
    internal_lexicon_tier_counts: Dict[str, int]
    internal_lexicon_matches: List[str]
    difficult_candidate_words: List[str]

class SyntacticFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    max_dependency_depth: int
    avg_dependency_depth: float
    clause_count: int
    subordinate_conjunction_count: int
    passive_voice_detected: bool
    coordination_count: int
    avg_noun_phrase_length: float
    svo_triplets_available: bool
    root_count: int
    parse_failure_count: int
    fragment_detected: bool
    imperative_detected: bool

class ProtectedMeaningFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    negation_markers: List[str]
    quantity_numbers: List[str]
    named_entities: List[Dict[str, str]]
    spatial_prepositions: List[str]
    temporal_connectives: List[str]
    action_verbs: List[str]
    aligned_protected_units: List[Dict[str, Any]]

class LinguisticFeatureSet(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    surface: SurfaceFeatures
    lexical: LexicalFeatures
    syntactic: SyntacticFeatures
    protected_elements: ProtectedMeaningFeatures

class LanguageVerificationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    verification_engine: Literal["fasttext", "deterministic_heuristic"]
    model_version: str
    confidence: float
    decision: Literal["verified", "manual_review_required", "rejected"]
    fallback_reason: Optional[str] = None

class PreprocessedRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    text_instance_id: str
    parent_record_id: str
    parent_record_type: str
    text_role: str
    source_dataset_version: str = "0.2.0"
    pipeline_version: str = "1.0.0"
    schema_version: str = "1.0.0"
    language: str = "en"
    dataset_split: DatasetSplit
    source_group_id: Optional[str] = None
    original_text: str
    normalized_text: str
    language_verification: LanguageVerificationRecord
    sentences: List[SentenceRecord]
    features: LinguisticFeatureSet
    processing_status: Literal["success", "fallback_success", "manual_review_required", "failed", "skipped_locked_test"]
    text_hash: str
    feature_hash: str
    record_hash: str
