"""
Stage 34 — External Protected Storage Service
Ensures all protected reviewer PII, credentials, restricted item texts, raw annotations,
free-text comments, and adjudication rationales are stored strictly OUTSIDE the Git repository.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent


class ProtectedStorageManager:
    def __init__(self, override_root: Optional[Path] = None):
        if override_root:
            self.root = Path(override_root).resolve()
        else:
            env_val = os.environ.get("SINHALA_EXPERT_VALIDATION_PROTECTED_ROOT")
            if env_val:
                self.root = Path(env_val).resolve()
            else:
                self.root = (Path.home() / ".sinhala_expert_validation_protected_data" / "stage34").resolve()

        self.validate_isolation()
        self.subdirs = {
            "reviewers": self.root / "reviewers",
            "assignments": self.root / "assignments",
            "item_text": self.root / "item_text",
            "annotations": self.root / "annotations",
            "amendments": self.root / "amendments",
            "adjudications": self.root / "adjudications",
            "comments": self.root / "comments",
            "exports": self.root / "exports",
            "audit": self.root / "audit",
        }
        self.initialize_directories()

    def validate_isolation(self):
        """Fails closed if the protected root resolves inside the git repository working tree."""
        try:
            is_inside = self.root.is_relative_to(PROJECT_ROOT)
        except AttributeError:
            # Fallback for Python < 3.9 if applicable
            try:
                self.root.relative_to(PROJECT_ROOT)
                is_inside = True
            except ValueError:
                is_inside = False

        if is_inside:
            raise PermissionError(
                f"Security violation: protected storage root {self.root} must NOT reside inside git workspace {PROJECT_ROOT}"
            )

    def initialize_directories(self):
        self.root.mkdir(parents=True, exist_ok=True)
        for d in self.subdirs.values():
            d.mkdir(parents=True, exist_ok=True)

    def store_json(self, category: str, filename: str, data: Any) -> Path:
        if category not in self.subdirs:
            raise ValueError(f"Unknown protected category: {category}")
        target = self.subdirs[category] / filename
        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return target

    def load_json(self, category: str, filename: str) -> Any:
        if category not in self.subdirs:
            raise ValueError(f"Unknown protected category: {category}")
        target = self.subdirs[category] / filename
        if not target.exists():
            raise FileNotFoundError(f"Protected artifact {filename} not found in {category}")
        with open(target, "r", encoding="utf-8") as f:
            return json.load(f)

    def store_text(self, category: str, filename: str, text: str) -> Path:
        if category not in self.subdirs:
            raise ValueError(f"Unknown protected category: {category}")
        target = self.subdirs[category] / filename
        with open(target, "w", encoding="utf-8") as f:
            f.write(text)
        return target

    def load_text(self, category: str, filename: str) -> str:
        if category not in self.subdirs:
            raise ValueError(f"Unknown protected category: {category}")
        target = self.subdirs[category] / filename
        if not target.exists():
            raise FileNotFoundError(f"Protected text file {filename} not found in {category}")
        with open(target, "r", encoding="utf-8") as f:
            return f.read()
