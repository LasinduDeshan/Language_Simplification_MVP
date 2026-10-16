"""
Stage 33 — Rule Registry & Policy Generator.
Generates:
1. data/sinhala_simplification/registry/rule_registry_public.json (opaque metadata)
2. data/sinhala_simplification/registry/protected_span_policy.json
3. data/sinhala_simplification/registry/ranking_precedence.json
4. External protected payloads: $SINHALA_SIMPLIFICATION_PROTECTED_ROOT/rules/rule_payloads_protected.json
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.sinhala_simplification.enums import (
    AuthoringMethod,
    GuardType,
    RuleStatus,
    RuleType,
)
from app.sinhala_simplification.schemas import SimplificationRule
from app.sinhala_simplification.serialization import compute_keyed_hmac
from app.sinhala_simplification.storage import get_protected_storage_root

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_DIR = PROJECT_ROOT / "data" / "sinhala_simplification" / "registry"

RULES_DEFINITIONS = [
    {
        "rule_id": "SI-PHR-SUB-0001",
        "rule_version": 1,
        "rule_type": RuleType.PHRASE_SUBSTITUTION,
        "priority": 150,
        "source_pattern": "මේ හේතුවෙන්",
        "target_template": "මේ නිසා",
        "evidence_type": "empirical_pilot_concordance",
        "evidence_refs": ["SI-LEX-000675", "SI-LEX-000681"],
        "rights_profile_refs": ["SRC-SI-001-RP-01"],
        "required_guards": [GuardType.ENTITY_PRESERVATION, GuardType.NEGATION_PRESERVATION]
    },
    {
        "rule_id": "SI-PHR-SUB-0002",
        "rule_version": 1,
        "rule_type": RuleType.PHRASE_SUBSTITUTION,
        "priority": 140,
        "source_pattern": "ක්‍රියාත්මක කරනු ලබයි",
        "target_template": "කරයි",
        "evidence_type": "empirical_pilot_concordance",
        "evidence_refs": ["SI-LEX-000164", "SI-LEX-000216"],
        "rights_profile_refs": ["SRC-SI-001-RP-01"],
        "required_guards": [GuardType.ENTITY_PRESERVATION, GuardType.NEGATION_PRESERVATION]
    },
    {
        "rule_id": "SI-LEX-SUB-0001",
        "rule_version": 1,
        "rule_type": RuleType.LEXICAL_SUBSTITUTION,
        "priority": 100,
        "source_pattern": "පිළිබඳව",
        "target_template": "ගැන",
        "evidence_type": "empirical_pilot_concordance",
        "evidence_refs": ["SI-LEX-000550", "SI-LEX-000185"],
        "rights_profile_refs": ["SRC-SI-001-RP-01"],
        "required_guards": [GuardType.ENTITY_PRESERVATION, GuardType.NEGATION_PRESERVATION]
    },
    {
        "rule_id": "SI-LEX-SUB-0002",
        "rule_version": 1,
        "rule_type": RuleType.LEXICAL_SUBSTITUTION,
        "priority": 90,
        "source_pattern": "තවදුරටත්",
        "target_template": "තවත්",
        "evidence_type": "empirical_pilot_concordance",
        "evidence_refs": ["SI-LEX-000326", "SI-LEX-000325"],
        "rights_profile_refs": ["SRC-SI-001-RP-01"],
        "required_guards": [GuardType.ENTITY_PRESERVATION, GuardType.NEGATION_PRESERVATION]
    },
    {
        "rule_id": "SI-LEX-SUB-0003",
        "rule_version": 1,
        "rule_type": RuleType.LEXICAL_SUBSTITUTION,
        "priority": 80,
        "source_pattern": "නිරීක්ෂණය",
        "target_template": "බැලීම",
        "evidence_type": "empirical_pilot_concordance",
        "evidence_refs": ["SI-LEX-000427"],
        "rights_profile_refs": ["SRC-SI-001-RP-01"],
        "required_guards": [GuardType.ENTITY_PRESERVATION, GuardType.NEGATION_PRESERVATION]
    },
    {
        "rule_id": "SI-SYN-CON-0001",
        "rule_version": 1,
        "rule_type": RuleType.CONSERVATIVE_SYNTACTIC,
        "priority": 70,
        "source_pattern": "ඇත්තෙන්ම",
        "target_template": "",
        "evidence_type": "syntactic_discourse_filler_analysis",
        "evidence_refs": ["SI-SYN-FILLER-01"],
        "rights_profile_refs": ["SRC-SI-001-RP-01"],
        "required_guards": [GuardType.ENTITY_PRESERVATION, GuardType.NEGATION_PRESERVATION]
    },
    {
        "rule_id": "SI-SNT-SPL-0002",
        "rule_version": 1,
        "rule_type": RuleType.SENTENCE_SPLIT,
        "priority": 60,
        "source_pattern": "නමුත්",
        "target_template": ". ",
        "evidence_type": "syntactic_coordination_split_analysis",
        "evidence_refs": ["SI-SPLIT-MARKER-02"],
        "rights_profile_refs": ["SRC-SI-001-RP-01"],
        "required_guards": [GuardType.ENTITY_PRESERVATION, GuardType.NEGATION_PRESERVATION, GuardType.NUMBER_PRESERVATION]
    },
    {
        "rule_id": "SI-SNT-SPL-0001",
        "rule_version": 1,
        "rule_type": RuleType.SENTENCE_SPLIT,
        "priority": 50,
        "source_pattern": "සහ",
        "target_template": ". ",
        "evidence_type": "syntactic_coordination_split_analysis",
        "evidence_refs": ["SI-LEX-000908"],
        "rights_profile_refs": ["SRC-SI-001-RP-01"],
        "required_guards": [GuardType.ENTITY_PRESERVATION, GuardType.NEGATION_PRESERVATION, GuardType.NUMBER_PRESERVATION]
    }
]


def generate_registries():
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    protected_root = get_protected_storage_root()
    protected_rules_dir = protected_root / "rules"
    protected_rules_dir.mkdir(parents=True, exist_ok=True)

    public_rules = []
    protected_payloads = {}

    for rd in RULES_DEFINITIONS:
        rid = rd["rule_id"]
        src = rd["source_pattern"]
        tgt = rd["target_template"]

        src_hmac = compute_keyed_hmac(src, domain="stage33_rule_source")
        tgt_hmac = compute_keyed_hmac(tgt, domain="stage33_rule_target")

        rule_meta = SimplificationRule(
            rule_id=rid,
            rule_version=rd["rule_version"],
            rule_type=rd["rule_type"],
            status=RuleStatus.TECHNICAL_DRAFT,
            authoring_method=AuthoringMethod.TECHNICAL_RULE_AUTHORING,
            author_id_or_team="stage33_technical_team",
            evidence_type=rd["evidence_type"],
            evidence_refs=rd["evidence_refs"],
            rights_profile_refs=rd["rights_profile_refs"],
            source_pattern_ref=src_hmac,
            target_template_ref=tgt_hmac,
            priority=rd["priority"],
            applicability_conditions=[],
            blocking_conditions=[],
            required_guards=rd["required_guards"],
            expert_validated=False,
            approved_for_child_delivery=False
        )

        public_rules.append(rule_meta.model_dump(mode="json"))
        protected_payloads[rid] = {
            "rule_id": rid,
            "source_pattern": src,
            "target_template": tgt
        }

    # Write public rule registry
    pub_file = REGISTRY_DIR / "rule_registry_public.json"
    with open(pub_file, "w", encoding="utf-8") as f:
        json.dump(public_rules, f, indent=2, ensure_ascii=False)

    # Write external protected rule payloads
    prot_file = protected_rules_dir / "rule_payloads_protected.json"
    with open(prot_file, "w", encoding="utf-8") as f:
        json.dump(protected_payloads, f, indent=2, ensure_ascii=False)

    # Write protected span policy
    span_policy = {
        "policy_id": "SI-PROT-POLICY-V1",
        "stage": "stage33",
        "description": "Governed protected span categories requiring inviolable preservation",
        "categories": [
            "NAMED_ENTITY", "NUMBER_NUMERIC", "DATE_TIME", "UNIT_MEASUREMENT",
            "CURRENCY", "NEGATION_MARKER", "MODALITY_CONDITION", "QUOTATION_DIRECT_SPEECH",
            "IDENTIFIER_CODE_URL", "PARENTHETICAL_REFERENCE", "MIXED_SCRIPT_TERM",
            "STAGE32_REVIEW_REQUIRED_VOCABULARY"
        ],
        "incompleteness_acknowledgment": True
    }
    with open(REGISTRY_DIR / "protected_span_policy.json", "w", encoding="utf-8") as f:
        json.dump(span_policy, f, indent=2, ensure_ascii=False)

    # Write ranking precedence definition
    ranking_policy = {
        "precedence_order": [
            "LONGEST_APPROVED_PHRASE_MATCH",
            "HIGHER_RULE_PRIORITY",
            "FEWER_TRANSFORMATIONS",
            "LOWER_EDIT_DISTANCE",
            "STABLE_RULE_ID_ORDER"
        ],
        "blocked_candidates_participate_in_ranking": False
    }
    with open(REGISTRY_DIR / "ranking_precedence.json", "w", encoding="utf-8") as f:
        json.dump(ranking_policy, f, indent=2, ensure_ascii=False)

    print(f"Public rule registry generated at: {pub_file} ({len(public_rules)} rules)")
    print(f"Protected rule payloads generated at: {prot_file}")


if __name__ == "__main__":
    generate_registries()
