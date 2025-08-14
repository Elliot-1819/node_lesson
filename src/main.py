"""CLI entry and orchestrator skeleton.

Implements a minimal Typer CLI for developer workflows:
 - info: print effective settings
 - check-templates: validate template schema presence
 - scaffold-ok: verify key directories/files exist

No pipeline logic is executed here yet; steps are implemented incrementally.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer

# Make local src imports work when running directly
CURRENT_DIR = Path(__file__).resolve().parent

try:
    # Local imports
    from config.settings import get_settings
    from utils.logging_utils import configure_json_logging
except Exception as exc:  # pragma: no cover - import aid
    # Fallback if run in unusual contexts
    sys.path.append(str(CURRENT_DIR))
    from config.settings import get_settings  # type: ignore
    from utils.logging_utils import configure_json_logging  # type: ignore


app = typer.Typer(help="Lesson Builder CLI (architecture scaffold)")


# -----------------------------
# Artifact-driven step commands
# -----------------------------

@app.command("step1")
def cli_step1(limit: int = typer.Option(10, min=1, help="Max number of sections to fetch from DB"),
              out_path: Path = typer.Option(..., help="Where to write step1_sections.json")) -> None:
    from pipeline.step1_fetch import fetch_sections
    from cli.artifacts import write_json

    sections = fetch_sections(limit)
    payload = [s.__dict__ for s in sections]
    write_json(out_path, payload)
    typer.echo(f"Wrote sections: {len(sections)} (limit={limit}) → {out_path}")


@app.command("step2")
def cli_step2(in_path: Path = typer.Option(..., exists=True, help="Path to step1_sections.json"),
              section_id: int = typer.Option(..., help="Required: section_id to process"),
              out_path: Path = typer.Option(..., help="Where to write step2_sentences.json")) -> None:
    from cli.artifacts import read_json, write_json
    from pipeline.step2_normalize import normalize_and_split

    data = read_json(in_path)
    if not isinstance(data, list):
        raise typer.Exit(code=1)
    # find the requested section by id
    match = next((s for s in data if int(s.get("section_id")) == int(section_id)), None)
    if not match:
        typer.echo(f"section_id {section_id} not found in {in_path}")
        raise typer.Exit(code=1)
    sentences = normalize_and_split(str(match.get("text", "")))
    write_json(out_path, {"section_id": section_id, "sentences": sentences})
    typer.echo(f"Wrote sentences: {len(sentences)} → {out_path}")


@app.command("step3")
def cli_step3(in_path: Path = typer.Option(..., exists=True, help="Path to step2_sentences.json"),
              out_path: Path = typer.Option(..., help="Where to write step3_labeled.json"),
              context_path: Path = typer.Option(Path('.out/step1_sections.json'), exists=False, help="Optional: path to step1 sections for keywords"),
              no_llm: bool = typer.Option(False, help="Disable LLM fallback for classification")) -> None:
    from cli.artifacts import read_json, write_json
    from pipeline.step3_label import label_sentences
    from config.settings import get_settings

    data = read_json(in_path)
    section_id = data.get("section_id") if isinstance(data, dict) else None
    sentences = data.get("sentences", []) if isinstance(data, dict) else data

    # Load section keywords if context is provided and section_id is known
    section_keywords = None
    if section_id and context_path.exists():
        try:
            ctx = read_json(context_path)
            for rec in ctx:
                if int(rec.get("section_id")) == int(section_id):
                    section_keywords = rec.get("keywords")
                    break
        except Exception:
            section_keywords = None

    # Optionally disable LLM fallback
    settings = get_settings()
    if no_llm:
        object.__setattr__(settings, 'classifier_use_llm_fallback', False)  # type: ignore

    labeled = label_sentences(sentences, section_keywords=section_keywords)
    result = [{
        "section_id": section_id,
        "text": t,
        "label": c.label,
        "probability": c.probability,
        "rule_hit": c.rule_hit,
        "source": c.source,
    } for t, c in labeled]
    write_json(out_path, result)
    typer.echo(f"Wrote labeled: {len(result)} → {out_path}")


@app.command("step4")
def cli_step4(in_path: Path = typer.Option(..., exists=True, help="Path to step2_sentences.json"),
              out_path: Path = typer.Option(..., help="Where to write step4_scores.json")) -> None:
    from cli.artifacts import read_json, write_json
    from pipeline.step4_score import score_sentences

    data = read_json(in_path)
    sentences = data.get("sentences", []) if isinstance(data, dict) else data
    scores = score_sentences(sentences)
    write_json(out_path, [{"text": s.text, "score": s.score} for s in scores])
    typer.echo(f"Wrote scores: {len(scores)} → {out_path}")


@app.command("step5")
def cli_step5(in_path: Path = typer.Option(..., exists=True, help="Path to step3_labeled.json"),
              out_path: Path = typer.Option(..., help="Where to write step5_selected.json")) -> None:
    from cli.artifacts import read_json, write_json
    from services.classifier import Classification
    from pipeline.step5_select import select_minimal_set

    data = read_json(in_path)
    labeled = [(d["text"], Classification(label=d["label"], probability=float(d.get("probability", 0)), rule_hit=d.get("rule_hit"))) for d in data]
    selected = select_minimal_set(labeled)
    write_json(out_path, selected)
    typer.echo(f"Wrote selected → {out_path}")


@app.command("step6")
def cli_step6(in_path: Path = typer.Option(..., exists=True, help="Path to step5_selected.json"),
              out_path: Path = typer.Option(..., help="Where to write step6_step_count.json")) -> None:
    from cli.artifacts import read_json, write_json
    from pipeline.step6_steps import decide_step_count

    selected = read_json(in_path)
    step_count = decide_step_count(selected)
    write_json(out_path, {"step_count": step_count})
    typer.echo(f"Wrote step_count={step_count} → {out_path}")


@app.command("step7")
def cli_step7(in_path: Path = typer.Option(..., exists=True, help="Path to step5_selected.json"),
              templates_path: Path = typer.Option(Path(__file__).parent / "config" / "templates.json", exists=True, help="Path to templates.json"),
              out_path: Path = typer.Option(..., help="Where to write step7_mapped.json")) -> None:
    from cli.artifacts import read_json, write_json
    from pipeline.step7_templates import load_templates, map_to_templates

    selected = read_json(in_path)
    templates = load_templates(templates_path)
    mapped = map_to_templates(selected, templates)
    write_json(out_path, mapped)
    typer.echo(f"Wrote mapped steps: {len(mapped)} → {out_path}")


@app.command("step8")
def cli_step8(in_path: Path = typer.Option(..., exists=True, help="Path to step7_mapped.json or a list of texts"),
              out_path: Path = typer.Option(..., help="Where to write step8_rewritten.json")) -> None:
    from cli.artifacts import read_json, write_json
    from pipeline.step8_rewrite import micro_rewrite

    data = read_json(in_path)
    # Accept either a list of strings or mapped steps with 'content'
    if isinstance(data, list) and data and isinstance(data[0], dict) and "content" in data[0]:
        texts = []
        for step in data:
            texts.extend(step.get("content", []))
    else:
        texts = data
    rewritten = micro_rewrite(texts)
    write_json(out_path, rewritten)
    typer.echo(f"Wrote rewritten: {len(rewritten)} → {out_path}")


@app.command("step9")
def cli_step9(in_path: Path = typer.Option(..., exists=True, help="Path to a JSON array of texts to rate"),
              out_path: Path = typer.Option(..., help="Where to write step9_difficulty.json")) -> None:
    from cli.artifacts import read_json, write_json
    from pipeline.step9_difficulty import determine_difficulty

    texts = read_json(in_path)
    text = "\n".join(texts if isinstance(texts, list) else [str(texts)])
    difficulty = determine_difficulty(text, [])
    write_json(out_path, {"difficulty": difficulty})
    typer.echo(f"Wrote difficulty={difficulty} → {out_path}")


@app.command("step10")
def cli_step10(in_path: Path = typer.Option(..., exists=True, help="Path to a JSON array of texts or a single string"),
               out_path: Path = typer.Option(..., help="Where to write step10_quality.json")) -> None:
    from cli.artifacts import read_json, write_json
    from pipeline.step10_quality import check_quality

    data = read_json(in_path)
    text = "\n".join(data if isinstance(data, list) else [str(data)])
    ok, reason = check_quality(text)
    write_json(out_path, {"ok": ok, "reason": reason})
    typer.echo(f"Wrote quality ok={ok} reason={reason} → {out_path}")


@app.command("step11")
def cli_step11(in_path: Path = typer.Option(..., exists=True, help="Path to mapped steps or rewritten texts"),
               lesson_id: int = typer.Option(1, help="Lesson id to assign"),
               lesson_title: str = typer.Option("Untitled", help="Lesson title"),
               section_style: str = typer.Option("Definition", help="Information style for this section"),
               out_path: Path = typer.Option(..., help="Where to write step11_lesson_rows.json")) -> None:
    from cli.artifacts import read_json, write_json
    from pipeline.step11_persist import LessonRow

    data = read_json(in_path)
    # Accept either mapped steps or a list of strings
    contents = []
    if isinstance(data, list) and data and isinstance(data[0], dict) and "content" in data[0]:
        for idx, step in enumerate(data):
            for i, text in enumerate(step.get("content", [])):
                contents.append((idx + 1, step.get("info_type", section_style), text))
    else:
        # treat as a single section with multiple lines
        for i, text in enumerate(data if isinstance(data, list) else [str(data)]):
            contents.append((i + 1, section_style, text))

    rows = [LessonRow(lesson_id=lesson_id, lesson_title=lesson_title, section_id=sec_id, section_style=style, content=text).__dict__ for sec_id, style, text in contents]
    write_json(out_path, rows)
    typer.echo(f"Wrote lesson rows: {len(rows)} → {out_path}")


@app.command()
def info() -> None:
    """Print effective settings as JSON."""
    settings = get_settings()
    configure_json_logging()
    typer.echo(json.dumps(settings.__dict__, indent=2, sort_keys=True))


@app.command("check-templates")
def check_templates() -> None:
    """Validate `templates.json` exists and is well-formed."""
    templates_path = CURRENT_DIR / "config" / "templates.json"
    if not templates_path.exists():
        raise typer.Exit(code=1)
    try:
        data = json.loads(templates_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        typer.echo(f"Invalid JSON: {exc}")
        raise typer.Exit(code=1)

    if not isinstance(data, list) or not data:
        typer.echo("templates.json must be a non-empty list")
        raise typer.Exit(code=1)
    typer.echo(f"Loaded {len(data)} templates from {templates_path}")


@app.command("scaffold-ok")
def scaffold_ok() -> None:
    """Check that the scaffolded directories/files exist."""
    required = [
        CURRENT_DIR / "config" / "settings.py",
        CURRENT_DIR / "config" / "templates.json",
        CURRENT_DIR / "utils" / "logging_utils.py",
        CURRENT_DIR / "services" / "llm_service.py",
        CURRENT_DIR / "pipeline",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        typer.echo("Missing required files:\n" + "\n".join(missing))
        raise typer.Exit(code=1)
    typer.echo("Scaffold looks good.")


if __name__ == "__main__":  # pragma: no cover
    app()


