"""
StoryWeaver JSON parser for open educational graded narrative stories.
"""

import json
from typing import List
from app.datasets.sinhala_external.parsers.base import BaseFormatParser, ParsedDocumentItem

class StoryWeaverJsonParser(BaseFormatParser):
    parser_name = "storyweaver_json_parser"
    parser_version = "1.0.0"

    def parse(self, raw_bytes: bytes, source_id: str) -> List[ParsedDocumentItem]:
        data = json.loads(raw_bytes.decode("utf-8"))
        stories = data.get("stories", [])
        items = []

        for idx, story in enumerate(stories):
            story_id = story.get("story_id") or f"SW-{idx + 1:04d}"
            title = story.get("title")
            content = story.get("content", "").strip()

            if not content:
                continue

            items.append(ParsedDocumentItem(
                source_native_key=str(story_id),
                source_offset_or_locator=f"story_idx:{idx + 1:04d}",
                raw_text=content,
                document_group_id=f"GRP-STORY-{story_id}",
                provisional_domain="educational_narrative_provisional",
                authoring_origin="human_authored_claimed",
                title=title
            ))

        return items
