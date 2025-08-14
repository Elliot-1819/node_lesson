"""Step 9 — Determine Difficulty (placeholder)."""

from __future__ import annotations

from typing import Iterable

from services.keyword_service import keyword_density, flesch_kincaid_grade


def determine_difficulty(text: str, domain_vocab: Iterable[str]) -> str:
    density = keyword_density(text, domain_vocab)
    grade = flesch_kincaid_grade(text)
    # Simple rule-of-thumb: more density + higher grade -> harder
    if density < 0.05 and grade <= 8.5:
        return "Beginner"
    if density < 0.1 and grade <= 10:
        return "Intermediate"
    return "Master"


