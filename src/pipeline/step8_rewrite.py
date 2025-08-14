"""Step 8 — Micro-rewrite (style only, placeholder)."""

from __future__ import annotations

from typing import List

from config.settings import get_settings
from services.llm_service import rewrite_style


def micro_rewrite(texts: List[str]) -> List[str]:
    settings = get_settings()
    rewritten: List[str] = []
    for t in texts:
        prompt = (
            "Rewrite the following content to be in a clear, concise 2nd-person "
            "conversational style without changing any facts. Keep it under the token cap.\n\n" + t
        )
        resp = rewrite_style(prompt, temperature=settings.llm_temperature)
        rewritten.append(resp.text.strip())
    return rewritten


