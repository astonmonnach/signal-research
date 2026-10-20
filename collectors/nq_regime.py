"""NQ regime check: Thomas's 'WHEN, not WHAT' finding turned into a daily flag.

Usage:  python collectors/nq_regime.py
Finding (OVERVIEW.md, NQ 2017-25): big days cluster. P(big day | prior day big) ~40% vs a ~10%
base rate (4x). Compression does NOT predict expansion; expansion predicts expansion.
70.6% of the largest 30-min NQ moves start 09:00-11:00 ET (14:00-16:00 UK).

Big day = daily range (high-low, % of prior close) in the top 10% of the trailing 252 sessions.
This script re-measures the clustering on the last ~3 years of NQ=F data (so the number is
current, not quoted) and says whether TOMORROW is a high-probability expansion day.
Writes watch/nq_regime.md and appends to data/nq_regime_log.csv.
"""
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def daily(ticker="NQ=F", rng="5y"):
    raw = subprocess.run(["curl", "-s", "-A", "Mozilla/5.0",
                          f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={rng}&interval=1d"],
                         capture_output=True, timeout=30).stdout
    r = json.loads(raw)["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    rows = []
    for t, h, l, c in zip(r["timestamp"], q["high"], q["low"], q["close"]):
        if None not in (h, l, c):
            rows.append((datetime.fromtimestamp(t, timezone.utc).date(), h, l, c))
    return rows


def completed(rows, now_utc):
    """Drop today's bar while the session is still trading (CME daily bar closes ~21:00 UTC)."""
    if rows and rows[-1][0] == now_utc.date() and now_utc.hour < 21:
        return rows[:-1]
    return rows


def label(state, rates, base):
    """Rule 2026-10-20: the label comes from measured rates, not from a percentile.
    ELEVATED only when the measured big-day rate after a 75th-90th percentile day beats the base rate."""
    if state == "big":
        return "EXPANSION LIKELY"
    p_high = rates["high"][0]
    if state == "high" and p_high is not None and p_high > base:
        return "ELEVATED"
    return "NORMAL"


def measure(rows):
    """Big day = range in the top 10% of the trailing 252 sessions. Each day is 'big', 'high'
    (75th percentile up to big) or 'normal'; rates are P(next day big) after each state."""
    rng = [None] + [(rows[i][1] - rows[i][2]) / rows[i - 1][3] * 100 for i in range(1, len(rows))]
    big, state, pctile = [None] * len(rows), [None] * len(rows), [None] * len(rows)
    for i in range(253, len(rows)):
        prior = rng[i - 252:i]
        window = sorted(prior)
        big[i] = rng[i] >= window[int(0.9 * 252)]
        pctile[i] = sum(x <= rng[i] for x in prior) / 252 * 100
        state[i] = "big" if big[i] else ("high" if pctile[i] >= 75 else "normal")
    pairs = [(state[i - 1], big[i]) for i in range(254, len(rows))]
    base = sum(b for _, b in pairs) / len(pairs)
    rates = {}
    for s in ("big", "high", "normal"):
        after = [b for p, b in pairs if p == s]
        rates[s] = (sum(after) / len(after) if after else None, len(after))
    last = state[-1]
    return {"last_day": rows[-1][0], "last_range_pct": rng[-1], "last_pctile": pctile[-1],
            "state": last, "base": base, "rates": rates, "pairs": len(pairs),
            "p_next": rates[last][0], "label": label(last, rates, base)}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    m = measure(completed(daily(), datetime.now(timezone.utc)))
    last_day, last_rng, pct = m["last_day"], m["last_range_pct"], m["last_pctile"]
    last_big, base, p_next, rates = m["state"] == "big", m["base"], m["p_next"], m["rates"]

    def rate(s):
        p, n = rates[s]
        return f"{p*100:.0f}% (n={n})" if p is not None else f"n/a (n={n})"

    lines = [f"# NQ regime: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC", "",
             f"Last session **{last_day}**: range **{last_rng:.2f}%** of prior close, "
             f"{pct:.0f}th percentile of the past year. Big day: **{'YES' if last_big else 'no'}**.", "",
             f"**Next session: {m['label']}.** P(big day) = **{p_next*100:.0f}%** vs a {base*100:.0f}% base rate "
             f"({p_next/base:.1f}x).", "",
             f"Measured on {m['pairs']} sessions: after a big day {rate('big')}, after a 75th-90th percentile day "
             f"{rate('high')}, after any other day {rate('normal')}.", "",
             "Timing (from research): the largest moves cluster 09:00-11:00 ET = **14:00-16:00 UK**. "
             "Direction is NOT predicted, only the size and timing."]
    out = ROOT / "watch" / "nq_regime.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log = ROOT / "data" / "nq_regime_log.csv"
    new = not log.exists()
    with open(log, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["checked_utc", "session", "range_pct", "pctile", "big", "p_next_big", "base"])
        w.writerow([datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), last_day, round(last_rng, 3),
                    round(pct, 1), last_big, round(p_next, 3), round(base, 3)])
    print("\n".join(lines))


if __name__ == "__main__":
    main()
