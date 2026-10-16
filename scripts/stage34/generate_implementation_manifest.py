"""
Stage 34 — Implementation Manifest Generator (WP9)
Generates data/sinhala_expert_validation/manifests/stage34_implementation_manifest.sha256 covering:
- Backend implementation modules in backend/app/datasets/sinhala_expert_validation/
- Registry and configuration files in data/sinhala_expert_validation/registry/
- Assignment ledger in data/sinhala_expert_validation/assignments/
- Sanitized ledgers in data/sinhala_expert_validation/ledgers/
- Reports in data/sinhala_expert_validation/reports/
- Prerequisite snapshot in data/sinhala_expert_validation/snapshots/
- Pipeline scripts in scripts/stage34/
- Unit and integration tests in backend/tests/sinhala_expert_validation/
Excluding itself. Strictly zero protected reviewer PII or restricted texts.
"""

import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "sinhala_expert_validation"
MANIFESTS_DIR = DATA_DIR / "manifests"
MANIFEST_FILE = MANIFESTS_DIR / "stage34_implementation_manifest.sha256"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def generate_implementation_manifest():
    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

    files_to_hash = []

    # 1. Backend modules
    backend_dir = PROJECT_ROOT / "backend" / "app" / "datasets" / "sinhala_expert_validation"
    for py_file in sorted(backend_dir.glob("*.py")):
        files_to_hash.append(py_file)

    # 2. Registries
    reg_dir = DATA_DIR / "registry"
    for j_file in sorted(reg_dir.glob("*.json")):
        files_to_hash.append(j_file)

    # 3. Assignment ledger
    asn_dir = DATA_DIR / "assignments"
    for l_file in sorted(asn_dir.glob("*.jsonl")):
        files_to_hash.append(l_file)

    # 4. Sanitized ledgers
    ledgers_dir = DATA_DIR / "ledgers"
    for l_file in sorted(ledgers_dir.glob("*.jsonl")):
        files_to_hash.append(l_file)

    # 5. Reports
    reports_dir = DATA_DIR / "reports"
    for r_file in sorted(reports_dir.glob("*.json")):
        files_to_hash.append(r_file)

    # 6. Snapshots
    snap_dir = DATA_DIR / "snapshots"
    for s_file in sorted(snap_dir.glob("*.json")):
        files_to_hash.append(s_file)

    # 7. Scripts
    scripts_dir = PROJECT_ROOT / "scripts" / "stage34"
    for s_file in sorted(scripts_dir.glob("*.py")):
        files_to_hash.append(s_file)

    # 8. Tests
    tests_dir = PROJECT_ROOT / "backend" / "tests" / "sinhala_expert_validation"
    for t_file in sorted(tests_dir.glob("*.py")):
        files_to_hash.append(t_file)

    manifest_lines = []
    for fpath in files_to_hash:
        rel_path = fpath.relative_to(PROJECT_ROOT).as_posix()
        # Ensure manifest does not contain itself
        if "stage34_implementation_manifest.sha256" in rel_path:
            continue
        # Ensure no actual protected storage records or raw texts
        assert not rel_path.endswith(".txt"), f"Raw text file leaked to manifest: {rel_path}"
        assert ".sinhala_expert_validation_protected_data" not in rel_path, f"External protected data leaked: {rel_path}"
        digest = sha256_file(fpath)
        manifest_lines.append(f"{digest}  {rel_path}\n")

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        f.writelines(manifest_lines)

    print(f"Generated {MANIFEST_FILE} with {len(manifest_lines)} entries.")


if __name__ == "__main__":
    generate_implementation_manifest()
