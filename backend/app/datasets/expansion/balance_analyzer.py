"""
Stage 20 Balance Analyzer Module
Analyzes multidimensional distribution balance across domains, age bands, difficulty tiers, and support levels.
"""
import os
import csv
from collections import Counter
from typing import Dict, Any, List

class BalanceAnalyzer:
    def __init__(self, target_domain_pct: float = 25.0, domain_tolerance: float = 5.0):
        self.target_domain_pct = target_domain_pct
        self.domain_tolerance = domain_tolerance
        self.min_domain_pct = target_domain_pct - domain_tolerance  # 20.0%
        self.max_domain_pct = target_domain_pct + domain_tolerance  # 30.0%

    def analyze_records(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(records)
        if total == 0:
            return {"total_records": 0, "is_balanced": False}

        domains = Counter(r.get("primary_domain", "unknown") for r in records)
        diffs = Counter(r.get("source_difficulty") or r.get("original_difficulty") or r.get("difficulty") or "medium" for r in records)
        supports = Counter(r.get("support_level", "unspecified") for r in records)
        
        ages = Counter()
        for r in records:
            min_a = r.get("age_min", 4)
            max_a = r.get("age_max", 8)
            for a in range(min_a, max_a + 1):
                ages[a] += 1

        domain_percentages = {dom: round((cnt / total) * 100, 2) for dom, cnt in domains.items()}
        
        # Check domain balance tolerance
        domain_imbalances = []
        for dom, pct in domain_percentages.items():
            if pct < self.min_domain_pct or pct > self.max_domain_pct:
                domain_imbalances.append({
                    "domain": dom,
                    "percentage": pct,
                    "target_range": f"{self.min_domain_pct}% - {self.max_domain_pct}%"
                })

        is_balanced = len(domain_imbalances) == 0

        return {
            "total_records": total,
            "is_balanced": is_balanced,
            "domain_counts": dict(domains),
            "domain_percentages": domain_percentages,
            "domain_imbalances": domain_imbalances,
            "difficulty_counts": dict(diffs),
            "support_level_counts": dict(supports),
            "age_coverage": dict(sorted(ages.items()))
        }

    def generate_csv_report(self, records: List[Dict[str, Any]], output_path: str):
        analysis = self.analyze_records(records)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["dimension", "category", "count", "percentage", "status"])
            
            # Domains
            for dom, cnt in analysis["domain_counts"].items():
                pct = analysis["domain_percentages"].get(dom, 0.0)
                status = "balanced" if (self.min_domain_pct <= pct <= self.max_domain_pct) else "imbalanced"
                writer.writerow(["primary_domain", dom, cnt, f"{pct}%", status])
                
            # Difficulties
            for diff, cnt in analysis["difficulty_counts"].items():
                pct = round((cnt / analysis["total_records"]) * 100, 2)
                writer.writerow(["difficulty", diff, cnt, f"{pct}%", "normal"])
                
            # Support levels
            for supp, cnt in analysis["support_level_counts"].items():
                pct = round((cnt / analysis["total_records"]) * 100, 2)
                writer.writerow(["support_level", supp, cnt, f"{pct}%", "normal"])
                
            # Ages
            for age, cnt in analysis["age_coverage"].items():
                writer.writerow(["age_coverage", f"age_{age}", cnt, "N/A", "covered"])
                
        return output_path
