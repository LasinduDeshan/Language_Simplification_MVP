"""Unit tests for ComplexityExplainer and ComplexityFactor generation."""

from app.complexity_analysis.explanation import ComplexityExplainer


def test_explainer_generates_standard_codes():
    explainer = ComplexityExplainer()
    features = {
        "avg_sentence_length": 18.0,
        "max_dependency_depth": 5.0,
        "clause_count": 3.0,
        "long_word_ratio": 0.25,
        "negation_count": 2.0,
        "passive_voice": 1.0,
        "word_count": 20.0,
    }

    factors = explainer.generate_factors(features=features, predicted_difficulty="hard")
    codes = [f.explanation_code for f in factors]

    assert "LONG_AVERAGE_SENTENCE" in codes
    assert "HIGH_DEPENDENCY_DEPTH" in codes
    assert "MULTIPLE_SUBORDINATE_CLAUSES" in codes
    assert "ADVANCED_LEXICAL_DENSITY" in codes
    assert "NEGATION_LOAD" in codes
    assert "PASSIVE_VOICE_STRUCTURE" in codes


def test_explainer_simple_structure_codes():
    explainer = ComplexityExplainer()
    features = {
        "avg_sentence_length": 4.0,
        "max_dependency_depth": 1.0,
        "clause_count": 0.0,
        "long_word_ratio": 0.0,
        "negation_count": 0.0,
        "passive_voice": 0.0,
        "word_count": 4.0,
    }

    factors = explainer.generate_factors(features=features, predicted_difficulty="easy")
    codes = [f.explanation_code for f in factors]

    assert "SHORT_SIMPLE_STRUCTURE" in codes
    assert "SHALLOW_PARSE_TREE" in codes
    assert "SINGLE_MAIN_CLAUSE" in codes
