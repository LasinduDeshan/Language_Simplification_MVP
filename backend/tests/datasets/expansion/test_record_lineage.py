"""
Unit tests for Stage 20 Record Lineage & Provenance.
"""
import pytest
from app.datasets.expansion.schemas import ProvenanceMetadata, AuthoringMethodEnum
from pydantic import ValidationError

def test_provenance_metadata_valid():
    prov = ProvenanceMetadata(
        authoring_method=AuthoringMethodEnum.HUMAN_AUTHORED_WITH_AI_ASSISTANCE,
        created_by="researcher_1",
        generation_model="gemini-1.5-flash",
        human_edited=True,
        batch_id="STAGE20-BATCH-PILOT",
        revision_id="REV-001"
    )
    assert prov.authoring_method == "human_authored_with_ai_assistance"
    assert prov.rights_status == "internal_team_owned"
    assert prov.human_edited is True

def test_provenance_invalid_method():
    with pytest.raises(ValidationError):
        ProvenanceMetadata(
            authoring_method="invalid_method_xyz",
            created_by="user",
            batch_id="BATCH-01"
        )
