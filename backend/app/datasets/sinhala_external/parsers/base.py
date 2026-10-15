"""
Base parser interface and data structures for Stage 31 format parsers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class ParsedDocumentItem:
    """Represents a single parsed document extracted from raw source bytes."""
    source_native_key: str
    source_offset_or_locator: str
    raw_text: str
    document_group_id: str
    provisional_domain: str = "unclassified_provisional"
    authoring_origin: str = "human_authored_claimed"
    title: Optional[str] = None

class BaseFormatParser(ABC):
    """Abstract base class for all deterministic source format parsers."""
    parser_name: str = "base_parser"
    parser_version: str = "1.0.0"

    @abstractmethod
    def parse(self, raw_bytes: bytes, source_id: str) -> List[ParsedDocumentItem]:
        """Parses raw bytes into a list of ParsedDocumentItem instances."""
        pass
