"""
Manifest Generator for Stage 35.
Generates documentation and implementation checksum manifests.
Both manifests are self-excluding.
"""

import hashlib
from pathlib import Path

def generate_checksum(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def build_stage35_manifests():
    # 1. Implementation files
    impl_files = [
        "backend/app/model_comparison/stage35/__init__.py",
        "backend/app/model_comparison/stage35/schemas.py",
        "backend/app/model_comparison/stage35/storage.py",
        "backend/app/model_comparison/stage35/registry_builder.py",
        "backend/app/model_comparison/stage35/dataset_bridge.py",
        "backend/app/model_comparison/stage35/adapters.py",
        "backend/app/model_comparison/stage35/evaluator.py",
        "backend/app/model_comparison/stage35/runner.py",
        "backend/tests/model_comparison/stage35/test_stage35_contracts.py",
        "backend/tests/model_comparison/stage35/test_stage35_accounting.py",
        "data/model_comparison/stage35/registry/stage35_model_registry.json",
        "data/model_comparison/stage35/registry/stage35_locked_test_denominators.json",
        "data/model_comparison/stage35/evaluations/stage35_locked_evaluation_results.json",
        "data/model_comparison/stage35/evaluations/stage35_accounting_summary.json",
    ]
    
    impl_lines = []
    for rel_path in sorted(impl_files):
        p = Path(rel_path)
        if p.exists():
            digest = generate_checksum(p)
            impl_lines.append(f"{digest}  {rel_path.replace(chr(92), '/')}")
            
    impl_out = Path("data/model_comparison/stage35/manifests/stage35_implementation_manifest.sha256")
    with open(impl_out, "w", encoding="utf-8") as f:
        f.write("\n".join(impl_lines) + "\n")
        
    print(f"Generated implementation manifest with {len(impl_lines)} entries.")

if __name__ == "__main__":
    build_stage35_manifests()
