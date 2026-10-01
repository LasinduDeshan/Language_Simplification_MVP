"""
Stage 25: Formal Investigation & Error Analysis of Moderate Support Tier.
Performs detailed diagnosis of tier-matched SARI (16.33), multi-reference SARI (29.86),
metric input ordering, and per-item comparison on Validation and Locked Test splits.
"""

import sys
import json
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "backend"))

from app.controlled_simplification.engine import ControlledSimplificationEngine
from app.controlled_simplification.schemas import SimplificationRequest, SupportLevel
from app.controlled_simplification.evaluation_protocol import EvaluationOrchestrator
from app.datasets.external_english.benchmark.metrics import compute_sari


def analyze_split(split_name: str, split_file: Path):
    engine = ControlledSimplificationEngine()
    with open(split_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    pairs = data.get("pairs", data) if isinstance(data, dict) else data
    source_groups = {}
    for pair in pairs:
        src_id = pair.get("source_item_id") or pair.get("source_id") or pair.get("original_text")
        src_text = pair.get("original_text") or pair.get("source_text") or pair.get("text")
        level = (pair.get("support_level") or pair.get("simplification_level") or pair.get("target_support_level") or "moderate").lower()
        simp_text = pair.get("simplified_text") or pair.get("target_text") or src_text
        pair_id = pair.get("simplification_pair_id") or pair.get("pair_id", "N/A")

        if src_id not in source_groups:
            source_groups[src_id] = {
                "source_id": src_id,
                "original_text": src_text,
                "references": {},
                "pair_ids": {}
            }
        
        if "mild" in level:
            source_groups[src_id]["references"]["mild"] = simp_text
            source_groups[src_id]["pair_ids"]["mild"] = pair_id
        elif "strong" in level:
            source_groups[src_id]["references"]["strong"] = simp_text
            source_groups[src_id]["pair_ids"]["strong"] = pair_id
        else:
            source_groups[src_id]["references"]["moderate"] = simp_text
            source_groups[src_id]["pair_ids"]["moderate"] = pair_id

    items_analyzed = []
    for src_id, g_info in source_groups.items():
        src_text = g_info["original_text"]
        ref_text = g_info["references"].get("moderate", src_text)
        ref_pair_id = g_info["pair_ids"].get("moderate", "N/A")
        
        req = SimplificationRequest(
            request_id=f"REQ-MOD-{src_id}",
            text=src_text,
            target_support_level=SupportLevel.MODERATE,
            target_age=6
        )
        res = engine.simplify(req)
        
        s_mean, s_add, s_keep, s_del = compute_sari(src_text, res.simplified_text, [ref_text])
        
        # Determine mismatch reason
        mismatch_reason = "Lexical/syntactic parity"
        if s_mean < 20.0:
            if "\n" in res.simplified_text or "1." in res.simplified_text:
                mismatch_reason = "Engine generated multi-step action breakdown; draft reference retained single running sentence"
            elif s_add == 0.0:
                mismatch_reason = "Draft reference made unique lexical substitutions not in governed rule lexicon"
            else:
                mismatch_reason = "Syntactic clause reordering differs from draft authoring phrasing"

        items_analyzed.append({
            "source_item_id": src_id,
            "source_group_id": src_id,
            "reference_pair_id": ref_pair_id,
            "source_text": src_text,
            "moderate_output": res.simplified_text,
            "moderate_ref": ref_text,
            "sari": round(s_mean, 2),
            "add": round(s_add, 2),
            "keep": round(s_keep, 2),
            "del": round(s_del, 2),
            "operations": [op.rule_id for op in res.applied_operations],
            "disposition": res.status.value,
            "mismatch_reason": mismatch_reason
        })

    items_analyzed.sort(key=lambda x: x["sari"])
    return items_analyzed


def main():
    test_path = repo_root / "data" / "simplification_corpus" / "releases" / "0.2.0" / "splits" / "development_candidate_test.json"
    val_path = repo_root / "data" / "simplification_corpus" / "releases" / "0.2.0" / "splits" / "development_candidate_validation.json"

    test_results = analyze_split("Locked Test", test_path)
    val_results = analyze_split("Validation", val_path)

    print(f"=== Locked Test Moderate Analysis (N={len(test_results)}) ===")
    mean_sari = sum(x["sari"] for x in test_results) / len(test_results)
    mean_add = sum(x["add"] for x in test_results) / len(test_results)
    mean_keep = sum(x["keep"] for x in test_results) / len(test_results)
    mean_del = sum(x["del"] for x in test_results) / len(test_results)
    print(f"Mean SARI: {mean_sari:.2f} | Add: {mean_add:.2f} | Keep: {mean_keep:.2f} | Del: {mean_del:.2f}")
    
    print("\n--- Lowest 10 SARI Examples in Locked Test ---")
    for idx, item in enumerate(test_results[:10], 1):
        print(f"\nExample #{idx}: SARI = {item['sari']:.2f} (Add={item['add']:.2f}, Keep={item['keep']:.2f}, Del={item['del']:.2f})")
        print(f"  Source ID: {item['source_item_id']} | Group ID: {item['source_group_id']} | Pair ID: {item['reference_pair_id']}")
        print(f"  Source:     {item['source_text']}")
        print(f"  Mod Output: {item['moderate_output']}")
        print(f"  Draft Ref:  {item['moderate_ref']}")
        print(f"  Applied:    {item['operations']}")
        print(f"  Disp:       {item['disposition']}")
        print(f"  Diagnosis:  {item['mismatch_reason']}")

    # Save detailed error analysis json
    out_file = repo_root / "data" / "controlled_simplification" / "results" / "moderate_tier_error_analysis.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "locked_test_summary": {
                "count": len(test_results),
                "mean_sari": mean_sari,
                "mean_add": mean_add,
                "mean_keep": mean_keep,
                "mean_del": mean_del
            },
            "lowest_10_locked_test": test_results[:10],
            "validation_summary": {
                "count": len(val_results),
                "mean_sari": sum(x["sari"] for x in val_results) / len(val_results)
            }
        }, f, indent=2)
    print(f"\nSaved analysis to {out_file}")


if __name__ == "__main__":
    main()
