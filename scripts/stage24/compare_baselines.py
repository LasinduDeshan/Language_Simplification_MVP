"""
Stage 24: Generate comparative performance tables and export docs/stage24_baseline_comparison.csv.
"""
import csv
import json
from pathlib import Path

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    int_file = repo_root / "data" / "baseline_simplification" / "results" / "internal" / "internal_locked_test_summary.json"
    asset_file = repo_root / "data" / "baseline_simplification" / "results" / "asset" / "asset_benchmark_summary.json"
    
    with open(int_file, "r", encoding="utf-8") as f:
        int_data = json.load(f)
    with open(asset_file, "r", encoding="utf-8") as f:
        asset_data = json.load(f)

    out_csv = repo_root / "docs" / "stage24_baseline_comparison.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "baseline_id",
        "baseline_name",
        "internal_sari",
        "internal_sari_add",
        "internal_sari_keep",
        "internal_sari_del",
        "internal_bleu",
        "internal_fkgl_delta",
        "internal_word_comp",
        "asset_sari",
        "asset_sari_add",
        "asset_sari_keep",
        "asset_sari_del",
        "asset_bleu",
        "asset_fkgl_delta",
        "asset_word_comp",
        "mean_latency_ms",
        "disposition_pass_rate",
    ]

    method_names = {
        "B0": "Identity Baseline",
        "B1": "Lexical Substitution",
        "B2": "Sentence Splitting",
        "B3": "Syntactic Rules",
        "B4": "Combined Deterministic",
        "B5": "Existing Offline Fallback",
    }

    rows = []
    for m in ["B0", "B1", "B2", "B3", "B4", "B5"]:
        i_m = int_data.get(m, {})
        a_m = asset_data.get(m, {})
        
        i_metrics = i_m.get("metrics", {})
        a_metrics = a_m.get("metrics", {})
        i_disp = i_m.get("dispositions", {})
        tot_i = i_m.get("total_records", 45)
        pass_rate = (i_disp.get("automatic_check_passed", 0) / tot_i * 100.0) if tot_i > 0 else 0.0

        rows.append({
            "baseline_id": m,
            "baseline_name": method_names[m],
            "internal_sari": f"{i_metrics.get('sari', {}).get('mean', 0.0):.2f}",
            "internal_sari_add": f"{i_metrics.get('sari_add', 0.0):.2f}",
            "internal_sari_keep": f"{i_metrics.get('sari_keep', 0.0):.2f}",
            "internal_sari_del": f"{i_metrics.get('sari_del', 0.0):.2f}",
            "internal_bleu": f"{i_metrics.get('corpus_bleu', 0.0):.2f}",
            "internal_fkgl_delta": f"{i_metrics.get('fkgl', {}).get('reduction_delta', 0.0):.2f}",
            "internal_word_comp": f"{i_metrics.get('compression', {}).get('word_ratio', 1.0):.2f}",
            "asset_sari": f"{a_metrics.get('sari', {}).get('mean', 0.0):.2f}",
            "asset_sari_add": f"{a_metrics.get('sari_add', 0.0):.2f}",
            "asset_sari_keep": f"{a_metrics.get('sari_keep', 0.0):.2f}",
            "asset_sari_del": f"{a_metrics.get('sari_del', 0.0):.2f}",
            "asset_bleu": f"{a_metrics.get('corpus_bleu', 0.0):.2f}",
            "asset_fkgl_delta": f"{a_metrics.get('fkgl', {}).get('reduction_delta', 0.0):.2f}",
            "asset_word_comp": f"{a_metrics.get('compression', {}).get('word_ratio', 1.0):.2f}",
            "mean_latency_ms": f"{i_m.get('operational', {}).get('mean_latency_ms', 0.0):.2f}",
            "disposition_pass_rate": f"{pass_rate:.1f}%",
        })

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Exported baseline comparison to: {out_csv}")

if __name__ == "__main__":
    main()
