"""
End-to-end integration tests for Stage 29 Sinhala Technical Foundation.
Covers: request DTO -> API endpoint -> repository -> persistence -> JSON/CSV export -> byte integrity.
"""
from fastapi.testclient import TestClient
from app.main import app

def test_stage29_end_to_end_round_trip():
    client = TestClient(app)

    # 1. Negotiate and select Sinhala locale
    loc_res = client.post("/api/v1/localization/locale", json={"locale": "si-LK"})
    assert loc_res.status_code == 200
    loc_data = loc_res.json()
    assert loc_data["language"] == "si"
    assert loc_data["script"] == "Sinh"
    assert loc_data["direction"] == "ltr"

    # 2. Submit localized content item with ZWJ ligature
    sample_sinhala = "ක්‍ෂීරපායී සතුන්ගේ ව්‍යුහය"
    content_payload = {
        "text_role": "sample_educational",
        "text_value": sample_sinhala,
        "language": "si",
        "locale": "si-LK",
        "source_type": "technical_fixture",
        "validation_status": "draft",
        "research_eligible": False,
        "approved_for_child_delivery": False,
        "requires_expert_review": True
    }

    create_res = client.post("/api/v1/localization/content", json=content_payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["status"] == "success"
    content_id = created_data["content_id"]

    # 3. Retrieve content item by ID
    get_res = client.get(f"/api/v1/localization/content/{content_id}")
    assert get_res.status_code == 200
    retrieved_data = get_res.json()
    assert retrieved_data["text_value"] == sample_sinhala
    assert retrieved_data["language"] == "si"
    assert retrieved_data["source_type"] == "technical_fixture"
    assert retrieved_data["approved_for_child_delivery"] is False

    # 4. Export to JSON and verify byte integrity
    exp_json = client.get("/api/v1/localization/export/json?language=si")
    assert exp_json.status_code == 200
    assert "application/json" in exp_json.headers["content-type"]
    assert exp_json.headers.get("X-Artifact-SHA256") is not None
    json_bytes = exp_json.content
    assert sample_sinhala in json_bytes.decode("utf-8")

    # 5. Export to CSV and verify byte integrity
    exp_csv = client.get("/api/v1/localization/export/csv?language=si&use_bom=true")
    assert exp_csv.status_code == 200
    assert "text/csv" in exp_csv.headers["content-type"]
    csv_bytes = exp_csv.content
    assert sample_sinhala in csv_bytes.decode("utf-8-sig")
