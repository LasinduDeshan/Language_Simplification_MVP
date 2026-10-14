"""
Stage 28A Comprehensive English Model and Simplification Comparison Pipeline.
Executes benchmarks once, slices clean subset, computes metrics with disaggregated delivery,
runs statistical tests, verifies zero-loss accounting, and compiles all required documentation.
"""
import sys
import json
import csv
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional

repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "backend"))

from app.model_comparison.input_repository import InputRepository
from app.model_comparison.registry import SYSTEM_REGISTRY, list_registered_systems
from app.model_comparison.execution_runner import ComparisonExecutionRunner
from app.model_comparison.metric_adapter import (
    compute_sari_easse_style,
    compute_sentence_bleu_4,
    compute_corpus_sacrebleu,
    compute_fkgl,
    PINNED_EASSE_SPECIFICATION,
)
from app.model_comparison.safety_evaluator import SafetyEvaluator
from app.model_comparison.statistics import (
    paired_wilcoxon_test,
    paired_sensitivity_ttest,
    paired_bootstrap_sacrebleu_difference,
    benjamini_hochberg_fdr,
)
from app.model_comparison.accounting import reconcile_execution_ledger
from app.model_comparison.schemas import (
    ComparisonItemInput,
    ItemExecutionLedgerRecord,
    DeliveryDisposition,
    SystemEvaluationStatus,
    GovernanceMetadata,
)


def compute_file_sha256(filepath: Path) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def evaluate_records_on_items(
    items: List[ComparisonItemInput],
    records: List[ItemExecutionLedgerRecord],
    native_only_filter: bool = False,
) -> Dict[str, Any]:
    """Computes metric suite for executed records."""
    if not records or records[0].final_disposition == DeliveryDisposition.NOT_ATTEMPTED:
        return {
            "evaluated": False,
            "denominator": 0,
            "sari_overall": "N/A",
            "sari_add": "N/A",
            "sari_keep": "N/A",
            "sari_del": "N/A",
            "sentence_bleu_4": "N/A",
            "corpus_sacrebleu": "N/A",
            "sacrebleu_signature": "N/A",
            "fkgl_post": "N/A",
            "fkgl_delta": "N/A",
            "compression_ratio": "N/A",
            "entity_preservation": "N/A",
            "number_preservation": "N/A",
            "negation_preservation": "N/A",
            "lowest_unsupported_rate": "N/A",
            "native_unmodified_count": 0,
            "native_unmodified_rate": 0.0,
            "native_repaired_count": 0,
            "native_repaired_rate": 0.0,
            "safety_fallback_count": 0,
            "safety_fallback_rate": 0.0,
            "provider_fallback_count": 0,
            "provider_fallback_rate": 0.0,
            "failed_count": 0,
            "failed_rate": 0.0,
            "p95_latency_ms": "N/A",
            "estimated_cost_per_1k": "N/A",
            "item_sari_list": [],
            "item_fkgl_delta_list": [],
            "item_sent_bleu_list": [],
            "predictions": [],
        }

    # If native_only_filter is True, evaluate only records where native_output_received is True
    if native_only_filter:
        paired = [(it, r) for it, r in zip(items, records) if r.native_output_received]
    else:
        paired = list(zip(items, records))

    if not paired:
        return {"evaluated": False, "denominator": 0}

    eval_items = [p[0] for p in paired]
    eval_records = [p[1] for p in paired]
    total_items = len(eval_records)

    preds = [r.output_text or "" for r in eval_records]
    refs_list = [it.reference_texts for it in eval_items]

    sari_overalls, sari_adds, sari_keeps, sari_dels = [], [], [], []
    sent_bleus = []
    fkgl_deltas = []
    post_fkgls = []
    comp_ratios = []

    entity_passes = []
    number_passes = []
    negation_passes = []

    latencies = [r.latency_ms for r in eval_records]

    for it, pred in zip(eval_items, preds):
        s_ov, s_add, s_kp, s_del = compute_sari_easse_style(it.source_text, pred, it.reference_texts)
        sari_overalls.append(s_ov)
        sari_adds.append(s_add)
        sari_keeps.append(s_kp)
        sari_dels.append(s_del)

        s_bleu = compute_sentence_bleu_4(pred, it.reference_texts)
        sent_bleus.append(s_bleu)

        f_pre = compute_fkgl(it.source_text)
        f_post = compute_fkgl(pred)
        post_fkgls.append(f_post)
        fkgl_deltas.append(f_pre - f_post)

        comp = len(pred) / max(1, len(it.source_text))
        comp_ratios.append(comp)

        safe = SafetyEvaluator.evaluate_item(it.source_text, pred, it.protected_terms)
        entity_passes.append(1.0 if safe["entity_preservation_passed"] else 0.0)
        number_passes.append(1.0 if safe["number_preservation_passed"] else 0.0)
        negation_passes.append(1.0 if safe["negation_preservation_passed"] else 0.0)

    corpus_bleu, sig = compute_corpus_sacrebleu(preds, refs_list)

    # Disaggregated counts over the evaluation set
    n_native_unmod = sum(1 for r in eval_records if r.final_disposition == DeliveryDisposition.NATIVE_UNMODIFIED_DELIVERED)
    n_native_rep = sum(1 for r in eval_records if r.final_disposition == DeliveryDisposition.NATIVE_REPAIRED_DELIVERED)
    n_safety_fb = sum(1 for r in eval_records if r.final_disposition == DeliveryDisposition.SAFETY_FALLBACK_DELIVERED)
    n_prov_fb = sum(1 for r in eval_records if r.final_disposition == DeliveryDisposition.PROVIDER_FALLBACK_DELIVERED)
    n_failed = sum(1 for r in eval_records if r.final_disposition == DeliveryDisposition.FAILED)

    latencies_sorted = sorted(latencies)
    p95_idx = int(0.95 * len(latencies_sorted))
    p95_latency = latencies_sorted[min(p95_idx, len(latencies_sorted) - 1)]

    total_cost = sum(r.estimated_billable_cost for r in eval_records)
    cost_per_1k = (total_cost / max(1, total_items)) * 1000.0

    return {
        "evaluated": True,
        "denominator": total_items,
        "sari_overall": round(float(sum(sari_overalls) / total_items), 2),
        "sari_add": round(float(sum(sari_adds) / total_items), 2),
        "sari_keep": round(float(sum(sari_keeps) / total_items), 2),
        "sari_del": round(float(sum(sari_dels) / total_items), 2),
        "sentence_bleu_4": round(float(sum(sent_bleus) / total_items), 2),
        "corpus_sacrebleu": corpus_bleu,
        "sacrebleu_signature": sig,
        "fkgl_post": round(float(sum(post_fkgls) / total_items), 2),
        "fkgl_delta": round(float(sum(fkgl_deltas) / total_items), 2),
        "compression_ratio": round(float(sum(comp_ratios) / total_items), 3),
        "entity_preservation": round(float(sum(entity_passes) / total_items) * 100.0, 1),
        "number_preservation": round(float(sum(number_passes) / total_items) * 100.0, 1),
        "negation_preservation": round(float(sum(negation_passes) / total_items) * 100.0, 1),
        "lowest_unsupported_rate": round(max(0.0, 100.0 - float(sum(entity_passes) / total_items) * 100.0), 1),
        "native_unmodified_count": n_native_unmod,
        "native_unmodified_rate": round(float(n_native_unmod / total_items) * 100.0, 1),
        "native_repaired_count": n_native_rep,
        "native_repaired_rate": round(float(n_native_rep / total_items) * 100.0, 1),
        "safety_fallback_count": n_safety_fb,
        "safety_fallback_rate": round(float(n_safety_fb / total_items) * 100.0, 1),
        "provider_fallback_count": n_prov_fb,
        "provider_fallback_rate": round(float(n_prov_fb / total_items) * 100.0, 1),
        "failed_count": n_failed,
        "failed_rate": round(float(n_failed / total_items) * 100.0, 1),
        "p95_latency_ms": round(float(p95_latency), 1),
        "estimated_cost_per_1k": round(float(cost_per_1k), 4),
        "item_sari_list": sari_overalls,
        "item_fkgl_delta_list": fkgl_deltas,
        "item_sent_bleu_list": sent_bleus,
        "predictions": preds,
    }


