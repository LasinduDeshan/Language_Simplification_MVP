"""
Stage 20 Target Planner Module
Calculates granular expansion targets per batch, domain, and record type.
"""
import os
import csv
from typing import Dict, Any, List

class TargetPlanner:
    def __init__(self):
        self.batch_plan = [
            {
                "batch_id": "STAGE20-BATCH-PILOT",
                "batch_name": "Pilot Multi-Domain Gate",
                "source_items": 80,
                "simplification_pairs": 240,
                "adaptation_activities": 40,
                "lexicon_entries": 60,
                "vocab_items": 20,
                "grammar_items": 20,
                "comp_items": 20,
                "instruction_items": 20,
                "status": "planned"
            },
            {
                "batch_id": "STAGE20-BATCH-02",
                "batch_name": "Expansion Batch 1 (Ages 4-5)",
                "source_items": 50,
                "simplification_pairs": 150,
                "adaptation_activities": 20,
                "lexicon_entries": 60,
                "vocab_items": 15,
                "grammar_items": 15,
                "comp_items": 10,
                "instruction_items": 10,
                "status": "planned"
            },
            {
                "batch_id": "STAGE20-BATCH-03",
                "batch_name": "Expansion Batch 2 (Ages 6-7)",
                "source_items": 50,
                "simplification_pairs": 150,
                "adaptation_activities": 20,
                "lexicon_entries": 60,
                "vocab_items": 10,
                "grammar_items": 15,
                "comp_items": 10,
                "instruction_items": 15,
                "status": "planned"
            },
            {
                "batch_id": "STAGE20-BATCH-04",
                "batch_name": "Expansion Batch 3 (Ages 7-8)",
                "source_items": 50,
                "simplification_pairs": 150,
                "adaptation_activities": 20,
                "lexicon_entries": 60,
                "vocab_items": 10,
                "grammar_items": 10,
                "comp_items": 15,
                "instruction_items": 15,
                "status": "planned"
            },
            {
                "batch_id": "STAGE20-BATCH-05",
                "batch_name": "Expansion Batch 4 (Gap-Targeted)",
                "source_items": 70,
                "simplification_pairs": 210,
                "adaptation_activities": 20,
                "lexicon_entries": 110,
                "vocab_items": 20,
                "grammar_items": 15,
                "comp_items": 20,
                "instruction_items": 15,
                "status": "planned"
            }
        ]

    def get_totals(self) -> Dict[str, Any]:
        return {
            "total_source_items": sum(b["source_items"] for b in self.batch_plan),
            "total_simplification_pairs": sum(b["simplification_pairs"] for b in self.batch_plan),
            "total_adaptation_activities": sum(b["adaptation_activities"] for b in self.batch_plan),
            "total_lexicon_entries": sum(b["lexicon_entries"] for b in self.batch_plan),
            "total_vocab_items": sum(b["vocab_items"] for b in self.batch_plan),
            "total_grammar_items": sum(b["grammar_items"] for b in self.batch_plan),
            "total_comp_items": sum(b["comp_items"] for b in self.batch_plan),
            "total_instruction_items": sum(b["instruction_items"] for b in self.batch_plan),
        }

    def generate_csv_report(self, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fieldnames = [
            "batch_id", "batch_name", "source_items", "simplification_pairs",
            "adaptation_activities", "lexicon_entries", "vocab_items",
            "grammar_items", "comp_items", "instruction_items", "status"
        ]
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in self.batch_plan:
                writer.writerow(row)
                
            # Write summary total row
            totals = self.get_totals()
            writer.writerow({
                "batch_id": "TOTAL",
                "batch_name": "Stage 20 Target Corpus Total",
                "source_items": totals["total_source_items"],
                "simplification_pairs": totals["total_simplification_pairs"],
                "adaptation_activities": totals["total_adaptation_activities"],
                "lexicon_entries": totals["total_lexicon_entries"],
                "vocab_items": totals["total_vocab_items"],
                "grammar_items": totals["total_grammar_items"],
                "comp_items": totals["total_comp_items"],
                "instruction_items": totals["total_instruction_items"],
                "status": "target"
            })
        return output_path
