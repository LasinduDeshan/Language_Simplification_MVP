"""Quality validation orchestrator coordinating dataset loaders, registry, DB persistence, and accounting."""
import asyncio
import uuid
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.datasets.quality.enums import QualityStatus, RuleSeverity, ValidationRunStatus, ReviewPriority
from app.datasets.quality.models import ValidationRun, QualityRuleResult, RecordQualitySummary, ManualReviewQueueEntry
from app.datasets.quality.schemas import ValidationRunCreateRequestV1, ValidationRunManifestV1, QualityScoreBreakdownV1
from app.datasets.quality.registry import QualityValidatorRegistry
from app.datasets.quality.scoring import QualityScorer
from app.datasets.quality.reporting import QualityReportGenerator
from app.datasets.adaptation_test_set.repository import AdaptationTestSetRepository
from app.datasets.simplification_corpus.repository import SimplificationCorpusRepository
from app.datasets.lexicons.schemas import LexiconEntryV1
from app.datasets.common.paths import (
    ADAPTATION_RELEASE_DIR,
    SIMPLIFICATION_RELEASE_DIR,
    LEXICONS_RELEASE_DIR
)
import json
import os

# Concurrency lock for validation runs
_VALIDATION_LOCK = asyncio.Lock()


class QualityOrchestrator:
    """Orchestrates quality validation sessions across governed datasets."""

    def __init__(self, db: Session, base_path: str = ""):
        self.db = db
        self.base_path = base_path
        self.registry = QualityValidatorRegistry()

    def create_run(
        self,
        request: ValidationRunCreateRequestV1,
        idempotency_key: Optional[str] = None,
        created_by: str = "researcher_api"
    ) -> ValidationRun:
        """Initializes a persistent ValidationRun record."""
        # Check idempotency
        if idempotency_key:
            existing = self.db.query(ValidationRun).filter(ValidationRun.idempotency_key == idempotency_key).first()
            if existing:
                return existing

        run_id = f"VAL-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
        run = ValidationRun(
            run_id=run_id,
            dataset_layer=request.dataset_layer,
            dataset_version=request.dataset_version,
            quality_rule_set_version=request.quality_rule_set_version,
            status=ValidationRunStatus.QUEUED.value,
            idempotency_key=idempotency_key,
            created_by=created_by,
            created_at=datetime.datetime.utcnow()
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def load_dataset_records(self, dataset_layer: str) -> Dict[str, List[Dict[str, Any]]]:
        """Loads records from canonical governed repositories."""
        layer_records: Dict[str, List[Dict[str, Any]]] = {}

        # 1. Adaptation Test Set
        if dataset_layer in ("all", "adaptation_test_set"):
            adapt_file = os.path.join(self.base_path, ADAPTATION_RELEASE_DIR, "0.1.0", "adaptation_test_set.json")
            if os.path.exists(adapt_file):
                with open(adapt_file, "r", encoding="utf-8") as f:
                    layer_records["adaptation_test_set"] = json.load(f)
            else:
                # Fallback to repository
                adapt_repo = AdaptationTestSetRepository()
                layer_records["adaptation_test_set"] = [
                    a.model_dump(mode="json") if hasattr(a, "model_dump") else (a.to_dict() if hasattr(a, "to_dict") else dict(a))
                    for a in adapt_repo.get_all_activities()
                ]

        # 2. Simplification Corpus
        if dataset_layer in ("all", "simplification_corpus"):
            simp_file = os.path.join(self.base_path, SIMPLIFICATION_RELEASE_DIR, "0.1.0", "simplification_corpus.json")
            if os.path.exists(simp_file):
                with open(simp_file, "r", encoding="utf-8") as f:
                    layer_records["simplification_corpus"] = json.load(f)
            else:
                simp_repo = SimplificationCorpusRepository()
                layer_records["simplification_corpus"] = [
                    p.model_dump(mode="json") if hasattr(p, "model_dump") else (p.to_dict() if hasattr(p, "to_dict") else dict(p))
                    for p in simp_repo.list_all_pairs()
                ]

        # 3. Lexicons
        if dataset_layer in ("all", "lexicons"):
            lex_file = os.path.join(self.base_path, LEXICONS_RELEASE_DIR, "0.1.0", "lexicon_repository.json")
            if os.path.exists(lex_file):
                with open(lex_file, "r", encoding="utf-8") as f:
                    layer_records["lexicons"] = json.load(f)
            else:
                layer_records["lexicons"] = []

        return layer_records

    async def execute_validation_run(
        self,
        run_id: str,
        enable_nlp: bool = True,
        enable_llm_review: bool = False
    ) -> ValidationRun:
        """Executes full validation pass with concurrency locking and atomic persistence."""
        async with _VALIDATION_LOCK:
            run = self.db.query(ValidationRun).filter(ValidationRun.run_id == run_id).first()
            if not run:
                raise ValueError(f"Run '{run_id}' not found.")

            run.status = ValidationRunStatus.RUNNING.value
            self.db.commit()

            try:
                datasets_to_validate = self.load_dataset_records(run.dataset_layer)
                all_summaries: List[RecordQualitySummary] = []
                all_results: List[QualityRuleResult] = []
                all_review_entries: List[ManualReviewQueueEntry] = []

                total_records = 0
                passed_count = 0
                failed_count = 0
                review_required_count = 0
                quarantined_count = 0

                for layer_name, records in datasets_to_validate.items():
                    for rec in records:
                        total_records += 1
                        rec_id = rec.get("activity_id") or rec.get("pair_id") or rec.get("entry_id") or rec.get("record_id") or f"REC-{uuid.uuid4().hex[:8]}"
                        
                        # Execute rules
                        rule_results_dto = self.registry.validate_record(
                            record=rec,
                            dataset_layer=layer_name,
                            run_id=run_id,
                            enable_nlp=enable_nlp
                        )

                        # Calculate dimension scores
                        breakdown_dto, overall_score = QualityScorer.calculate_scores(rule_results_dto)
                        status, warn_c, err_c, crit_c = QualityScorer.resolve_status(rule_results_dto, overall_score)

                        # Increment accounting disposition counters
                        if status == QualityStatus.AUTOMATIC_CHECK_PASSED:
                            passed_count += 1
                        elif status == QualityStatus.AUTOMATIC_CHECK_FAILED:
                            failed_count += 1
                        elif status == QualityStatus.MANUAL_REVIEW_REQUIRED:
                            review_required_count += 1
                        elif status == QualityStatus.QUARANTINED:
                            quarantined_count += 1

                        # Persist QualityRuleResults
                        for r_dto in rule_results_dto:
                            db_res = QualityRuleResult(
                                result_id=r_dto.result_id,
                                run_id=run_id,
                                record_id=rec_id,
                                dataset_layer=layer_name,
                                rule_id=r_dto.rule_id,
                                rule_version=r_dto.rule_version,
                                validator_name=r_dto.validator_name,
                                validator_version=r_dto.validator_version,
                                severity=r_dto.severity.value if hasattr(r_dto.severity, "value") else str(r_dto.severity),
                                passed=r_dto.passed,
                                score=r_dto.score,
                                threshold=r_dto.threshold,
                                message=r_dto.message,
                                recommended_action=r_dto.recommended_action,
                                details=r_dto.details,
                                validated_at=datetime.datetime.utcnow()
                            )
                            self.db.add(db_res)
                            all_results.append(db_res)

                        # Persist RecordQualitySummary
                        db_sum = RecordQualitySummary(
                            summary_id=f"SUM-{uuid.uuid4().hex[:12]}",
                            run_id=run_id,
                            record_id=rec_id,
                            dataset_layer=layer_name,
                            schema_version="1.0.0",
                            quality_rule_set_version="1.0.0",
                            quality_status=status.value if hasattr(status, "value") else str(status),
                            overall_quality_score=overall_score,
                            dimension_scores=breakdown_dto.model_dump() if hasattr(breakdown_dto, "model_dump") else dict(breakdown_dto),
                            rules_executed=len(rule_results_dto),
                            rules_passed=sum(1 for r in rule_results_dto if r.passed),
                            warnings_count=warn_c,
                            errors_count=err_c,
                            critical_count=crit_c,
                            requires_expert_review=True,
                            research_eligible=False,
                            approved_for_child_delivery=False,
                            validated_at=datetime.datetime.utcnow()
                        )
                        self.db.add(db_sum)
                        all_summaries.append(db_sum)

                        # Create Review Queue Entry if failed, warning, or quarantined
                        if status in (QualityStatus.AUTOMATIC_CHECK_FAILED, QualityStatus.MANUAL_REVIEW_REQUIRED, QualityStatus.QUARANTINED):
                            priority = ReviewPriority.MEDIUM
                            if status == QualityStatus.QUARANTINED:
                                priority = ReviewPriority.URGENT
                            elif status == QualityStatus.AUTOMATIC_CHECK_FAILED:
                                priority = ReviewPriority.HIGH

                            trigger_rules = [r.rule_id for r in rule_results_dto if not r.passed]
                            summary_text = f"Quality status {status.value}: {len(trigger_rules)} failed rule(s)."
                            
                            db_entry = ManualReviewQueueEntry(
                                entry_id=f"REV-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}",
                                run_id=run_id,
                                record_id=rec_id,
                                dataset_layer=layer_name,
                                priority=priority.value if hasattr(priority, "value") else str(priority),
                                triggering_rule_ids=trigger_rules,
                                summary=summary_text,
                                recommended_review_type="linguistic_triage",
                                review_status="pending",
                                created_at=datetime.datetime.utcnow()
                            )
                            self.db.add(db_entry)
                            all_review_entries.append(db_entry)

                # Update Run totals
                run.total_records = total_records
                run.passed_count = passed_count
                run.failed_count = failed_count
                run.review_required_count = review_required_count
                run.quarantined_count = quarantined_count
                run.status = ValidationRunStatus.COMPLETED.value
                run.completed_at = datetime.datetime.utcnow()

                self.db.commit()
                self.db.refresh(run)

                # Generate public and private export reports
                QualityReportGenerator.generate_reports(
                    run=run,
                    summaries=all_summaries,
                    results=all_results,
                    review_entries=all_review_entries,
                    base_dir=self.base_path
                )

                return run

            except Exception as e:
                self.db.rollback()
                run = self.db.query(ValidationRun).filter(ValidationRun.run_id == run_id).first()
                if run:
                    run.status = ValidationRunStatus.FAILED.value
                    run.error_message = str(e)
                    run.completed_at = datetime.datetime.utcnow()
                    self.db.commit()
                raise e
