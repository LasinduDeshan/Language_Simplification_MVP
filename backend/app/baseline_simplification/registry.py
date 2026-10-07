"""
Baseline Registry manager for Stage 24 English simplification baselines.
"""
from typing import Dict, List, Optional
import csv
from pathlib import Path
from app.baseline_simplification.schemas import (
    BaselineMethodId,
    BaselineConfiguration,
    AgeConfiguration,
)

DEFAULT_CONFIGURATIONS: Dict[BaselineMethodId, BaselineConfiguration] = {
    BaselineMethodId.B0: BaselineConfiguration(
        method_id=BaselineMethodId.B0,
        method_name="Identity Baseline",
        method_version="1.0.0",
        configuration_version="1.0.0",
        generator_method="identity_baseline",
        description="Returns the canonical source text unchanged after standard preprocessing to establish a strict lower-bound reference.",
        ordered_rules=[],
        parameters={},
        required_resources={},
        governance_status="provisional_baseline_only",
    ),
    BaselineMethodId.B1: BaselineConfiguration(
        method_id=BaselineMethodId.B1,
        method_name="Lexical Substitution Baseline",
        method_version="1.0.0",
        configuration_version="1.0.0",
        generator_method="lexical_baseline",
        description="Substitutes complex vocabulary words with child-friendly alternatives using governed English lexicon and developmental age-gating.",
        ordered_rules=["LEX-01-LEMMA-POS-MATCH", "LEX-02-AGE-TIER-GATE", "LEX-03-INFLECTION-REPAIR"],
        age_configuration=AgeConfiguration(
            internal_policy="source_item_target_age",
            asset_policy="fixed_generic_age_band",
            asset_target_age_band="4-8",
            uses_learner_profile=False,
        ),
        parameters={
            "max_substitutions_per_sentence": 5,
            "preserve_capitalization": True,
            "prohibit_cycles": True,
        },
        required_resources={
            "lexicon_repository": "data/simplification_corpus/releases/0.2.0/",
            "spacy_model": "en_core_web_sm",
        },
        governance_status="provisional_baseline_only",
    ),
    BaselineMethodId.B2: BaselineConfiguration(
        method_id=BaselineMethodId.B2,
        method_name="Sentence Splitting Baseline",
        method_version="1.0.0",
        configuration_version="1.0.0",
        generator_method="sentence_split_baseline",
        description="Splits compound sentences at safe coordinating and subordinate conjunctions while preserving discourse order and rejecting fragments.",
        ordered_rules=["SPLIT-01-COORD-CONJ", "SPLIT-02-SUBORD-CLAUSE", "SPLIT-03-FRAGMENT-CHECK"],
        parameters={
            "min_clause_tokens": 3,
            "allow_short_imperatives": True,
            "coordinating_conjunctions": ["and", "but", "so"],
            "subordinating_conjunctions": ["because", "when", "after", "while"],
        },
        required_resources={
            "spacy_model": "en_core_web_sm",
        },
        governance_status="provisional_baseline_only",
    ),
    BaselineMethodId.B3: BaselineConfiguration(
        method_id=BaselineMethodId.B3,
        method_name="Syntactic Rule Baseline",
        method_version="1.0.0",
        configuration_version="1.0.0",
        generator_method="syntactic_rule_baseline",
        description="Applies allowlisted grammatical transformations (passive-to-active with explicit agent, relative clause simplification, nominalization unpacking).",
        ordered_rules=["SYN-01-PASSIVE-ACTIVE", "SYN-02-RELATIVE-APPOSITIVE", "SYN-03-NOMINALIZATION-UNPACK"],
        parameters={
            "require_explicit_agent": True,
            "route_ambiguous_to_review": True,
        },
        required_resources={
            "spacy_model": "en_core_web_sm",
        },
        governance_status="provisional_baseline_only",
    ),
    BaselineMethodId.B4: BaselineConfiguration(
        method_id=BaselineMethodId.B4,
        method_name="Combined Deterministic Baseline",
        method_version="1.0.0",
        configuration_version="1.0.0",
        generator_method="combined_deterministic",
        description="Fixed-order deterministic orchestration (Syntax -> Splitting -> Lexical -> Repair -> Validation) with isolated operation rollback.",
        ordered_rules=[
            "PROT-01-ELEMENT-MASKING",
            "SYN-01-PASSIVE-ACTIVE",
            "SYN-02-RELATIVE-APPOSITIVE",
            "SYN-03-NOMINALIZATION-UNPACK",
            "SPLIT-01-COORD-CONJ",
            "SPLIT-02-SUBORD-CLAUSE",
            "LEX-01-LEMMA-POS-MATCH",
            "LEX-02-AGE-TIER-GATE",
            "REPAIR-01-PUNCT-CASING",
            "VAL-01-PROTECTED-MEANING",
        ],
        parameters={
            "enable_operation_rollback": True,
            "max_pipeline_passes": 1,
        },
        required_resources={
            "lexicon_repository": "data/simplification_corpus/releases/0.2.0/",
            "spacy_model": "en_core_web_sm",
        },
        governance_status="provisional_baseline_only",
    ),
    BaselineMethodId.B5: BaselineConfiguration(
        method_id=BaselineMethodId.B5,
        method_name="Existing Offline Fallback",
        method_version="1.0.0",
        configuration_version="1.0.0",
        generator_method="deterministic_fallback",
        description="Standard offline heuristic fallback comparator without LLM attribution, providing continuity from Stage 23 benchmark results.",
        ordered_rules=["FB-01-RULE-HEURISTIC-EXTRACT"],
        parameters={
            "requested_provider": "deterministic_fallback",
        },
        required_resources={},
        governance_status="provisional_baseline_only",
    ),
}

class BaselineRegistry:
    """Registry maintaining baseline simplification configurations and methods."""

    def __init__(self, configs: Optional[Dict[BaselineMethodId, BaselineConfiguration]] = None):
        self._configs: Dict[BaselineMethodId, BaselineConfiguration] = configs or DEFAULT_CONFIGURATIONS.copy()

    def get_configuration(self, method_id: BaselineMethodId) -> BaselineConfiguration:
        if method_id not in self._configs:
            raise KeyError(f"Method {method_id} not registered in BaselineRegistry")
        return self._configs[method_id]

    def get_configuration_hash(self, method_id: BaselineMethodId) -> str:
        return self.get_configuration(method_id).compute_configuration_hash()

    def list_methods(self) -> List[BaselineConfiguration]:
        return list(self._configs.values())

    def export_to_csv(self, output_csv_path: Path) -> None:
        """Exports the baseline registry to standard CSV documentation format."""
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "method_id",
            "method_name",
            "method_version",
            "configuration_version",
            "configuration_hash",
            "generator_method",
            "ordered_rules",
            "governance_status",
            "description",
        ]
        with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for config in self._configs.values():
                writer.writerow({
                    "method_id": config.method_id.value,
                    "method_name": config.method_name,
                    "method_version": config.method_version,
                    "configuration_version": config.configuration_version,
                    "configuration_hash": config.compute_configuration_hash(),
                    "generator_method": config.generator_method,
                    "ordered_rules": ";".join(config.ordered_rules),
                    "governance_status": config.governance_status,
                    "description": config.description,
                })
