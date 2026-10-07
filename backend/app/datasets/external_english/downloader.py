"""Secure, deterministic downloader for external datasets with strict safety guardrails."""

import hashlib
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import List, Optional, Tuple
import urllib.request
import urllib.parse


class SecureDatasetDownloader:
    """Safely downloads and extracts dataset files with domain allowlisting and size limits."""

    ALLOWED_DOMAINS = {
        "raw.githubusercontent.com",
        "github.com",
        "oasissimpdataset.github.io",
    }
    MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB per file limit
    DEFAULT_TIMEOUT_SECONDS = 30

    def __init__(self, allowed_domains: Optional[set] = None):
        self.allowed_domains = allowed_domains or self.ALLOWED_DOMAINS

    def validate_url(self, url: str) -> Tuple[bool, str]:
        """Validates that a URL uses HTTPS and is in the allowed domain list."""
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https":
            return False, f"Insecure scheme '{parsed.scheme}'. Only HTTPS downloads are permitted."
        if parsed.netloc.lower() not in self.allowed_domains:
            return False, f"Domain '{parsed.netloc}' is not in the approved download allowlist."
        return True, "URL is valid and permitted."

    def compute_sha256(self, filepath: Path) -> str:
        """Computes SHA-256 hash of a local file."""
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def download_file(
        self,
        url: str,
        destination: Path,
        expected_sha256: Optional[str] = None,
        force: bool = False,
    ) -> Tuple[Path, str]:
        """Downloads a file atomically to a staging directory and verifies size and hash."""
        valid, err = self.validate_url(url)
        if not valid:
            raise ValueError(f"Download blocked by safety policy: {err}")

        # Idempotency check
        if destination.exists() and not force:
            actual_hash = self.compute_sha256(destination)
            if expected_sha256 and actual_hash != expected_sha256:
                raise ValueError(
                    f"Existing file {destination} has hash {actual_hash}, expected {expected_sha256}."
                )
            return destination, actual_hash

        destination.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as staging_dir:
            staging_path = Path(staging_dir) / destination.name
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "LanguageSimplificationMVP-Stage23Downloader/1.0"},
            )

            with urllib.request.urlopen(req, timeout=self.DEFAULT_TIMEOUT_SECONDS) as response:
                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > self.MAX_FILE_SIZE_BYTES:
                    raise ValueError(
                        f"Download exceeded maximum size limit ({content_length} > {self.MAX_FILE_SIZE_BYTES} bytes)"
                    )

                downloaded_bytes = 0
                with open(staging_path, "wb") as out_f:
                    while chunk := response.read(65536):
                        downloaded_bytes += len(chunk)
                        if downloaded_bytes > self.MAX_FILE_SIZE_BYTES:
                            raise ValueError("Download exceeded maximum file size during transfer.")
                        out_f.write(chunk)

            actual_hash = self.compute_sha256(staging_path)
            if expected_sha256 and actual_hash != expected_sha256:
                raise ValueError(
                    f"SHA-256 mismatch for {url}: expected {expected_sha256}, got {actual_hash}"
                )

            # Atomic move from staging to final destination
            shutil.move(str(staging_path), str(destination))

        return destination, actual_hash
