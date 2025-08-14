"""Step 4 — Score Sentences (deterministic, no heavy deps).

Inputs:
- sentences (required)
- section_keywords (optional)
- labeled (optional) — Step 3 output to apply label priors

Output: list of dicts with text, section_id, score, features
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional


LABEL_PRIOR = {
    "Definition": 0.05,
    "Mechanism": 0.10,
    "Procedure": 0.12,
    "Comparison": 0.10,
    "Example": 0.05,
}


WORD_RE = re.compile(r"[a-z0-9']+")
NUM_RE = re.compile(r"\b\d+(?:[.,]\d+)?%?\b")


def _tokens(text: str) -> List[str]:
    return WORD_RE.findall(text.lower())


def _keyword_density(text: str, keywords: Optional[List[str]]) -> float:
    if not keywords:
        return 0.0
    toks = _tokens(text)
    if not toks:
        return 0.0
    vocab = {k.lower() for k in keywords}
    hits = sum(1 for t in toks if t in vocab)
    return hits / max(len(toks), 1)


def _number_presence(text: str) -> int:
    return 1 if NUM_RE.search(text) else 0


def _length_bonus(num_tokens: int) -> float:
    # Ideal window 8–30 tokens
    if 8 <= num_tokens <= 30:
        return 1.0
    if 5 <= num_tokens <= 40:
        return 0.85
    return 0.6


def _label_prior_boost(label: Optional[str], prob: Optional[float]) -> float:
    if not label or label not in LABEL_PRIOR:
        return 0.0
    p = max(0.0, min(float(prob or 0.0), 1.0))
    return LABEL_PRIOR[label] * (1.0 + 0.5 * p)


def score_sentences(
    sentences: List[str],
    *,
    section_id: Optional[int] = None,
    section_keywords: Optional[List[str]] = None,
    labeled: Optional[List[Dict]] = None,
) -> List[Dict]:
    # Build lookup for labeled results (match by exact text)
    labeled_map: Dict[str, Dict] = {}
    if labeled:
        for rec in labeled:
            t = (rec.get("text") or "").strip()
            if t:
                labeled_map[t] = rec

    out: List[Dict] = []
    for s in sentences:
        toks = _tokens(s)
        kd = _keyword_density(s, section_keywords)
        num_flag = _number_presence(s)
        lb = _length_bonus(len(toks))

        base = 0.35
        score = base + 0.35 * kd + 0.10 * num_flag + 0.20 * lb

        # Optional label prior
        lab = labeled_map.get(s)
        if lab:
            score += _label_prior_boost(lab.get("label"), lab.get("probability"))

        # Clamp and round
        score = max(0.0, min(score, 1.0))
        score = round(score, 3)

        out.append(
            {
                "section_id": section_id,
                "text": s,
                "score": score,
                "features": {
                    "keyword_density": round(kd, 3),
                    "number_presence": int(num_flag),
                    "length_tokens": len(toks),
                    "length_bonus": lb,
                    **({"label": lab.get("label"), "probability": lab.get("probability")} if lab else {}),
                },
            }
        )
    return out


