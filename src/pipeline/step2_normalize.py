"""Step 2 — Normalize & Split (exact dedupe only)."""

from __future__ import annotations

from typing import List

from src.utils.text_clean import normalize, split_sentences, dedupe_exact


def normalize_and_split(text: str) -> List[str]:
    normalized = normalize(text)
    parts = split_sentences(normalized)
    return dedupe_exact(parts)


