"""
JSONL parser for AI4Bharat IndicCorp Sinhala corpus.
"""

import json
from typing import List
from app.datasets.sinhala_external.parsers.base import BaseFormatParser, ParsedDocumentItem

class IndicCorpJsonlParser(BaseFormatParser):
    parser_name = "indiccorp_jsonl_parser"
    parser_version = "1.0.0"

    def parse(self, raw_bytes: bytes, source_id: str) -> List[ParsedDocumentItem]:
        lines = raw_bytes.decode("utf-8").splitlines()
        items = []

        for idx, line in enumerate(lines):
            line_str = line.strip()
            if not line_str:
                continue

            try:
                obj = json.loads(line_str)
                native_id = obj.get("id") or f"indic_{idx:05d}"
                text = obj.get("text", "").strip()
            except Exception:
                continue

            if not text:
                continue

            items.append(ParsedDocumentItem(
                source_native_key=str(native_id),
                source_offset_or_locator=f"line_idx:{idx:05d}",
                raw_text=text,
                document_group_id=f"GRP-INDIC-{native_id}",
                provisional_domain="informational_provisional",
                authoring_origin="human_authored_claimed"
            ))

        return items
