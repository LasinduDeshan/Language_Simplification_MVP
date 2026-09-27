"""
Unit tests for Stage 20 Gap Analysis.
"""
import pytest
from app.datasets.expansion.gap_analysis import GapAnalyzer

def test_gap_matrix_computation():
    analyzer = GapAnalyzer()
    matrix = analyzer.compute_gap_matrix()
    
    assert len(matrix) == 12  # 4 domains * 3 difficulties
    domains = set(r["primary_domain"] for r in matrix)
    assert domains == {"vocabulary", "grammar", "comprehension", "instruction_following"}
    
    for row in matrix:
        assert row["target_source_items"] == 25
        assert row["target_pairs"] == 75
        assert row["gap_source_items"] >= 0
        assert row["gap_pairs"] >= 0
