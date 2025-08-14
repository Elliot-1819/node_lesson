"""Step 5 — Select Minimal Teaching Set (placeholder signatures)."""

from __future__ import annotations

from typing import Dict, List, Tuple

from services.classifier import INFO_TYPES, Classification


def select_minimal_set(labeled: List[Tuple[str, Classification]]) -> Dict[str, List[str]]:
    """Keep top-1 per info type (placeholder: first occurrence per type)."""
    selected: Dict[str, List[str]] = {t: [] for t in INFO_TYPES}
    for text, cls in labeled:
        if not selected[cls.label]:
            selected[cls.label] = [text]
    return selected


