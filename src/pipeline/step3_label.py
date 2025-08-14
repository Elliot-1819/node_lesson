"""Step 3 — Auto-label (rules-first with optional LLM fallback)."""

from __future__ import annotations

from typing import List, Tuple, Optional

from services.classifier import classify_with_fallback, Classification


def label_sentences(sentences: List[str], section_keywords: Optional[List[str]] = None) -> List[Tuple[str, Classification]]:
    labeled: List[Tuple[str, Classification]] = []
    for s in sentences:
        labeled.append((s, classify_with_fallback(s, section_keywords=section_keywords)))
    return labeled


