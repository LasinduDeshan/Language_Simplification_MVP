"""
MediaWiki XML dump parser for Sinhala Wikipedia.
"""

import re
import xml.etree.ElementTree as ET
from typing import List
from app.datasets.sinhala_external.parsers.base import BaseFormatParser, ParsedDocumentItem

class WikipediaXmlParser(BaseFormatParser):
    parser_name = "wikipedia_xml_parser"
    parser_version = "1.0.0"

    def clean_wikitext(self, raw_text: str) -> str:
        # Strip comments
        text = re.sub(r'<!--.*?-->', '', raw_text, flags=re.DOTALL)
        # Strip templates {{...}}
        text = re.sub(r'\{\{.*?\}\}', '', text, flags=re.DOTALL)
        # Strip headings == Heading ==
        text = re.sub(r'=+([^=]+)=+', r'\1', text)
        # Strip links [[target|label]] -> label, [[target]] -> target
        text = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', text)
        # Strip ref tags <ref...>...</ref> or <ref.../>
        text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL)
        text = re.sub(r'<ref[^>]*/>', '', text)
        # Collapse multiple spaces/newlines
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        return text

    def parse(self, raw_bytes: bytes, source_id: str) -> List[ParsedDocumentItem]:
        root = ET.fromstring(raw_bytes)
        items = []
        
        # Find all page elements (handling optional xml namespaces)
        for idx, page in enumerate(root.iter()):
            if page.tag.endswith("page"):
                page_id = page.findtext("{*}id") or page.findtext("id") or str(idx + 1)
                title = page.findtext("{*}title") or page.findtext("title") or f"Article_{idx + 1}"
                
                # Extract text inside revision
                text_elem = page.find(".//{*}text")
                if text_elem is None:
                    text_elem = page.find(".//text")
                
                raw_body = text_elem.text if text_elem is not None and text_elem.text else ""
                cleaned = self.clean_wikitext(raw_body)
                
                if not cleaned:
                    continue

                items.append(ParsedDocumentItem(
                    source_native_key=f"wiki_page_{page_id}",
                    source_offset_or_locator=f"page_id:{page_id}:seq:{idx:04d}",
                    raw_text=cleaned,
                    document_group_id=f"GRP-WIKI-{page_id}",
                    provisional_domain="encyclopedic_provisional",
                    authoring_origin="human_authored_claimed",
                    title=title
                ))

        return items
