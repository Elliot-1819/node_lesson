from src.pipeline.step2_normalize import normalize_and_split


def test_normalize_and_split_exact_dedupe():
    # Two exact duplicates after normalization (same punctuation), one case variant
    text = "Hello world. Hello world. HELLO world. Another line."
    out = normalize_and_split(text)
    # Only one 'hello world.' sentence should remain after normalization + exact dedupe
    hello_variants = [s for s in out if s == "hello world."]
    assert len(hello_variants) == 1
    # 'another line.' should be present
    assert "another line." in out


