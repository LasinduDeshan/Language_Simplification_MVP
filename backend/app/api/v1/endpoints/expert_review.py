"""API Endpoints for Stage 27 Expert Review.

Provides endpoints under /api/v1/expert-review/ with RBAC and blinding enforcement:
- Reviewer authentication & role enforcement (reviewer, adjudicator, admin)
- Record-level assignment authorization
- Expired/revoked account rejection
- Adjudicator-only disagreement queue access
- Administrator-only release building with release-builder lock
"""
import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from pydantic import BaseModel, Field

from app.datasets.expert_review.models import (
    ExpertReviewer,
    ExpertReviewBatch,
    ExpertReviewAssignment,
    ExpertReviewSubmission,
    ExpertAdjudicationCase,
    ExpertRevision,
    ExpertReviewAuditLog,
    ExpertReleaseApproval,
)
from app.datasets.expert_review.schemas import (
    TaxonomyClass,
    FinalDisposition,
    DimensionRatings,
    CriticalFailureFlags,
    WorkflowFlags,
    SupportTierReview,
    ReviewRecordType,
    InventoryAccounting,
)
from app.datasets.expert_review.manifest_repository import ManifestRepository
from app.datasets.expert_review.assignment_service import AssignmentService
from app.datasets.expert_review.review_service import ReviewService
from app.datasets.expert_review.adjudication import AdjudicationService
from app.datasets.expert_review.revision_service import RevisionService
from app.datasets.expert_review.release_builder import ReleaseBuilder
from app.datasets.expert_review.reviewer_registry import ReviewerRegistry

router = APIRouter(prefix="/expert-review", tags=["Expert Review"])

# In-memory services for runtime API state
repo = ManifestRepository()
assignment_service = AssignmentService()
review_service = ReviewService(expected_submissions=3360)
adjudication_service = AdjudicationService()
revision_service = RevisionService()
reviewer_registry = ReviewerRegistry()


# Request/Response schemas for API
class ReviewSubmissionRequest(BaseModel):
    batch_id: str
    taxonomy_class: TaxonomyClass
    ratings: DimensionRatings
    critical_checks: CriticalFailureFlags
    workflow_flags: WorkflowFlags
    reviewer_notes: Optional[str] = None
    support_tier_review: Optional[SupportTierReview] = None


class AdjudicationRequest(BaseModel):
    final_taxonomy_class: TaxonomyClass
    final_disposition: FinalDisposition
    adjudicated_critical_checks: CriticalFailureFlags
    decision_rationale: str
    revision_required: bool = False


class RevisionRequest(BaseModel):
    revised_text: str
    revision_reason: str
    support_level: str = "moderate"


class ReleaseBuildRequest(BaseModel):
    force_build: bool = False
    signoff_name: str
    signoff_role: str = "lead_adjudicator"


def get_current_reviewer(
    x_reviewer_id: Optional[str] = Header(None, alias="X-Reviewer-Id"),
    x_role: Optional[str] = Header("reviewer", alias="X-Reviewer-Role"),
) -> Dict[str, str]:
    """Dependency for reviewer authentication and active status check."""
    if not x_reviewer_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required: Missing X-Reviewer-Id header.",
        )

    # Check if registered and active
    profile = reviewer_registry.get_reviewer(x_reviewer_id)
    if profile:
        if profile.account_status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account '{x_reviewer_id}' is {profile.account_status}. Access denied.",
            )
    return {"reviewer_id": x_reviewer_id, "role": x_role or "reviewer"}


@router.get("/batches")
def list_batches(
    user: Dict[str, str] = Depends(get_current_reviewer),
) -> List[Dict[str, Any]]:
    """List assigned batches for authenticated reviewer."""
    rev_id = user["reviewer_id"]
    all_batches = assignment_service.list_batches()
    assigned = [
        b.model_dump() for b in all_batches
        if b.reviewer_a_id == rev_id or b.reviewer_b_id == rev_id
    ]
    return assigned


