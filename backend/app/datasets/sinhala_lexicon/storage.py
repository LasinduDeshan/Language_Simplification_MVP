"""
External Protected Storage Management for Stage 32 Sinhala Lexicon.
Enforces physical decoupling of concordances and token texts from the Git repository,
validates that storage paths resolve strictly outside the repository,
and provides abstract URI translations (protected://sinhala_lexicon/...).
"""

import os
from pathlib import Path
from typing import Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent

class LexiconProtectedStorageManager:
    """Manages protected storage for lexicon contexts, concordance lines, and isolated tokens."""

    def __init__(self, protected_root: Optional[Path] = None):
        if protected_root is not None:
            self.root = Path(protected_root).resolve()
        else:
            env_val = os.environ.get("SINHALA_LEXICON_PROTECTED_ROOT")
            if env_val:
                self.root = Path(env_val).resolve()
            else:
                self.root = (Path.home() / ".sinhala_lexicon_protected_data").resolve()

        # Security Invariant: Protected root must never resolve inside the Git repository
        if self._is_within_repo(self.root):
            raise SecurityError(
                f"Security violation: SINHALA_LEXICON_PROTECTED_ROOT ({self.root}) "
                f"must NOT resolve inside the Git repository ({REPO_ROOT})"
            )

        self.lexicon_root = self.root / "sinhala_lexicon"
        self.contexts_dir = self.lexicon_root / "contexts"
        self.tokens_dir = self.lexicon_root / "tokens"
        self.exports_dir = self.lexicon_root / "exports"

        self._ensure_dirs()

    def _is_within_repo(self, path: Path) -> bool:
        try:
            return path.resolve().is_relative_to(REPO_ROOT.resolve())
        except AttributeError:
            try:
                path.resolve().relative_to(REPO_ROOT.resolve())
                return True
            except ValueError:
                return False

    def _ensure_dirs(self) -> None:
        for d in [self.contexts_dir, self.tokens_dir, self.exports_dir]:
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

    def write_context_file(self, occurrence_id: str, context_data: dict) -> Tuple[Path, str]:
        """Writes context payload to protected storage and returns (local_path, protected_uri)."""
        import json
        filename = f"{occurrence_id}.json"
        target_path = self.contexts_dir / filename
        target_path.write_text(json.dumps(context_data, ensure_ascii=False, indent=2), encoding="utf-8")
        uri = self.path_to_uri(target_path)
        return target_path, uri

    def write_token_file(self, occurrence_id: str, token_surface: str) -> Tuple[Path, str]:
        """Writes isolated token surface to protected storage and returns (local_path, protected_uri)."""
        filename = f"{occurrence_id}.txt"
        target_path = self.tokens_dir / filename
        target_path.write_text(token_surface, encoding="utf-8")
        uri = self.path_to_uri(target_path)
        return target_path, uri

    def read_file_text(self, uri: str) -> str:
        """Reads UTF-8 text from abstract protected URI."""
        path = self.uri_to_path(uri)
        return path.read_text(encoding="utf-8")

lexicon_storage = LexiconProtectedStorageManager()
