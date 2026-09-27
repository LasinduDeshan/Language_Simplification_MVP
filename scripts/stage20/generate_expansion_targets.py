"""
Stage 20 Script: Generate Expansion Targets
Calculates batch-by-batch expansion targets and writes docs/stage20_expansion_targets.csv.
"""
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.datasets.expansion.target_planner import TargetPlanner

def main():
    print("=" * 60)
    print("STAGE 20: Generating Granular Dataset Expansion Targets")
    print("=" * 60)
    
    planner = TargetPlanner()
    output_path = os.path.join(ROOT_DIR, "docs", "stage20_expansion_targets.csv")
    planner.generate_csv_report(output_path)
    
    totals = planner.get_totals()
    print(f"Expansion targets successfully written to: {output_path}")
    print(f" - Target Source Items:         {totals['total_source_items']}")
    print(f" - Target Simplification Pairs: {totals['total_simplification_pairs']}")
    print(f" - Target Activities:           {totals['total_adaptation_activities']}")
    print(f" - Target Lexicon Entries:      {totals['total_lexicon_entries']}")
    print("=" * 60)

if __name__ == "__main__":
    main()
