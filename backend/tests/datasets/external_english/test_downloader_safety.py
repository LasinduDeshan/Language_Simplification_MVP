"""Tests for SecureDatasetDownloader guardrails and safety controls."""

import hashlib
from pathlib import Path
import pytest
import tempfile
import urllib.error

from app.datasets.external_english.downloader import SecureDatasetDownloader


@pytest.fixture
def downloader():
    return SecureDatasetDownloader()


def test_downloader_rejects_insecure_scheme(downloader):
    valid, err = downloader.validate_url("http://raw.githubusercontent.com/facebookresearch/asset/file.txt")
    assert not valid
    assert "Insecure scheme" in err


def test_downloader_rejects_unapproved_domain(downloader):
    valid, err = downloader.validate_url("https://malicious-domain.com/data.txt")
    assert not valid
    assert "not in the approved download allowlist" in err


def test_downloader_accepts_approved_domain(downloader):
    valid, err = downloader.validate_url(
        "https://raw.githubusercontent.com/facebookresearch/asset/main/dataset/asset.test.orig"
    )
    assert valid
    assert "valid and permitted" in err


def test_downloader_sha256_computation(downloader, tmp_path):
    test_file = tmp_path / "sample.txt"
    test_content = b"Sample dataset content for hashing verification."
    test_file.write_bytes(test_content)

    expected_hash = hashlib.sha256(test_content).hexdigest()
    assert downloader.compute_sha256(test_file) == expected_hash


def test_downloader_idempotent_existing_file(downloader, tmp_path):
    test_file = tmp_path / "existing.txt"
    test_content = b"Deterministic payload"
    test_file.write_bytes(test_content)
    expected_hash = hashlib.sha256(test_content).hexdigest()

    # If destination exists and hash matches, it shouldn't re-download
    dest, actual_hash = downloader.download_file(
        url="https://raw.githubusercontent.com/facebookresearch/asset/mock/file",
        destination=test_file,
        expected_sha256=expected_hash,
        force=False,
    )
    assert dest == test_file
    assert actual_hash == expected_hash


def test_downloader_fails_on_existing_file_mismatch(downloader, tmp_path):
    test_file = tmp_path / "corrupted.txt"
    test_file.write_bytes(b"corrupted content")

    with pytest.raises(ValueError, match="has hash .*, expected"):
        downloader.download_file(
            url="https://raw.githubusercontent.com/facebookresearch/asset/mock/file",
            destination=test_file,
            expected_sha256="0000000000000000000000000000000000000000000000000000000000000000",
            force=False,
        )
