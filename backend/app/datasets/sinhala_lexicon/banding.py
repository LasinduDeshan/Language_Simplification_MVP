"""
Provisional Vocabulary Banding Engine for Stage 32 Sinhala Lexicon.
Assigns technical review bands with explicit rule evidence, confidence scores,
tie-break governance, and calibration isolation.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.datasets.sinhala_lexicon.enums import (
    ProvisionalVocabularyBand,
    TerminalEntryDisposition
)
from app.datasets.sinhala_lexicon.schemas import CandidateLexiconEntry

class ProvisionalBandingEngine:
    """Evaluates multi-dimensional criteria and assigns provisional review bands."""

    def __init__(self, config_path: Optional[Path] = None):
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        self.config_file = config_path or (repo_root / "data" / "sinhala_lexicon" / "registry" / "stage32_configuration.json")
        self.config_data = self._load_or_create_config()
        self.configuration_sha256 = self._compute_config_hash()

    def _load_or_create_config(self) -> dict:
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)

        # Default frozen configuration
        config = {
            "configuration_version": "1.0.0",
            "stage": "stage32",
            "calibration_protocol": {
                "predeclared_subset": "TRAIN_ONLY_SPLIT_GROUPS",
                "random_seed": 42,
                "forbidden_splits": ["validation", "locked_test"],
                "group_selection_algorithm": "deterministic_train_hash_modulo_v1"
            },
            "banding_thresholds": {
                "foundational": {
                    "min_canonical_frequency": 15,
                    "min_source_dispersion": 0.50,
                    "max_grapheme_count": 5
                },
                "early": {
                    "min_canonical_frequency": 8,
                    "max_canonical_frequency": 14,
                    "min_source_dispersion": 0.40,
                    "max_grapheme_count": 7
                },
                "developing": {
                    "min_canonical_frequency": 3,
                    "max_canonical_frequency": 7,
                    "max_grapheme_count": 10
                },
                "advanced": {
                    "max_canonical_frequency": 2,
                    "min_syllable_proxy": 4
                }
            },
            "tie_break_policy": "ROUTE_TO_REVIEW_REQUIRED"
        }
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return config

    def _compute_config_hash(self) -> str:
        data_str = json.dumps(self.config_data, sort_keys=True)
        return hashlib.sha256(data_str.encode("utf-8")).hexdigest()

    def assign_provisional_band(
        self,
        entry: CandidateLexiconEntry
    ) -> Tuple[ProvisionalVocabularyBand, float, List[str]]:
        """
        Assigns provisional technical band based on frozen multi-dimensional thresholds.
        Returns:
            (provisional_band, band_confidence, band_evidence_list)
        """
        # 1. Non-lexical or manual review dispositions
        if entry.terminal_entry_disposition == TerminalEntryDisposition.EXCLUDED_NON_LEXICAL:
            return ProvisionalVocabularyBand.EXCLUDED_NON_LEXICAL, 1.0, ["excluded_non_lexical_disposition"]
        if entry.terminal_entry_disposition == TerminalEntryDisposition.MANUAL_REVIEW_REQUIRED:
            return ProvisionalVocabularyBand.REVIEW_REQUIRED, 0.90, ["manual_review_disposition_flag"]

        if entry.quality_flags:
            return ProvisionalVocabularyBand.REVIEW_REQUIRED, 0.85, [f"quality_flag:{q}" for q in entry.quality_flags]

        # Criteria metrics
        fc = entry.canonical_frequency
        ds = entry.source_dispersion
        g = entry.grapheme_count
        sp = entry.syllable_proxy_count or 1

        th = self.config_data["banding_thresholds"]
        matching_rules: List[Tuple[ProvisionalVocabularyBand, float, List[str]]] = []

        # Rule 1: Foundational Candidate
        f_th = th["foundational"]
        if fc >= f_th["min_canonical_frequency"] and ds >= f_th["min_source_dispersion"] and g <= f_th["max_grapheme_count"]:
            matching_rules.append((
                ProvisionalVocabularyBand.FOUNDATIONAL_CANDIDATE,
                0.90,
                ["high_canonical_frequency", "wide_source_dispersion", "low_grapheme_complexity"]
            ))

        # Rule 2: Early Candidate
        e_th = th["early"]
        if e_th["min_canonical_frequency"] <= fc <= e_th["max_canonical_frequency"] and ds >= e_th["min_source_dispersion"] and g <= e_th["max_grapheme_count"]:
            matching_rules.append((
                ProvisionalVocabularyBand.EARLY_CANDIDATE,
                0.85,
                ["moderate_high_canonical_frequency", "adequate_dispersion", "moderate_length"]
            ))

        # Rule 3: Developing Candidate
        d_th = th["developing"]
        if d_th["min_canonical_frequency"] <= fc <= d_th["max_canonical_frequency"] and g <= d_th["max_grapheme_count"]:
            matching_rules.append((
                ProvisionalVocabularyBand.DEVELOPING_CANDIDATE,
                0.80,
                ["moderate_frequency", "standard_length"]
            ))

        # Rule 4: Advanced Candidate
        a_th = th["advanced"]
        if fc <= a_th["max_canonical_frequency"] or sp >= a_th["min_syllable_proxy"]:
            matching_rules.append((
                ProvisionalVocabularyBand.ADVANCED_CANDIDATE,
                0.75,
                ["low_frequency_or_high_syllable_complexity"]
            ))

        # Tie-break governance: if multiple rules match with equal precedence, route to REVIEW_REQUIRED
        if len(matching_rules) == 0:
            return ProvisionalVocabularyBand.REVIEW_REQUIRED, 0.50, ["unmatched_threshold_boundaries"]
        if len(matching_rules) > 1:
            # Check for conflict
            return ProvisionalVocabularyBand.REVIEW_REQUIRED, 0.60, ["multi_rule_precedence_tie"]

        # Exactly one rule matched
        band, conf, evidence = matching_rules[0]
        return band, conf, evidence

    def apply_banding_to_candidates(
        self,
        candidates: List[CandidateLexiconEntry]
    ) -> List[CandidateLexiconEntry]:
        """Applies banding to all candidate entries and updates records."""
        banded = []
        for c in candidates:
            band, conf, ev = self.assign_provisional_band(c)
            updated = c.model_copy(update={
                "provisional_band": band,
                "band_confidence": conf,
                "band_evidence": ev
            })
            banded.append(updated)
        return banded
