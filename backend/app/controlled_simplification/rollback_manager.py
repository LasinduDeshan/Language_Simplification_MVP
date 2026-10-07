"""
Safe rollback manager for operation-level rollback and terminal status assignment.
"""

from typing import List, Tuple, Optional
from app.controlled_simplification.schemas import (
    AppliedOperation,
    TerminalStatus,
    ValidationResults
)


class RollbackManager:
    """
    Manages safe operation rollback when validation gates are violated.
    Prevents silent tier downgrades and ensures fail-closed routing.
    """

    @staticmethod
    def resolve_terminal_status(
        validation_results: ValidationResults,
        has_rollback: bool,
        is_adult_support: bool = False
    ) -> TerminalStatus:
        """
        Assigns terminal status based on validation results and rollback history.
        """
        if is_adult_support:
            return TerminalStatus.ADULT_SUPPORT_REQUIRED

        if not validation_results.all_critical_passed:
            # If critical gates failed, check severity
            if any("Blocked language pattern" in v for v in validation_results.detected_violations):
                return TerminalStatus.REJECTED
            if any("Forbidden disclosure" in v for v in validation_results.detected_violations):
                return TerminalStatus.REJECTED
            # Default to MANUAL_REVIEW_REQUIRED
            return TerminalStatus.MANUAL_REVIEW_REQUIRED

        if has_rollback:
            return TerminalStatus.PASSED_WITH_ROLLBACK

        return TerminalStatus.PASSED
