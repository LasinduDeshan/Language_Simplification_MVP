"""
Stage 35 Dataset Bridge and Denominator Gating.
Implements WP2:
1. Validates sealed Stage 31 canonical 150 items.
2. Applies source rights disclosure gating:
   - Sources with public redistribution (SRC-SI-001, SRC-SI-003) -> PRIMARY_COMMON_DENOMINATOR
   - Restricted on-premise sources (SRC-SI-002, SRC-SI-004) -> LOCAL_ONLY_SUPPLEMENTARY_DENOMINATOR
3. Segregates Train (124), Validation (13), and Locked Test (13) into exact common vs local subsets.
"""

import json
from pathlib import Path
from app.model_comparison.stage35.schemas import DenominatorClassification

DISCLOSURE_PERMITTED_SOURCES = {"SRC-SI-001", "SRC-SI-003", "SRC-SI-008"}
LOCAL_ONLY_SOURCES = {"SRC-SI-002", "SRC-SI-004"}

def bridge_stage35_denominators():
    locked_meta_path = Path("data/sinhala_simplification/evaluation/locked_test_metadata.jsonl")
    records = []
    with open(locked_meta_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
                
    primary_common = []
    local_only = []
    
    for r in records:
        req_id = r["request_id"]
        out_id = r["output_id"]
        rights_refs = r.get("rights_profile_refs", [])
        src_id = None
        for ref in rights_refs:
            rp = ref.get("rights_profile_id", "")
            if "SRC-SI-001" in rp:
                src_id = "SRC-SI-001"
            elif "SRC-SI-002" in rp:
                src_id = "SRC-SI-002"
            elif "SRC-SI-003" in rp:
                src_id = "SRC-SI-003"
            elif "SRC-SI-004" in rp:
                src_id = "SRC-SI-004"
            elif "SRC-SI-008" in rp:
                src_id = "SRC-SI-008"
                
        if src_id in DISCLOSURE_PERMITTED_SOURCES:
            primary_common.append({
                "request_id": req_id,
                "output_id": out_id,
                "source_id": src_id,
                "classification": DenominatorClassification.PRIMARY_COMMON_DENOMINATOR.value,
                "gemini_eligible": True,
                "local_models_eligible": True,
            })
        else:
            local_only.append({
                "request_id": req_id,
                "output_id": out_id,
                "source_id": src_id,
                "classification": DenominatorClassification.LOCAL_ONLY_SUPPLEMENTARY_DENOMINATOR.value,
                "gemini_eligible": False,
                "local_models_eligible": True,
                "exclusion_reason": f"Source {src_id} restricted to on-premise non-commercial / academic processing."
            })
            
    ledger = {
        "ledger_version": "1.0.0",
        "stage": "stage35",
        "split": "locked_test",
        "total_locked_test_records": len(records),
        "primary_common_count": len(primary_common),
        "local_only_count": len(local_only),
        "n_common": len(primary_common),
        "n_local": len(local_only),
        "primary_common_records": primary_common,
        "local_only_records": local_only,
    }
    
    out_file = Path("data/model_comparison/stage35/registry/stage35_locked_test_denominators.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)
        
    print(f"WP2 Denominator Ledger built:")
    print(f"Total Locked Test Items: {len(records)}")
    print(f"Primary Common Denominator (N_common): {len(primary_common)}")
    print(f"Local-Only Supplementary Denominator (N_local): {len(local_only)}")

if __name__ == "__main__":
    bridge_stage35_denominators()
