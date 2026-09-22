import os
import json
from typing import Optional, List
from app.integrations.component2_ar.interface import Component2ARInterface
from app.integrations.component2_ar.schemas import Component2AROutputSchema
from app.integrations.common.statuses import STATUS_NOT_CONNECTED

class Component2ARMockAdapter(Component2ARInterface):
    """
    Mock adapter that generates AR preview payloads and saves them locally under data/integration_previews/component2_ar_outputs/
    """
    def __init__(self, previews_dir: Optional[str] = None):
        if previews_dir is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
            previews_dir = os.path.join(base_dir, "data", "integration_previews", "component2_ar_outputs")
        self.previews_dir = previews_dir
        os.makedirs(self.previews_dir, exist_ok=True)

    def generate_ar_payload(
        self,
        task_code: str,
        instruction: str,
        support_level: str = "moderate",
        steps: Optional[List[str]] = None,
        vocabulary_targets: Optional[List[dict]] = None
    ) -> Component2AROutputSchema:
        if steps is None or len(steps) == 0:
            # Create default sequential steps from instruction
            steps = [f"Step 1: {instruction}"]

        vocab_support = []
        if vocabulary_targets:
            for vt in vocabulary_targets:
                if isinstance(vt, dict):
                    vocab_support.append(vt)
                elif isinstance(vt, str):
                    vocab_support.append({"word": vt, "cue": f"Look for {vt}"})

        payload = Component2AROutputSchema(
            schema_version="1.0",
            task_id=task_code,
            language="en",
            instruction=instruction,
            support_level=support_level,
            steps=steps,
            vocabulary_support=vocab_support,
            audio_text=instruction,
            validation_status="approved",
            delivery_status=STATUS_NOT_CONNECTED,
            is_simulated=True,
            environment="development",
            research_eligible=False
        )

        # Save to previews folder
        output_file = os.path.join(self.previews_dir, f"{task_code}_ar_preview.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(payload.model_dump(), f, indent=2)

        return payload
