"""
Child-delivery governance and validation status policy.
Enforces draft status and mandatory expert review on all Stage 25 outputs.
"""

from app.controlled_simplification.schemas import GovernanceMetadata, TerminalStatus


class DeliveryPolicy:
    """
    Enforces that Stage 25 outputs are treated strictly as research and development candidates.
    """

    @staticmethod
    def get_governance_metadata(status: TerminalStatus) -> GovernanceMetadata:
        """
        Returns governance metadata. All outputs default to unapproved for direct child delivery.
        """
        return GovernanceMetadata(
            validation_status="draft",
            approved_for_child_delivery=False,
            requires_expert_review=True
        )
