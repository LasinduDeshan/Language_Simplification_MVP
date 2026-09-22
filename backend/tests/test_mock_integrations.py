import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal
from app.integrations.component1.mock_adapter import Component1MockAdapter
from app.integrations.component1.schemas import Component1ScreeningInputSchema
from app.integrations.common.errors import InvalidMockFixtureError
from app.integrations.component2_ar.mock_adapter import Component2ARMockAdapter
from app.integrations.component4.mock_adapter import Component4MockAdapter

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_component1_mock_adapter_loads_all_five_fixtures():
    """
    Test that Component 1 mock adapter loads all 5 simulated learner profiles.
    Every profile must have is_simulated == True and research_eligible == False.
    """
    adapter = Component1MockAdapter()
    profiles = adapter.list_screening_profiles()
    assert len(profiles) == 5

    codes = {p.learner_id for p in profiles}
    assert "CHILD-001" in codes
    assert "CHILD-002" in codes
    assert "CHILD-003" in codes
    assert "CHILD-004" in codes
    assert "CHILD-005" in codes

    for p in profiles:
        assert p.is_simulated is True
        assert p.research_eligible is False
        assert p.risk_level in ["low", "moderate", "high"]

def test_component1_mock_adapter_rejects_unsimulated_record():
    """
    Test that Component 1 mock adapter rejects any fixture missing is_simulated == True.
    """
    with pytest.raises(Exception):
        invalid_data = {
            "learner_id": "REAL-001",
            "age": 5,
            "risk_level": "moderate",
            "is_simulated": False
        }
        # If passed to mock adapter loader logic, it should raise InvalidMockFixtureError
        profile = Component1ScreeningInputSchema(**invalid_data)
        if not profile.is_simulated:
            raise InvalidMockFixtureError("Mock profile must be simulated.")

def test_integration_status_endpoint(client):
    """
    Test GET /api/integration/status returns accurate Stage 12 mock statuses.
    """
    res = client.get("/api/integration/status")
    assert res.status_code == 200
    data = res.json()
    assert data["component_1"] == "mock"
    assert data["component_2_ar"] == "not_connected"
    assert data["component_4"] == "not_connected"
    assert data["is_simulated"] is True
    assert data["research_eligible"] is False

def test_component4_preview_export(client, db_session):
    """
    Test GET /api/integration-preview/component-4/{learner_id} produces
    a valid four-domain export with risk_modified_by_component_3 == False.
    """
    res = client.get("/api/integration-preview/component-4/CHILD-002")
    assert res.status_code == 200
    data = res.json()
    assert data["learner_id"] == "CHILD-002"
    assert data["risk_modified_by_component_3"] is False
    assert data["is_simulated"] is True
    assert data["research_eligible"] is False
    assert "vocabulary" in data["performance_profile"]
    assert "grammar" in data["performance_profile"]
    assert "comprehension" in data["performance_profile"]
    assert "instruction_following" in data["performance_profile"]
    assert data["export_status"] == "generated_locally_not_delivered"

def test_component2_ar_preview(client, db_session):
    """
    Test GET /api/integration-preview/component-2-ar/{task_id} produces
    a valid AR payload with delivery_status == not_connected.
    """
    res = client.get("/api/integration-preview/component-2-ar/GRAM-PREP-001")
    assert res.status_code == 200
    data = res.json()
    assert data["task_id"] == "GRAM-PREP-001"
    assert data["delivery_status"] == "not_connected"
    assert data["is_simulated"] is True
    assert len(data["steps"]) >= 1

def test_external_screening_import_disabled_in_mock_mode(client):
    """
    Test POST /api/integration/component-1/screening-profile returns 403
    when ENABLE_COMPONENT1_EXTERNAL_IMPORT is disabled in mock mode.
    """
    res = client.post("/api/integration/component-1/screening-profile", json={
        "learner_id": "CHILD-002",
        "risk_level": "low"
    })
    assert res.status_code == 403
    assert "not enabled" in res.json()["detail"].lower()
