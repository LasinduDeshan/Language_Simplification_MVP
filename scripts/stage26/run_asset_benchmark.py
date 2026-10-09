"""
Stage 26 WP9: ASSET External Benchmark Evaluation under Non-Commercial Research Policy.
Preserves quota schedule by marking ASSET benchmark as NOT_EXECUTED (deferred to Day 3 quota window)
while enforcing governance invariants.
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

repo_root = Path(__file__).resolve().parent.parent.parent
docs_dir = repo_root / "docs"
docs_dir.mkdir(parents=True, exist_ok=True)
out_doc = docs_dir / "stage26_asset_evaluation_report.md"


def main():
    report_md = f"""# Stage 26 ASSET External Benchmark Evaluation Report

**Stage:** Stage 26 — Pretrained Model / LLM-Based English Simplification  
**Date:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}  
**Status:** `NOT_EXECUTED`  
**Execution Policy:** Deferred to Quota Window Day 3 to prevent daily free-tier quota exhaustion during validation and locked benchmark runs.  

---

## 1. Governance & Permissions Invariants

```json
{{
  "dataset_name": "ASSET",
  "license": "CC-BY-NC-4.0",
  "training_eligible": false,
  "benchmark_eligible": true,
  "approved_for_child_delivery": false,
  "requires_expert_review": true
}}
```

## 2. Quota Isolation Schedule

| Quota Window | Evaluation Phase | Request Volume | Status |
| :--- | :--- | :---: | :---: |
| **Day 1** | Smoke Test & Internal Validation | 135 calls | **COMPLETED** |
| **Day 2** | Official Locked Benchmark & Clean Subset | 135 calls | **COMPLETED** |
| **Day 3** | ASSET External Benchmark (Optional) | 359 calls | **DEFERRED (NOT_EXECUTED)** |

## 3. Summary
ASSET evaluation is deferred to an independent quota allocation day. No partial aggregate metrics are reported as final results. Stage 26 internal locked benchmark freeze and validation remain authoritative.
"""
    with open(out_doc, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"[+] ASSET report saved with NOT_EXECUTED status: {out_doc}")


if __name__ == "__main__":
    main()
