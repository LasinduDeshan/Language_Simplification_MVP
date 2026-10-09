"""Assignment Service for Stage 27.

Creates blinded batches, assigns independent Reviewer A / Reviewer B pairings,
enforces cross-reviewer isolation, tracks independent submissions, and handles
reassignment upon reviewer revocation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from .schemas import (
    ReviewBatch,
    ReviewManifestItem,
    SubmissionAccounting,
)


class AssignmentService:
    """Manages double-blind batch assignments and reviewer isolation guards."""

    def __init__(self) -> None:
        self._batches: Dict[str, ReviewBatch] = {}
        self._item_assignments: Dict[str, List[str]] = {}  # item_id -> [reviewer_ids]
        self._accounting = SubmissionAccounting(expected_submissions=3360)
        self._active_panel_pairs: Dict[str, Tuple[str, str]] = {}

    def create_batches(
        self,
        items: List[ReviewManifestItem],
        reviewer_pairs: List[tuple],  # List of (panel_id, rev_a_id, rev_b_id)
        batch_size: int = 70,
    ) -> List[ReviewBatch]:
        """Partitions manifest items into batches and assigns Reviewer A & Reviewer B pairs.
        
        Preserves source group continuity so all tiers of a source group reside in the same batch.
        """
        self._batches.clear()
        self._item_assignments.clear()

        # Group items by source_group_id to keep source groups together
        groups: Dict[str, List[ReviewManifestItem]] = {}
        for it in items:
            groups.setdefault(it.source_group_id, []).append(it)

        # Pack groups into chunks
        batch_chunks: List[List[str]] = []
        current_chunk: List[str] = []

        for group_items in groups.values():
            item_ids = [it.item_id for it in group_items]
            if len(current_chunk) + len(item_ids) > batch_size and current_chunk:
                batch_chunks.append(current_chunk)
                current_chunk = []
            current_chunk.extend(item_ids)

        if current_chunk:
            batch_chunks.append(current_chunk)

        # Distribute chunks across reviewer pairs
        num_pairs = len(reviewer_pairs)
        if num_pairs == 0:
            raise ValueError("At least one reviewer pair (Reviewer A, Reviewer B) is required.")

        batches = []
        total_assignments = 0

        for idx, chunk in enumerate(batch_chunks):
            panel_id, rev_a, rev_b = reviewer_pairs[idx % num_pairs]
            batch_id = f"BATCH-ENG-{idx + 1:03d}"

            batch = ReviewBatch(
                batch_id=batch_id,
                reviewer_panel_id=panel_id,
                reviewer_a_id=rev_a,
                reviewer_b_id=rev_b,
                item_ids=chunk,
                status="assigned",
                created_at=datetime.utcnow(),
            )
            self._batches[batch_id] = batch
            batches.append(batch)

            for item_id in chunk:
                # Exactly 2 reviewers assigned per item (Reviewer A & B)
                assigned = self._item_assignments.setdefault(item_id, [])
                if rev_a not in assigned:
                    assigned.append(rev_a)
                    total_assignments += 1
                if rev_b not in assigned:
                    assigned.append(rev_b)
                    total_assignments += 1

        self._accounting.unaccounted_submissions = total_assignments
        return batches

    def create_assignment_batches(
        self,
        items: List[ReviewManifestItem],
        reviewer_pairs: List[Any],
        batch_size: int = 70,
    ) -> List[ReviewBatch]:
        """Convenience alias accepting 2-tuples or 3-tuples for reviewer pairs."""
        formatted_pairs = []
        for idx, p in enumerate(reviewer_pairs):
            if len(p) == 2:
                formatted_pairs.append((f"PANEL-{idx+1:02d}", p[0], p[1]))
            else:
                formatted_pairs.append(p)
        return self.create_batches(items, formatted_pairs, batch_size=batch_size)

    def generate_blinded_item_view(
        self, item: ReviewManifestItem, reviewer_id: str
    ) -> Dict[str, Any]:
        """Returns a strictly blinded view of an item for an assigned reviewer.
        
        Strips: model origin, dataset split, locked status, and all NLP scores.
        """
        return {
            "item_id": item.item_id,
            "source_group_id": item.source_group_id,
            "record_type": item.record_type.value,
            "text_stimulus": item.text_stimulus,
            "target_text": item.target_text,
            "support_level": item.support_level.value if item.support_level else None,
            "target_age_min": item.target_age_min,
            "target_age_max": item.target_age_max,
            "domain": item.domain,
            "difficulty": item.difficulty,
            "reviewer_id": reviewer_id,
        }

    def get_blinded_item_view(
        self, item: ReviewManifestItem, requesting_reviewer_id: str
    ) -> Dict[str, Any]:
        """Returns a strictly blinded view after checking reviewer assignment."""
        assigned_reviewers = self._item_assignments.get(item.item_id, [])
        if requesting_reviewer_id not in assigned_reviewers:
            raise PermissionError(
                f"Reviewer {requesting_reviewer_id} is not assigned to item {item.item_id}."
            )
        return self.generate_blinded_item_view(item, requesting_reviewer_id)

    def verify_no_duplicate_assignments(self) -> bool:
        """Verifies that each item has at most 2 distinct reviewers (A and B) and zero duplicates."""
        for item_id, reviewers in self._item_assignments.items():
            if len(reviewers) != len(set(reviewers)):
                return False
            if len(reviewers) > 2:
                return False
        return True

    def reassign_incomplete_batch(
        self, batch_id: str, old_reviewer_id: str, replacement_reviewer_id: str
    ) -> ReviewBatch:
        """Revokes incomplete assignments of a reviewer and reassigns to replacement reviewer."""
        batch = self._batches.get(batch_id)
        if not batch:
            raise KeyError(f"Batch {batch_id} not found.")

        if batch.reviewer_a_id == old_reviewer_id:
            batch.reviewer_a_id = replacement_reviewer_id
        elif batch.reviewer_b_id == old_reviewer_id:
            batch.reviewer_b_id = replacement_reviewer_id
        else:
            raise ValueError(f"Reviewer {old_reviewer_id} is not assigned to batch {batch_id}.")

        # Update item assignments
        for item_id in batch.item_ids:
            assigned = self._item_assignments.get(item_id, [])
            if old_reviewer_id in assigned:
                assigned.remove(old_reviewer_id)
                assigned.append(replacement_reviewer_id)

        return batch

    def get_accounting(self) -> SubmissionAccounting:
        """Return submission accounting metrics."""
        return self._accounting

    def list_batches(self) -> List[ReviewBatch]:
        """List all active batches."""
        return list(self._batches.values())
