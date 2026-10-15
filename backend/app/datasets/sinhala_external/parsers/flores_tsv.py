"""
TSV parser for FLORES-200 Sinhala benchmark evaluation splits.
"""

from typing import List
from app.datasets.sinhala_external.parsers.base import BaseFormatParser, ParsedDocumentItem

class FloresTsvParser(BaseFormatParser):
    parser_name = "flores_tsv_parser"
    parser_version = "1.0.0"

    def parse(self, raw_bytes: bytes, source_id: str) -> List[ParsedDocumentItem]:
        lines = raw_bytes.decode("utf-8").splitlines()
        items = []

        start_row = 0
        if lines and ("\t" in lines[0]) and ("sentence_id" in lines[0] or "text" in lines[0]):
            start_row = 1

        for idx in range(start_row, len(lines)):
            line = lines[idx].strip()
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) >= 2:
                sentence_id = parts[0].strip()
                text = parts[1].strip()
            else:
                sentence_id = str(idx)
                text = parts[0].strip()

            if not text:
                continue

            items.append(ParsedDocumentItem(
                source_native_key=f"flores_{sentence_id}",
                source_offset_or_locator=f"row_idx:{idx:05d}",
                raw_text=text,
                document_group_id=f"GRP-FLORES-{sentence_id}",
                provisional_domain="benchmark_reference_provisional",
                authoring_origin="human_authored_claimed"
            ))

        return items
