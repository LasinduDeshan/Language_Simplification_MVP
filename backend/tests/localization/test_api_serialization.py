"""
API serialization tests verifying UTF-8 decoded equality, media types, and DTO round trips.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_api_locales_endpoint(client):
    res = client.get("/api/v1/localization/locales")
    assert res.status_code == 200
    assert "application/json" in res.headers["content-type"]
    data = res.json()
    assert data["default_locale"] == "en-LK"
    assert "si-LK" in data["locales"]
    assert "en-LK" in data["locales"]

def test_api_locale_selection_endpoint(client):
    # Valid selection
    res = client.post("/api/v1/localization/locale", json={"locale": "si-LK"})
    assert res.status_code == 200
    data = res.json()
    assert data["language"] == "si"
    assert data["locale"] == "si-LK"
    assert data["script"] == "Sinh"
    assert data["direction"] == "ltr"

    # Extra fields forbidden (422)
    res_bad = client.post("/api/v1/localization/locale", json={"locale": "si-LK", "script": "Latn"})
    assert res_bad.status_code == 422

def test_api_unicode_probe_round_trip(client):
    probe_payload = {
        "test_id": "PRB-001",
        "payload": "ශ්‍රී ලංකා",
        "expected_code_points": ["U+0DC1", "U+0DCA", "U+200D", "U+0DBB", "U+0DD3", "U+0020", "U+0DBD", "U+0D82", "U+0D9A", "U+0DCF"],
        "category": "combining_sequence"
    }

    res = client.post("/api/v1/localization/probe/round-trip", json=probe_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "PASSED"
    assert data["matches_expected"] is True
    assert data["replacement_character_detected"] is False

    # Body bytes decode successfully as UTF-8 without corruption
    decoded_text = res.content.decode("utf-8")
    assert "ශ්‍රී ලංකා" in decoded_text
