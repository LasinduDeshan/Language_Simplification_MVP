"""Unit tests for ReviewRouter confidence, margin, and OOD checks."""

from app.complexity_analysis.review_router import ReviewRouter


def test_high_confidence_clean_accepted():
    router = ReviewRouter(confidence_threshold=0.80, margin_threshold=0.15)
    probs = {"easy": 0.85, "medium": 0.10, "hard": 0.05}
    review_req, reasons, conf, margin = router.evaluate_routing(
        class_probabilities=probs,
        is_out_of_distribution=False,
        parser_failed=False,
    )
    assert not review_req
    assert len(reasons) == 0
    assert conf == 0.85
    assert margin == 0.75


def test_low_confidence_routed_to_review():
    router = ReviewRouter(confidence_threshold=0.80, margin_threshold=0.15)
    probs = {"easy": 0.50, "medium": 0.40, "hard": 0.10}
    review_req, reasons, conf, margin = router.evaluate_routing(
        class_probabilities=probs,
        is_out_of_distribution=False,
        parser_failed=False,
    )
    assert review_req
    assert any("confidence" in r.lower() for r in reasons)


def test_low_margin_routed_to_review():
    router = ReviewRouter(confidence_threshold=0.70, margin_threshold=0.15)
    probs = {"easy": 0.45, "medium": 0.40, "hard": 0.15}
    review_req, reasons, conf, margin = router.evaluate_routing(
        class_probabilities=probs,
        is_out_of_distribution=False,
        parser_failed=False,
    )
    assert review_req
    assert any("margin" in r.lower() for r in reasons)


def test_ood_routed_to_review():
    router = ReviewRouter(confidence_threshold=0.80, margin_threshold=0.15)
    probs = {"easy": 0.90, "medium": 0.05, "hard": 0.05}
    review_req, reasons, conf, margin = router.evaluate_routing(
        class_probabilities=probs,
        is_out_of_distribution=True,
        ood_violations=["word_count"],
        parser_failed=False,
    )
    assert review_req
    assert any("out-of-distribution" in r.lower() for r in reasons)
