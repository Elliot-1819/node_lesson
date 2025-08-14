from src.services.classifier import classify_with_scores


def test_definition_rule():
    c = classify_with_scores("A funding rate is a periodic payment.")
    assert c.label in {"Definition", "Mechanism"}


def test_mechanism_rule():
    c = classify_with_scores("Funding accrues hourly and is settled twice daily.")
    assert c.label == "Mechanism"


def test_procedure_rule():
    c = classify_with_scores("First, compute the mark price. Then, apply the funding.")
    assert c.label == "Procedure"


def test_comparison_rule():
    c = classify_with_scores("Compared to spot, futures may differ in pricing.")
    assert c.label == "Comparison"


def test_example_rule():
    c = classify_with_scores("For example, an investor enters a long position.")
    assert c.label == "Example"


