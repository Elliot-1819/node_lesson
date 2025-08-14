"""Step 4 — Score Sentences (placeholder signatures)."""

from __future__ import annotations

from typing import List, Tuple

from utils.scoring import SentenceScore, simple_length_penalty


def score_sentences(sentences: List[str]) -> List[SentenceScore]:
    scores: List[SentenceScore] = []
    for s in sentences:
        base = 1.0
        penalty = simple_length_penalty(s)
        scores.append(SentenceScore(text=s, score=base * penalty))
    return scores


