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


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows = daily()
    now = datetime.now(timezone.utc)
    if rows[-1][0] == now.date() and now.hour < 21:   # session still trading (CME daily bar closes ~21:00 UTC)
        rows = rows[:-1]
    rng =[None] + [(rows[i][1] - rows[i][2]) / rows[i - 1][3] * 100 for i in range(1, len(rows))]
    big = [None] * len(rows)
    for i in range(253, len(rows)):
        window = sorted(rng[i - 252:i])
        big[i] = rng[i] >= window[int(0.9 * 252)]
    pairs = [(big[i - 1], big[i]) for i in range(254, len(rows))]
    base = sum(b for _, b in pairs) / len(pairs)
    after_big = [b for p, b in pairs if p]
    after_quiet = [b for p, b in pairs if not p]
    p_big = sum(after_big) / len(after_big)
    p_quiet = sum(after_quiet) / len(after_quiet)

    last_day, last_rng, last_big = rows[-1][0], rng[-1], big[-1]
    pct = sum(x <= last_rng for x in rng[-253:-1]) / 252 * 100
    p_next = p_big if last_big else p_quiet
    verdict = "EXPANSION LIKELY" if last_big else ("ELEVATED" if pct >= 75 else "NORMAL")

    lines = [f"# NQ regime: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC", "",
             f"Last session **{last_day}**: range **{last_rng:.2f}%** of prior close, "
             f"{pct:.0f}th percentile of the past year. Big day: **{'YES' if last_big else 'no'}**.", "",
             f"**Next session: {verdict}.** P(big day) = **{p_next*100:.0f}%** vs a {base*100:.0f}% base rate "
             f"({p_next/base:.1f}x).", "",
             f"Measured on {len(pairs)} sessions: after a big day {p_big*100:.0f}% (n={len(after_big)}), "
             f"after a non-big day {p_quiet*100:.0f}% (n={len(after_quiet)}).", "",
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
