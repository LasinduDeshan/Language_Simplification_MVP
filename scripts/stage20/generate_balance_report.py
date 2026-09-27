"""
Stage 20 Script: Generate Balance Report
Calculates multidimensional balance across the expanded corpus and writes docs/stage20_balance_report.csv.
"""
import os
import sys
import json

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.datasets.expansion.balance_analyzer import BalanceAnalyzer

def main():
    print("=" * 60)
    print("STAGE 20: Generating Corpus Balance Report")
    print("=" * 60)
    
    batch_dir = os.path.join(ROOT_DIR, "data", "dataset_expansion", "stage20", "authoring_batches")
    all_pairs = []
    
    for filename in sorted(os.listdir(batch_dir)):
        if filename.endswith(".json"):
            filepath = os.path.join(batch_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_pairs.extend(data.get("simplification_pairs", []))

    analyzer = BalanceAnalyzer(target_domain_pct=25.0, domain_tolerance=5.0)
    out_csv = os.path.join(ROOT_DIR, "docs", "stage20_balance_report.csv")
    analyzer.generate_csv_report(all_pairs, out_csv)
    
    analysis = analyzer.analyze_records(all_pairs)
    print(f"Balance analysis complete across {analysis['total_records']} simplification pairs:")
    for dom, pct in analysis["domain_percentages"].items():
        print(f"  - {dom.title()}: {analysis['domain_counts'][dom]} pairs ({pct}%)")
    print(f"  - Overall Balance Status: {'BALANCED (Within 20-30% tolerance)' if analysis['is_balanced'] else 'IMBALANCED'}")
    print(f"Report written to: {out_csv}")
    print("=" * 60)

if __name__ == "__main__":
    main()
