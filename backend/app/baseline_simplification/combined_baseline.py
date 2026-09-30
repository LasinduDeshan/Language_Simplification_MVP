"""
B4: Combined Deterministic Baseline Pipeline.
Executes ordered pipeline (Syntax -> Splitting -> Lexical -> Repair -> Validation) with isolated step rollback.
"""
from typing import Any, Dict, List, Optional, Set
import spacy
from app.baseline_simplification.schemas import (
    BaselineMethodId,
    FinalDisposition,
    MeaningValidationStatus,
    ProtectedElementSource,
)
from app.baseline_simplification.lexical_baseline import LexicalSubstitutionBaseline
from app.baseline_simplification.sentence_split_baseline import SentenceSplitBaseline
from app.baseline_simplification.syntactic_rule_baseline import SyntacticRuleBaseline
from app.baseline_simplification.protected_meaning_validator import ProtectedMeaningValidator
from app.baseline_simplification.output_validator import OutputValidator

class CombinedDeterministicBaseline:
    """Fixed-order deterministic baseline pipeline with isolated operation rollback."""

    def __init__(self, nlp: Optional[Any] = None):
        self.method_id = BaselineMethodId.B4
        self.method_version = "1.0.0"
        
        if nlp is not None:
            self.nlp = nlp
        else:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.nlp = spacy.blank("en")

        self.b1 = LexicalSubstitutionBaseline(nlp=self.nlp)
        self.b2 = SentenceSplitBaseline(nlp=self.nlp)
        self.b3 = SyntacticRuleBaseline(nlp=self.nlp)
        self.meaning_validator = ProtectedMeaningValidator(nlp=self.nlp)
        self.output_validator = OutputValidator(nlp=self.nlp)

    def simplify(
        self,
        text: str,
        target_content_age: Optional[int] = 6,
        validation_mode: ProtectedElementSource = ProtectedElementSource.AUTOMATED_EXTRACTOR_ONLY,
        governed_annotations: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Runs the fixed-order deterministic pipeline with step-level validation and rollback."""
        cleaned = text.strip()
        current_text = cleaned
        rules_applied: List[Dict[str, Any]] = []
        operation_outcomes: List[Dict[str, Any]] = []

        # Step 1: Protected elements extraction
        prot_dict = self.meaning_validator.extract_elements(cleaned)
        prot_tokens = prot_dict["entities"].union(prot_dict["quantities"]).union(prot_dict["colors"])

        # Step 2: Syntactic Rules (B3)
        pre_b3_text = current_text
        res_b3 = self.b3.simplify(current_text)
        if res_b3["rules_applied"]:
            # Check meaning validity after syntax step
            v_status, v_disp, v_issues = self.meaning_validator.validate(
                cleaned, res_b3["output_text"], mode=validation_mode, governed_annotations=governed_annotations
            )
            if v_disp == FinalDisposition.AUTOMATIC_CHECK_FAILED:
                # Rollback B3
                current_text = pre_b3_text
                operation_outcomes.append({
                    "rule_id": "SYN-01-PASSIVE-ACTIVE",
                    "outcome": "reverted",
                    "reason": f"Rollback triggered due to validation failure: {v_issues}",
                })
            else:
                current_text = res_b3["output_text"]
                rules_applied.extend(res_b3["rules_applied"])
                operation_outcomes.extend(res_b3["operation_outcomes"])

        # Step 3: Sentence Splitting (B2)
        pre_b2_text = current_text
        res_b2 = self.b2.simplify(current_text)
        if res_b2["rules_applied"]:
            v_status, v_disp, v_issues = self.meaning_validator.validate(
                cleaned, res_b2["output_text"], mode=validation_mode, governed_annotations=governed_annotations
            )
            if v_disp == FinalDisposition.AUTOMATIC_CHECK_FAILED:
                current_text = pre_b2_text
                operation_outcomes.append({
                    "rule_id": "SPLIT-01-COORD-CONJ",
                    "outcome": "reverted",
                    "reason": f"Rollback triggered: {v_issues}",
                })
            else:
                current_text = res_b2["output_text"]
                rules_applied.extend(res_b2["rules_applied"])
                operation_outcomes.extend(res_b2["operation_outcomes"])

        # Step 4: Lexical Substitution (B1)
        pre_b1_text = current_text
        res_b1 = self.b1.simplify(
            current_text,
            target_content_age=target_content_age,
            protected_tokens=prot_tokens,
        )
        if res_b1["rules_applied"]:
            v_status, v_disp, v_issues = self.meaning_validator.validate(
                cleaned, res_b1["output_text"], mode=validation_mode, governed_annotations=governed_annotations
            )
            if v_disp == FinalDisposition.AUTOMATIC_CHECK_FAILED:
                current_text = pre_b1_text
                operation_outcomes.append({
                    "rule_id": "LEX-02-AGE-TIER-GATE",
                    "outcome": "reverted",
                    "reason": f"Rollback triggered: {v_issues}",
                })
            else:
                current_text = res_b1["output_text"]
                rules_applied.extend(res_b1["rules_applied"])
                operation_outcomes.extend(res_b1["operation_outcomes"])

        # Step 5: Final Repair & Quality Disposition
        final_valid_meaning, final_disp, final_violations = self.meaning_validator.validate(
            cleaned, current_text, mode=validation_mode, governed_annotations=governed_annotations
        )
        is_struct_valid, struct_issues = self.output_validator.validate_text(current_text)

        if not is_struct_valid:
            final_disp = FinalDisposition.AUTOMATIC_CHECK_FAILED
            final_valid_meaning = MeaningValidationStatus.FAILED

        return {
            "output_text": current_text,
            "rules_applied": rules_applied,
            "operation_outcomes": operation_outcomes,
            "meaning_validation_status": final_valid_meaning,
            "quality_disposition": final_disp,
            "violations": final_violations + struct_issues,
            "fallback_used": False,
        }
