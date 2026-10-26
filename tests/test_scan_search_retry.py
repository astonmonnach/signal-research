import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "watch"))
import scan_market  # noqa: E402

GOOD = json.dumps({"hits": {"hits": [{"_id": "0001:a.htm", "_source": {}}]}}).encode()


def _flaky(failures, monkeypatch):
    calls, waits = {"n": 0}, []

    def fetch(url):
        calls["n"] += 1
        if calls["n"] <= failures:
            return b'{"error": "rate limited"}'          # what EDGAR sent on 23 Oct: no "hits" key
        return GOOD

    monkeypatch.setattr(scan_market, "fetch", fetch)
    monkeypatch.setattr(scan_market.time, "sleep", waits.append)
    return calls, waits


def test_search_survives_an_outage_longer_than_three_quick_tries(monkeypatch):
    calls, waits = _flaky(3, monkeypatch)
    assert len(scan_market.search('"agreement and plan of merger"', "2026-10-23", "8-K")) == 1
    assert calls["n"] == 4
    assert sum(waits) >= 30          # it backs off, not just three 2-second retries


def test_search_still_reports_a_failure_it_cannot_recover(monkeypatch):
    _flaky(99, monkeypatch)
    try:
        scan_market.search('"tender offer"', "2026-10-23", "6-K")
    except Exception:
        return
    raise AssertionError("a search that never recovers must raise, so the report says it failed")
