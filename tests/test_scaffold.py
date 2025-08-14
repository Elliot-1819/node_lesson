from pathlib import Path


def test_templates_exist_and_parse():
    templates_path = Path(__file__).resolve().parents[1] / "src" / "config" / "templates.json"
    assert templates_path.exists(), "templates.json missing"
    content = templates_path.read_text(encoding="utf-8")
    assert content.strip().startswith("["), "templates.json should be a list"


def test_can_import_modules():
    # Smoke imports
    import src.main as _
    import src.pipeline.step1_fetch as _
    import src.services.llm_service as _
    import src.utils.logging_utils as _


