"""
External Protected Storage Management for Stage 31.

Enforces physical decoupling of raw/normalized text from the Git repository,
validates that the storage path resolves outside the repository, and provides
abstract URI translations (protected://...).
"""

import os
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent

class ProtectedStorageManager:
    """Manages secure access to storage outside the Git repository."""

    def __init__(self, protected_root: Optional[Path] = None):
        if protected_root is not None:
            self.root = Path(protected_root).resolve()
        else:
            env_val = os.environ.get("SINHALA_EXTERNAL_PROTECTED_ROOT")
            if env_val:
                self.root = Path(env_val).resolve()
            else:
                self.root = (Path.home() / ".sinhala_external_protected_data").resolve()

        # Critical Security Invariant 7 & 10:
        # Protected root must never resolve inside the Git repository
        if self._is_within_repo(self.root):
            raise SecurityError(
                f"Security violation: SINHALA_EXTERNAL_PROTECTED_ROOT ({self.root}) "
                f"must NOT resolve inside the Git repository ({REPO_ROOT})"
            )

        self.sinhala_root = self.root / "sinhala_external"
        self.raw_dir = self.sinhala_root / "raw"
        self.normalized_dir = self.sinhala_root / "normalized"
        self.quarantine_dir = self.sinhala_root / "quarantine"
        self.dedup_dir = self.sinhala_root / "deduplication"
        self.manifest_dir = self.sinhala_root / "manifests"

        self._ensure_dirs()

    def _is_within_repo(self, path: Path) -> bool:
        try:
            return path.resolve().is_relative_to(REPO_ROOT.resolve())
        except AttributeError:
            # Python < 3.9 compatibility fallback
            try:
                path.resolve().relative_to(REPO_ROOT.resolve())
                return True
            except ValueError:
                return False

    def _ensure_dirs(self) -> None:
        for d in [self.raw_dir, self.normalized_dir, self.quarantine_dir, self.dedup_dir, self.manifest_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def uri_to_path(self, uri: str) -> Path:
        """Converts an abstract protected:// URI to a local filesystem Path."""
        if not uri.startswith("protected://"):
            raise ValueError(f"Invalid abstract URI prefix: {uri}")
        rel_str = uri[len("protected://"):]
        local_path = (self.root / rel_str).resolve()
        
        # Guard against path traversal attacks
        if not local_path.is_relative_to(self.root):
            raise SecurityError(f"Path traversal detected in URI: {uri}")
        return local_path

    def path_to_uri(self, path: Path) -> str:
        """Converts a local filesystem path to an abstract protected:// URI."""
        resolved = Path(path).resolve()
        if not resolved.is_relative_to(self.root):
            raise ValueError(f"Path {resolved} is not inside protected root {self.root}")
        rel = resolved.relative_to(self.root)
        return f"protected://{rel.as_posix()}"

    def write_raw_file(self, source_id: str, retrieval_id: str, filename: str, data: bytes) -> tuple[Path, str]:
        """Writes raw file bytes to protected storage and returns (local_path, protected_uri)."""
        target_dir = self.raw_dir / source_id / retrieval_id
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / filename
        target_path.write_bytes(data)
        uri = self.path_to_uri(target_path)
        return target_path, uri

    def read_raw_file(self, uri: str) -> bytes:
        """Reads raw bytes from abstract URI."""
        path = self.uri_to_path(uri)
        return path.read_bytes()

# Default singleton instance
storage_manager = ProtectedStorageManager()
