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
        "backend/app/model_comparison/stage35/config_freezer.py",
        "backend/app/model_comparison/stage35/dataset_bridge.py",
        "backend/app/model_comparison/stage35/adapters.py",
        "backend/app/model_comparison/stage35/evaluator.py",
        "backend/app/model_comparison/stage35/runner.py",
        "backend/tests/model_comparison/stage35/test_stage35_contracts.py",
        "backend/tests/model_comparison/stage35/test_stage35_accounting.py",
        "backend/tests/model_comparison/stage35/test_stage35_manifest.py",
        "data/model_comparison/stage35/registry/stage35_model_registry.json",
        "data/model_comparison/stage35/registry/stage35_prompt_template.json",
        "data/model_comparison/stage35/registry/stage35_decoding_config.json",
        "data/model_comparison/stage35/registry/stage35_safety_settings.json",
        "data/model_comparison/stage35/registry/stage35_evaluator_spec.json",
        "data/model_comparison/stage35/registry/stage35_metrics_and_gates_spec.json",
        "data/model_comparison/stage35/registry/stage35_operational_policy.json",
        "data/model_comparison/stage35/registry/stage35_authorization_record.json",
        "data/model_comparison/stage35/registry/stage35_validation_run_record.json",
        "data/model_comparison/stage35/registry/stage35_retry_and_failure_policy.json",
        "data/model_comparison/stage35/registry/stage35_software_dependency_lock.json",
        "data/model_comparison/stage35/registry/stage35_code_commit_record.json",
        "data/model_comparison/stage35/registry/stage35_eligibility_and_decision_thresholds.json",
        "data/model_comparison/stage35/registry/stage35_configuration_freeze_bundle.json",
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
        
    # 2. Documentation files (N=16 controlled documents)
    doc_files = [
        "docs/stage35_accounting_summary.md",
        "docs/stage35_completion_record.md",
        "docs/stage35_configuration_freeze_record.md",
        "docs/stage35_cost_latency_and_resource_report.md",
        "docs/stage35_dataset_partition_and_disclosure_report.md",
        "docs/stage35_development_and_validation_report.md",
        "docs/stage35_error_analysis.md",
        "docs/stage35_implementation_plan.md",
        "docs/stage35_limitations_and_risk_report.md",
        "docs/stage35_locked_test_comparison_report.md",
        "docs/stage35_metrics_and_statistical_analysis_plan.md",
        "docs/stage35_model_registry_and_rights_report.md",
        "docs/stage35_model_selection_and_fallback_record.md",
        "docs/stage35_output_validation_and_safety_policy.md",
        "docs/stage35_prompt_and_decoding_protocol.md",
        "docs/stage35_reproducibility_record.json",
    ]
    doc_lines = []
    for rel_path in sorted(doc_files):
        p = Path(rel_path)
        if p.exists():
            digest = generate_checksum(p)
            doc_lines.append(f"{digest}  {rel_path.replace(chr(92), '/')}")
            
    doc_out = Path("docs/stage35_manifest.sha256")
    with open(doc_out, "w", encoding="utf-8") as f:
        f.write("\n".join(doc_lines) + "\n")
        
    print(f"Generated implementation manifest with {len(impl_lines)} entries.")
    print(f"Generated documentation manifest with {len(doc_lines)} entries.")

if __name__ == "__main__":
    build_stage35_manifests()
