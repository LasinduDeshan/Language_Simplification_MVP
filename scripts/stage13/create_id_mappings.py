import os
import sys
import json
import csv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
ADAPT_MAP = os.path.join(BASE_DIR, "data", "adaptation_test_set", "id_mappings", "task_id_mappings.json")
CORPUS_MAP = os.path.join(BASE_DIR, "data", "simplification_corpus", "id_mappings", "corpus_id_mappings.json")
INTER_MAP = os.path.join(BASE_DIR, "data", "interaction_dataset", "id_mappings", "interaction_id_mappings.json")

def generate_master_id_mappings():
    print("=== GENERATING MASTER ID MAPPINGS ===")
    
    master_records = []
    
    for layer_name, map_file in [
        ("Adaptation Test Set", ADAPT_MAP),
        ("Simplification Corpus", CORPUS_MAP),
        ("Interaction Dataset", INTER_MAP)
    ]:
        if os.path.exists(map_file):
            with open(map_file, "r", encoding="utf-8") as f:
                recs = json.load(f)
            print(f"Loaded {len(recs)} mappings from {layer_name}")
            for r in recs:
                r["layer"] = layer_name
                master_records.append(r)

    out_csv = os.path.join(DOCS_DIR, "stage13_master_id_mappings.csv")
    os.makedirs(DOCS_DIR, exist_ok=True)

    fieldnames = ["layer", "source_path", "source_id", "target_layer", "target_id", "disposition", "migration_timestamp", "notes"]

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(master_records)

    print(f"Master ID mappings written to {out_csv} ({len(master_records)} total mappings)")
    return len(master_records)

if __name__ == "__main__":
    generate_master_id_mappings()
