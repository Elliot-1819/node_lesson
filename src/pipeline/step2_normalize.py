"""Step 2 — Normalize & Split (exact dedupe only)."""

from __future__ import annotations

from typing import List

from src.utils.text_clean import normalize, split_sentences, dedupe_exact


def normalize_and_split(text: str) -> List[str]:
    # Split first (preserve newline/bullet boundaries), then normalize each
    raw_parts = split_sentences(text)
    parts = [normalize(p) for p in raw_parts]
    return dedupe_exact(parts)


