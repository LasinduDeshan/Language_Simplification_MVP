"""
Stage 34 — Sampling and Corpus Population Service
Loads the 150-record canonical analytical corpus and Stage 33 disposition ledger dynamically,
constructing the complete evaluation item set.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent


def load_canonical_items() -> List[Dict[str, Any]]:
    corpus_file = (
        PROJECT_ROOT
        / "data"
        / "sinhala_external"
        / "corpus"
        / "canonical_analytical_corpus.jsonl"
    )
    disp_file = (
        PROJECT_ROOT
        / "data"
        / "sinhala_simplification"
        / "ledgers"
        / "final_disposition_ledger.jsonl"
    )

    if not corpus_file.exists():
        raise FileNotFoundError(f"Missing canonical corpus: {corpus_file}")
    if not disp_file.exists():
        raise FileNotFoundError(f"Missing disposition ledger: {disp_file}")

    corpus_records = []
    with open(corpus_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                corpus_records.append(json.loads(line))

    dispositions = []
    with open(disp_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                dispositions.append(json.loads(line))

    assert len(corpus_records) == len(dispositions), (
        f"Mismatch between corpus records ({len(corpus_records)}) and dispositions ({len(dispositions)})"
    )

    items = []
    for idx, (rec, disp) in enumerate(zip(corpus_records, dispositions), 1):
        item_id = f"ITEM-S34-{idx:06d}"
        items.append({
            "item_id": item_id,
            "record_id": rec.get("record_id", f"REC-{idx:04d}"),
            "split": rec.get("split", "train"),
            "stage33_output_id": disp.get("output_id"),
            "final_disposition": disp.get("final_disposition"),
            "applied_rule_ids": disp.get("applied_rule_ids", []),
            "selected_candidate_id": disp.get("selected_candidate_id"),
            "output_storage_ref": disp.get("output_storage_ref"),
            "output_sha256": disp.get("output_sha256_internal"),
            "is_control": disp.get("final_disposition") != "DRAFT_REWRITE_SELECTED",
        })

    return items
