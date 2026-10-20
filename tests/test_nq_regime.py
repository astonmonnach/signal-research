import random
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "collectors"))
from nq_regime import completed, label, measure  # noqa: E402

RATES = {"big": (0.30, 93), "high": (0.07, 120), "normal": (0.06, 790)}


def rows(n=700, seed=1):
    rnd = random.Random(seed)
    out, close, d = [], 10000.0, date(2023, 1, 2)
    for _ in range(n):
        rng = close * rnd.uniform(0.005, 0.04)
        out.append((d, close + rng / 2, close - rng / 2, close))
        close *= 1 + rnd.uniform(-0.01, 0.01)
        d += timedelta(days=1)
    return out


def test_label_big():
    assert label("big", RATES, 0.09) == "EXPANSION LIKELY"


def test_label_high_not_measured_higher():
    assert label("high", RATES, 0.09) == "NORMAL"


def test_label_high_measured_higher():
    assert label("high", {**RATES, "high": (0.15, 120)}, 0.09) == "ELEVATED"


def test_label_normal():
    assert label("normal", RATES, 0.09) == "NORMAL"


def test_measure_is_consistent():
    m = measure(rows())
    assert m["state"] in ("big", "high", "normal")
    assert m["p_next"] == m["rates"][m["state"]][0]
    assert sum(n for _, n in m["rates"].values()) == m["pairs"]
    assert 0 <= m["base"] <= 1
    assert m["label"] == label(m["state"], m["rates"], m["base"])
    assert m["last_day"] == rows()[-1][0]


def test_completed_drops_live_bar():
    r = [(date(2026, 10, 19), 1, 1, 1), (date(2026, 10, 20), 1, 1, 1)]
    assert completed(r, datetime(2026, 10, 20, 6, 30, tzinfo=UTC))[-1][0] == date(2026, 10, 19)
    assert completed(r, datetime(2026, 10, 20, 21, 30, tzinfo=UTC))[-1][0] == date(2026, 10, 20)
