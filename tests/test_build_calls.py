import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "calls"))
from build_calls import post_text, side_label  # noqa: E402


def test_long_call_label():
    assert side_label({"direction": "1"}) == "LONG"
    assert side_label({"direction": "1", "horizon": "long"}) == "LONG (long-term)"


def test_down_call_reads_avoid_not_short():
    # He has a cash account and cannot short: a -1 call is an AVOID (rule 2026-10-23).
    assert side_label({"direction": "-1"}) == "AVOID"


def test_post_text_uses_avoid():
    c = {"id": "2", "direction": "-1", "ticker": "AEHL", "thesis": "ATM of ~70% of Class A", "review_date": "2026-11-20",
         "control": "IWM", "benchmark": "IWM", "invalidation_close": ""}
    assert post_text(c, link=False).startswith("CALL #2 · AVOID $AEHL")
