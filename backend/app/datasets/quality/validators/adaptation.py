"""Adaptation Test Set quality validator."""
import uuid
import re
from typing import List, Dict, Any
from app.datasets.quality.enums import RuleSeverity, QualityDimension
from app.datasets.quality.schemas import QualityRuleResultV1
from app.datasets.quality.validators.base import BaseValidator
from app.datasets.common.enums import ActivityOwner, PrimaryDomain

ALLOWED_DOMAINS = {"vocabulary", "grammar", "comprehension", "instruction_following"}
ALLOWED_OWNERS = {"component_1", "component_2_ar", "component_3_local", "component_3_language", "component_3"}


class AdaptationValidator(BaseValidator):
    """Validates Adaptation Test Set activities for alignment, ownership, distractors, monotonicity, and AR integrity."""

    validator_name = "adaptation_validator"
    validator_version = "1.0.0"

    def validate(self, record: Dict[str, Any], run_id: str = "adhoc_run") -> List[QualityRuleResultV1]:
        results: List[QualityRuleResultV1] = []
        record_id = record.get("activity_id", "UNKNOWN_ACTIVITY")
        dataset_layer = "adaptation_test_set"

        # 1. ADAPT-OWNER-001: Ownership boundary check
        owner = record.get("activity_owner")
        owner_passed = owner in ALLOWED_OWNERS or any(o.value == owner for o in ActivityOwner)
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="ADAPT-OWNER-001",
            validator_name=self.validator_name,
            dimension=QualityDimension.METADATA_INTEGRITY,
            severity=RuleSeverity.ERROR,
            passed=owner_passed,
            threshold="valid_activity_owner",
            message=f"Activity owner is '{owner}'." if owner_passed else f"Invalid activity owner '{owner}'.",
            recommended_action=None if owner_passed else "Assign valid owner (component_1, component_2_ar, or component_3_local)."
        ))

        # 2. ADAPT-DOM-002: Domain classification check
        domain = record.get("primary_domain")
        domain_passed = domain in ALLOWED_DOMAINS or any(d.value == domain for d in PrimaryDomain)
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="ADAPT-DOM-002",
            validator_name=self.validator_name,
            dimension=QualityDimension.METADATA_INTEGRITY,
            severity=RuleSeverity.ERROR,
            passed=domain_passed,
            threshold="valid_4_domains",
            message=f"Primary domain is '{domain}'." if domain_passed else f"Invalid domain '{domain}'. Must be vocabulary, grammar, comprehension, or instruction_following.",
            recommended_action=None if domain_passed else "Reclassify activity into one of the 4 approved educational domains."
        ))

        # 3. ADAPT-ALIGN-003: Instruction and expected answer alignment
        protected = record.get("protected", {})
        expected_ans = str(protected.get("answer") or protected.get("protected_answer", "")).strip().lower()
        instruction = str(record.get("child_friendly_instruction") or record.get("original_instruction") or record.get("instruction", "")).strip()
        
        align_passed = bool(expected_ans and instruction)
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="ADAPT-ALIGN-003",
            validator_name=self.validator_name,
            dimension=QualityDimension.SAFETY_ANSWER_BOUNDARY,
            severity=RuleSeverity.ERROR,
            passed=align_passed,
            threshold="non_empty_instruction_and_answer",
            message="Instruction and protected answer are both populated." if align_passed else "Missing instruction or protected answer.",
            recommended_action=None if align_passed else "Ensure both instruction and protected answer are clearly defined."
        ))

        # 4. ADAPT-DIST-004: Distractor validity check
        distractors = record.get("distractors") or protected.get("distractors", [])
        acceptable = protected.get("acceptable_answers", [])
        
        distractor_collision = False
        collided_distractors = []
        if isinstance(distractors, list) and expected_ans:
            for d in distractors:
                d_clean = str(d).strip().lower()
                if d_clean == expected_ans or (isinstance(acceptable, list) and d_clean in [str(a).strip().lower() for a in acceptable]):
                    distractor_collision = True
                    collided_distractors.append(d)

        dist_passed = not distractor_collision
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="ADAPT-DIST-004",
            validator_name=self.validator_name,
            dimension=QualityDimension.SAFETY_ANSWER_BOUNDARY,
            severity=RuleSeverity.ERROR,
            passed=dist_passed,
            threshold="no_answer_distractor_overlap",
            message="Distractors are distinct from correct answer." if dist_passed else f"Distractor collision detected: {collided_distractors} matches correct answer.",
            recommended_action=None if dist_passed else "Replace distractors that accidentally duplicate the correct answer."
        ))

        # 5. ADAPT-MONO-005: Support progression monotonicity check
        mild_text = str(record.get("mild_scaffold", "") or record.get("instruction", ""))
        strong_text = str(record.get("strong_scaffold", "") or record.get("instruction", ""))
        
        # Word count proxy: strong support instruction should not be substantially longer than mild
        mild_words = len(mild_text.split())
        strong_words = len(strong_text.split())
        
        # If strong support is > 2.0x length of mild, flag warning
        mono_passed = not (strong_words > mild_words * 2.5 and strong_words > 25)
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="ADAPT-MONO-005",
            validator_name=self.validator_name,
            dimension=QualityDimension.SIMPLICITY_IMPROVEMENT,
            severity=RuleSeverity.WARNING,
            passed=mono_passed,
            threshold="strong_words <= 2.5x mild_words",
            message="Support tier word progression is balanced." if mono_passed else f"Strong support is excessively lengthy ({strong_words} words vs mild {mild_words} words).",
            recommended_action=None if mono_passed else "Simplify and condense strong support scaffolding."
        ))

        # 6. ADAPT-AR-006: AR integrity check
        is_ar = record.get("activity_owner") == "component_2_ar" or "ar" in record_id.lower() or "ar_assets" in record
        ar_passed = True
        if is_ar and "ar_assets" in record:
            assets = record["ar_assets"]
            if not isinstance(assets, (list, dict)):
                ar_passed = False

        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="ADAPT-AR-006",
            validator_name=self.validator_name,
            dimension=QualityDimension.METADATA_INTEGRITY,
            severity=RuleSeverity.ERROR,
            passed=ar_passed,
            threshold="valid_ar_asset_schema",
            message="AR integrity contract satisfied." if ar_passed else "Malformed AR asset metadata.",
            recommended_action=None if ar_passed else "Ensure AR assets conform to Component 2 contract."
        ))

        # 7. ADAPT-ENG-008: English language consistency check
        # Check for non-ASCII or mixed scripts in English MVP
        non_ascii = [c for c in instruction if ord(c) > 127 and c not in "“”‘’—–•"]
        eng_passed = len(non_ascii) == 0
        results.append(QualityRuleResultV1(
            result_id=f"RES-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            record_id=record_id,
            dataset_layer=dataset_layer,
            rule_id="ADAPT-ENG-008",
            validator_name=self.validator_name,
            dimension=QualityDimension.GRAMMAR_FLUENCY,
            severity=RuleSeverity.ERROR,
            passed=eng_passed,
            threshold="english_ascii_clean",
            message="Instruction text is clean English." if eng_passed else f"Unintended non-English characters detected: {non_ascii[:5]}.",
            recommended_action=None if eng_passed else "Remove unintended non-English characters."
        ))

        return results
