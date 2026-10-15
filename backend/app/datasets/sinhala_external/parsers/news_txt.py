"""
Plain text / delimited news story parser for UCSC LTRL Sinhala News corpus.
"""

from typing import List
from app.datasets.sinhala_external.parsers.base import BaseFormatParser, ParsedDocumentItem

class NewsTxtParser(BaseFormatParser):
    parser_name = "news_txt_parser"
    parser_version = "1.0.0"

    def parse(self, raw_bytes: bytes, source_id: str) -> List[ParsedDocumentItem]:
        content = raw_bytes.decode("utf-8")
        
        # Split on explicit delimiter '---' or double newlines
        if "\n\n---\n\n" in content:
            stories = content.split("\n\n---\n\n")
        else:
            stories = content.split("\n\n")

        items = []
        for idx, story in enumerate(stories):
            cleaned = story.strip()
            if not cleaned:
                continue

            items.append(ParsedDocumentItem(
                source_native_key=f"ltrl_story_{idx + 1:04d}",
                source_offset_or_locator=f"story_idx:{idx + 1:04d}",
                raw_text=cleaned,
                document_group_id=f"GRP-LTRL-{idx + 1:04d}",
                provisional_domain="news_provisional",
                authoring_origin="human_authored_claimed"
            ))

        return items
