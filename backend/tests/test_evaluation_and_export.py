import io
import zipfile
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal
from app.database.models import Adaptation, ExpertEvaluation
from app.services.evaluation_service import evaluation_service

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


def test_submit_expert_evaluation_valid(client, db_session):
    """
    Verifies that submitting a valid 5-dimension Likert evaluation succeeds
    and correctly stores the ratings and qualitative feedback.
    """
    adaptation = db_session.query(Adaptation).first()
    assert adaptation is not None, "At least one adaptation must exist in the database."

    payload = {
        "adaptation_id": adaptation.id,
        "evaluator_code": "SLP-TEST-99",
        "age_appropriateness": 5,
        "clarity": 4,
        "grammar_correctness": 5,
        "meaning_preservation": 4,
        "personalization_suitability": 5,
        "comments": "Vocabulary is exceptionally clear and targeted for young children with language delays."
    }

    resp = client.post("/api/expert-evaluations", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["evaluator_code"] == "SLP-TEST-99"
    assert data["age_appropriateness"] == 5
    assert data["clarity"] == 4
    assert data["grammar_correctness"] == 5
    assert data["meaning_preservation"] == 4
    assert data["personalization_suitability"] == 5
    assert data["comments"] == payload["comments"]


def test_submit_expert_evaluation_invalid_bounds(client, db_session):
    """
    Verifies that submitting Likert scores outside 1-5 scale is strictly rejected.
    """
    adaptation = db_session.query(Adaptation).first()
    assert adaptation is not None

    # Score > 5 via HTTP
    payload_high = {
        "adaptation_id": adaptation.id,
        "evaluator_code": "SLP-TEST-ERR",
        "age_appropriateness": 6,
        "clarity": 4,
        "grammar_correctness": 5,
        "meaning_preservation": 4,
        "personalization_suitability": 5
    }
    resp1 = client.post("/api/expert-evaluations", json=payload_high)
    assert resp1.status_code in [400, 422]

    # Score < 1 via HTTP
    payload_low = {
        "adaptation_id": adaptation.id,
        "evaluator_code": "SLP-TEST-ERR",
        "age_appropriateness": 0,
        "clarity": 4,
        "grammar_correctness": 5,
        "meaning_preservation": 4,
        "personalization_suitability": 5
    }
    resp2 = client.post("/api/expert-evaluations", json=payload_low)
    assert resp2.status_code in [400, 422]

    # Direct service method call raises ValueError
    with pytest.raises(ValueError):
        evaluation_service.submit_expert_evaluation(
            db=db_session,
            adaptation_id=adaptation.id,
            evaluator_code="SLP-TEST-ERR",
            age_appropriateness=10,
            clarity=4,
            grammar_correctness=5,
            meaning_preservation=4,
            personalization_suitability=5
        )


def test_get_evaluation_statistics(client, db_session):
    """
    Verifies that /api/expert-evaluations/stats returns aggregate metrics,
    including dimension averages and method-specific breakdown.
    """
    resp = client.get("/api/expert-evaluations/stats")
    assert resp.status_code == 200
    stats = resp.json()

    assert "total_evaluations" in stats
    assert stats["total_evaluations"] > 0
    assert "overall_mean" in stats
    assert 1.0 <= stats["overall_mean"] <= 5.0
    assert "dimensions" in stats
    dims = stats["dimensions"]
    assert "age_appropriateness" in dims
    assert "clarity" in dims
    assert "grammar_correctness" in dims
    assert "meaning_preservation" in dims
    assert "personalization_suitability" in dims

    assert "by_generation_method" in stats
    by_method = stats["by_generation_method"]
    assert "rule" in by_method
    assert "llm" in by_method
    assert "hybrid" in by_method


def test_get_evaluations_for_adaptation(client, db_session):
    """
    Verifies fetching evaluations for a single adaptation.
    """
    adaptation = db_session.query(Adaptation).first()
    assert adaptation is not None

    resp = client.get(f"/api/expert-evaluations/adaptation/{adaptation.id}")
    assert resp.status_code == 200
    evals = resp.json()
    assert isinstance(evals, list)
    if len(evals) > 0:
        first = evals[0]
        assert "mean_score" in first
        assert "evaluator_code" in first


def test_export_experiments_json(client):
    """
    Verifies the hierarchical JSON export returns a list of experiment runs
    with nested attempts and adaptations.
    """
    resp = client.get("/api/export/experiments/json")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    exp = data[0]
    assert "experiment_id" in exp
    assert "learner" in exp
    assert "task" in exp
    assert "attempts" in exp
    assert "adaptations" in exp


def test_export_csv_endpoints(client):
    """
    Verifies that all 4 modular CSV export endpoints return valid CSV streams with expected headers.
    """
    endpoints = [
        ("/api/export/experiments/csv", "experiment_id"),
        ("/api/export/adaptations/csv", "adaptation_id"),
        ("/api/export/attempts/csv", "attempt_id"),
        ("/api/export/evaluations/csv", "evaluation_id"),
    ]

    for ep, expected_col in endpoints:
        resp = client.get(ep)
        assert resp.status_code == 200
        assert "text/csv" in resp.headers.get("content-type", "")
        csv_text = resp.text
        lines = csv_text.strip().split("\n")
        assert len(lines) >= 1
        assert expected_col in lines[0]


def test_export_research_bundle_zip(client):
    """
    Verifies that /api/export/research-bundle/zip downloads a valid ZIP archive
    containing all modular CSVs, JSON tree, and dataset metadata.
    """
    resp = client.get("/api/export/research-bundle/zip")
    assert resp.status_code == 200
    assert "application/zip" in resp.headers.get("content-type", "")

    # Inspect zip contents in-memory
    zip_bytes = io.BytesIO(resp.content)
    with zipfile.ZipFile(zip_bytes, "r") as zf:
        file_names = zf.namelist()
        expected_files = [
            "experiments.csv",
            "adaptations.csv",
            "attempts.csv",
            "expert_evaluations.csv",
            "experiments_full_tree.json",
            "evaluation_statistics.json",
            "DATASET_METADATA.txt"
        ]
        for f in expected_files:
            assert f in file_names, f"Expected {f} in ZIP archive"

        # Check metadata manifest content
        manifest_text = zf.read("DATASET_METADATA.txt").decode("utf-8")
        assert "ENGLISH-FIRST ADAPTIVE CHILD-FRIENDLY LANGUAGE SUPPORT MVP" in manifest_text
