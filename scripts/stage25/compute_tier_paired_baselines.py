"""
Stage 25: Compute complete 6x3 baseline evaluation matrix and perform full 900-pair dataset defect audit.
"""

import sys
import json
import re
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "backend"))

from app.baseline_simplification.runner import BaselineRunner
from app.controlled_simplification.engine import ControlledSimplificationEngine
from app.controlled_simplification.schemas import SimplificationRequest, SupportLevel
from app.controlled_simplification.evaluation_protocol import bootstrap_ci
from app.datasets.external_english.benchmark.metrics import compute_sari, compute_bleu


def run_6x3_matrix():
    test_path = repo_root / "data" / "simplification_corpus" / "releases" / "0.2.0" / "splits" / "development_candidate_test.json"
    with open(test_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pairs = data.get("pairs", data) if isinstance(data, dict) else data
    source_groups = {}
    for pair in pairs:
        src_id = pair.get("source_item_id") or pair.get("source_id") or pair.get("original_text")
        src_text = pair.get("original_text") or pair.get("source_text") or pair.get("text")
        level = (pair.get("support_level") or pair.get("simplification_level") or pair.get("target_support_level") or "moderate").lower()
        simp_text = pair.get("simplified_text") or pair.get("target_text") or src_text
        
        if src_id not in source_groups:
            source_groups[src_id] = {"original_text": src_text, "mild": src_text, "moderate": src_text, "strong": src_text}
        if "mild" in level:
            source_groups[src_id]["mild"] = simp_text
        elif "strong" in level:
            source_groups[src_id]["strong"] = simp_text
        else:
            source_groups[src_id]["moderate"] = simp_text

    runner = BaselineRunner()
    engine = ControlledSimplificationEngine()
    baselines = ["B0", "B1", "B2", "B3", "B4", "B5"]

    sources = [g["original_text"] for g in source_groups.values()]
    mild_refs = [g["mild"] for g in source_groups.values()]
    mod_refs = [g["moderate"] for g in source_groups.values()]
    str_refs = [g["strong"] for g in source_groups.values()]

    matrix_results = {}
    from app.baseline_simplification.schemas import BaselineMethodId
    for bid in baselines:
        b_inst = runner.baselines[BaselineMethodId(bid)]
        preds = []
        for s in sources:
            res = b_inst.simplify(s)
            simp_t = res.simplified_text if hasattr(res, "simplified_text") else str(res)
            preds.append(simp_t)
        
        # SARI lists
        sari_mild = [compute_sari(s, p, [r])[0] for s, p, r in zip(sources, preds, mild_refs)]
        sari_mod = [compute_sari(s, p, [r])[0] for s, p, r in zip(sources, preds, mod_refs)]
        sari_str = [compute_sari(s, p, [r])[0] for s, p, r in zip(sources, preds, str_refs)]
        
        # BLEU lists
        bleu_mild = [compute_bleu(p, [r]) for p, r in zip(preds, mild_refs)]
        bleu_mod = [compute_bleu(p, [r]) for p, r in zip(preds, mod_refs)]
        bleu_str = [compute_bleu(p, [r]) for p, r in zip(preds, str_refs)]

        matrix_results[bid] = {
            "mild_sari": sum(sari_mild) / len(sari_mild),
            "mod_sari": sum(sari_mod) / len(sari_mod),
            "str_sari": sum(sari_str) / len(sari_str),
            "mild_bleu": sum(bleu_mild) / len(bleu_mild),
            "mod_bleu": sum(bleu_mod) / len(bleu_mod),
            "str_bleu": sum(bleu_str) / len(bleu_str),
            "mild_sari_list": sari_mild,
            "mod_sari_list": sari_mod,
            "str_sari_list": sari_str
        }

    # Stage 25 per-tier runs
    s25_mild_preds = [engine.simplify(SimplificationRequest(request_id=f"S25-M-{i}", text=s, target_support_level=SupportLevel.MILD)).simplified_text for i, s in enumerate(sources)]
    s25_mod_preds = [engine.simplify(SimplificationRequest(request_id=f"S25-O-{i}", text=s, target_support_level=SupportLevel.MODERATE)).simplified_text for i, s in enumerate(sources)]
    s25_str_preds = [engine.simplify(SimplificationRequest(request_id=f"S25-S-{i}", text=s, target_support_level=SupportLevel.STRONG)).simplified_text for i, s in enumerate(sources)]

    s25_mild_sari = [compute_sari(s, p, [r])[0] for s, p, r in zip(sources, s25_mild_preds, mild_refs)]
    s25_mod_sari = [compute_sari(s, p, [r])[0] for s, p, r in zip(sources, s25_mod_preds, mod_refs)]
    s25_str_sari = [compute_sari(s, p, [r])[0] for s, p, r in zip(sources, s25_str_preds, str_refs)]

    # Cohen's d paired vs B0 under same reference protocol
    b0_mild = matrix_results["B0"]["mild_sari_list"]
    b0_mod = matrix_results["B0"]["mod_sari_list"]
    b0_str = matrix_results["B0"]["str_sari_list"]

    _, _, _, d_mild = bootstrap_ci(s25_mild_sari, b0_mild)
    _, _, _, d_mod = bootstrap_ci(s25_mod_sari, b0_mod)
    _, _, _, d_str = bootstrap_ci(s25_str_sari, b0_str)

    print("=== 6x3 Baseline SARI Matrix ===")
    print("Baseline | Mild Reference | Moderate Reference | Strong Reference")
    for bid in baselines:
        print(f"{bid:8} | {matrix_results[bid]['mild_sari']:14.2f} | {matrix_results[bid]['mod_sari']:18.2f} | {matrix_results[bid]['str_sari']:16.2f}")

    print(f"\nStage 25 Tier-Matched:")
    print(f"Mild vs B0 (Mild Ref): SARI {sum(s25_mild_sari)/len(s25_mild_sari):.2f} vs {matrix_results['B0']['mild_sari']:.2f} (Cohen's d = {d_mild:+.2f})")
    print(f"Mod vs B0 (Mod Ref):   SARI {sum(s25_mod_sari)/len(s25_mod_sari):.2f} vs {matrix_results['B0']['mod_sari']:.2f} (Cohen's d = {d_mod:+.2f})")
    print(f"Str vs B0 (Str Ref):   SARI {sum(s25_str_sari)/len(s25_str_sari):.2f} vs {matrix_results['B0']['str_sari']:.2f} (Cohen's d = {d_str:+.2f})")

    return matrix_results, (d_mild, d_mod, d_str)


def audit_corpus_dataset_defects():
    """Scan all 900 pairs in 0.2.0 release for task reformulations."""
    splits = [
        ("development_candidate_train.json", "train"),
        ("development_candidate_validation.json", "validation"),
        ("development_candidate_test.json", "locked_test")
    ]
    
    flagged = []
    total_pairs = 0
    
    for fname, sname in splits:
        fpath = repo_root / "data" / "simplification_corpus" / "releases" / "0.2.0" / "splits" / fname
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        pairs = data.get("pairs", data) if isinstance(data, dict) else data
        total_pairs += len(pairs)
        
        for p in pairs:
            src = p.get("original_text") or p.get("source_text") or ""
            ref = p.get("simplified_text") or p.get("target_text") or ""
            lvl = (p.get("support_level") or p.get("simplification_level") or "moderate").lower()
            pid = p.get("simplification_pair_id") or p.get("pair_id") or "N/A"
            sid = p.get("source_item_id") or p.get("source_id") or "N/A"
            
            # Detect task reformulation patterns
            is_qa_prompt = ("?" in ref and "?" not in src)
            is_pointing = ("point to" in ref.lower() and "point to" not in src.lower())
            is_choice = ("choose:" in ref.lower() or "choose the" in ref.lower())
            is_look_at = ("look at the picture" in ref.lower() and "look at" not in src.lower())
            
            if is_qa_prompt or is_pointing or is_choice or is_look_at:
                rec_type = "response_mode_adaptation" if is_pointing else ("activity_format_transformation" if is_choice else "question_generation")
                flagged.append({
                    "split": sname,
                    "source_item_id": sid,
                    "simplification_pair_id": pid,
                    "target_support_level": lvl,
                    "source_text": src,
                    "draft_reference_text": ref,
                    "simplification_pair_eligible": False,
                    "record_type": rec_type,
                    "review_reason": "response_mode_or_task_intent_changed",
                    "requires_expert_review": True
                })

    print(f"\n=== Corpus-Wide Dataset Issue Audit ===")
    print(f"Total pairs scanned: {total_pairs}")
    print(f"Total flagged task reformulations: {len(flagged)} ({len(flagged)/total_pairs*100:.1f}%)")
    
    # Save full audit
    out_file = repo_root / "data" / "simplification_corpus" / "releases" / "0.2.0" / "dataset_issue_register.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "register_id": "STAGE25-DATASET-DEFECT-001",
            "created_at": "2026-10-01T07:45:00Z",
            "stage": "Stage 25 — Controlled English Simplification Engine",
            "source_release": "Release 0.2.0 (Stage 20 Internal Benchmark)",
            "total_corpus_pairs_scanned": total_pairs,
            "total_flagged_reformulations": len(flagged),
            "flagged_percentage": f"{len(flagged)/total_pairs*100:.2f}%",
            "governance_disposition": "Locked test benchmark preserved unmodified for Stage 25; dataset defects registered for remediation in Stage 26 / expert review",
            "taxonomy_classification_future": [
                "text_simplification",
                "instruction_rephrasing",
                "activity_format_transformation",
                "question_generation",
                "response_mode_adaptation"
            ],
            "flagged_records": flagged
        }, f, indent=2)
    print(f"Saved full corpus defect register to {out_file}")


if __name__ == "__main__":
    run_6x3_matrix()
    audit_corpus_dataset_defects()
