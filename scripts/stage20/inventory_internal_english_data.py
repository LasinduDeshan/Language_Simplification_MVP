"""
Stage 20 Script: Inventory Internal English Data
Runs the manifest-driven dataset inventory and writes docs/stage20_dataset_inventory.md.
"""
import os
import sys

# Ensure backend directory is in PYTHONPATH
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.datasets.expansion.inventory import DatasetInventory

def main():
    print("=" * 60)
    print("STAGE 20: Generating Manifest-Driven Dataset Inventory")
    print("=" * 60)
    
    inventory = DatasetInventory(root_dir=ROOT_DIR)
    report_md = inventory.generate_markdown_report()
    
    output_path = os.path.join(ROOT_DIR, "docs", "stage20_dataset_inventory.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_md)
        
    print(f"Inventory report successfully written to: {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
