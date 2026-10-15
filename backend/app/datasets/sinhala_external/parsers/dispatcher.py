"""
Parser dispatcher for Stage 31 format parsing and document staging.
Enforces method-development predeclaration status, blocks METADATA_ONLY sources,
and writes raw text exclusively to external protected storage.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from app.datasets.sinhala_external.schemas import (
    ParsingStatus,
    StagedDocumentRecord,
)
from app.datasets.sinhala_external.storage import ProtectedStorageManager, storage_manager
from app.datasets.sinhala_external.parsers.base import BaseFormatParser
from app.datasets.sinhala_external.parsers.wikipedia_xml import WikipediaXmlParser
from app.datasets.sinhala_external.parsers.indiccorp_jsonl import IndicCorpJsonlParser
from app.datasets.sinhala_external.parsers.flores_tsv import FloresTsvParser
from app.datasets.sinhala_external.parsers.news_txt import NewsTxtParser
from app.datasets.sinhala_external.parsers.storyweaver_json import StoryWeaverJsonParser

class DocumentStagingDispatcher:
    """Dispatches raw payload parsing and stores staged documents with abstract URIs."""

    def __init__(
        self,
        predeclaration_path: Path,
        storage: ProtectedStorageManager = storage_manager
    ):
        self.predeclaration_path = predeclaration_path
        self.storage = storage
        self.parsers: Dict[str, BaseFormatParser] = {
            "SRC-SI-001": WikipediaXmlParser(),
            "SRC-SI-002": IndicCorpJsonlParser(),
            "SRC-SI-003": FloresTsvParser(),
            "SRC-SI-004": NewsTxtParser(),
            "SRC-SI-008": StoryWeaverJsonParser(),
        }
        self.dev_ranges: Dict[str, tuple[int, int]] = self._load_predeclarations()

    def _load_predeclarations(self) -> Dict[str, tuple[int, int]]:
        data = json.loads(self.predeclaration_path.read_text(encoding="utf-8"))
        res = {}
        for s in data.get("sources", []):
            src_id = s["source_id"]
            rng = s["method_development_unit_range"]
            res[src_id] = (rng[0], rng[1])
        return res

    def parse_payload(
        self,
        source_id: str,
        retrieval_id: str,
        rights_profile_id: str,
        rights_profile_version: int,
        raw_file_sha256: str,
        raw_bytes: bytes,
        start_doc_seq: int = 1
    ) -> List[StagedDocumentRecord]:
        # Critical Invariant 22: METADATA_ONLY sources must never enter text parsing
        if source_id == "SRC-SI-006":
            raise PermissionError("METADATA_ONLY source SRC-SI-006 is barred from text preprocessing pipelines")

        parser = self.parsers.get(source_id)
        if not parser:
            raise ValueError(f"No registered parser for source {source_id}")

        parsed_items = parser.parse(raw_bytes, source_id)
        staged_records = []
        dev_range = self.dev_ranges.get(source_id, (-1, -1))

        for idx, item in enumerate(parsed_items):
            doc_seq = start_doc_seq + idx
            doc_id = f"DOC-SI-{doc_seq:06d}"
            
            # Check if this index was predeclared for method development
            is_dev = (dev_range[0] <= idx <= dev_range[1])

            # Write document text to external protected storage
            doc_filename = f"doc_{doc_id}.txt"
            target_path, storage_ref = self.storage.write_raw_file(
                source_id=source_id,
                retrieval_id=retrieval_id,
                filename=doc_filename,
                data=item.raw_text.encode("utf-8")
            )

            record = StagedDocumentRecord(
                document_id=doc_id,
                source_id=source_id,
                retrieval_id=retrieval_id,
                rights_profile_id=rights_profile_id,
                rights_profile_version=rights_profile_version,
                raw_file_sha256=raw_file_sha256,
                source_document_key=item.source_native_key,
                document_group_id=item.document_group_id,
                source_offset_or_locator=item.source_offset_or_locator,
                authoring_origin=item.authoring_origin,
                is_method_development_unit=is_dev,
                provisional_domain=item.provisional_domain,
                parsing_status=ParsingStatus.PARSED,
                raw_text_storage_ref=storage_ref
            )
            staged_records.append(record)

        return staged_records