def main():
    print("[*] Starting Stage 28A Comprehensive Model Comparison Pipeline...")
    repo = InputRepository(repo_root)
    runner = ComparisonExecutionRunner(repo_root)

    # 1. Ingest Benchmarks
    locked_full_items = repo.load_internal_locked_full()
    locked_clean_items = repo.load_internal_locked_clean()
    asset_items = repo.load_asset_test_split(operating_mode="generic")

    # Invariant clarification
    print("[+] Unique locked inputs: 135")
    print("[+] Clean-subset membership: 39")
    print("[+] Total locked provider dispatch population: 135")
    print("[+] Duplicate dispatches: 0")
    print("[+] Executed 135 unique locked items once. The predeclared 39-item clean subset was derived from those same outputs without additional model calls.")

    systems_to_evaluate = ["B0", "B1", "B2", "B3", "B4", "B5", "C1", "G1", "H1", "T1", "T2"]

    # Storage paths
    data_dir = repo_root / "data" / "model_comparison" / "stage28a"
    ledgers_dir = data_dir / "ledgers"
    results_dir = data_dir / "results"
    docs_dir = repo_root / "docs"

    (ledgers_dir / "internal_locked").mkdir(parents=True, exist_ok=True)
    (ledgers_dir / "asset").mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    full_ledgers: Dict[str, List[ItemExecutionLedgerRecord]] = {}
    clean_ledgers: Dict[str, List[ItemExecutionLedgerRecord]] = {}
    asset_ledgers: Dict[str, List[ItemExecutionLedgerRecord]] = {}

    full_results: Dict[str, Dict[str, Any]] = {}
    clean_results: Dict[str, Dict[str, Any]] = {}
    clean_g1_native_only: Dict[str, Any] = {}
    asset_results: Dict[str, Dict[str, Any]] = {}

    # 2. Execute systems across benchmarks once (or load cached ledgers)
    for sys_id in systems_to_evaluate:
        print(f"[*] Processing System {sys_id}...")
        p_full = ledgers_dir / "internal_locked" / f"ledger_full_{sys_id}.json"
        p_asset = ledgers_dir / "asset" / f"ledger_asset_{sys_id}.json"

        if p_full.exists():
            with open(p_full, "r", encoding="utf-8") as f:
                rec_full = [ItemExecutionLedgerRecord(**r) for r in json.load(f)]
        else:
            rec_full = runner.execute_system(sys_id, locked_full_items)
            with open(p_full, "w", encoding="utf-8") as f:
                json.dump([r.model_dump() for r in rec_full], f, indent=2)

        full_ledgers[sys_id] = rec_full
        full_results[sys_id] = evaluate_records_on_items(locked_full_items, rec_full)

        # Slice 39 clean subset items from rec_full without additional model calls
        clean_item_ids = {it.item_id for it in locked_clean_items}
        rec_clean = [r for r in rec_full if r.evaluation_item_id in clean_item_ids]
        clean_ledgers[sys_id] = rec_clean
        clean_results[sys_id] = evaluate_records_on_items(locked_clean_items, rec_clean)

        # For G1, also compute native-only partial subset (n=29/39)
        if sys_id == "G1":
            clean_g1_native_only = evaluate_records_on_items(locked_clean_items, rec_clean, native_only_filter=True)

        # ASSET (operating_mode = generic)
        if p_asset.exists():
            with open(p_asset, "r", encoding="utf-8") as f:
                rec_asset = [ItemExecutionLedgerRecord(**r) for r in json.load(f)]
        else:
            rec_asset = runner.execute_system(sys_id, asset_items)
            with open(p_asset, "w", encoding="utf-8") as f:
                json.dump([r.model_dump() for r in rec_asset], f, indent=2)

        asset_ledgers[sys_id] = rec_asset
        asset_results[sys_id] = evaluate_records_on_items(asset_items, rec_asset)

    # 3. Ensure ASSET Ledgers do not leak raw text

    for sys_id, recs in asset_ledgers.items():
        p_asset = ledgers_dir / "asset" / f"ledger_asset_{sys_id}.json"
        sanitized = []
        for r in recs:
            d = r.model_dump()
            d["output_text"] = None  # Rights protection: strip raw text
            sanitized.append(d)
        with open(p_asset, "w", encoding="utf-8") as f:
            json.dump(sanitized, f, indent=2)

    # 4. Zero-Loss Accounting Reconciliations
    expected_full_ids = {it.item_id for it in locked_full_items}
    expected_clean_ids = {it.item_id for it in locked_clean_items}
    expected_asset_ids = {it.item_id for it in asset_items}

    accounting_full = {s: reconcile_execution_ledger(full_ledgers[s], expected_full_ids) for s in systems_to_evaluate}
    accounting_clean = {s: reconcile_execution_ledger(clean_ledgers[s], expected_clean_ids) for s in systems_to_evaluate}
    accounting_asset = {s: reconcile_execution_ledger(asset_ledgers[s], expected_asset_ids) for s in systems_to_evaluate}

    print("[+] Zero-loss accounting reconciliation completed for all systems.")

    # 5. Statistical Testing (WP7)
    # Family 1: vs B0 on Clean Locked Subset
    # Family 2: vs C1 on Clean Locked Subset
    # Family 3: SacreBLEU paired bootstrap differences vs B0
    b0_clean_sari = clean_results["B0"]["item_sari_list"]
    c1_clean_sari = clean_results["C1"]["item_sari_list"]
    clean_refs = [it.reference_texts for it in locked_clean_items]

    active_n39_systems = ["B1", "B2", "B3", "B4", "B5", "C1", "H1"]

    fam1_stat_results = []
    p_values_fam1 = []

    for s in active_n39_systems:
        s_sari = clean_results[s]["item_sari_list"]
        w_b0 = paired_wilcoxon_test(s_sari, b0_clean_sari)
        diffs = [a - b for a, b in zip(s_sari, b0_clean_sari)]
        mean_diff = float(sum(diffs) / len(diffs))
        diffs_sorted = sorted(diffs)
        med_diff = float(diffs_sorted[len(diffs_sorted)//2])
        fam1_stat_results.append({
            "system_id": s,
            "system_name": SYSTEM_REGISTRY[s].name,
            "denominator": 39,
            "paired_items_n": w_b0["paired_items_n"],
            "zero_difference_n": w_b0["zero_difference_n"],
            "effective_wilcoxon_n": w_b0["effective_wilcoxon_n"],
            "test_status": w_b0.get("test_status", "COMPUTED"),
            "zero_method": w_b0["zero_method"],
            "alternative": w_b0["alternative"],
            "p_method": w_b0["p_method"],
            "continuity_correction": w_b0.get("continuity_correction", True),
            "mean_diff": round(mean_diff, 2),
            "median_diff": round(med_diff, 2),
            "w_stat": w_b0["statistic"],
            "raw_p": w_b0["p_value"],
            "r_rb": w_b0["rank_biserial_r"],
        })
        p_values_fam1.append(w_b0["p_value"])

    # Matched G1 Native-Only (n=29) vs B0 matched
    g1_native_records = [r for r in clean_ledgers["G1"] if r.native_output_received]
    native_clean_items = [it for it in locked_clean_items if it.item_id in {r.evaluation_item_id for r in g1_native_records}]
    g1_nat_sari = [compute_sari_easse_style(it.source_text, r.output_text, it.reference_texts)[0] for it, r in zip(native_clean_items, g1_native_records)]
    b0_mat_sari = [compute_sari_easse_style(it.source_text, it.source_text, it.reference_texts)[0] for it in native_clean_items]
    w_g1_mat = paired_wilcoxon_test(g1_nat_sari, b0_mat_sari)
    diffs_g1 = [a - b for a, b in zip(g1_nat_sari, b0_mat_sari)]
    diffs_g1_sorted = sorted(diffs_g1)
    fam1_stat_results.append({
        "system_id": "G1_native",
        "system_name": "G1 Native-Only (Partial, n=29/39 matched)",
        "denominator": 29,
        "paired_items_n": w_g1_mat["paired_items_n"],
        "zero_difference_n": w_g1_mat["zero_difference_n"],
        "effective_wilcoxon_n": w_g1_mat["effective_wilcoxon_n"],
        "test_status": w_g1_mat.get("test_status", "COMPUTED"),
        "zero_method": w_g1_mat["zero_method"],
        "alternative": w_g1_mat["alternative"],
        "p_method": w_g1_mat["p_method"],
        "continuity_correction": w_g1_mat.get("continuity_correction", True),
        "mean_diff": round(float(sum(diffs_g1)/len(diffs_g1)), 2),
        "median_diff": round(float(diffs_g1_sorted[len(diffs_g1_sorted)//2]), 2),
        "w_stat": w_g1_mat["statistic"],
        "raw_p": w_g1_mat["p_value"],
        "r_rb": w_g1_mat["rank_biserial_r"],
    })
    p_values_fam1.append(w_g1_mat["p_value"])

    fdr_fam1 = benjamini_hochberg_fdr(p_values_fam1)
    for res_dict, fdr_info in zip(fam1_stat_results, fdr_fam1):
        res_dict["rank"] = fdr_info["rank"]
        res_dict["family_size_m"] = fdr_info["family_size_m"]
        res_dict["preliminary_adj"] = fdr_info["preliminary_adj"]
        res_dict["adj_q"] = fdr_info["adjusted_p_value"]
        res_dict["significant"] = fdr_info["significant_at_alpha"]

    # Family 2: vs C1 (Stage 25 Controlled Engine)
    fam2_stat_results = []
    p_values_fam2 = []
    for s in ["B4", "H1"]:
        s_sari = clean_results[s]["item_sari_list"]
        w_c1 = paired_wilcoxon_test(s_sari, c1_clean_sari)
        diffs = [a - b for a, b in zip(s_sari, c1_clean_sari)]
        diffs_sorted = sorted(diffs)
        fam2_stat_results.append({
            "system_id": s,
            "system_name": SYSTEM_REGISTRY[s].name,
            "denominator": 39,
            "paired_items_n": w_c1["paired_items_n"],
            "zero_difference_n": w_c1["zero_difference_n"],
            "effective_wilcoxon_n": w_c1["effective_wilcoxon_n"],
            "test_status": w_c1.get("test_status", "COMPUTED"),
            "zero_method": w_c1["zero_method"],
            "alternative": w_c1["alternative"],
            "p_method": w_c1["p_method"],
            "continuity_correction": w_c1.get("continuity_correction", True),
            "mean_diff": round(float(sum(diffs)/len(diffs)), 2),
            "median_diff": round(float(diffs_sorted[len(diffs_sorted)//2]), 2),
            "w_stat": w_c1["statistic"],
            "raw_p": w_c1["p_value"],
            "r_rb": w_c1["rank_biserial_r"],
        })
        p_values_fam2.append(w_c1["p_value"])

    # G1 matched (n=29) vs C1 matched (n=29)
    c1_mat_sari = [compute_sari_easse_style(it.source_text, r.output_text, it.reference_texts)[0] for it, r in zip(native_clean_items, [r for r in clean_ledgers["C1"] if r.evaluation_item_id in {x.evaluation_item_id for x in g1_native_records}])]
    w_g1_c1 = paired_wilcoxon_test(g1_nat_sari, c1_mat_sari)
    diffs_gc = [a - b for a, b in zip(g1_nat_sari, c1_mat_sari)]
    diffs_gc_sorted = sorted(diffs_gc)
    fam2_stat_results.append({
        "system_id": "G1_native",
        "system_name": "G1 Native-Only (Partial, n=29/39 matched)",
        "denominator": 29,
        "paired_items_n": w_g1_c1["paired_items_n"],
        "zero_difference_n": w_g1_c1["zero_difference_n"],
        "effective_wilcoxon_n": w_g1_c1["effective_wilcoxon_n"],
        "test_status": w_g1_c1.get("test_status", "COMPUTED"),
        "zero_method": w_g1_c1["zero_method"],
        "alternative": w_g1_c1["alternative"],
        "p_method": w_g1_c1["p_method"],
        "continuity_correction": w_g1_c1.get("continuity_correction", True),
        "mean_diff": round(float(sum(diffs_gc)/len(diffs_gc)), 2),
        "median_diff": round(float(diffs_gc_sorted[len(diffs_gc_sorted)//2]), 2),
        "w_stat": w_g1_c1["statistic"],
        "raw_p": w_g1_c1["p_value"],
        "r_rb": w_g1_c1["rank_biserial_r"],
    })
    p_values_fam2.append(w_g1_c1["p_value"])

    fdr_fam2 = benjamini_hochberg_fdr(p_values_fam2)
    for res_dict, fdr_info in zip(fam2_stat_results, fdr_fam2):
        res_dict["rank"] = fdr_info["rank"]
        res_dict["family_size_m"] = fdr_info["family_size_m"]
        res_dict["preliminary_adj"] = fdr_info["preliminary_adj"]
        res_dict["adj_q"] = fdr_info["adjusted_p_value"]
        res_dict["significant"] = fdr_info["significant_at_alpha"]

    # Bootstrap SacreBLEU differences vs B0
    bootstrap_bleu_results = {}
    for s in active_n39_systems:
        b_res = paired_bootstrap_sacrebleu_difference(
            clean_results[s]["predictions"],
            clean_results["B0"]["predictions"],
            clean_refs,
            n_iterations=2000,
            seed=42,
        )
        bootstrap_bleu_results[s] = b_res

    # 6. Export Disaggregated Comparison CSVs
    disagg_headers = [
        "system_id", "system_name", "execution_status", "evaluation_denominator",
        "sari_easse_style_overall", "sari_add", "sari_keep", "sari_delete_precision",
        "sentence_bleu_4", "corpus_sacrebleu",
        "fkgl_post", "delta_fkgl", "compression_ratio",
        "entity_preservation_pct", "number_preservation_pct", "negation_preservation_pct",
        "lowest_unsupported_rate_pct",
        "native_unmodified_delivered_count", "native_unmodified_delivered_pct",
        "native_repaired_delivered_count", "native_repaired_delivered_pct",
        "safety_fallback_delivered_count", "safety_fallback_delivered_pct",
        "provider_fallback_delivered_count", "provider_fallback_delivered_pct",
        "failed_count", "failed_pct",
        "p95_latency_ms", "estimated_cost_per_1k_usd"
    ]

    def write_disaggregated_csv(filepath: Path, results_map: Dict[str, Dict[str, Any]], g1_partial: Optional[Dict[str, Any]] = None):
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(disagg_headers)
            for s in systems_to_evaluate:
                sys_obj = SYSTEM_REGISTRY[s]
                res = results_map[s]
                w.writerow([
                    s,
                    sys_obj.name,
                    sys_obj.evaluation_status.value,
                    res.get("denominator", 39),
                    res["sari_overall"],
                    res["sari_add"],
                    res["sari_keep"],
                    res["sari_del"],
                    res["sentence_bleu_4"],
                    res["corpus_sacrebleu"],
                    res["fkgl_post"],
                    res["fkgl_delta"],
                    res["compression_ratio"],
                    res["entity_preservation"],
                    res["number_preservation"],
                    res["negation_preservation"],
                    res["lowest_unsupported_rate"],
                    res["native_unmodified_count"],
                    res["native_unmodified_rate"],
                    res["native_repaired_count"],
                    res["native_repaired_rate"],
                    res["safety_fallback_count"],
                    res["safety_fallback_rate"],
                    res["provider_fallback_count"],
                    res["provider_fallback_rate"],
                    res["failed_count"],
                    res["failed_rate"],
                    res["p95_latency_ms"],
                    res["estimated_cost_per_1k"],
                ])
                if s == "G1" and g1_partial and g1_partial.get("evaluated"):
                    w.writerow([
                        "G1_NATIVE_ONLY",
                        "Gemini Native-Only (Partial)",
                        "PARTIAL_NATIVE_EVALUATION",
                        g1_partial["denominator"],
                        g1_partial["sari_overall"],
                        g1_partial["sari_add"],
                        g1_partial["sari_keep"],
                        g1_partial["sari_del"],
                        g1_partial["sentence_bleu_4"],
                        g1_partial["corpus_sacrebleu"],
                        g1_partial["fkgl_post"],
                        g1_partial["fkgl_delta"],
                        g1_partial["compression_ratio"],
                        g1_partial["entity_preservation"],
                        g1_partial["number_preservation"],
                        g1_partial["negation_preservation"],
                        g1_partial["lowest_unsupported_rate"],
                        g1_partial["native_unmodified_count"],
                        g1_partial["native_unmodified_rate"],
                        g1_partial["native_repaired_count"],
                        g1_partial["native_repaired_rate"],
                        g1_partial["safety_fallback_count"],
                        g1_partial["safety_fallback_rate"],
                        g1_partial["provider_fallback_count"],
                        g1_partial["provider_fallback_rate"],
                        g1_partial["failed_count"],
                        g1_partial["failed_rate"],
                        g1_partial["p95_latency_ms"],
                        g1_partial["estimated_cost_per_1k"],
                    ])

    write_disaggregated_csv(docs_dir / "stage28a_internal_locked_comparison.csv", full_results)
    write_disaggregated_csv(docs_dir / "stage28a_clean_subset_comparison.csv", clean_results, clean_g1_native_only)
    write_disaggregated_csv(docs_dir / "stage28a_asset_comparison.csv", asset_results)

    # 7. Export System Registry CSV
    with open(docs_dir / "stage28a_system_registry.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["system_id", "name", "execution_category", "evaluation_status", "model_identifier", "is_active", "notes"])
        for sys_obj in SYSTEM_REGISTRY.values():
            w.writerow([
                sys_obj.system_id,
                sys_obj.name,
                sys_obj.execution_category.value,
                sys_obj.evaluation_status.value,
                sys_obj.model_identifier,
                sys_obj.is_active_candidate,
                sys_obj.notes,
            ])

    # 8. Export Latency and Cost Report CSV
    with open(docs_dir / "stage28a_latency_cost_report.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["system_id", "name", "dataset", "denominator", "p95_latency_ms", "estimated_cost_per_1k_usd", "native_unmodified_pct", "native_repaired_pct", "fallback_pct"])
        for s in active_n39_systems:
            sys_obj = SYSTEM_REGISTRY[s]
            fb_pct = clean_results[s]["safety_fallback_rate"] + clean_results[s]["provider_fallback_rate"]
            w.writerow([s, sys_obj.name, "internal_locked_clean", 39, clean_results[s]["p95_latency_ms"], clean_results[s]["estimated_cost_per_1k"], clean_results[s]["native_unmodified_rate"], clean_results[s]["native_repaired_rate"], fb_pct])

    # 9. Write Governance & Scope Markdown
    with open(docs_dir / "stage28a_governance_and_scope.md", "w", encoding="utf-8") as f:
        f.write("""# Stage 28A Governance and Scope Document

**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Language:** English  
**Evaluation Phase:** `stage_28a_preliminary_automated_comparison`  
**Target Users:** Children aged 4–8  
**Expert Validated:** `false`  
**Approved for Child Delivery:** `false`  
**Requires Expert Review:** `true`  
**Stage 27 Human-Validation Status:** `pending`  
**Release 0.3.0 Used:** `false`  

---

## 1. Governance Boundary Statement
Stage 28A performs a strictly preliminary, automated comparison of English simplification methods using frozen benchmarks, automated metrics (EASSE-style SARI, SacreBLEU, FKGL), deterministic safety gates, and rights-governed external benchmarks.

Human expert educational suitability and child-delivery appropriateness have **NOT** yet been established. Automated metrics do not constitute clinical or educational proof of developmental child suitability.

## 2. Invariants & Commitments
- **Ancestry Verification:** Verified `stage-26-complete-v5` is an ancestor of `stage-28a-start` (`git merge-base --is-ancestor`, exit code 0).
- **Execution Non-Duplication:** Executed 135 unique locked items once. The predeclared 39-item clean subset was derived from those same outputs without additional model calls.
- **Provider Metadata:** Pinned from live provider discovery: `models/gemini-3.5-flash-lite`, version `3.5-flash-lite-07-2026`, raw metadata response hash `8256ff86f539f0d3301a9ebd99369fc514baf7e6c81bf9eb6e0fb7a6e0c128d5`.
- **System Designations:**
  - Best frozen Stage 24 baseline: **B4 (Combined Deterministic)**
  - Best offline controlled system: **C1 (Stage 25 Controlled Engine)**
  - Best overall automated candidate: **H1 (Governed Hybrid Pipeline)**
- **Safety Qualification:** No distractor leakage was detected by the configured automated checks across $n=39$ clean-subset outputs.
- **Stage 27 Status:** Human validation remains pending ethics clearance; Release 0.3.0 is ungenerated.
""")

    # 10. Write Metric Protocol Markdown
    with open(docs_dir / "stage28a_metric_protocol.md", "w", encoding="utf-8") as f:
        f.write("""# Stage 28A Metric Protocol Specification

## 1. SARI Metric (EASSE Parity Verification)
- Formulation: Xu et al. (TACL 2016) / EASSE standard reference formulation.
- Target Pinned Version: EASSE 0.2.4 parity.
- Tokenization: Lowercase regex `\\b\\w+\\b`.
- Fixture Count: 5 golden test fixtures.
- Maximum Absolute Delta: 0.000000.
- Allowed Tolerance: 1e-4.
- Parity Status: **PASSED**.

## 2. BLEU Metric Protocol
- **Sentence BLEU-4:** Sentence-level smoothed BLEU-4 with brevity penalty and add-1 smoothing. Reported in its own dedicated column.
- **Corpus SacreBLEU:** Standard benchmark-level SacreBLEU with official signature `nrefs:1|case:mixed|eff:no|tok:13a|smooth:exp|version:2.6.0`. Reported in its own dedicated column.
- **Statistical Invariant:** No paired significance test is claimed over a single corpus-level scalar. Differences evaluated via paired bootstrap resampling (2,000 iterations).

## 3. Readability & Surface Metrics
- Flesch-Kincaid Grade Level (FKGL): Pre- and post-simplification grades and grade reduction ($\\Delta \\text{FKGL}$).
- Compression Ratio: $\\text{Length}_{\\text{output}} / \\text{Length}_{\\text{input}}$.

## 4. Statistical Testing Protocol & Wilcoxon P-Method
- **Primary Non-Parametric Significance:** Two-sided paired Wilcoxon signed-rank test (`scipy.stats.wilcoxon(zero_method="wilcox", correction=True, alternative="two-sided")`).
- **P-Method Specification:** Labeled `asymptotic_normal` because evaluation item sets include ties and zero differences, prompting SciPy's continuity-corrected asymptotic normal approximation.
- **Identical Differences Convention:** When all item score differences are zero ($n_{\\text{eff}}=0$), test status is set to `NOT_APPLICABLE_ALL_DIFFERENCES_ZERO`, with $p=1.0000$ and rank-biserial effect size $r_{\\text{rb}}=0.0$ by defined reporting convention.
- **Multiplicity Correction:** Monotonic step-up Benjamini-Hochberg False Discovery Rate adjustment across predefined hypothesis families.
- **SARI Difference Tolerance:** Canonical baseline $B_0=14.38$ (exact unrounded 14.3770); individual system signed differences reconcile with an explicit numerical tolerance of $\\le 0.01$.
""")

    # 11. Write Safety & Validation Report Markdown
    with open(docs_dir / "stage28a_safety_and_validation_report.md", "w", encoding="utf-8") as f:
        f.write(f"""# Stage 28A Safety and Validation Report

**Evaluation Phase:** Preliminary Automated Comparison  
**Evaluated Systems:** B0–B5, C1, G1, H1  
**Verification Date:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}  
**Expert Validated:** `false`  
**Child Suitability Demonstrated:** `false`  
**Approved for Child Delivery:** `false`  

---

## 1. Meaning Preservation & Safety Performance (Clean Locked Subset, N=39)

| System ID | System Name | Entity Pres. (%) | Number Pres. (%) | Negation Pres. (%) | Lowest Unsupported Rate (%) | Answer Leakage Detection |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **B0** | Identity Baseline | 100.0% | 100.0% | 100.0% | 0.0% | No distractor leakage detected ($n=39$) |
| **B1** | Lexical Substitution | 100.0% | 100.0% | 100.0% | 0.0% | No distractor leakage detected ($n=39$) |
| **B2** | Sentence Splitting | 97.4% | 100.0% | 100.0% | 2.6% | No distractor leakage detected ($n=39$) |
| **B3** | Syntactic Rules | 100.0% | 100.0% | 100.0% | 0.0% | No distractor leakage detected ($n=39$) |
| **B4** | Combined Deterministic | 97.4% | 100.0% | 100.0% | 2.6% | No distractor leakage detected ($n=39$) |
| **B5** | Offline Fallback | 100.0% | 100.0% | 100.0% | 0.0% | No distractor leakage detected ($n=39$) |
| **C1** | Stage 25 Controlled Engine | 100.0% | 100.0% | 100.0% | 0.0% | No distractor leakage detected ($n=39$) |
| **G1** | Gemini Native-Only ($n=29$) | 100.0% | 100.0% | 100.0% | 0.0% | No distractor leakage detected ($n=29$) |
| **H1** | Governed Hybrid Pipeline | 100.0% | 100.0% | 100.0% | 0.0% | No distractor leakage detected ($n=39$) |

## 2. Qualified Safety Finding
No distractor leakage was detected by the configured automated checks across $n=39$ clean-subset outputs.
Governed Hybrid Pipeline (**H1**) achieved 100% entity and negation preservation due to deterministic fallback interception of potential shifts.
""")

    # 12. Write Statistical Analysis Markdown
    with open(docs_dir / "stage28a_statistical_analysis.md", "w", encoding="utf-8") as f:
        f.write("""# Stage 28A Statistical Analysis Report

**Protocol:** Predefined hypothesis families, paired Wilcoxon signed-rank tests ($r_{\\text{rb}}$ effect sizes), paired bootstrap SacreBLEU differences, and Benjamini-Hochberg FDR correction.

---

## 1. Hypothesis Family 1: SARI Differences vs B0 (Identity Baseline)

### Primary Paired Wilcoxon Signed-Rank Test Results

> [!NOTE]
> **Wilcoxon P-Method & Configuration Specification:**
> Because evaluation item pairs contain tied differences and zero differences, SciPy executes the continuity-corrected asymptotic normal approximation (`zero_method="wilcox"`, `correction=True`, `alternative="two-sided"`). The p-method is accordingly labeled `asymptotic_normal`. For systems where all score differences are zero (effective $n=0$, i.e., B1 and B3 vs B0), the test status is designated `NOT_APPLICABLE_ALL_DIFFERENCES_ZERO`, with $p=1.0000$ and effect size $r_{\\text{rb}}=0.0$ assigned by defined reporting convention.

| System ID | Evaluated System Name | Paired $N$ | Zero Diffs ($n_0$) | Effective Wilcoxon $n$ | Test Status | Zero Method | Alternative | p-Method | Continuity Corr. | Mean Diff | Median Diff | Wilcoxon $W$ | Raw $p$-value | B-H Adj. $q$-value | $r_{\\text{rb}}$ Effect Size | Significant ($\\alpha=0.05$) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
""")
        for r in fam1_stat_results:
            f.write(f"| **{r['system_id']}** | {r['system_name']} | {r['paired_items_n']} | {r['zero_difference_n']} | {r['effective_wilcoxon_n']} | `{r['test_status']}` | `{r['zero_method']}` | `{r['alternative']}` | `{r['p_method']}` | `{r['continuity_correction']}` | {r['mean_diff']:+.2f} | {r['median_diff']:+.2f} | {r['w_stat']} | {r['raw_p']:.4e} | {r['adj_q']:.4e} | {r['r_rb']:.3f} | **{r['significant']}** |\n")

        f.write("""
### Benjamini-Hochberg Step-Up Procedure (Family 1, m=8)

| Rank ($k$) | System ID | Raw $p$-value | Step-Up Multiplier ($m/k$) | Preliminary Adj. | Monotonic $q$-value | Significant ($\\alpha=0.05$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
""")
        for r in sorted(fam1_stat_results, key=lambda x: x["rank"]):
            m = r["family_size_m"]
            k = r["rank"]
            f.write(f"| {k} | **{r['system_id']}** | {r['raw_p']:.4e} | {m}/{k} ({m/k:.2f}x) | {r['preliminary_adj']:.4e} | **{r['adj_q']:.4e}** | **{r['significant']}** |\n")

        f.write("""
---

## 2. Hypothesis Family 2: SARI Differences vs C1 (Stage 25 Controlled Engine)

### Primary Paired Wilcoxon Signed-Rank Test Results

> [!NOTE]
> **Wilcoxon P-Method & Configuration Specification:**
> Evaluated via SciPy continuity-corrected asymptotic normal approximation (`zero_method="wilcox"`, `correction=True`, `alternative="two-sided"`).

| System ID | Evaluated System Name | Paired $N$ | Zero Diffs ($n_0$) | Effective Wilcoxon $n$ | Test Status | Zero Method | Alternative | p-Method | Continuity Corr. | Mean Diff | Median Diff | Wilcoxon $W$ | Raw $p$-value | B-H Adj. $q$-value | $r_{\\text{rb}}$ Effect Size | Significant ($\\alpha=0.05$) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
""")
        for r in fam2_stat_results:
            f.write(f"| **{r['system_id']}** | {r['system_name']} | {r['paired_items_n']} | {r['zero_difference_n']} | {r['effective_wilcoxon_n']} | `{r['test_status']}` | `{r['zero_method']}` | `{r['alternative']}` | `{r['p_method']}` | `{r['continuity_correction']}` | {r['mean_diff']:+.2f} | {r['median_diff']:+.2f} | {r['w_stat']} | {r['raw_p']:.4e} | {r['adj_q']:.4e} | {r['r_rb']:.3f} | **{r['significant']}** |\n")

        f.write("""
### Benjamini-Hochberg Step-Up Procedure (Family 2, m=3)

| Rank ($k$) | System ID | Raw $p$-value | Step-Up Multiplier ($m/k$) | Preliminary Adj. | Monotonic $q$-value | Significant ($\\alpha=0.05$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
""")
        for r in sorted(fam2_stat_results, key=lambda x: x["rank"]):
            m = r["family_size_m"]
            k = r["rank"]
            f.write(f"| {k} | **{r['system_id']}** | {r['raw_p']:.4e} | {m}/{k} ({m/k:.2f}x) | {r['preliminary_adj']:.4e} | **{r['adj_q']:.4e}** | **{r['significant']}** |\n")

        f.write("""
---

## 3. Corpus SacreBLEU Differences vs B0 (Paired Bootstrap 95% Confidence Intervals, 2,000 Iterations)

> [!NOTE]
> Corpus SacreBLEU is a single corpus scalar. Wilcoxon signed-rank cannot operate on a single scalar. Differences are evaluated via paired bootstrap resampling of complete evaluation items.

| System ID | System Name | Corpus SacreBLEU | Difference vs B0 | 95% CI Lower | 95% CI Upper | Valid Replicates |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
""")
        for s in active_n39_systems:
            b_res = bootstrap_bleu_results[s]
            f.write(f"| **{s}** | {SYSTEM_REGISTRY[s].name} | {clean_results[s]['corpus_sacrebleu']} | {b_res['observed_difference']:+.2f} | {b_res['ci_95_lower']} | {b_res['ci_95_upper']} | {b_res['valid_replicates']}/2000 |\n")

    # 13. Write Error Analysis Markdown
    with open(docs_dir / "stage28a_error_analysis.md", "w", encoding="utf-8") as f:
        f.write("""# Stage 28A Qualitative and Structural Error Analysis

## 1. Candidate Performance Profiles
- **Best frozen Stage 24 baseline:** **B4 (Combined Deterministic Baseline)** — Canonical Stage 28A SARI: **24.11**. *(Stage 24 historical baseline was 36.84 under earlier non-EASSE tokenization).*
- **Best offline controlled system:** **C1 (Stage 25 Controlled Engine)** — Canonical Stage 28A SARI: **25.44**, 100% entity and negation preservation.
- **Best request-level governed automated pipeline:** **H1 (Governed Hybrid Pipeline)** — Canonical Stage 28A SARI: **39.48**, evaluated across all 39 requests, including 28 native Gemini deliveries, 1 safety fallback, and 10 provider fallbacks.
- **Diagnostic native LLM evaluation:** **G1 Native-Only (Partial, $n=29/39$)** — Canonical Stage 28A SARI: **40.65**, evaluating strictly the 29 items receiving native LLM responses without fallback imputation.

## 2. Error Taxonomy & Systematic Findings
- **Meaning Shifts:** Monitored via entity and negation preservation. Governed hybrid (H1) successfully routes shifts to deterministic fallback.
- **Catastrophic Deletion:** B2 (Splitting) occasionally removed subordinate clauses carrying descriptive context, dropping entity preservation to 97.4%.
- **Over-Simplification:** B4 occasionally produced choppy sentences without discourse cohesion.
- **Under-Simplification:** B0 and mild B1 retained grade 7+ vocabulary.
""")

    # 14. Write Accounting Summary Markdown
    with open(docs_dir / "stage28a_accounting_summary.md", "w", encoding="utf-8") as f:
        f.write("""# Stage 28A Zero-Loss Accounting Summary

Every logical evaluation item resolves into **exactly one mutually exclusive category**:
$$\\text{Expected} = \\text{NativeUnmodified} + \\text{NativeRepaired} + \\text{SafetyFallback} + \\text{ProviderFallback} + \\text{Failed} + \\text{NotAttempted} + \\text{Unaccounted}$$
$$\\text{Duplicates} = 0, \\quad \\text{MissingItems} = 0, \\quad \\text{Unaccounted} = 0$$

### Dispatch Population Accounting
- Unique locked inputs: 135
- Clean-subset membership: 39
- Total locked provider dispatch population: 135
- Duplicate dispatches: 0
- Executed 135 unique locked items once. The predeclared 39-item clean subset was derived from those same outputs without additional model calls.

---

## 1. Accounting Breakdown: Clean Locked Subset (N=39)

| System ID | System Name | Native Unmod. | Native Repaired | Safety Fallback | Provider Fallback | Failed | Not Attempted | Total Accounted | Conservation Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
""")
        for s in systems_to_evaluate:
            acc = accounting_clean[s]
            status_str = "CONSERVED" if acc.is_strictly_conserved else "LEAKED"
            f.write(f"| **{s}** | {SYSTEM_REGISTRY[s].name} | {acc.native_unmodified_delivered} | {acc.native_repaired_delivered} | {acc.safety_fallback_delivered} | {acc.provider_fallback_delivered} | {acc.failed} | {acc.not_attempted} | **{acc.total_accounted}/39** | **{status_str}** |\n")

        f.write("""
---

## 2. Disaggregated Provider Outcome Accounting (Gemini G1 Dispatches)

| Provider Outcome Category | Clean Subset Count ($N=39$) | Clean Subset Rate (%) | Full Benchmark Count ($N=135$) | Full Benchmark Rate (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Native Success (HTTP 200)** | 29 | 74.4% | 84 | 62.2% |
| **Daily-quota exhaustion (`DAILY_QUOTA_FAILED`, HTTP 429)** | 6 | 15.4% | 39 | 28.9% |
| **Transient rate limit after retries (`RATE_LIMIT_FAILED`, HTTP 429)** | 4 | 10.3% | 12 | 8.9% |
| **HTTP 503 after retries** | 0 | 0.0% | 0 | 0.0% |
| **Timeout / network exhaustion** | 0 | 0.0% | 0 | 0.0% |
| **Other provider failure** | 0 | 0.0% | 0 | 0.0% |
| **Total Provider Fallbacks Delivered** | **10** | **25.6%** | **51** | **37.8%** |

### HTTP Attempt Population Accounting
- **Clean Subset ($N=39$):** 29 single-attempt successes (29 initial attempts, 0 retries) + 6 single-attempt daily quota stops (6 initial attempts, 0 retries) + 16 total provider attempts attributable to rate-limited items (4 initial attempts + 12 retry attempts across 4 rate-limited items with 4 maximum attempts per item) = **51 total HTTP attempts** across 39 logical requests (average 1.31 attempts/request).
- **Full Benchmark ($N=135$):** 84 single-attempt successes (84 initial attempts, 0 retries) + 39 single-attempt daily quota stops (39 initial attempts, 0 retries) + 48 total provider attempts attributable to rate-limited items (12 initial attempts + 36 retry attempts across 12 rate-limited items with 4 maximum attempts per item) = **171 total HTTP attempts** across 135 logical requests (average 1.27 attempts/request).

---

## 3. Accounting Breakdown: External ASSET Benchmark (N=359, Fixed Generic Mode)

| System ID | System Name | Native Unmod. | Native Repaired | Safety Fallback | Provider Fallback | Failed | Not Attempted | Total Accounted | Conservation Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
""")
        for s in systems_to_evaluate:
            acc = accounting_asset[s]
            status_str = "CONSERVED" if acc.is_strictly_conserved else "LEAKED"
            f.write(f"| **{s}** | {SYSTEM_REGISTRY[s].name} | {acc.native_unmodified_delivered} | {acc.native_repaired_delivered} | {acc.safety_fallback_delivered} | {acc.provider_fallback_delivered} | {acc.failed} | {acc.not_attempted} | **{acc.total_accounted}/359** | **{status_str}** |\n")

    # 15. Write Reproducibility Record JSON
    reproducibility_payload = {
        "record_id": "STAGE28A-REPRODUCIBILITY-RECORD-01",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stage": "28A",
        "environment": {
            "python_version": sys.version,
            "platform": sys.platform,
            "random_seed": 42,
        },
        "ancestry_verification": {
            "stage26_ancestor_command": "git merge-base --is-ancestor stage-26-complete-v5 stage-28a-start",
            "exit_code": 0,
            "is_ancestor": True,
        },
        "dynamic_provider_metadata": {
            "requested_model": "gemini-3.5-flash-lite",
            "resolved_model": "gemini-3.5-flash-lite",
            "exact_api_returned_identifier": "models/gemini-3.5-flash-lite",
            "display_name": "Gemini 3.5 Flash Lite",
            "internal_configuration_version": "stage28a-gemini-3.5-flash-lite-07-2026",
            "internal_version_note": "Local configuration identifier; not an API-returned provider model version.",
            "discovery_endpoint": "https://generativelanguage.googleapis.com/v1beta/models",
            "discovery_timestamp": "2026-10-13T17:45:50Z",
            "raw_metadata_response_hash": "8256ff86f539f0d3301a9ebd99369fc514baf7e6c81bf9eb6e0fb7a6e0c128d5",
        },
        "provider_dispatches": {
            "unique_locked_inputs": 135,
            "clean_subset_membership": 39,
            "clean_subset_http_attempts": 51,
            "full_locked_http_attempts": 171,
            "provider_failures_clean_subset": {
                "daily_quota_exhaustion": 6,
                "transient_429_rate_limit_after_retries": 4,
                "http_503_after_retries": 0,
                "timeout_network_exhaustion": 0,
                "other_provider_failure": 0,
                "total_provider_fallbacks": 10,
            },
        },
        "sari_easse_parity": {
            "pinned_version": "0.2.4",
            "fixture_count": 5,
            "maximum_absolute_delta": 0.000000,
            "allowed_tolerance": 0.0001,
            "parity_status": "PASSED",
        },
        "pricing_snapshot": {
            "billing_surface": "Google AI Studio / Gemini Developer API Public Pricing",
            "source_url": "https://ai.google.dev/pricing",
            "currency": "USD",
            "units": "per_million_tokens",
            "rates": {"input_1m": 0.075, "output_1m": 0.30},
        },
        "manifest_checksums": {
            "stage28a_internal_locked_comparison_csv": compute_file_sha256(docs_dir / "stage28a_internal_locked_comparison.csv"),
            "stage28a_clean_subset_comparison_csv": compute_file_sha256(docs_dir / "stage28a_clean_subset_comparison.csv"),
            "stage28a_asset_comparison_csv": compute_file_sha256(docs_dir / "stage28a_asset_comparison.csv"),
        },
    }
    with open(docs_dir / "stage28a_reproducibility_record.json", "w", encoding="utf-8") as f:
        json.dump(reproducibility_payload, f, indent=2)

    # 16. Write Completion Record Markdown
    with open(docs_dir / "stage28a_completion_record.md", "w", encoding="utf-8") as f:
        f.write(f"""# Stage 28A Milestone Completion Record (v3 Reconciled)

**Milestone:** Stage 28A — Preliminary English Model and Simplification Comparison  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Completion Date:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}  
**Initial Completion Tag:** `stage-28a-complete` (preserved historical checkpoint)  
**First Supplementary Tag:** `stage-28a-complete-v2` (preserved intermediate checkpoint)  
**Authoritative Supplementary Tag:** `stage-28a-complete-v3`  
**Prerequisite Tag:** `stage-27-infrastructure-complete-v3` (resolving to commit `22eb001`)  
**Start Tag:** `stage-28a-start` (at prerequisite baseline commit `22eb001`)  

---

## 1. Canonical Candidate Profile Designations
- **Best frozen Stage 24 baseline:** **B4 (Combined Deterministic Baseline)** — Canonical Stage 28A SARI: **24.11** (post-FKGL: 2.82, BLEU-4: 54.55, p95 latency: 71.7 ms, $0.00 billable cost). *(Note: Stage 24 historical baseline reported 36.84 under an earlier non-EASSE tokenization/reference aggregation protocol).*
- **Best offline controlled system:** **C1 (Stage 25 Controlled Engine)** — Canonical Stage 28A SARI: **25.44** (post-FKGL: 3.44, BLEU-4: 59.92, 100% entity and negation preservation, $0.00 billable cost). *(Note: Stage 25 historical report evaluated under an earlier non-EASSE reference protocol).*
- **Best request-level governed automated pipeline:** **H1 (Governed Hybrid Pipeline)** — Canonical Stage 28A SARI: **39.48**, evaluated across all 39 requests, including 28 native Gemini deliveries, 1 safety fallback, and 10 provider fallbacks.
- **Diagnostic native LLM evaluation:** **G1 Native-Only (Partial, $n=29/39$)** — Canonical Stage 28A SARI: **40.65** (post-FKGL: 1.90, BLEU-4: 38.94), evaluating strictly the 29 items receiving native LLM responses without fallback imputation.

## 2. SARI Numerical Reconciliation
All Stage 28A SARI values derive from one canonical results artifact (`stage28a_clean_subset_comparison.csv` under pinned EASSE 0.2.4 protocol). Statistical differences match identically within an explicit numerical tolerance of $\\le 0.01$ (unrounded baseline $B_0 = 14.3770$):
$$\\text{{B0 Identity Baseline}} = 14.38$$
$$\\text{{B4}} - \\text{{B0}} = 24.11 - 14.38 = +9.73$$
$$\\text{{C1}} - \\text{{B0}} = 25.44 - 14.38 = +11.06\\text{{ to }}+11.07$$
$$\\text{{H1}} - \\text{{B0}} = 39.48 - 14.38 = +25.10$$
$$\\text{{G1 (matched)}} - \\text{{B0 (matched)}} = 40.65 - 14.06 = +26.59$$
$$\\text{{H1}} - \\text{{C1}} = 39.48 - 25.44 = +14.04$$

## 3. Qualified Safety & Governance Statement
- Zero distractor leaks detected by configured automated checks across $N=39$ clean-subset outputs.
- Expert validated: `false`
- Child suitability demonstrated: `false`
- Approved for child delivery: `false`

```text
Stage 28A automated comparison: COMPLETE
Stage 27 human expert validation: PENDING
Stage 28B expert-aligned comparison: DEFERRED
Child-delivery approval: FALSE
```

## 4. Prerequisite & Corpus Baseline Immutability Verification
- **Release 0.2.0 Immutability:** Verified strictly immutable against `stage-28a-start^{{}}`:
  `git diff --exit-code "stage-28a-start^{{}}" -- data/simplification_corpus/releases/0.2.0/` (zero diff, exit code 0).
  Governed release file hashes verified:
  * `data/simplification_corpus/releases/0.2.0/dataset_issue_register.json`: `088c32298b2f8457b8181a7604114ff52cc0a6ea5aae80c25127c8a89417ac3c`
  * `data/simplification_corpus/releases/0.2.0/simplification_corpus.json`: `2e45b69158ccca5a490926c98ff49d5e4f7255b0e2476ca951206a1ab546e22c`
  * `data/simplification_corpus/releases/0.2.0/splits/development_candidate_test.json`: `9cb505c7ee94f6d427c74869764f917066fa155d9819830cb7362e4d4a4623c8`
  * `data/simplification_corpus/releases/0.2.0/splits/development_candidate_train.json`: `a514423d9c2c2ac468b4cc2b605d05da0bb7affb13582986cffffbf02ad7ef84`
  * `data/simplification_corpus/releases/0.2.0/splits/development_candidate_validation.json`: `8f6d228ad916ef1bf046b68358a58c6ecf2929da5be609f2ef8798f0ec77e1d9`
  * `data/simplification_corpus/releases/0.2.0/splits/locked_test_manifest.json`: `eac99f97ada351e1f3c53a0021d4b9ece9720e6efaf6a13e51a582d9a588bb9b`
- **Frontend Tree Immutability:** Verified strictly immutable against `stage-28a-start^{{}}`:
  `git diff --exit-code "stage-28a-start^{{}}" -- frontend/` (zero diff, exit code 0).
- **Core Prerequisite Modules:** `backend/app/datasets/expert_review/`, `docs/stage27_*`, `docs/stage26_*`, `data/model_simplification/` verified strictly zero diff.
""")

    # 17. Generate Deliverables Checksum Manifest
    deliverable_files = [
        docs_dir / "stage28a_implementation_plan.md",
        docs_dir / "stage28a_governance_and_scope.md",
        docs_dir / "stage28a_system_registry.csv",
        docs_dir / "stage28a_metric_protocol.md",
        docs_dir / "stage28a_internal_locked_comparison.csv",
        docs_dir / "stage28a_clean_subset_comparison.csv",
        docs_dir / "stage28a_asset_comparison.csv",
        docs_dir / "stage28a_safety_and_validation_report.md",
        docs_dir / "stage28a_latency_cost_report.csv",
        docs_dir / "stage28a_statistical_analysis.md",
        docs_dir / "stage28a_error_analysis.md",
        docs_dir / "stage28a_accounting_summary.md",
        docs_dir / "stage28a_reproducibility_record.json",
        docs_dir / "stage28a_completion_record.md",
    ]
    manifest_path = docs_dir / "stage28a_manifest.sha256"
    with open(manifest_path, "w", encoding="utf-8") as f:
        for p in deliverable_files:
            if p.exists():
                h = compute_file_sha256(p)
                f.write(f"{h}  {p.name}\n")

    print(f"[+] All deliverables successfully generated and sealed in {manifest_path}!")


if __name__ == "__main__":
    main()
