"""
Backend governance tests for frontend translation resources and SHA-256 hashes.
"""
import json
import hashlib
from pathlib import Path

def test_translation_resources_governance():
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    i18n_dir = repo_root / "frontend" / "src" / "i18n"
    meta_path = i18n_dir / "translations.meta.json"

    assert meta_path.exists(), "translations.meta.json must exist"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    assert "resources" in meta
    assert len(meta["resources"]) == 2

    for res in meta["resources"]:
        assert res["translation_status"] == "technical_draft"
        assert res["approved_for_child_delivery"] is False
        assert res["reviewed_by"] is None
        assert res["authored_by_actor_id"] == "infrastructure_team"

        file_path = i18n_dir / res["resource_file"]
        assert file_path.exists()
        actual_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
        assert actual_hash == res["sha256"], f"SHA mismatch for {res['resource_file']}"
