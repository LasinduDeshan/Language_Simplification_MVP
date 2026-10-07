"""
Stage 21 Preprocessing Cache & Multi-Tier Content Hashing Module
"""
import hashlib
import json
import os
from typing import Dict, Any, Optional

class PreprocessingCache:
    def __init__(self, cache_dir: str = None, enabled: bool = True):
        self.enabled = enabled
        self.cache_dir = cache_dir
        if self.enabled and self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)

    @staticmethod
    def compute_sha256(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get_text_hash(self, normalized_text: str) -> str:
        return self.compute_sha256(normalized_text)

    def get_feature_hash(self, features_dict: Dict[str, Any]) -> str:
        canonical_json = json.dumps(features_dict, sort_keys=True)
        return self.compute_sha256(canonical_json)

    def get_record_hash(self, feature_hash: str, parent_id: str, text_role: str, split: str, pipeline_version: str) -> str:
        composite = f"{feature_hash}:{parent_id}:{text_role}:{split}:{pipeline_version}"
        return self.compute_sha256(composite)

    def get_processing_cache_key(
        self,
        normalized_text: str,
        language: str,
        pipeline_version: str,
        config_hash: str,
        model_hash: str,
        lexicon_version: str
    ) -> str:
        composite = f"{normalized_text}:{language}:{pipeline_version}:{config_hash}:{model_hash}:{lexicon_version}"
        return self.compute_sha256(composite)

    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        if not self.enabled or not self.cache_dir:
            return None
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def set(self, cache_key: str, payload: Dict[str, Any]):
        if not self.enabled or not self.cache_dir:
            return
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception:
            pass
