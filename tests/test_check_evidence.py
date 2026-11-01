import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "calls"))
from check_evidence import found, plain, problems  # noqa: E402

DOC = plain("<p>In no event will we sell the securities covered hereby in a public primary offering with a value "
            "exceeding more than one&#8209;third of the aggregate market value</p><p>a Leak-<b>Out</b> Agreement "
            "with the Company (the &#8220;Leak-Out Agreement&#8221;)</p>")
URL = "https://www.sec.gov/x.htm"


def get(url):
    return DOC


def row(**kw):
    r = dict(claim="The F-3 is a baby shelf", quote="more than one-third of the aggregate market value", url=URL)
    r.update(kw)
    return r


def test_exact_quote_passes():
    assert problems(9, [row()], get) == []


def test_curly_quotes_and_split_tags_still_match():
    assert found('the "Leak-Out Agreement"', DOC)
    assert found("a Leak-Out Agreement", DOC)


def test_paraphrase_fails():
    assert problems(9, [row(quote="no more than a third of the market value")], get)


def test_changed_number_fails():
    assert problems(9, [row(quote="more than one-half of the aggregate market value")], get)


def test_missing_url_fails():
    assert any("required" in p for p in problems(9, [row(url="")], get))


def test_empty_file_fails():
    assert problems(9, [], get)
