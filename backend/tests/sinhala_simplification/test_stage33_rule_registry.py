"""
Stage 33 — Unit Tests for Rule Registry & Authorship Governance.
"""

import pytest
from app.sinhala_simplification.enums import AuthoringMethod, RuleStatus
from app.sinhala_simplification.rule_registry import RuleRegistry


def test_rule_registry_loading():
    registry = RuleRegistry()
    rules = registry.load_registry()
    assert len(rules) == 8, f"Expected 8 registered rules, got {len(rules)}"

    # Verify all rules have valid attributes
    for rid, rule in rules.items():
        assert rule.rule_id == rid
        assert rule.rule_version >= 1
        assert rule.metadata.status == RuleStatus.TECHNICAL_DRAFT
        assert rule.metadata.authoring_method == AuthoringMethod.TECHNICAL_RULE_AUTHORING
        assert rule.metadata.author_id_or_team == "stage33_technical_team"
        assert len(rule.metadata.evidence_refs) > 0
        assert len(rule.metadata.rights_profile_refs) > 0
        assert rule.source_pattern != ""
        assert rule.metadata.expert_validated is False
        assert rule.metadata.approved_for_child_delivery is False


def test_rule_registry_unique_ids():
    registry = RuleRegistry()
    rules = registry.load_registry()
    rule_ids = [r.rule_id for r in rules.values()]
    assert len(rule_ids) == len(set(rule_ids)), "Rule IDs must be strictly unique"
