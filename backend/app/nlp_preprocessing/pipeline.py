"""
Stage 21 NLP Preprocessing Pipeline Master Coordinator
"""
import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from app.nlp_preprocessing.config import PreprocessingConfig
from app.nlp_preprocessing.version import PIPELINE_VERSION, SCHEMA_VERSION, SOURCE_DATASET_VERSION, MODEL_METADATA
from app.nlp_preprocessing.schemas import (
    TextInstance,
    PreprocessedRecord,
    LanguageVerificationRecord
)
from app.nlp_preprocessing.normalizer import UnicodeNormalizer
from app.nlp_preprocessing.cleaner import ConservativeCleaner
from app.nlp_preprocessing.language_verifier import LanguageVerifier
from app.nlp_preprocessing.linguistic_analyzer import LinguisticAnalyzer
from app.nlp_preprocessing.feature_extractor import FeatureExtractor
from app.nlp_preprocessing.fallback import DeterministicFallbackPipeline
from app.nlp_preprocessing.cache import PreprocessingCache

class NLPPreprocessingPipeline:
    def __init__(self, config: PreprocessingConfig = None, cache_dir: str = None, internal_lexicon_words: set = None):
        self.config = config or PreprocessingConfig()
        self.normalizer = UnicodeNormalizer(
            form=self.config.normalization_form,
            allow_nfkc_diagnostic=self.config.allow_nfkc_diagnostic
        )
        self.cleaner = ConservativeCleaner()
        self.language_verifier = LanguageVerifier(
            confidence_threshold=self.config.language_confidence_threshold
        )
        self.analyzer = LinguisticAnalyzer(spacy_model_name=MODEL_METADATA["spacy_model_name"])
        self.feature_extractor = FeatureExtractor(
            long_word_char_threshold=self.config.long_word_char_threshold,
            internal_lexicon_words=internal_lexicon_words or set()
        )
        self.fallback = DeterministicFallbackPipeline()
        self.cache = PreprocessingCache(cache_dir=cache_dir, enabled=self.config.cache_enabled)

    def process_text_instance(self, instance: TextInstance) -> PreprocessedRecord:
        # 1. Locked Test Guard
        if instance.dataset_split == "development_candidate_test" and not self.config.allow_locked_test:
            # Skip locked test record
            dummy_lang = LanguageVerificationRecord(
                verification_engine="deterministic_heuristic",
                model_version="heuristic_v1",
                confidence=1.0,
                decision="verified",
                fallback_reason="skipped_locked_test"
            )
            # Create minimal empty linguistic feature set via fallback
            _, dummy_feats = self.fallback.process("", [], instance.text_instance_id)
            return PreprocessedRecord(
                text_instance_id=instance.text_instance_id,
                parent_record_id=instance.parent_record_id,
                parent_record_type=instance.parent_record_type,
                text_role=instance.text_role,
                source_dataset_version=SOURCE_DATASET_VERSION,
                pipeline_version=PIPELINE_VERSION,
                schema_version=SCHEMA_VERSION,
                language="en",
                dataset_split=instance.dataset_split,
                source_group_id=instance.source_group_id,
                original_text="[LOCKED_TEST_PROTECTED]",
                normalized_text="[LOCKED_TEST_PROTECTED]",
                language_verification=dummy_lang,
                sentences=[],
                features=dummy_feats,
                processing_status="skipped_locked_test",
                text_hash="LOCKED_TEST_HASH",
                feature_hash="LOCKED_FEATURE_HASH",
                record_hash="LOCKED_RECORD_HASH"
            )

        # 2. Cleaning & Normalization
        cleaned_text, clean_audit = self.cleaner.clean(instance.text)
        normalized_text, offset_map = self.normalizer.normalize(cleaned_text)
        
        text_hash = self.cache.get_text_hash(normalized_text)
        config_hash = self.cache.compute_sha256(self.config.model_dump_json())
        cache_key = self.cache.get_processing_cache_key(
            normalized_text=normalized_text,
            language=instance.language,
            pipeline_version=PIPELINE_VERSION,
            config_hash=config_hash,
            model_hash=MODEL_METADATA["spacy_model_hash"],
            lexicon_version=MODEL_METADATA["lexicon_version"]
        )

        # Check Cache
        cached = self.cache.get(cache_key)
        if cached:
            # Reconstruct record with parent instance metadata
            cached["text_instance_id"] = instance.text_instance_id
            cached["parent_record_id"] = instance.parent_record_id
            cached["parent_record_type"] = instance.parent_record_type
            cached["text_role"] = instance.text_role
            cached["dataset_split"] = instance.dataset_split
            cached["source_group_id"] = instance.source_group_id
            return PreprocessedRecord(**cached)

        # 3. Language Verification
        lang_ver = self.language_verifier.verify_language(normalized_text)

        # 4. Sentence & Token Analysis (spaCy Primary or Fallback)
        status = "success"
        try:
            sentences = self.analyzer.analyze(
                normalized_text=normalized_text,
                original_text=instance.text,
                offset_map=offset_map,
                record_id=instance.text_instance_id
            )
            features = self.feature_extractor.extract_features(
                sentences=sentences,
                protected_meaning_units=instance.protected_meaning_units
            )
            if lang_ver.decision == "manual_review_required":
                status = "manual_review_required"
        except Exception as e:
            if self.config.enable_fallback:
                sentences, features = self.fallback.process(
                    normalized_text=normalized_text,
                    offset_map=offset_map,
                    record_id=instance.text_instance_id,
                    protected_meaning_units=instance.protected_meaning_units
                )
                status = "fallback_success"
            else:
                raise e

        feat_dict = features.model_dump()
        feature_hash = self.cache.get_feature_hash(feat_dict)
        record_hash = self.cache.get_record_hash(
            feature_hash=feature_hash,
            parent_id=instance.parent_record_id,
            text_role=instance.text_role,
            split=instance.dataset_split,
            pipeline_version=PIPELINE_VERSION
        )

        preprocessed_rec = PreprocessedRecord(
            text_instance_id=instance.text_instance_id,
            parent_record_id=instance.parent_record_id,
            parent_record_type=instance.parent_record_type,
            text_role=instance.text_role,
            source_dataset_version=SOURCE_DATASET_VERSION,
            pipeline_version=PIPELINE_VERSION,
            schema_version=SCHEMA_VERSION,
            language="en",
            dataset_split=instance.dataset_split,
            source_group_id=instance.source_group_id,
            original_text=instance.text,
            normalized_text=normalized_text,
            language_verification=lang_ver,
            sentences=sentences,
            features=features,
            processing_status=status,
            text_hash=text_hash,
            feature_hash=feature_hash,
            record_hash=record_hash
        )

        # Store in cache
        self.cache.set(cache_key, preprocessed_rec.model_dump())
        return preprocessed_rec

    def process_batch(self, instances: List[TextInstance]) -> List[PreprocessedRecord]:
        results = []
        for inst in instances:
            try:
                rec = self.process_text_instance(inst)
                results.append(rec)
            except Exception as e:
                # Isolate record-level failures
                dummy_lang = LanguageVerificationRecord(
                    verification_engine="deterministic_heuristic",
                    model_version="heuristic_v1",
                    confidence=0.0,
                    decision="rejected",
                    fallback_reason=f"unhandled_exception: {e}"
                )
                _, dummy_feats = self.fallback.process("", [], inst.text_instance_id)
                failed_rec = PreprocessedRecord(
                    text_instance_id=inst.text_instance_id,
                    parent_record_id=inst.parent_record_id,
                    parent_record_type=inst.parent_record_type,
                    text_role=inst.text_role,
                    source_dataset_version=SOURCE_DATASET_VERSION,
                    pipeline_version=PIPELINE_VERSION,
                    schema_version=SCHEMA_VERSION,
                    language="en",
                    dataset_split=inst.dataset_split,
                    source_group_id=inst.source_group_id,
                    original_text=inst.text,
                    normalized_text=inst.text,
                    language_verification=dummy_lang,
                    sentences=[],
                    features=dummy_feats,
                    processing_status="failed",
                    text_hash="FAILED_HASH",
                    feature_hash="FAILED_HASH",
                    record_hash="FAILED_HASH"
                )
                results.append(failed_rec)
        return results
