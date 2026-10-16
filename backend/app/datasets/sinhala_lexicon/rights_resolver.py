"""
Rights Resolver for Stage 32 Sinhala Lexicon.
Inherits and aggregates versioned rights profiles from all contributing sources,
resolves field-level export permissions, and enforces the most restrictive rule.
"""

from typing import Dict, List
from app.datasets.sinhala_lexicon.enums import FieldExportPolicy
from app.datasets.sinhala_lexicon.schemas import RightsProfileReference

class LexiconRightsResolver:
    """Resolves inherited rights and field-level export policies."""

    def resolve_entry_export_policies(
        self,
        rights_refs: List[RightsProfileReference]
    ) -> Dict[str, FieldExportPolicy]:
        """
        Resolves export policies per field across all contributing sources.
        Standalone lexical forms and aggregate statistics are public if permitted.
        Concordance lines and definitions remain strictly internal/protected.
        """
        # Baseline field policies
        policies = {
            "canonical_form": FieldExportPolicy.PUBLIC_PERMITTED_STANDALONE,
            "frequency_statistics": FieldExportPolicy.PUBLIC_PERMITTED_AGGREGATE,
            "definitions": FieldExportPolicy.RESTRICTED_PROTECTED_INTERNAL,
            "concordance_contexts": FieldExportPolicy.RESTRICTED_PROTECTED_INTERNAL
        }

        # If any contributing source is restricted, downgrade standalone form to METADATA_ONLY
        for ref in rights_refs:
            if "RESTRICTED" in ref.rights_profile_id:
                policies["canonical_form"] = FieldExportPolicy.METADATA_ONLY

        return policies
