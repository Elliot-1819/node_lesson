"""Classifier service interface (rules-first with tiny model fallback).

Implements a simple API that pipeline steps can call without caring about
the underlying implementation details. The model is intentionally tiny and
CPU-friendly so it can run locally without GPUs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple


INFO_TYPES = [
    "Definition",
    "Mechanism",
    "Procedure",
    "Comparison",
    "Example",
]


@dataclass
class Classification:
    label: str
    probability: float
    rule_hit: Optional[str] = None


def classify_rules_first(text: str) -> Classification:
    """Very lightweight rules with simple regex heuristics.

    This is not final; serves as a placeholder until we train a tiny model.
    """
    lowered = text.lower()

    # Definition: pattern "X is Y"
    if re.search(r"\bis\b", lowered) and re.search(r"\b(is|are)\b", lowered):
        return Classification(label="Definition", probability=0.7, rule_hit="def_is_pattern")

    # Mechanism: cause → effect signal words
    if any(k in lowered for k in ["because", "so that", "therefore", "enables", "keeps", "causes"]):
        return Classification(label="Mechanism", probability=0.65, rule_hit="mechanism_keywords")

    # Procedure: sequences / numbered steps
    if re.search(r"\b(step|first|second|then|finally|\d+\.)\b", lowered):
        return Classification(label="Procedure", probability=0.65, rule_hit="procedure_sequence")

    # Comparison: options / versus
    if re.search(r"\b(vs\.?|versus|compare|compared to|either|or)\b", lowered):
        return Classification(label="Comparison", probability=0.6, rule_hit="comparison_markers")

    # Example: concrete scenario signals
    if any(k in lowered for k in ["for example", "for instance", "e.g.", "an investor", "scenario"]):
        return Classification(label="Example", probability=0.6, rule_hit="example_markers")

    # Fallback heuristic
    return Classification(label="Example", probability=0.5, rule_hit=None)


# Placeholder for future ML fallback (TF-IDF + LogisticRegression)
def classify_tiny_model(text: str) -> Classification:  # pragma: no cover - not wired yet
    return Classification(label="Example", probability=0.51, rule_hit=None)


