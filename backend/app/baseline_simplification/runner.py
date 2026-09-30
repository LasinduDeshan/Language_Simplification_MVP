"""
Baseline Runner orchestrating evaluations across Internal Release 0.2.0 and ASSET test sets.
"""
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from app.baseline_simplification.schemas import (
    BaselineMethodId,
    BaselineOutputRecord,
    FinalDisposition,
    MeaningValidationStatus,
    ProtectedElementSource,
)
from app.baseline_simplification.registry import BaselineRegistry
from app.baseline_simplification.identity_baseline import IdentityBaseline
from app.baseline_simplification.lexical_baseline import LexicalSubstitutionBaseline
from app.baseline_simplification.sentence_split_baseline import SentenceSplitBaseline
from app.baseline_simplification.syntactic_rule_baseline import SyntacticRuleBaseline
from app.baseline_simplification.combined_baseline import CombinedDeterministicBaseline
from app.baseline_simplification.offline_fallback_adapter import OfflineFallbackAdapter
from app.baseline_simplification.protected_meaning_validator import ProtectedMeaningValidator

class BaselineRunner:
    """Orchestrates evaluation runs across baseline methods and datasets."""

    def __init__(self, registry: Optional[BaselineRegistry] = None):
        self.registry = registry or BaselineRegistry()
        self.baselines = {
            BaselineMethodId.B0: IdentityBaseline(),
            BaselineMethodId.B1: LexicalSubstitutionBaseline(),
            BaselineMethodId.B2: SentenceSplitBaseline(),
            BaselineMethodId.B3: SyntacticRuleBaseline(),
            BaselineMethodId.B4: CombinedDeterministicBaseline(),
            BaselineMethodId.B5: OfflineFallbackAdapter(),
        }
        self.validator = ProtectedMeaningValidator()

    def run_on_items(
        self,
        method_id: BaselineMethodId,
        items: List[Dict[str, Any]],
        dataset_id: str,
        dataset_version: str,
        split: str,
        run_id: str,
        validation_mode: ProtectedElementSource = ProtectedElementSource.AUTOMATED_EXTRACTOR_ONLY,
        target_age_default: int = 6,
    ) -> List[BaselineOutputRecord]:
        """Executes a baseline method on a list of unique source items (1 output per source group)."""
        baseline = self.baselines[method_id]
        config = self.registry.get_configuration(method_id)
        config_hash = config.compute_configuration_hash()
        
        output_records: List[BaselineOutputRecord] = []

        for item in items:
            source_id = item.get("source_item_id") or item.get("source_record_id") or item.get("id") or "SRC-UNKNOWN"
            group_id = item.get("source_group_id") or source_id
            input_text = item.get("source_text") or item.get("text") or item.get("input_text", "")
            target_age = item.get("target_content_age", target_age_default)
            ref_count = len(item.get("reference_texts", [])) or 3

            in_hash = hashlib.sha256(input_text.encode("utf-8")).hexdigest()
            
            start_t = time.perf_counter()
            res = baseline.simplify(
                input_text,
                target_content_age=target_age,
                validation_mode=validation_mode,
                governed_annotations=item.get("governed_annotations"),
            )
            lat_ms = (time.perf_counter() - start_t) * 1000.0

            output_text = res.get("output_text", input_text)
            out_hash = hashlib.sha256(output_text.encode("utf-8")).hexdigest()

            # Determine meaning validation & quality disposition if not returned by baseline directly
            if "meaning_validation_status" in res and "quality_disposition" in res:
                m_status = res["meaning_validation_status"]
                q_disp = res["quality_disposition"]
            else:
                m_status, q_disp, _ = self.validator.validate(
                    input_text, output_text, mode=validation_mode, governed_annotations=item.get("governed_annotations")
                )

            record = BaselineOutputRecord(
                run_id=run_id,
                dataset_id=dataset_id,
                dataset_version=dataset_version,
                schema_version="1.0.0",
                preprocessing_version="1.0.0",
                complexity_analyzer_version="1.0.0",
                evaluation_unit="source_group",
                reference_count=ref_count,
                target_support_level=None,
                uses_learner_profile=False,
                protected_element_source=validation_mode,
                target_content_age=target_age,
                source_record_id=source_id,
                source_group_id=group_id,
                split=split,
                method_id=method_id,
                method_version=config.method_version,
                configuration_version=config.configuration_version,
                configuration_hash=config_hash,
                input_text=input_text,
                output_text=output_text,
                input_hash=in_hash,
                output_hash=out_hash,
                rules_applied=res.get("rules_applied", []),
                operation_outcomes=res.get("operation_outcomes", []),
                generator_method=config.generator_method,
                fallback_used=res.get("fallback_used", False),
                meaning_validation_status=m_status,
                quality_disposition=q_disp,
                metric_eligibility=(q_disp in {FinalDisposition.AUTOMATIC_CHECK_PASSED, FinalDisposition.MANUAL_REVIEW_REQUIRED}),
                metric_exclusion_reason=None if (q_disp in {FinalDisposition.AUTOMATIC_CHECK_PASSED, FinalDisposition.MANUAL_REVIEW_REQUIRED}) else "quality_disposition_failed",
                latency_ms=lat_ms,
                validation_status="draft",
                research_eligible=False,
                approved_for_child_delivery=False,
                requires_expert_review=True,
            )
            output_records.append(record)

        return output_records
