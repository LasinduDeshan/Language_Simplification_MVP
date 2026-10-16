"""
Weighted Provenance Parity Diagnostic and Bounded Dispersion Engine (WP5).
Computes canonical frequency, document frequency, source frequency distribution,
and bounded source dispersion. Verifies exact weighted provenance parity across all 180 records.
"""

import collections
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

from app.datasets.sinhala_lexicon.schemas import CandidateLexiconEntry

class ParityAnalyzer:
    """Computes bounded dispersion and verifies weighted provenance parity."""

    def __init__(self, tolerance: float = 1e-6):
        self.tolerance = tolerance
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        self.diagnostic_file = repo_root / "data" / "sinhala_lexicon" / "ledgers" / "weighted_parity_diagnostic.json"

    def compute_bounded_source_dispersion(
        self,
        source_freq_dist: Dict[str, int],
        eligible_source_count: int
    ) -> float:
        """
        Computes normalized entropy over eligible sources K:
            D_s = - sum(p_s * ln(p_s)) / ln(K)  for K > 1
        where p_s = f_s / sum(f_j). If K <= 1 or total_freq == 0, returns 0.0.
        """
        K = eligible_source_count
        if K <= 1:
            return 0.0

        total_freq = sum(source_freq_dist.values())
        if total_freq == 0:
            return 0.0

        entropy = 0.0
        for count in source_freq_dist.values():
            if count > 0:
                p_s = count / total_freq
                entropy -= p_s * math.log(p_s)

        dispersion = entropy / math.log(K)
        return round(min(1.0, max(0.0, dispersion)), 4)

    def run_parity_diagnostic(
        self,
        candidates: List[CandidateLexiconEntry],
        provenance_records_path: Path,
        canonical_records_path: Path
    ) -> dict:
        """
        Runs exhaustive term-by-term parity verification between canonical frequency
        and cluster-weighted provenance frequency across all 180 records.
        """
        # Load canonical records
        canonical_ids = set()
        with open(canonical_records_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    canonical_ids.add(json.loads(line)["record_id"])

        # Load provenance records and check cluster weights
        provenance_count = 0
        canonical_to_prov = collections.defaultdict(list)
        prov_weights = {}
        invalid_weights = 0
        mapping_failures = 0

        with open(provenance_records_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                provenance_count += 1
                r_id = rec["record_id"]
                c_id = rec.get("canonical_record_id")
                weight = float(rec.get("exact_duplicate_weight", 1.0))
                prov_weights[r_id] = weight

                if not c_id or c_id not in canonical_ids:
                    mapping_failures += 1
                else:
                    canonical_to_prov[c_id].append(r_id)

        # Check weights sum per cluster
        for c_id, prov_members in canonical_to_prov.items():
            cluster_size = len(prov_members)
            expected_weight = 1.0 / cluster_size
            for m in prov_members:
                w = prov_weights[m]
                if abs(w - expected_weight) > 1e-5:
                    invalid_weights += 1

        # Check per-term parity
        max_delta = 0.0
        parity_failures = 0
        failing_terms = []

        for c in candidates:
            c_freq = float(c.canonical_frequency)
            w_freq = float(c.weighted_provenance_frequency)
            delta = abs(c_freq - w_freq)
            if delta > max_delta:
                max_delta = delta
            if delta > self.tolerance:
                parity_failures += 1
                failing_terms.append(c.canonical_form)

        diagnostic_report = {
            "parity_status": "VERIFIED_NO_INFLATION_DETECTED" if parity_failures == 0 else "PARITY_FAILED",
            "provenance_records": provenance_count,
            "canonical_records": len(canonical_ids),
            "cluster_count": len(canonical_to_prov),
            "invalid_weights": invalid_weights,
            "canonical_mapping_failures": mapping_failures,
            "per_term_parity_failures": parity_failures,
            "maximum_absolute_delta": round(max_delta, 8),
            "numerical_tolerance": self.tolerance,
            "failing_terms": failing_terms
        }

        self.diagnostic_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.diagnostic_file, "w", encoding="utf-8") as f:
            json.dump(diagnostic_report, f, indent=2)

        print(f"Parity diagnostic report written to: {self.diagnostic_file}")
        print(f"Status: {diagnostic_report['parity_status']} | Max delta: {max_delta} | Failures: {parity_failures}")
        assert parity_failures == 0, f"Weighted parity verification failed on {parity_failures} terms!"

        return diagnostic_report