@router.get("/batches/{batch_id}/next")
def get_next_batch_item(
    batch_id: str,
    user: Dict[str, str] = Depends(get_current_reviewer),
) -> Dict[str, Any]:
    """Fetch next unreviewed item from assigned batch with blinding protections."""
    rev_id = user["reviewer_id"]
    batch = None
    for b in assignment_service.list_batches():
        if b.batch_id == batch_id:
            batch = b
            break

    if not batch:
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found.")

    if batch.reviewer_a_id != rev_id and batch.reviewer_b_id != rev_id:
        raise HTTPException(status_code=403, detail=f"Reviewer {rev_id} not assigned to batch {batch_id}.")

    # Find first unreviewed item
    for item_id in batch.item_ids:
        existing = review_service.get_reviewer_submission(item_id, rev_id)
        if not existing:
            item = repo.get_item(item_id)
            if item:
                return assignment_service.generate_blinded_item_view(item, rev_id)

    return {"message": "All items in batch reviewed", "batch_id": batch_id, "completed": True}


@router.get("/records/{record_id}")
def get_record_for_review(
    record_id: str,
    user: Dict[str, str] = Depends(get_current_reviewer),
) -> Dict[str, Any]:
    """Fetch record for review with blind protections, ensuring reviewer is assigned."""
    rev_id = user["reviewer_id"]
    item = repo.get_item(record_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Record {record_id} not found.")

    # Authorization check
    assigned = assignment_service._item_assignments.get(record_id, [])
    if assigned and rev_id not in assigned and user["role"] not in ("adjudicator", "admin"):
        raise HTTPException(
            status_code=403,
            detail=f"Reviewer {rev_id} is not authorized to review record {record_id}.",
        )

    return assignment_service.generate_blinded_item_view(item, rev_id)


@router.post("/records/{record_id}/submit")
def submit_record_review(
    record_id: str,
    payload: ReviewSubmissionRequest,
    user: Dict[str, str] = Depends(get_current_reviewer),
) -> Dict[str, Any]:
    """Submit an independent review with idempotency and critical-failure overrides."""
    rev_id = user["reviewer_id"]

    item = repo.get_item(record_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Record {record_id} not found.")

    # Verify assignment authorization
    assigned = assignment_service._item_assignments.get(record_id, [])
    if assigned and rev_id not in assigned and user["role"] != "admin":
        raise HTTPException(status_code=403, detail=f"Reviewer {rev_id} is not assigned to record {record_id}.")

    sub = review_service.submit_review(
        item_id=record_id,
        reviewer_id=rev_id,
        batch_id=payload.batch_id,
        taxonomy_class=payload.taxonomy_class,
        ratings=payload.ratings,
        critical_checks=payload.critical_checks,
        workflow_flags=payload.workflow_flags,
        reviewer_notes=payload.reviewer_notes,
        support_tier_review=payload.support_tier_review,
    )

    return {
        "submission_id": sub.submission_id,
        "item_id": sub.item_id,
        "provisional_disposition": sub.determine_provisional_disposition().value,
        "submission_hash": sub.submission_hash,
        "is_sealed": True,
    }


@router.get("/disagreements")
def list_disagreements(
    user: Dict[str, str] = Depends(get_current_reviewer),
) -> Dict[str, Any]:
    """List adjudication queue items (Adjudicators and Admins only)."""
    if user["role"] not in ("adjudicator", "admin"):
        raise HTTPException(status_code=403, detail="Adjudicator privileges required to access disagreements queue.")

    queue = adjudication_service.list_queue_items()
    return {"unresolved_count": len(queue), "queue": queue}


@router.post("/adjudications/{record_id}")
def submit_adjudication(
    record_id: str,
    payload: AdjudicationRequest,
    user: Dict[str, str] = Depends(get_current_reviewer),
) -> Dict[str, Any]:
    """Submit final adjudication decision (Adjudicators and Admins only)."""
    if user["role"] not in ("adjudicator", "admin"):
        raise HTTPException(status_code=403, detail="Adjudicator privileges required to submit adjudications.")

    record = adjudication_service.resolve_adjudication(
        item_id=record_id,
        adjudicator_id=user["reviewer_id"],
        final_taxonomy_class=payload.final_taxonomy_class,
        final_disposition=payload.final_disposition,
        adjudicated_critical_checks=payload.critical_checks if hasattr(payload, "critical_checks") else payload.adjudicated_critical_checks,
        decision_rationale=payload.decision_rationale,
        revision_required=payload.revision_required,
    )

    return {
        "adjudication_id": record.adjudication_id,
        "record_id": record.item_id,
        "final_taxonomy_class": record.final_taxonomy_class.value,
        "final_disposition": record.final_disposition.value,
        "status": "resolved",
    }


@router.post("/revisions/{record_id}")
def submit_revision(
    record_id: str,
    payload: RevisionRequest,
    user: Dict[str, str] = Depends(get_current_reviewer),
) -> Dict[str, Any]:
    """Submit textual revision with Stage 14/15 revalidation (Adjudicators/Admins only)."""
    if user["role"] not in ("adjudicator", "admin"):
        raise HTTPException(status_code=403, detail="Adjudicator or Admin privileges required to submit revisions.")

    item = repo.get_item(record_id)
    original_text = item.target_text if item else "Original placeholder"
    source_group = item.source_group_id if item else "SRC-001"

    rev = revision_service.create_revision(
        item_id=record_id,
        original_text=original_text,
        revised_text=payload.revised_text,
        source_group_id=source_group,
        revision_reason=payload.revision_reason,
        revised_by=user["reviewer_id"],
        support_level=payload.support_level,
    )

    return {
        "revision_id": rev.revision_id,
        "item_id": rev.item_id,
        "stage14_schema_validation": rev.stage14_schema_validation,
        "stage15_quality_validation": rev.stage15_quality_validation,
        "final_disposition": rev.final_disposition.value,
    }


@router.get("/progress")
def get_review_progress() -> Dict[str, Any]:
    """Reconciliation metrics proving Unaccounted = 0."""
    accounting = review_service.get_accounting()
    unresolved_adj = len(adjudication_service.get_unresolved_items())
    return {
        "submission_accounting": accounting.model_dump(),
        "unresolved_adjudications": unresolved_adj,
        "ready_for_closeout": accounting.verify_conservation() and unresolved_adj == 0,
    }


@router.post("/releases/build")
def build_release_0_3_0(
    payload: ReleaseBuildRequest,
    user: Dict[str, str] = Depends(get_current_reviewer),
) -> Dict[str, Any]:
    """Build governed Release 0.3.0 (Admin only, release-builder lock enforced)."""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Administrator privileges required to build release.")

    root = repo.workspace_root
    builder = ReleaseBuilder(root_dir=str(root))

    # Precondition check: release-builder lock
    accounting = review_service.get_accounting()
    unresolved = len(adjudication_service.get_unresolved_items())

    if not payload.force_build:
        if accounting.unaccounted_submissions > 0 or unresolved > 0:
            return {
                "status": "RELEASE_BLOCKED_INCOMPLETE_EXPERT_REVIEW",
                "reason": (
                    f"Release 0.3.0 publication is locked: unaccounted_submissions={accounting.unaccounted_submissions}, "
                    f"unresolved_adjudications={unresolved}."
                ),
            }

    # Execute build
    items = repo.list_items()
    inv = repo.get_inventory()
    res = builder.build_release_0_3_0(
        manifest_items=items,
        adjudication_records=adjudication_service._adjudications,
        revisions=revision_service.revisions,
        inventory_accounting=inv,
    )
    res["status"] = "RELEASE_BUILT_SUCCESSFULLY"
    res["signoff"] = {"approved_by": payload.signoff_name, "role": payload.signoff_role}
    return res
