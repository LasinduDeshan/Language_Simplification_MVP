"""
Shared spaCy model manager with singleton caching for Stage 25 controlled simplification.
"""

import spacy
from typing import Optional


class SpacyPipelineManager:
    """
    Manages loaded spaCy pipeline instances to avoid re-loading weights on every call.
    """
    _instance = None
    _nlp = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpacyPipelineManager, cls).__new__(cls)
            try:
                cls._nlp = spacy.load("en_core_web_sm")
            except Exception:
                try:
                    cls._nlp = spacy.load("en_core_web_md")
                except Exception:
                    cls._nlp = spacy.blank("en")
        return cls._instance

    def get_doc(self, text: str):
        """Parse text and return spaCy Doc."""
        return self._nlp(text)

    @property
    def nlp(self):
        return self._nlp
