import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import json
from app.database.db import SessionLocal
from app.services.evaluation_service import evaluation_service

def export_benchmark_dataset():
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "research_exports"))
    os.makedirs(output_dir, exist_ok=True)

    db = SessionLocal()
    try:
        print("Exporting research benchmark datasets...")

        # 1. Full Tree JSON
        json_data = evaluation_service.export_experiments_json(db)
        json_path = os.path.join(output_dir, "experiments_full_tree.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)
        print(f"[OK] Exported JSON: {json_path} ({len(json_data)} runs)")

        # 2. Experiments CSV
        exp_csv = evaluation_service.export_experiments_csv(db)
        exp_csv_path = os.path.join(output_dir, "experiments.csv")
        with open(exp_csv_path, "w", encoding="utf-8") as f:
            f.write(exp_csv)
        print(f"[OK] Exported Experiments CSV: {exp_csv_path}")

        # 3. Adaptations CSV
        ad_csv = evaluation_service.export_adaptations_csv(db)
        ad_csv_path = os.path.join(output_dir, "adaptations.csv")
        with open(ad_csv_path, "w", encoding="utf-8") as f:
            f.write(ad_csv)
        print(f"[OK] Exported Adaptations CSV: {ad_csv_path}")

        # 4. Attempts CSV
        att_csv = evaluation_service.export_attempts_csv(db)
        att_csv_path = os.path.join(output_dir, "attempts.csv")
        with open(att_csv_path, "w", encoding="utf-8") as f:
            f.write(att_csv)
        print(f"[OK] Exported Attempts CSV: {att_csv_path}")

        # 5. Expert Evaluations CSV
        eval_csv = evaluation_service.export_evaluations_csv(db)
        eval_csv_path = os.path.join(output_dir, "expert_evaluations.csv")
        with open(eval_csv_path, "w", encoding="utf-8") as f:
            f.write(eval_csv)
        print(f"[OK] Exported Expert Evaluations CSV: {eval_csv_path}")

        # 6. Complete Research Bundle ZIP
        zip_bytes = evaluation_service.export_research_bundle_zip(db)
        zip_path = os.path.join(output_dir, "research_dataset_bundle.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_bytes)
        print(f"[OK] Exported Research ZIP Bundle: {zip_path} ({len(zip_bytes)} bytes)")

        # 7. Print Evaluation Statistics
        stats = evaluation_service.get_evaluation_statistics(db)
        print("\n=== Research Benchmark Evaluation Statistics ===")
        print(f"Total Evaluations: {stats['total_evaluations']}")
        print(f"Overall Likert Mean: {stats['overall_mean']}/5.00")
        print("Dimension Averages:")
        for dim, val in stats["dimensions"].items():
            print(f"  - {dim}: {val}/5.00")
        print("Performance by Generation Method:")
        for m, m_data in stats["by_generation_method"].items():
            print(f"  - {m.upper()}: Mean {m_data['overall_mean']}/5.00 (n={m_data['count']})")
        print("================================================\n")

    finally:
        db.close()

if __name__ == "__main__":
    export_benchmark_dataset()
