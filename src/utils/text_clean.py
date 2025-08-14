"""Text normalization and sentence utilities (placeholders).

These are wired later in Step 2. For now, provide minimal helpers used by
tests and stubs.
"""

from __future__ import annotations

import re


def normalize(text: str) -> str:
    """Lowercase, normalize whitespace, strip stray punctuation spacing."""
    t = text.strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t


SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def split_sentences(text: str) -> list[str]:
    parts = SENTENCE_SPLIT_RE.split(text.strip()) if text else []
    return [p.strip() for p in parts if p.strip()]


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

