"""
Stage 24: Prepare and normalize evaluation inputs for Internal Release 0.2.0 and ASSET test set.
Constructs source groups and multi-reference groupings (3 references for Internal, 10 for ASSET).
"""
import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List

def load_json(filepath: Path) -> Any:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def build_internal_groups(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Groups internal dataset records by source_item_id / source_group_id."""
    groups: Dict[str, Dict[str, Any]] = {}
    
    for r in records:
        src_id = r.get("source_item_id") or r.get("source_id") or r.get("id")
        grp_id = r.get("source_group_id") or src_id
        src_text = r.get("source_text") or r.get("original_text") or r.get("text", "")
        simp_text = r.get("simplified_text") or r.get("target_text") or ""
        target_age = r.get("target_content_age") or 6
        support_level = r.get("target_support_level") or r.get("level", "moderate")

        if grp_id not in groups:
            groups[grp_id] = {
                "source_item_id": src_id,
                "source_group_id": grp_id,
                "source_text": src_text,
                "target_content_age": target_age,
                "references": {}, # support_level -> text
                "reference_texts": [],
                "governed_annotations": r.get("governed_annotations", {}),
            }
        
        if simp_text and simp_text not in groups[grp_id]["reference_texts"]:
            groups[grp_id]["reference_texts"].append(simp_text)
            groups[grp_id]["references"][str(support_level).lower()] = simp_text

    return list(groups.values())

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    cache_dir = repo_root / "data" / "baseline_simplification" / "evaluation_inputs"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    corpus_rel_dir = repo_root / "data" / "simplification_corpus" / "releases" / "0.2.0" / "splits"
    
    # 1. Internal Splits
    val_file = corpus_rel_dir / "development_candidate_validation.json"
    test_file = corpus_rel_dir / "development_candidate_test.json"
    
    val_records = load_json(val_file) if val_file.exists() else []
    test_records = load_json(test_file) if test_file.exists() else []
    
    val_groups = build_internal_groups(val_records)
    test_groups = build_internal_groups(test_records)
    
    with open(cache_dir / "internal_validation_groups.json", "w", encoding="utf-8") as f:
        json.dump(val_groups, f, indent=2)
    with open(cache_dir / "internal_locked_test_groups.json", "w", encoding="utf-8") as f:
        json.dump(test_groups, f, indent=2)
        
    print(f"Internal Validation Source Groups: {len(val_groups)}")
    print(f"Internal Locked Test Source Groups: {len(test_groups)}")

    # 2. ASSET Test Split (359 items)
    asset_meta_file = repo_root / "data" / "external_english" / "releases" / "0.1.0" / "record_metadata.jsonl"
    asset_groups: List[Dict[str, Any]] = []
    if asset_meta_file.exists():
        with open(asset_meta_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    if item.get("split") == "test":
                        # In release 0.1.0 metadata, source_text and references are preserved in normalized form or id mapping
                        asset_groups.append({
                            "source_item_id": item["source_record_id"],
                            "source_group_id": item["source_group_id"],
                            "source_text": item.get("source_text", ""),
                            "target_content_age": 6,
                            "reference_texts": item.get("reference_texts", []),
                        })

    # If raw ASSET is cached locally in data/external_english/asset/
    raw_asset_test = repo_root / "data" / "external_english" / "asset" / "raw" / "asset.test.orig"
    raw_asset_refs = [repo_root / "data" / "external_english" / "asset" / "raw" / f"asset.test.simp.{i}" for i in range(10)]
    if raw_asset_test.exists() and all(r.exists() for r in raw_asset_refs):
        with open(raw_asset_test, "r", encoding="utf-8") as f:
            orig_lines = [l.strip() for l in f.readlines()]
        ref_lines_matrix = []
        for r_path in raw_asset_refs:
            with open(r_path, "r", encoding="utf-8") as f:
                ref_lines_matrix.append([l.strip() for l in f.readlines()])
        
        asset_groups = []
        for idx, orig_text in enumerate(orig_lines):
            refs = [ref_lines_matrix[r_idx][idx] for r_idx in range(10) if idx < len(ref_lines_matrix[r_idx])]
            asset_groups.append({
                "source_item_id": f"ASSET-TEST-SRC-{idx+1:04d}",
                "source_group_id": f"ASSET-TEST-GRP-{idx+1:04d}",
                "source_text": orig_text,
                "target_content_age": 6,
                "reference_texts": refs,
            })

    with open(cache_dir / "asset_test_groups.json", "w", encoding="utf-8") as f:
        json.dump(asset_groups, f, indent=2)

    print(f"ASSET Test Groups: {len(asset_groups)}")

if __name__ == "__main__":
    main()
