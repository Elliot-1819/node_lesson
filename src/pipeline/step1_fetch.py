"""Step 1 — Fetch Work (DB only).

Fetch N pending sections from the Neon Postgres database. Example-file logic
has been moved out and should not be used for Step 1 in normal runs.
"""

from __future__ import annotations

import logging
from typing import List

from db.db_utils import fetch_pending_sections
from db.models import RawSection
from utils.logging_utils import log_event


logger = logging.getLogger(__name__)

def fetch_sections(limit: int) -> List[RawSection]:
    sections = fetch_pending_sections(limit)
    log_event(logger, "step1_fetch.loaded_sections", count=len(sections), source="db")
    return sections


