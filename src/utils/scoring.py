"""Scoring utilities placeholders.

Actual TF-IDF, entity boosts, and penalties will be implemented in Step 4.
For now, provide a minimal interface so tests can import symbols.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SentenceScore:
    text: str
    score: float


def simple_length_penalty(text: str) -> float:
    length = len(text.split())
    if length > 40:
        return 0.8
    return 1.0


