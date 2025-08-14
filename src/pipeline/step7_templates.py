"""Step 7 — Fill Interactive Templates (placeholder signatures)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any


def load_templates(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def map_to_templates(selected: Dict[str, List[str]], templates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Placeholder: wrap texts into minimal slot mapping by info_type."""
    result: list[dict[str, Any]] = []
    by_type = {tpl["info_type"]: tpl for tpl in templates}
    for info_type, texts in selected.items():
        if not texts:
            continue
        tpl = by_type.get(info_type)
        if not tpl:
            continue
        step = {
            "template_id": tpl["id"],
            "info_type": info_type,
            "content": texts,
        }
        result.append(step)
    return result


