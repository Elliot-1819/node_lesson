import pytest

from src.config.settings import get_settings
from src.db.db_utils import fetch_pending_sections
from src.pipeline.step2_normalize import normalize_and_split
from src.pipeline.step3_label import label_sentences
from src.pipeline.step4_score import score_sentences


def test_page_end_to_end_pipeline():
    settings = get_settings()

    if not settings.database_url:
        pytest.skip("DATABASE_URL not configured; skipping DB integration test")

    # Ensure LLM fallback is disabled for deterministic test
    try:
        object.__setattr__(settings, 'classifier_use_llm_fallback', False)  # type: ignore
    except Exception:
        pass

    try:
        sections = fetch_pending_sections(limit=1)
    except Exception as exc:
        pytest.skip(f"DB not reachable or table missing: {exc}")

    assert sections, "Expected at least one section from the DB"

    # Take the first page's sections
    first_page_id = sections[0].page_id
    page_sections = [s for s in sections if s.page_id == first_page_id]
    assert page_sections, "No sections found for the first page"

    total_sentences = 0

    for sec in page_sections:
        # Step 2
        sentences = normalize_and_split(sec.text)
        total_sentences += len(sentences)

        # Step 3
        labeled_pairs = label_sentences(sentences, section_keywords=sec.keywords)
        assert len(labeled_pairs) == len(sentences)
        labeled_for_scoring = [
            {"text": t, "label": c.label, "probability": c.probability}
            for t, c in labeled_pairs
        ]

        # Step 4
        scored = score_sentences(
            sentences,
            section_id=sec.section_id,
            section_keywords=sec.keywords,
            labeled=labeled_for_scoring,
        )
        assert len(scored) == len(sentences)
        for rec in scored:
            assert 0.0 <= rec["score"] <= 1.0
            feats = rec.get("features", {})
            for key in ("keyword_density", "number_presence", "length_tokens", "length_bonus"):
                assert key in feats

    assert total_sentences > 0, "Expected at least one sentence across sections"


