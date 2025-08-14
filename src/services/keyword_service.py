"""Keyword and complexity utilities.

Provides tokenization-lite helpers and keyword density/complexity scoring
for difficulty estimation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Set

from textstat import textstat


WORD_RE = re.compile(r"[A-Za-z0-9_']+")


def tokenize(text: str) -> list[str]:
    return WORD_RE.findall(text.lower())


def keyword_density(text: str, domain_vocab: Iterable[str]) -> float:
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    vocab: Set[str] = {w.lower() for w in domain_vocab}
    hits = sum(1 for t in tokens if t in vocab)
    return hits / max(len(tokens), 1)


def flesch_kincaid_grade(text: str) -> float:
    return float(textstat.flesch_kincaid_grade(text))


