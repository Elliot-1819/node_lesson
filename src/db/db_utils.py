"""DB utilities for fetching raw sections from Neon Postgres.

Provides `fetch_pending_sections(limit)` for production/dev DB reads.
"""

from __future__ import annotations

from typing import List, Optional

import psycopg

from config.settings import get_settings
from .models import RawSection


def fetch_pending_sections(limit: int = 10) -> List[RawSection]:
    """Fetch N pages and flatten their `page_content` JSON into sections.

    Source table (default `lesson_dirty`) contains page-level fields and a
    `page_content` array of sections. We parse and emit one `RawSection` per
    section item. No status filter is applied.
    """
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL not configured in environment")

    table = settings.db_table_raw_sections
    query = f"""
        SELECT serial_id AS page_id,
               page_title,
               topic,
               _key_words,
               page_content
        FROM {table}
        ORDER BY serial_id ASC
        LIMIT %s
    """
    out: List[RawSection] = []
    with psycopg.connect(settings.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            for page_id, page_title, page_topic, page_keywords, page_content in cur.fetchall():
                import json as _json
                try:
                    sections = page_content if isinstance(page_content, list) else _json.loads(page_content)
                except Exception:
                    sections = []
                for s in sections or []:
                    if not isinstance(s, dict):
                        continue
                    section_serial_id: Optional[int] = s.get("section_serial_id")
                    section_title: Optional[str] = s.get("section_title")
                    text: str = (s.get("text") or "")
                    section_topic: Optional[str] = s.get("topic")
                    section_keywords = s.get("section_key_words") or page_keywords

                    # Compute a stable synthetic section_id for convenience (internal use)
                    computed_id: Optional[int] = None
                    try:
                        if page_id is not None and section_serial_id is not None:
                            computed_id = int(page_id) * 10000 + int(section_serial_id)
                    except Exception:
                        computed_id = None

                    out.append(
                        RawSection(
                            section_id=int(computed_id) if computed_id is not None else int(page_id),
                            page_id=int(page_id) if page_id is not None else None,
                            page_title=page_title,
                            title=section_title,
                            text=text,
                            topic=section_topic or page_topic,
                            keywords=section_keywords,
                            status="pending",
                        )
                    )
    return out
 
