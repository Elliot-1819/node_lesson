"""Text normalization and sentence utilities.

Improvements for Step 2:
- Split BEFORE normalization to preserve natural boundaries (newlines/bullets)
- Support splitting on punctuation, newlines, and bullet markers
"""

from __future__ import annotations

import re


def normalize(text: str) -> str:
    """Lowercase, normalize whitespace, strip stray punctuation spacing."""
    t = text.strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t


SENTENCE_SPLIT_RE = re.compile(
    r"(?:(?<=[.!?])\s+)|(?:[\r\n]+)|(?:^\s*[-•–]\s+)",
    flags=re.MULTILINE,
)


def split_sentences(text: str) -> list[str]:
    """Split raw text into sentence-like chunks.

    Rules:
    - Split on sentence-ending punctuation followed by space
    - Split on newlines
    - Split at bullet markers at line starts ("- ", "• ", "– ")
    """
    if not text:
        return []
    parts = SENTENCE_SPLIT_RE.split(text.strip())
    # Clean up: strip leading bullet characters/spaces
    cleaned: list[str] = []
    for p in parts:
        s = p.strip()
        if not s:
            continue
        # remove leading bullets/hyphens left from splits
        s = s.lstrip("-•– ")
        if s:
            cleaned.append(s)
    return cleaned


def dedupe_exact(sentences: list[str]) -> list[str]:
    """Remove exact duplicate sentences while preserving order.

    Assumes sentences are already normalized. Keeps the first occurrence
    of each unique sentence.
    """
    seen: set[str] = set()
    unique: list[str] = []
    for s in sentences:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique

