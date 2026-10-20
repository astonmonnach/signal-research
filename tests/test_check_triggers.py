import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ledger"))
from check_triggers import problems  # noqa: E402

STRATS = {"govfilings", "overhang", "spinoff", "activist", "mergerarb"}
TODAY = date(2026, 10, 20)


def row(**kw):
    r = dict(id="T1", set_date="2026-10-20", ticker="BMM", verdict="TRACKED", strategy="govfilings",
             trigger="ELMT's US$25M prepayment to Blue Moon is announced as closed", kind="filing",
             value="6-K|8-K@BMM", deadline="2026-10-29", source="research/BMM-2026-10-20.html",
             status="open", status_date="", note="")
    r.update(kw)
    return r


def test_good_row_passes():
    assert problems([row()], {}, STRATS, TODAY) == []


def test_missing_deadline_fails():
    assert any("deadline" in p for p in problems([row(deadline="")], {}, STRATS, TODAY))


def test_deadline_before_set_date_fails():
    assert any("deadline" in p for p in problems([row(deadline="2026-10-01")], {}, STRATS, TODAY))


def test_bad_kind_fails():
    assert any("kind" in p for p in problems([row(kind="vibes")], {}, STRATS, TODAY))


def test_price_kind_needs_number():
    assert any("value" in p for p in problems([row(kind="price_above", value="abc")], {}, STRATS, TODAY))
    assert problems([row(kind="price_above", value="4.50")], {}, STRATS, TODAY) == []


def test_filing_kind_needs_forms_at_ticker():
    assert any("value" in p for p in problems([row(value="6-K")], {}, STRATS, TODAY))


def test_unknown_strategy_fails():
    assert any("strategy" in p for p in problems([row(strategy="memes")], {}, STRATS, TODAY))


def test_duplicate_id_fails():
    assert any("duplicate" in p for p in problems([row(), row()], {}, STRATS, TODAY))


def test_latest_watch_verdict_needs_open_row():
    out = problems([row()], {"RYAM": "WATCH", "TWST": "AVOID"}, STRATS, TODAY)
    assert any("RYAM" in p for p in out)
    assert not any("TWST" in p for p in out)


def test_watch_with_open_row_passes():
    r = row(ticker="RYAM", verdict="WATCH", kind="date", value="")
    assert problems([r], {"RYAM": "WATCH (sale review)"}, STRATS, TODAY) == []


def test_overdue_open_row_is_reported():
    out = problems([row(deadline="2026-10-19", set_date="2026-10-10")], {}, STRATS, TODAY)
    assert any("overdue" in p for p in out)
