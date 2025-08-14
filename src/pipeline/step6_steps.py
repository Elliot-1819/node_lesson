"""Step 6 — Decide Step Count (placeholder signatures)."""

from __future__ import annotations

from typing import Dict, List


def decide_step_count(selected: Dict[str, List[str]]) -> int:
    non_empty = sum(1 for v in selected.values() if v)
    if non_empty >= 3:
        return 2
    return 1


