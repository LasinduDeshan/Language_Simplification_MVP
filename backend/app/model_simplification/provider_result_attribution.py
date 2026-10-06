"""
Stage 26 Provider Result Attribution Engine.
Guarantees transparent fallback attribution and prevents attribution of fallback outputs to requested external providers.
Maps execution results into mutually exclusive accounting categories under FinalOutcomes.
"""
from typing import Dict, Any, Tuple
from app.model_simplification.schemas import (
    ModelGenerationResult,
    ExecutionStatus,
    NativeValidationDisposition,
)


class ProviderResultAttribution:
    """
    Classifies generation outcomes into unambiguous accounting buckets.
    """

    # Final Outcomes Categories (Mutually Exclusive)
    CAT_NATIVE_DELIVERED = "native_delivered"
    CAT_REPAIR_DELIVERED = "repair_delivered"
    CAT_FALLBACK_DELIVERED = "fallback_delivered"
    CAT_MANUAL_REVIEW = "manual_review_required"
    CAT_REJECTED = "rejected"

    ALL_CATEGORIES = [
        CAT_NATIVE_DELIVERED,
        CAT_REPAIR_DELIVERED,
        CAT_FALLBACK_DELIVERED,
        CAT_MANUAL_REVIEW,
        CAT_REJECTED,
    ]

    @classmethod
    def classify_outcome(cls, result: ModelGenerationResult) -> Tuple[str, str]:
        """
        Classifies result into (accounting_category, effective_delivering_provider).
        """
        # If fallback was used, delivery is credited to fallback provider
        if result.fallback_used:
            return cls.CAT_FALLBACK_DELIVERED, (result.fallback_provider or "stage25_rule_engine")

        val = result.native_validation
        if val is None:
            return cls.CAT_REJECTED, result.requested_provider

        if val.disposition == NativeValidationDisposition.PASSED:
            return cls.CAT_NATIVE_DELIVERED, result.requested_provider
        elif val.disposition == NativeValidationDisposition.PASSED_WITH_CONTROLLED_REPAIR:
            return cls.CAT_REPAIR_DELIVERED, result.requested_provider
        elif val.disposition == NativeValidationDisposition.MANUAL_REVIEW_REQUIRED:
            return cls.CAT_MANUAL_REVIEW, result.requested_provider
        else:
            return cls.CAT_REJECTED, result.requested_provider

    @classmethod
    def is_successful_draft_delivery(cls, result: ModelGenerationResult) -> bool:
        """
        Returns True if candidate passed or repaired or fallback delivered.
        """
        cat, _ = cls.classify_outcome(result)
        return cat in {cls.CAT_NATIVE_DELIVERED, cls.CAT_REPAIR_DELIVERED, cls.CAT_FALLBACK_DELIVERED}
