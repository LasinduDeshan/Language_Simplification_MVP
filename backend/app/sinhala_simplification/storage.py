"""
Stage 33 — External Protected Storage Manager.
Enforces strict physical separation of restricted and reconstructable Sinhala text
outside the Git working tree under SINHALA_SIMPLIFICATION_PROTECTED_ROOT.
"""

import hashlib
import os
from pathlib import Path
from typing import Any, Dict, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def get_protected_storage_root() -> Path:
    """
    Resolves the external protected storage root directory.
    Fails closed immediately if unset, nonexistent, not writable,
    or resolving within the project repository workspace.
    """
    env_path = os.environ.get("SINHALA_SIMPLIFICATION_PROTECTED_ROOT")
    if not env_path or not env_path.strip():
        raise RuntimeError(
            "Security violation: SINHALA_SIMPLIFICATION_PROTECTED_ROOT is mandatory and unset."
        )
    root = Path(env_path).resolve()
    if not root.exists():
        raise RuntimeError(
            f"Security violation: SINHALA_SIMPLIFICATION_PROTECTED_ROOT ({root}) does not exist."
        )
    if not os.access(root, os.W_OK):
        raise RuntimeError(
            f"Security violation: SINHALA_SIMPLIFICATION_PROTECTED_ROOT ({root}) is not writable."
        )
    if root == PROJECT_ROOT or root.is_relative_to(PROJECT_ROOT):
        raise RuntimeError(
            f"Security violation: SINHALA_SIMPLIFICATION_PROTECTED_ROOT ({root}) "
            f"must NOT resolve inside working tree ({PROJECT_ROOT})"
        )

    # Ensure required protected subdirectories exist
    for sub in ["keys", "rules", "candidates", "outputs", "debug"]:
        (root / sub).mkdir(parents=True, exist_ok=True)

    return root


def purge_protected_debug_directory() -> int:
    """
    Purges temporary diagnostic debug artifacts according to retention policy.
    Returns count of removed debug files.
    """
    root = get_protected_storage_root()
    debug_dir = root / "debug"
    count = 0
    if debug_dir.exists():
        for item in debug_dir.iterdir():
            if item.is_file():
                item.unlink()
                count += 1
    return count


def compute_sha256(text: str) -> str:
    """Computes binary SHA-256 hex digest of UTF-8 encoded text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_protected_text(subdir: str, filename: str, text: str) -> Tuple[str, str]:
    """
    Writes restricted text to an external protected subdirectory.
    Returns (storage_ref, sha256_internal).
    """
    root = get_protected_storage_root()
    target_dir = root / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / filename
    file_path.write_text(text, encoding="utf-8")
    sha256_val = compute_sha256(text)
    storage_ref = f"protected://sinhala_simplification/{subdir}/{filename}"
    return storage_ref, sha256_val


def read_protected_text(storage_ref: str) -> str:
    """Reads protected text referenced by a protected:// URI."""
    if not storage_ref.startswith("protected://sinhala_simplification/"):
        raise ValueError(f"Invalid protected storage ref schema: {storage_ref}")

    rel_part = storage_ref.replace("protected://sinhala_simplification/", "")
    root = get_protected_storage_root()
    file_path = root / rel_part
    if not file_path.exists():
        raise FileNotFoundError(f"Protected storage file not found: {file_path}")
    return file_path.read_text(encoding="utf-8")
