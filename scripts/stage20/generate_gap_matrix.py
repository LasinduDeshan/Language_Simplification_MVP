"""
Stage 20 Script: Generate Gap Matrix
Calculates multidimensional coverage gaps and writes docs/stage20_dataset_gap_matrix.csv.
"""
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.datasets.expansion.gap_analysis import GapAnalyzer
from app.datasets.expansion.inventory import DatasetInventory

def main():
    print("=" * 60)
    print("STAGE 20: Generating Multidimensional Dataset Gap Matrix")
    print("=" * 60)
    
    inventory = DatasetInventory(root_dir=ROOT_DIR)
    analyzer = GapAnalyzer(inventory=inventory)
    
    output_path = os.path.join(ROOT_DIR, "docs", "stage20_dataset_gap_matrix.csv")
    analyzer.generate_csv_report(output_path)
    
    print(f"Gap matrix successfully written to: {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
