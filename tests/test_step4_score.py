from src.pipeline.step4_score import score_sentences


def test_scoring_basic_features():
    sentences = [
        "funding accrues hourly and is settled twice daily.",
        "a simple overview sentence.",
    ]
    kw = ["funding", "settled"]
    out = score_sentences(sentences, section_keywords=kw)
    s_dict = {o["text"]: o["score"] for o in out}
    assert s_dict[sentences[0]] > s_dict[sentences[1]]


def test_label_prior_boost():
    sentences = ["first, compute the mark price."]
    labeled = [{"text": sentences[0], "label": "Procedure", "probability": 0.8}]
    base = score_sentences(sentences)
    boosted = score_sentences(sentences, labeled=labeled)
    assert boosted[0]["score"] >= base[0]["score"]


