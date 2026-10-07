"""
Stage 21 Sentence Segmenter and Tokenizer Wrappers
"""
from typing import List
from app.nlp_preprocessing.linguistic_analyzer import LinguisticAnalyzer
from app.nlp_preprocessing.schemas import SentenceRecord, TokenRecord

class SentenceSegmenter:
    def __init__(self, analyzer: LinguisticAnalyzer = None):
        self.analyzer = analyzer or LinguisticAnalyzer()

    def segment(self, normalized_text: str, original_text: str, offset_map: List[int], record_id: str) -> List[SentenceRecord]:
        return self.analyzer.analyze(normalized_text, original_text, offset_map, record_id)

class Tokenizer:
    def __init__(self, analyzer: LinguisticAnalyzer = None):
        self.analyzer = analyzer or LinguisticAnalyzer()

    def tokenize_sentence(self, sentence_record: SentenceRecord) -> List[TokenRecord]:
        return sentence_record.tokens
