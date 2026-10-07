"""Optional Gemini LLM review adapter for advisory linguistic evaluation."""
import os
import json
import logging
from typing import Dict, Any, Optional
from app.datasets.quality.schemas import LLMReviewResponseV1
from app.datasets.quality.llm_review.interface import AbstractLLMReviewAdapter

logger = logging.getLogger(__name__)


class GeminiLLMReviewAdapter(AbstractLLMReviewAdapter):
    """Optional advisory adapter using Gemini for semantic evaluation behind a feature flag."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        self.prompt_version = "1.0.0"

    async def evaluate_pair(self, original_text: str, simplified_text: str, context: Optional[Dict[str, Any]] = None) -> Optional[LLMReviewResponseV1]:
        # Privacy guarantee: Never process interaction exports or sensitive records
        if context and context.get("dataset_layer") == "interaction_exports":
            return None

        if not self.api_key:
            logger.info("Gemini API key not configured; skipping advisory LLM review.")
            return None

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            
            prompt = (
                f"Evaluate this original and simplified English text pair for children aged 4-8.\n"
                f"Original: {original_text}\n"
                f"Simplified: {simplified_text}\n\n"
                f"Respond ONLY in valid JSON with these fields:\n"
                f"{{\n"
                f'  "meaning_preserved": true/false,\n'
                f'  "meaning_confidence": 0.0-1.0,\n'
                f'  "age_appropriate": true/false,\n'
                f'  "naturalness_score": 0.0-1.0,\n'
                f'  "identified_issues": ["list of issues if any"],\n'
                f'  "suggested_review_notes": "optional note"\n'
                f"}}"
            )

            # Avoid logging raw prompt/text content for privacy
            response = await model.generate_content_async(prompt)
            raw_text = response.text.strip()
            
            # Clean possible markdown json fences
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            
            data = json.loads(raw_text.strip())
            return LLMReviewResponseV1(
                meaning_preserved=bool(data.get("meaning_preserved", True)),
                meaning_confidence=float(data.get("meaning_confidence", 0.9)),
                age_appropriate=bool(data.get("age_appropriate", True)),
                naturalness_score=float(data.get("naturalness_score", 0.9)),
                identified_issues=list(data.get("identified_issues", [])),
                suggested_review_notes=data.get("suggested_review_notes")
            )
        except Exception as e:
            logger.warning(f"Advisory LLM evaluation failed safely: {e}")
            return None
