"""
Unit tests for Stage 20 Balance Analyzer.
"""
import pytest
from app.datasets.expansion.balance_analyzer import BalanceAnalyzer

def test_balance_analyzer_balanced():
    analyzer = BalanceAnalyzer(target_domain_pct=25.0, domain_tolerance=5.0)
    # Equal 25 records across 4 domains
    records = []
    for dom in ["vocabulary", "grammar", "comprehension", "instruction_following"]:
        for _ in range(25):
            records.append({"primary_domain": dom, "source_difficulty": "medium", "support_level": "mild", "age_min": 4, "age_max": 6})

    res = analyzer.analyze_records(records)
    assert res["total_records"] == 100
    assert res["is_balanced"] is True
    assert len(res["domain_imbalances"]) == 0

def test_balance_analyzer_imbalanced():
    analyzer = BalanceAnalyzer(target_domain_pct=25.0, domain_tolerance=5.0)
    # Heavy vocabulary imbalance
    records = []
    for _ in range(80):
        records.append({"primary_domain": "vocabulary"})
    for _ in range(20):
        records.append({"primary_domain": "grammar"})

    res = analyzer.analyze_records(records)
    assert res["is_balanced"] is False
    assert len(res["domain_imbalances"]) > 0
