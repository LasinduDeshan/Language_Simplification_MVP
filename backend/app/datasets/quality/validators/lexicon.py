"""Lexicon repository quality validator."""
import uuid
from typing import List, Dict, Any
from app.datasets.quality.enums import RuleSeverity, QualityDimension
from app.datasets.quality.schemas import QualityRuleResultV1
from app.datasets.quality.validators.base import BaseValidator


class LexiconValidator(BaseValidator):
    """Validates Lexicon entries for headword uniqueness, circularity, POS, senses, and explanations."""

    validator_name = "lexicon_validator"
    validator_version = "1.0.0"

    def validate(self, record: Dict[str, Any], run_id: str = "adhoc_run") -> List[QualityRuleResultV1]:
        results: List[QualityRuleResultV1] = []
        entry_id = record.get("entry_id", "UNKNOWN_LEXICON_ENTRY")
        headword = str(record.get("word") or record.get("normalized_form") or record.get("headword", "")).strip().lower()
        dataset_layer = "lexicons"

        # 1. LEX-HEAD-001: Non-empty normalized headword
        head_passed = bool(headword and headword.isalpha())
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=entry_id,
            dataset_layer=dataset_layer,
            rule_id="LEX-HEAD-001",
            validator_name=self.validator_name,
            dimension=QualityDimension.METADATA_INTEGRITY,
            severity=RuleSeverity.ERROR,
            passed=head_passed,
            threshold="non_empty_alphabetic_headword",
            message=f"Headword '{headword}' is valid." if head_passed else f"Invalid headword '{headword}'.",
            recommended_action=None if head_passed else "Provide a valid, alphabetic English headword."
        ))

        # 2. LEX-EXP-003: Child-friendly explanation check
        explanation = str(
            record.get("child_friendly_definition") or
            record.get("child_friendly_explanation") or
            record.get("explanation", "")
        ).strip()
        exp_passed = len(explanation) >= 5
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=entry_id,
            dataset_layer=dataset_layer,
            rule_id="LEX-EXP-003",
            validator_name=self.validator_name,
            dimension=QualityDimension.AGE_APPROPRIATENESS,
            severity=RuleSeverity.ERROR,
            passed=exp_passed,
            threshold="len(explanation) >= 5",
            message="Child-friendly explanation is present." if exp_passed else "Missing or inadequate child explanation.",
            recommended_action=None if exp_passed else "Provide a clear, simple explanation for children aged 4-8."
        ))

        # 3. LEX-CIRC-002: Circular replacement check (headword != replacement)
        simpler_alts = record.get("simpler_alternatives", [])
        if isinstance(simpler_alts, list) and simpler_alts:
            simplified_rep = str(simpler_alts[0]).strip().lower()
        else:
            simplified_rep = str(record.get("simplified_replacement", "") or record.get("replacement", "")).strip().lower()

        is_explanation_only = record.get("is_explanation_only", False) or not bool(simplified_rep)
        
        circ_passed = True
        if not is_explanation_only and simplified_rep:
            if simplified_rep == headword:
                circ_passed = False

        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=entry_id,
            dataset_layer=dataset_layer,
            rule_id="LEX-CIRC-002",
            validator_name=self.validator_name,
            dimension=QualityDimension.SIMPLICITY_IMPROVEMENT,
            severity=RuleSeverity.ERROR,
            passed=circ_passed,
            threshold="headword != replacement",
            message="No self-replacement circularity detected." if circ_passed else f"Self-circular replacement: '{headword}' -> '{simplified_rep}'.",
            recommended_action=None if circ_passed else "Provide a simpler synonym or mark entry as explanation-only."
        ))

        # 4. LEX-POS-004: Part of speech presence & validity
        pos = record.get("part_of_speech")
        pos_passed = pos in ("noun", "verb", "adjective", "adverb", "preposition", "conjunction", "pronoun", None)
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=entry_id,
            dataset_layer=dataset_layer,
            rule_id="LEX-POS-004",
            validator_name=self.validator_name,
            dimension=QualityDimension.GRAMMAR_FLUENCY,
            severity=RuleSeverity.WARNING,
            passed=pos_passed,
            threshold="valid_pos_tag",
            message=f"Part of speech '{pos}' is valid." if pos_passed else f"Unknown part of speech '{pos}'.",
            recommended_action=None if pos_passed else "Assign a recognized part of speech."
        ))

        # 5. LEX-EXSENT-006: Example sentence validation
        ex_sentence = str(record.get("example_sentence", "")).strip()
        has_ex = len(ex_sentence) > 5
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=entry_id,
            dataset_layer=dataset_layer,
            rule_id="LEX-EXSENT-006",
            validator_name=self.validator_name,
            dimension=QualityDimension.AGE_APPROPRIATENESS,
            severity=RuleSeverity.WARNING,
            passed=has_ex,
            threshold="len(example_sentence) > 5",
            message="Example sentence is provided." if has_ex else "No example sentence provided.",
            recommended_action=None if has_ex else "Add a simple example sentence illustrating usage."
        ))

        # 6. LEX-COMP-007: Lexical complexity proxy
        # Replacement word length should not exceed headword length by > 4 characters
        comp_passed = True
        if not is_explanation_only and simplified_rep:
            if len(simplified_rep) > len(headword) + 4:
                comp_passed = False

        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=entry_id,
            dataset_layer=dataset_layer,
            rule_id="LEX-COMP-007",
            validator_name=self.validator_name,
            dimension=QualityDimension.SIMPLICITY_IMPROVEMENT,
            severity=RuleSeverity.WARNING,
            passed=comp_passed,
            threshold="len(replacement) <= len(headword) + 4",
            message="Replacement complexity proxy is satisfactory." if comp_passed else f"Replacement '{simplified_rep}' appears longer/more complex than headword '{headword}'.",
            recommended_action=None if comp_passed else "Choose a simpler replacement term."
        ))

        return results
