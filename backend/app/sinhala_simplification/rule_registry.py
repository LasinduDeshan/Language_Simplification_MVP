"""
Stage 33 — Rule Registry Loader & Rights Partitioning Boundary.
Separates public rule metadata from restricted rule payloads in external storage.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.sinhala_simplification.enums import GuardType, RuleType
from app.sinhala_simplification.schemas import SimplificationRule
from app.sinhala_simplification.serialization import compute_keyed_hmac
from app.sinhala_simplification.storage import get_protected_storage_root

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PUBLIC_REGISTRY_PATH = PROJECT_ROOT / "data" / "sinhala_simplification" / "registry" / "rule_registry_public.json"


class GovernedRuleDefinition:
    """
    Combined in-memory representation of a rule with its public metadata
    and externally stored protected payload.
    """
    def __init__(self, metadata: SimplificationRule, source_pattern: str, target_template: str):
        self.metadata = metadata
        self.source_pattern = source_pattern
        self.target_template = target_template

    @property
    def rule_id(self) -> str:
        return self.metadata.rule_id

    @property
    def rule_version(self) -> int:
        return self.metadata.rule_version

    @property
    def rule_type(self) -> RuleType:
        return self.metadata.rule_type

    @property
    def priority(self) -> int:
        return self.metadata.priority

    @property
    def required_guards(self) -> List[GuardType]:
        return self.metadata.required_guards


class RuleRegistry:
    """
    Rule registry loader enforcing field-level rights partitioning.
    """
    def __init__(self, public_registry_path: Optional[Path] = None):
        self.public_path = public_registry_path or PUBLIC_REGISTRY_PATH
        self._rules: Dict[str, GovernedRuleDefinition] = {}

    def load_registry(self) -> Dict[str, GovernedRuleDefinition]:
        """Loads and validates public rule metadata joined with external protected payloads."""
        if not self.public_path.exists():
            raise FileNotFoundError(f"Public rule registry not found: {self.public_path}")

        with open(self.public_path, "r", encoding="utf-8") as f:
            public_rules_data = json.load(f)

        # Load protected payloads from external protected storage
        protected_root = get_protected_storage_root()
        payload_file = protected_root / "rules" / "rule_payloads_protected.json"
        if not payload_file.exists():
            raise FileNotFoundError(f"Protected rule payload file not found: {payload_file}")

        with open(payload_file, "r", encoding="utf-8") as f:
            protected_payloads = json.load(f)

        loaded: Dict[str, GovernedRuleDefinition] = {}
        for r_data in public_rules_data:
            meta = SimplificationRule(**r_data)
            rid = meta.rule_id

            if rid in loaded:
                raise ValueError(f"Duplicate rule_id detected: {rid}")

            payload = protected_payloads.get(rid)
            if not payload:
                raise ValueError(f"Missing protected payload for rule: {rid}")

            src_pattern = payload["source_pattern"]
            tgt_template = payload["target_template"]

            # Validate HMAC integrity
            expected_src_hmac = compute_keyed_hmac(src_pattern, domain="stage33_rule_source")
            expected_tgt_hmac = compute_keyed_hmac(tgt_template, domain="stage33_rule_target")

            if meta.source_pattern_ref != expected_src_hmac:
                raise ValueError(f"Integrity check failed for rule {rid} source_pattern_ref")
            if meta.target_template_ref != expected_tgt_hmac:
                raise ValueError(f"Integrity check failed for rule {rid} target_template_ref")

            loaded[rid] = GovernedRuleDefinition(meta, src_pattern, tgt_template)

        self._rules = loaded
        return self._rules

    def get_rule(self, rule_id: str) -> Optional[GovernedRuleDefinition]:
        return self._rules.get(rule_id)

    def list_rules(self) -> List[GovernedRuleDefinition]:
        return list(self._rules.values())
