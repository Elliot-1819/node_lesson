"""Local LLM service wrapper.

Targets a local endpoint compatible with simple JSON POST using fields:
 - model: str
 - prompt: str
 - temperature: float

This is a placeholder; actual schema can be adapted to your local runner
(e.g., Ollama or custom gateway).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional

import requests

from config.settings import get_settings


@dataclass
class LlmResponse:
    text: str
    raw: dict


def rewrite_style(prompt: str, temperature: Optional[float] = None) -> LlmResponse:
    """Send a prompt to the local LLM for micro-rewrite."""
    settings = get_settings()
    payload = {
        "model": settings.local_llm_model,
        "prompt": prompt,
        "temperature": float(temperature if temperature is not None else settings.llm_temperature),
    }
    resp = requests.post(settings.local_llm_endpoint, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # Heuristic extraction depending on provider: use 'response' or 'text'
    text = data.get("response") or data.get("text") or json.dumps(data)
    return LlmResponse(text=text, raw=data)


