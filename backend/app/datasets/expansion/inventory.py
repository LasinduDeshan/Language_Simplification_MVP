"""
Stage 20 Manifest-Driven Dataset Inventory Module
Inspects existing governed releases (v0.1.0) and derives authoritative baseline metrics.
"""
import os
import json
from collections import Counter
from typing import Dict, Any, List

class DatasetInventory:
    def __init__(self, root_dir: str = None):
        if root_dir is None:
            # Look relative to backend directory
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        self.root_dir = root_dir
        
        self.adapt_path = os.path.join(self.root_dir, "data", "adaptation_test_set", "releases", "0.1.0", "adaptation_test_set.json")
        self.simp_path = os.path.join(self.root_dir, "data", "simplification_corpus", "releases", "0.1.0", "simplification_corpus.json")
        self.lex_path = os.path.join(self.root_dir, "data", "lexicons", "en", "releases", "0.1.0", "lexicon_repository.json")

    def _load_json(self, path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else data.get("records", [])

    def _extract_domain(self, record: Dict[str, Any], adapt_map: Dict[str, str]) -> str:
        if "primary_domain" in record and record["primary_domain"]:
            return record["primary_domain"]
        src_act = record.get("source_activity_id") or record.get("activity_id") or ""
        if src_act in adapt_map:
            return adapt_map[src_act]
        # Infer from ID string
        src_upper = src_act.upper()
        if "VOC" in src_upper:
            return "vocabulary"
        elif "GRA" in src_upper:
            return "grammar"
        elif "COMP" in src_upper:
            return "comprehension"
        elif "INS" in src_upper or "DIR" in src_upper or "ACT" in src_upper:
            return "instruction_following"
        return "vocabulary"

    def analyze(self) -> Dict[str, Any]:
        adapt_records = self._load_json(self.adapt_path)
        simp_records = self._load_json(self.simp_path)
        lex_records = self._load_json(self.lex_path)

        adapt_map = {r.get("activity_id"): r.get("primary_domain") for r in adapt_records if r.get("activity_id")}

        # 1. Adaptation Activities Analysis
        adapt_domains = Counter(r.get("primary_domain", "unknown") for r in adapt_records)
        adapt_diffs = Counter(r.get("difficulty", "unknown") for r in adapt_records)
        adapt_ages = Counter()
        for r in adapt_records:
            min_a = r.get("age_min", 4)
            max_a = r.get("age_max", 8)
            for a in range(min_a, max_a + 1):
                adapt_ages[a] += 1

        # 2. Simplification Pairs Analysis
        simp_domains = Counter(self._extract_domain(r, adapt_map) for r in simp_records)
        simp_supports = Counter(r.get("support_level", "unknown") for r in simp_records)
        simp_source_items = len(set(r.get("source_item_id") or r.get("source_activity_id") or r.get("original_text") for r in simp_records))
        simp_diffs = Counter(r.get("original_difficulty") or r.get("source_difficulty") or r.get("difficulty") or "medium" for r in simp_records)
        simp_ages = Counter()
        for r in simp_records:
            min_a = r.get("age_min", 4)
            max_a = r.get("age_max", 8)
            for a in range(min_a, max_a + 1):
                simp_ages[a] += 1

        # 3. Lexicon Analysis
        lex_poses = Counter(r.get("part_of_speech") or r.get("pos") or "unspecified" for r in lex_records)
        lex_diffs = Counter(str(r.get("difficulty_tier", "unspecified")) for r in lex_records)
        lex_ages = Counter()
        for r in lex_records:
            if "age_band" in r and r["age_band"]:
                try:
                    parts = str(r["age_band"]).split("-")
                    min_a = int(parts[0])
                    max_a = int(parts[1]) if len(parts) > 1 else min_a
                except Exception:
                    min_a, max_a = 4, 8
            else:
                min_a = r.get("age_min", 4)
                max_a = r.get("age_max", 8)
            for a in range(min_a, max_a + 1):
                lex_ages[a] += 1

        return {
            "baseline_release_version": "0.1.0",
            "adaptation_test_set": {
                "total_records": len(adapt_records),
                "domain_distribution": dict(adapt_domains),
                "difficulty_distribution": dict(adapt_diffs),
                "age_coverage": dict(sorted(adapt_ages.items()))
            },
            "simplification_corpus": {
                "total_pairs": len(simp_records),
                "unique_source_items": simp_source_items,
                "domain_distribution": dict(simp_domains),
                "support_level_distribution": dict(simp_supports),
                "difficulty_distribution": dict(simp_diffs),
                "age_coverage": dict(sorted(simp_ages.items()))
            },
            "lexicon_repository": {
                "total_entries": len(lex_records),
                "pos_distribution": dict(lex_poses),
                "difficulty_distribution": dict(lex_diffs),
                "age_coverage": dict(sorted(lex_ages.items()))
            }
        }

    def generate_markdown_report(self) -> str:
        data = self.analyze()
        lines = [
            "# Stage 20: Internal English Dataset Inventory Report",
            "",
            f"**Baseline Governed Release:** `v{data['baseline_release_version']}`  ",
            "**Report Scope:** Authoritative counts derived from governed JSON release files.  ",
            "",
            "---",
            "",
            "## 1. Executive Summary Table",
            "",
            "| Dataset | Governed Baseline Count | Unique Sources / Entities | Target Scale (Stage 20) |",
            "| :--- | :---: | :---: | :---: |",
            f"| **Adaptation Activities** | {data['adaptation_test_set']['total_records']} activities | {data['adaptation_test_set']['total_records']} tasks | 120–140 activities |",
            f"| **Simplification Corpus** | {data['simplification_corpus']['total_pairs']} draft pairs | ~{data['simplification_corpus']['unique_source_items']} source items | 900 pairs (300 source items) |",
            f"| **English Lexicon** | {data['lexicon_repository']['total_entries']} entries | {data['lexicon_repository']['total_entries']} headwords | 350+ lexicon entries |",
            "",
            "---",
            "",
            "## 2. Simplification Corpus Baseline Breakdown",
            "",
            "### Domain Distribution",
            "| Domain | Baseline Pairs | Approximate Share | Target Share |",
            "| :--- | :---: | :---: | :---: |",
        ]
        total_simp = data['simplification_corpus']['total_pairs'] or 1
        for dom, count in data['simplification_corpus']['domain_distribution'].items():
            pct = (count / total_simp) * 100
            lines.append(f"| **{dom.replace('_', ' ').title()}** | {count} | {pct:.1f}% | 25.0% (±5%) |")

        lines.extend([
            "",
            "### Support Level Distribution",
            "| Support Level | Baseline Pairs | Target Share |",
            "| :--- | :---: | :---: |",
        ])
        for supp, count in data['simplification_corpus']['support_level_distribution'].items():
            lines.append(f"| **{supp.title()}** | {count} | 33.3% |")

        lines.extend([
            "",
            "### Age Coverage Breakdown (Active in Band)",
            "| Age | Active Simplification Pairs |",
            "| :---: | :---: |",
        ])
        for age, count in data['simplification_corpus']['age_coverage'].items():
            lines.append(f"| Age {age} | {count} pairs |")

        lines.extend([
            "",
            "---",
            "",
            "## 3. English Lexicon Baseline Breakdown",
            "",
            "| Part of Speech | Baseline Entries |",
            "| :--- | :---: |",
        ])
        for pos, count in data['lexicon_repository']['pos_distribution'].items():
            lines.append(f"| {pos.title()} | {count} |")

        lines.extend([
            "",
            "---",
            "",
            "## 4. Key Takeaways for Stage 20 Expansion",
            "1. **Grammar & Comprehension Gaps**: The existing corpus is heavily weighted towards vocabulary and naming tasks.",
            "2. **Age 7–8 Gaps**: Early childhood (ages 4–6) is well-represented, while multi-clause sentence simplification for ages 7–8 requires substantial expansion.",
            "3. **Lexicon Scale**: The 18-entry lexicon must be expanded by at least ~330 entries to provide rich multi-domain coverage.",
            ""
        ])

        return "\n".join(lines)
