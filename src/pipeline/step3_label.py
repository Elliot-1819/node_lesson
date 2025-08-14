"""Step 3 — Auto-label (placeholder signatures)."""

from __future__ import annotations

from typing import List, Tuple

from services.classifier import classify_rules_first, Classification


def label_sentences(sentences: List[str]) -> List[Tuple[str, Classification]]:
    return [(s, classify_rules_first(s)) for s in sentences]


