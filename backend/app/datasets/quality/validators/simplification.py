"""Simplification Corpus quality validator."""
import uuid
import re
from typing import List, Dict, Any
from app.datasets.quality.enums import RuleSeverity, QualityDimension
from app.datasets.quality.schemas import QualityRuleResultV1
from app.datasets.quality.validators.base import BaseValidator

NEGATION_TOKENS = {"not", "no", "never", "neither", "nor", "none", "nobody", "nowhere", "nothing", "can't", "cannot", "don't", "doesn't", "didn't", "won't", "isn't", "aren't", "wasn't", "weren't"}


def extract_numbers(text: str) -> List[str]:
    """Extracts numeric digits and number words."""
    digits = re.findall(r'\b\d+\b', text)
    word_nums = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"}
    words = [w for w in re.findall(r'\b[a-zA-Z]+\b', text.lower()) if w in word_nums]
    return digits + words


def extract_negations(text: str) -> List[str]:
    """Extracts negation tokens from text."""
    tokens = re.findall(r"\b[a-zA-Z']+\b", text.lower())
    return [t for t in tokens if t in NEGATION_TOKENS]


class SimplificationValidator(BaseValidator):
    """Validates original-simplified text pairs for meaning preservation, negation, numbers, and draft governance."""

    validator_name = "simplification_validator"
    validator_version = "1.0.0"

    def validate(self, record: Dict[str, Any], run_id: str = "adhoc_run") -> List[QualityRuleResultV1]:
        results: List[QualityRuleResultV1] = []
        record_id = record.get("pair_id", "UNKNOWN_PAIR")
        dataset_layer = "simplification_corpus"

        orig_text = str(record.get("original_text", "")).strip()
        simp_text = str(record.get("simplified_text", "")).strip()

        # 1. SIMP-MEAN-001: Meaning Unit & Content Presence
        non_empty = bool(orig_text and simp_text)
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="SIMP-MEAN-001",
            validator_name=self.validator_name,
            dimension=QualityDimension.MEANING_PRESERVATION,
            severity=RuleSeverity.ERROR,
            passed=non_empty,
            threshold="non_empty_texts",
            message="Original and simplified text pairs are present." if non_empty else "Missing original or simplified text.",
            recommended_action=None if non_empty else "Ensure both original and simplified text fields are populated."
        ))

        # 2. SIMP-NEG-002: Negation consistency check
        orig_negs = extract_negations(orig_text)
        simp_negs = extract_negations(simp_text)
        # Check if original had negation but simplified completely lost it, or simplified added new negation
        neg_mismatch = (bool(orig_negs) != bool(simp_negs))
        neg_passed = not neg_mismatch

        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="SIMP-NEG-002",
            validator_name=self.validator_name,
            dimension=QualityDimension.MEANING_PRESERVATION,
            severity=RuleSeverity.ERROR,
            passed=neg_passed,
            threshold="negation_polarity_preserved",
            message="Negation polarity preserved." if neg_passed else f"Negation mismatch: original has {orig_negs}, simplified has {simp_negs}.",
            recommended_action=None if neg_passed else "Restore accurate polarity (negation) in simplified text."
        ))

        # 3. SIMP-NUM-003: Quantity & number preservation check
        orig_nums = sorted(extract_numbers(orig_text))
        simp_nums = sorted(extract_numbers(simp_text))
        num_passed = (orig_nums == simp_nums) or (len(orig_nums) == 0 and len(simp_nums) == 0)

        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="SIMP-NUM-003",
            validator_name=self.validator_name,
            dimension=QualityDimension.MEANING_PRESERVATION,
            severity=RuleSeverity.ERROR,
            passed=num_passed,
            threshold="numbers_preserved",
            message="Quantities and numbers preserved." if num_passed else f"Number divergence: original has {orig_nums}, simplified has {simp_nums}.",
            recommended_action=None if num_passed else "Ensure numbers and quantities are accurately preserved during simplification."
        ))

        # 4. SIMP-COPY-005: Identical copy check
        is_identical = (orig_text.lower() == simp_text.lower()) and len(orig_text.split()) > 4
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="SIMP-COPY-005",
            validator_name=self.validator_name,
            dimension=QualityDimension.SIMPLICITY_IMPROVEMENT,
            severity=RuleSeverity.WARNING,
            passed=not is_identical,
            threshold="simplified != original",
            message="Simplified text differs from original." if not is_identical else "Simplified text is identical to complex original text.",
            recommended_action=None if not is_identical else "Apply simplification operations to reduce complexity."
        ))

        # 5. SIMP-GOV-006: Draft Governance Invariant Check
        validation_status = record.get("validation_status", "draft")
        research_eligible = record.get("research_eligible", False)
        approved_delivery = record.get("approved_for_child_delivery", False)

        gov_passed = (
            validation_status == "draft" and
            research_eligible is False and
            approved_delivery is False
        )

        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="SIMP-GOV-006",
            validator_name=self.validator_name,
            dimension=QualityDimension.METADATA_INTEGRITY,
            severity=RuleSeverity.CRITICAL,
            passed=gov_passed,
            threshold="draft_invariants_locked",
            message="Draft governance invariants strictly locked." if gov_passed else f"Governance invariant violation: status='{validation_status}', research_eligible={research_eligible}, approved_for_child_delivery={approved_delivery}.",
            recommended_action=None if gov_passed else "Enforce draft status and lock research/delivery flags to False."
        ))

        return results
