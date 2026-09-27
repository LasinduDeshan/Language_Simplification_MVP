"""
Stage 20 Gap Analysis Module
Analyzes deficits across domain, age, difficulty, and support dimensions against target tolerances.
"""
import os
import csv
from typing import Dict, Any, List
from collections import defaultdict
from app.datasets.expansion.inventory import DatasetInventory

class GapAnalyzer:
    def __init__(self, inventory: DatasetInventory = None):
        self.inventory = inventory or DatasetInventory()
        self.target_source_items = 300
        self.target_domain_items = 75       # 25% of 300
        self.target_domain_pairs = 225      # 75 * 3
        self.domains = ["vocabulary", "grammar", "comprehension", "instruction_following"]
        self.ages = [4, 5, 6, 7, 8]
        self.difficulties = ["easy", "medium", "hard"]

    def compute_gap_matrix(self) -> List[Dict[str, Any]]:
        raw_inv = self.inventory.analyze()
        simp_records = self.inventory._load_json(self.inventory.simp_path)

        # Count existing source items / pairs per cell: (domain, age_band, difficulty)
        current_counts = defaultdict(int)
        for r in simp_records:
            dom = r.get("primary_domain", "unknown")
            diff = r.get("source_difficulty", "medium")
            # Bucket age
            age_min = r.get("age_min", 4)
            age_max = r.get("age_max", 8)
            current_counts[(dom, age_min, age_max, diff)] += 1

        # Calculate domain aggregate gaps
        domain_counts = raw_inv["simplification_corpus"]["domain_distribution"]
        
        matrix = []
        for dom in self.domains:
            curr_pairs = domain_counts.get(dom, 0)
            curr_sources = curr_pairs // 3
            gap_sources = max(0, self.target_domain_items - curr_sources)
            gap_pairs = gap_sources * 3
            
            for diff in self.difficulties:
                # Target per (domain, difficulty) slice: 25 items
                diff_target = self.target_domain_items // 3
                # Approximate current
                diff_curr = sum(
                    v for k, v in current_counts.items() 
                    if k[0] == dom and k[3] == diff
                ) // 3
                diff_gap = max(0, diff_target - diff_curr)

                matrix.append({
                    "primary_domain": dom,
                    "difficulty": diff,
                    "target_source_items": diff_target,
                    "current_source_items": diff_curr,
                    "gap_source_items": diff_gap,
                    "target_pairs": diff_target * 3,
                    "current_pairs": diff_curr * 3,
                    "gap_pairs": diff_gap * 3,
                    "recommended_action": "Author new items" if diff_gap > 0 else "Maintain balance"
                })

        return matrix

    def generate_csv_report(self, output_path: str):
        matrix = self.compute_gap_matrix()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        fieldnames = [
            "primary_domain", "difficulty", "target_source_items",
            "current_source_items", "gap_source_items", "target_pairs",
            "current_pairs", "gap_pairs", "recommended_action"
        ]
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in matrix:
                writer.writerow(row)
        return output_path
