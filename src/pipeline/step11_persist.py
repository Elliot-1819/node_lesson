"""Step 11 — Persist (placeholder).

For now, returns in-memory structures matching the simplified output schema:
 - lesson_id
 - lesson_title
 - section_id
 - section_style
 - content
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class LessonRow:
    lesson_id: int
    lesson_title: str
    section_id: int
    section_style: str
    content: str


def persist_in_memory(rows: List[LessonRow]) -> List[LessonRow]:
    # Placeholder for DB write; simply returns the rows
    return rows


