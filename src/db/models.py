"""DB model placeholders.

We avoid importing SQLAlchemy for now, providing light Pydantic-style
dataclasses to describe the intended schema. Real ORM will be added later.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class LessonStep:
    lesson_id: int
    lesson_title: str
    section_id: int
    section_style: str  # Definition | Mechanism | Procedure | Comparison | Example
    content: str


@dataclass
class RawSection:
    section_id: int
    page_id: Optional[int]
    page_title: Optional[str]
    title: Optional[str]
    text: str
    topic: Optional[str] = None
    keywords: Optional[List[str]] = None
    status: str = "pending"  # pending | processing | done
    idempotency_key: Optional[str] = None


