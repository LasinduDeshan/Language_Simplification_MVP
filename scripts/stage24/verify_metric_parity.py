"""
Stage 24: Verify metric parity and numerical precision (Delta < 0.05 points on 0-100 scale).
"""
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "backend"))

import json

def main():
    int_file = repo_root / "data" / "baseline_simplification" / "results" / "internal" / "internal_locked_test_summary.json"
    asset_file = repo_root / "data" / "baseline_simplification" / "results" / "asset" / "asset_benchmark_summary.json"
    
    with open(int_file, "r", encoding="utf-8") as f:
        int_data = json.load(f)
    with open(asset_file, "r", encoding="utf-8") as f:
        asset_data = json.load(f)

    parity_records = []
    
    print("=== Metric Parity & Numerical Precision Verification ===")
    for ds_name, ds_data in [("Internal Locked Test", int_data), ("ASSET Benchmark", asset_data)]:
        print(f"\nDataset: {ds_name}")
        for m_id, m_res in ds_data.items():
            sari_mean = m_res["metrics"]["sari"]["mean"]
            sari_add = m_res["metrics"]["sari_add"]
            sari_keep = m_res["metrics"]["sari_keep"]
            sari_del = m_res["metrics"]["sari_del"]
            
            reconstructed_sari = (sari_add + sari_keep + sari_del) / 3.0
            diff = abs(sari_mean - reconstructed_sari)
            
            passed = diff < 0.05
            print(f"[{m_id}] SARI: {sari_mean:.4f} | Recomputed: {reconstructed_sari:.4f} | Delta: {diff:.6f} | Parity: {'PASSED' if passed else 'FAILED'}")
            parity_records.append({
                "dataset": ds_name,
                "method": m_id,
                "reported_sari": sari_mean,
                "recomputed_sari": reconstructed_sari,
                "delta": diff,
                "passed": passed,
            })
            assert passed, f"Parity violation on {ds_name} {m_id}: delta {diff} >= 0.05"

    out_file = repo_root / "data" / "baseline_simplification" / "results" / "metric_parity_record.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(parity_records, f, indent=2)
    print(f"\nAll metric parity checks passed within tolerance (< 0.05 points)!")

if __name__ == "__main__":
    main()
