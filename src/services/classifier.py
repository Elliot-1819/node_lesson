"""Classifier service (Step 3): rules-first with optional local LLM fallback.

Design goals:
- High precision, deterministic rules and features per info type
- Softmax probabilities from rule scores (no heavy ML deps)
- Optional bounded fallback to a local LLM for low-confidence cases
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import re

from config.settings import get_settings
from services.llm_service import rewrite_style  # reuse transport; function is generic


INFO_TYPES: List[str] = [
    "Definition",
    "Mechanism",
    "Procedure",
    "Comparison",
    "Example",
]


@dataclass
class Classification:
    label: str
    probability: float
    rule_hit: List[str]
    source: str  # "rules" | "llm_fallback"


_RE = {
    # Definition: require article after is/are to avoid passive forms like "is settled"
    "def_is": re.compile(r"\b(is|are)\s+(a|an|the)\b"),
    "def_defined_as": re.compile(r"\bdefined as\b|\brefers to\b|\bis a type of\b"),
    "mech_causal": re.compile(r"\bbecause\b|\btherefore\b|\bso that\b|\benables\b|\bkeeps\b|\bcauses\b"),
    "mech_settle": re.compile(r"\bsettled\b|\baccrues\b|\baligns?\b|\bfunding\b|\bmark price\b"),
    "proc_steps": re.compile(r"\b(step|first|second|third|then|finally)\b|\b\d+\.\b"),
    # Avoid broad imperative pattern to prevent false positives like "compared to spot"
    "comp_markers": re.compile(r"\bvs\.?\b|\bversus\b|\bcompared to\b|\bas opposed to\b|\beither\b.*\bor\b"),
    "ex_markers": re.compile(r"\bfor example\b|\bfor instance\b|\be\.g\.\b|\ban investor\b|\bscenario\b|\btim\b"),
}


def _feature_boosts(lowered: str) -> Dict[str, float]:
    boosts = {t: 0.0 for t in INFO_TYPES}
    if re.search(r"\b\d+\b|\b\d+%\b", lowered):
        boosts["Mechanism"] += 0.2
        boosts["Procedure"] += 0.2
    if _RE["proc_steps"].search(lowered):
        boosts["Procedure"] += 0.4
    if _RE["mech_causal"].search(lowered):
        boosts["Mechanism"] += 0.4
    return boosts


def _rule_scores(lowered: str) -> Tuple[Dict[str, float], List[str]]:
    scores = {t: 0.0 for t in INFO_TYPES}
    hits: List[str] = []
    if _RE["def_is"].search(lowered) or _RE["def_defined_as"].search(lowered):
        scores["Definition"] += 1.0
        hits.append("definition")
    if _RE["mech_causal"].search(lowered) or _RE["mech_settle"].search(lowered):
        scores["Mechanism"] += 1.0
        hits.append("mechanism")
    if _RE["proc_steps"].search(lowered):
        scores["Procedure"] += 1.0
        hits.append("procedure")
    if _RE["comp_markers"].search(lowered):
        scores["Comparison"] += 1.0
        hits.append("comparison")
    if _RE["ex_markers"].search(lowered):
        scores["Example"] += 1.0
        hits.append("example")
    return scores, hits


def _keyword_density_boost(lowered: str, keywords: Optional[List[str]]) -> float:
    if not keywords:
        return 0.0
    toks = [t for t in re.findall(r"[a-z0-9']+", lowered)]
    if not toks:
        return 0.0
    vocab = {k.lower() for k in keywords}
    hits = sum(1 for t in toks if t in vocab)
    return 0.5 * (hits / max(len(toks), 1))


def _softmax(scores: Dict[str, float]) -> Dict[str, float]:
    import math
    vals = list(scores.values())
    m = max(vals) if vals else 0.0
    exp = {k: math.exp(v - m) for k, v in scores.items()}
    s = sum(exp.values()) or 1.0
    return {k: v / s for k, v in exp.items()}


def classify_with_scores(text: str, section_keywords: Optional[List[str]] = None) -> Classification:
    lowered = text.strip().lower()
    rule_scores, hits = _rule_scores(lowered)
    boosts = _feature_boosts(lowered)
    for k in rule_scores:
        rule_scores[k] += boosts.get(k, 0.0)
    # Keyword density multiplies all scores slightly to prefer on-topic sentences
    kd = _keyword_density_boost(lowered, section_keywords)
    for k in rule_scores:
        rule_scores[k] *= (1.0 + kd)

    probs = _softmax(rule_scores)
    label = max(probs.items(), key=lambda kv: kv[1])[0]
    prob = probs[label]
    return Classification(label=label, probability=prob, rule_hit=hits, source="rules")


def classify_with_fallback(text: str, section_keywords: Optional[List[str]] = None) -> Classification:
    settings = get_settings()
    base = classify_with_scores(text, section_keywords)
    if not settings.classifier_use_llm_fallback:
        return base

    # Confidence check
    threshold = settings.classifier_score_threshold
    margin = settings.classifier_margin_threshold
    # Compute second best for margin
    # Recompute scores to get full distribution
    lowered = text.strip().lower()
    rule_scores, _ = _rule_scores(lowered)
    boosts = _feature_boosts(lowered)
    for k in rule_scores:
        rule_scores[k] += boosts.get(k, 0.0)
    kd = _keyword_density_boost(lowered, section_keywords)
    for k in rule_scores:
        rule_scores[k] *= (1.0 + kd)
    probs = _softmax(rule_scores)
    top = sorted(probs.items(), key=lambda kv: kv[1], reverse=True)
    second = top[1][1] if len(top) > 1 else 0.0

    if base.probability >= threshold and (base.probability - second) >= margin:
        return base

    # LLM fallback
    prompt = (
        "Classify the sentence into one label from this set: "
        "[Definition, Mechanism, Procedure, Comparison, Example].\n"
        "Respond in strict JSON as {\"label\": \"...\", \"confidence\": 0-1}.\n"
        f"Sentence: {text}"
    )
    try:
        resp = rewrite_style(prompt, temperature=0.1)  # reuse HTTP transport
        import json
        data = json.loads(resp.text) if isinstance(resp.text, str) else resp.text
        lbl = data.get("label")
        conf = float(data.get("confidence", 0))
        if lbl in INFO_TYPES and 0.0 <= conf <= 1.0:
            return Classification(label=lbl, probability=conf, rule_hit=["llm"], source="llm_fallback")
    except Exception:
        pass
    return base


# Legacy placeholder kept for API compatibility; not used
def classify_tiny_model(text: str) -> Classification:  # pragma: no cover - not wired yet
    return Classification(label="Example", probability=0.51, rule_hit=["legacy"], source="rules")


