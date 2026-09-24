"""Researcher-only API endpoints for Stage 15 Dataset Quality Validation."""
import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.datasets.quality.enums import ValidationRunStatus
from app.datasets.quality.models import ValidationRun, QualityRuleResult, RecordQualitySummary, ManualReviewQueueEntry
from app.datasets.quality.schemas import (
    ValidationRunCreateRequestV1,
    ValidationRunResponseV1,
    TriageDecisionRequestV1,
    RecordCorrectionRequestV1
)
from app.datasets.quality.orchestrator import QualityOrchestrator
from app.datasets.quality.review_queue import ReviewQueueManager
from app.datasets.quality.correction_service import CorrectionService

router = APIRouter(prefix="/datasets/quality", tags=["Dataset Quality Validation"])


def verify_researcher_access(x_user_role: Optional[str] = Header(None)):
    """Guards quality endpoints against unauthorized or child-facing access."""
    if x_user_role and x_user_role.lower() in ("child", "learner", "student"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Quality validation endpoints are strictly restricted from child/learner access."
        )
    return True


@router.post("/validate", response_model=ValidationRunResponseV1, status_code=status.HTTP_202_ACCEPTED)
async def trigger_validation_run(
    request: ValidationRunCreateRequestV1,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    x_idempotency_key: Optional[str] = Header(None),
    _: bool = Depends(verify_researcher_access)
):
    """
    Triggers an asynchronous quality validation run across governed datasets.
    Returns HTTP 202 Accepted immediately.
    """
    orchestrator = QualityOrchestrator(db=db)
    run = orchestrator.create_run(
        request=request,
        idempotency_key=x_idempotency_key,
        created_by="researcher_api"
    )

    if run.status == ValidationRunStatus.QUEUED.value:
        # Schedule async background task
        background_tasks.add_task(
            orchestrator.execute_validation_run,
            run_id=run.run_id,
            enable_nlp=request.enable_nlp,
            enable_llm_review=request.enable_llm_review
        )

    return ValidationRunResponseV1(
        run_id=run.run_id,
        status=ValidationRunStatus(run.status),
        message="Validation run queued successfully.",
        created_at=run.created_at
    )


@router.get("/runs/{run_id}")
def get_validation_run(
    run_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_researcher_access)
):
    """Retrieves execution status, metrics, and accounting for a validation run."""
    run = db.query(ValidationRun).filter(ValidationRun.run_id == run_id).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Validation run '{run_id}' not found.")

    return {
        "run_id": run.run_id,
        "dataset_layer": run.dataset_layer,
        "dataset_version": run.dataset_version,
        "quality_rule_set_version": run.quality_rule_set_version,
        "status": run.status,
        "total_records": run.total_records,
        "passed_count": run.passed_count,
        "failed_count": run.failed_count,
        "review_required_count": run.review_required_count,
        "quarantined_count": run.quarantined_count,
        "created_at": run.created_at,
        "completed_at": run.completed_at,
        "error_message": run.error_message
    }


@router.get("/runs/{run_id}/results")
def get_run_results(
    run_id: str,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
    _: bool = Depends(verify_researcher_access)
):
    """Retrieves paginated rule execution results for a run."""
    results = db.query(QualityRuleResult).filter(QualityRuleResult.run_id == run_id).offset(skip).limit(limit).all()
    return [
        {
            "result_id": r.result_id,
            "record_id": r.record_id,
            "dataset_layer": r.dataset_layer,
            "rule_id": r.rule_id,
            "validator_name": r.validator_name,
            "severity": r.severity,
            "passed": r.passed,
            "message": r.message,
            "recommended_action": r.recommended_action
        }
        for r in results
    ]


@router.get("/review-queue")
def list_review_queue(
    dataset_layer: Optional[str] = None,
    priority: Optional[str] = None,
    review_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_researcher_access)
):
    """Retrieves paginated manual review queue items with optional filters."""
    entries = ReviewQueueManager.get_entries(
        db=db,
        dataset_layer=dataset_layer,
        priority=priority,
        status=review_status,
        skip=skip,
        limit=limit
    )
    return [
        {
            "entry_id": e.entry_id,
            "run_id": e.run_id,
            "record_id": e.record_id,
            "dataset_layer": e.dataset_layer,
            "priority": e.priority,
            "triggering_rule_ids": e.triggering_rule_ids,
            "summary": e.summary,
            "review_status": e.review_status,
            "assigned_reviewer_id": e.assigned_reviewer_id,
            "created_at": e.created_at
        }
        for e in entries
    ]


@router.post("/review-queue/{entry_id}/decision")
def apply_review_decision(
    entry_id: str,
    request: TriageDecisionRequestV1,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_researcher_access)
):
    """
    Applies a Stage 15 triage decision to a review queue entry.
    Strictly forbids 'approved' or 'expert_reviewed' actions.
    """
    try:
        updated_entry = ReviewQueueManager.apply_triage_decision(
            db=db,
            entry_id=entry_id,
            request=request
        )
        return {
            "entry_id": updated_entry.entry_id,
            "review_status": updated_entry.review_status,
            "assigned_reviewer_id": updated_entry.assigned_reviewer_id,
            "resolution_notes": updated_entry.resolution_notes,
            "resolved_at": updated_entry.resolved_at
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
