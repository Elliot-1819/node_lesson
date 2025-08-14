"""Step 10 — Quality Gates (placeholder)."""

from __future__ import annotations

from typing import Tuple

from config.settings import get_settings
from services.keyword_service import flesch_kincaid_grade


def check_quality(text: str) -> Tuple[bool, str]:
    settings = get_settings()
    grade = flesch_kincaid_grade(text)
    if grade > 9.0:
        return False, f"reading_grade_too_high:{grade:.2f}"

    # Token cap: approximate by words (placeholder)
    words = len(text.split())
    approx_tokens = int(words * 1.3)
    if approx_tokens > settings.token_cap_per_step:
        return False, f"token_cap_exceeded:{approx_tokens}>{settings.token_cap_per_step}"

    return True, "ok"


