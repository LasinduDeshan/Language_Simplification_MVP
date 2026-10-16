"""
Tests for Version-Pinned Rights Inheritance in Stage 32 Lexicon (WP7).
"""

import pytest
from app.datasets.sinhala_lexicon.rights_resolver import LexiconRightsResolver
from app.datasets.sinhala_lexicon.schemas import RightsProfileReference
from app.datasets.sinhala_lexicon.enums import FieldExportPolicy

def test_version_pinned_rights_resolution():
    """Verify rights resolver resolves field policies and applies most restrictive rules."""
    resolver = LexiconRightsResolver()
    refs = [
        RightsProfileReference(source_id="SRC-1", rights_profile_id="RP-SRC-1", rights_profile_version=1),
        RightsProfileReference(source_id="SRC-2", rights_profile_id="RP-RESTRICTED-2", rights_profile_version=2)
    ]
    policies = resolver.resolve_entry_export_policies(refs)
    assert policies["canonical_form"] == FieldExportPolicy.METADATA_ONLY
    assert policies["concordance_contexts"] == FieldExportPolicy.RESTRICTED_PROTECTED_INTERNAL
