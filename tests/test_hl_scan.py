import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "crypto" / "hyperliquid"))
from scan import cleanness, daily_bars, passes, profile  # noqa: E402

H = 3_600_000  # one hour in ms


def bar(i, o, h, l, c, v=1000.0):
    return {"t": i * H, "o": o, "h": h, "l": l, "c": c, "v": v}


def test_cleanness_is_one_for_a_straight_line():
    closes = [100 + i for i in range(49)]
    assert abs(cleanness(closes, 24) - 1.0) < 1e-9


def test_cleanness_is_low_for_chop():
    closes = [100, 102] * 25
    assert cleanness(closes, 24) < 0.1


def test_daily_bars_group_24_hours():
    hours = [bar(i, 10, 11 if i == 5 else 10.5, 9.5, 10.2) for i in range(48)]
    days = daily_bars(hours)
    assert len(days) == 2
    assert days[0]["h"] == 11 and days[0]["l"] == 9.5 and days[0]["o"] == 10 and days[0]["c"] == 10.2


def test_profile_measures_ranges():
    hours = [bar(i, 10, 10.5, 9.5, 10) for i in range(48)]
    p = profile(hours)
    assert abs(p["hour_range_pct"] - 10.0) < 1e-9          # (10.5 - 9.5) / 10
    assert abs(p["day_range_pct"] - 10.0) < 1e-9
    assert p["days_10pct"] == 1.0                           # both days moved 10%


def test_passes_barriers():
    ok = {"max_lev": 10, "vol_24h": 2e6, "oi_usd": 1e6, "delisted": False}
    assert passes(ok, min_lev=10, min_vol=1e6, min_oi=5e5)
    assert not passes({**ok, "max_lev": 5}, min_lev=10, min_vol=1e6, min_oi=5e5)
    assert not passes({**ok, "vol_24h": 5e5}, min_lev=10, min_vol=1e6, min_oi=5e5)
    assert not passes({**ok, "delisted": True}, min_lev=10, min_vol=1e6, min_oi=5e5)
