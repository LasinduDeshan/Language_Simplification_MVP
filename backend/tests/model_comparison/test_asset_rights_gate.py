"""
Test ASSET external benchmark data protection and rights gate enforcement.
Ensures zero raw ASSET strings appear in public repository deliverables.
"""
from pathlib import Path
import pytest
from app.model_comparison.input_repository import InputRepository


def test_asset_rights_gate_zero_raw_text_in_public_reports():
    repo = InputRepository()
    asset_items = repo.load_asset_test_split(operating_mode="generic")
    assert len(asset_items) == 359

    # Extract sample unique substrings from first 5 ASSET source sentences
    sample_phrases = []
    for it in asset_items[:5]:
        words = it.source_text.split()
        if len(words) >= 5:
            sample_phrases.append(" ".join(words[1:5]))

    # Verify that docs/ public files do not contain these raw phrases
    docs_dir = repo.repo_root / "docs"
    checked_files = [
        docs_dir / "stage28a_implementation_plan.md",
    ]

    for p in docs_dir.glob("stage28a_*.csv"):
        checked_files.append(p)
    for p in docs_dir.glob("stage28a_*.md"):
        checked_files.append(p)

    for doc_file in checked_files:
        if not doc_file.exists():
            continue
        content = doc_file.read_text(encoding="utf-8")
        for phrase in sample_phrases:
            assert phrase not in content, (
                f"Data protection violation: Raw ASSET phrase '{phrase}' found in public file {doc_file.name}"
            )
