"""Fill data/outcomes.csv from data/signals.csv (rebuilt fully on every run).

Entry = the OPEN of the first trading day after the signal could have been acted on:
  - live rows: the day after detected_at_utc (for after-close events, the next open)
  - BACKFILL rows: the day after the event date in the signal_id (a research view only)
Returns: entry open -> close on trading days 5, 20, 60. A window is left blank until it has passed.
Benchmark by market: IWM (US), ^TPX (Japan), ^FTAI (AIM). Excess is signal minus benchmark.
excess_20d_net subtracts est_cost_pct. That's the number the scoreboard judges.
"""
import csv
import json
import subprocess
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIGNALS, OUTCOMES = ROOT / "data" / "signals.csv", ROOT / "data" / "outcomes.csv"
BENCH = {"US": "IWM", "JP": "^TPX", "UK": "^FTAI"}
HORIZONS = (5, 20, 60)
COLS = ["signal_id", "ret_5d", "ret_20d", "ret_60d", "bench", "bench_ret_5d", "bench_ret_20d",
        "bench_ret_60d", "excess_5d", "excess_20d", "excess_60d", "excess_20d_net", "max_drawdown_20d"]
_cache = {}


def bars(ticker, start):
    """[(date, open, low, close)] from start-10d to today, Yahoo daily (split-adjusted)."""
    key = (ticker, start)
    if key in _cache:
        return _cache[key]
    p1 = int(datetime.combine(start - timedelta(days=10), datetime.min.time(), timezone.utc).timestamp())
    p2 = int(time.time()) + 86400
    raw = subprocess.run(["curl", "-s", "-A", "Mozilla/5.0",
                          f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
                          f"?period1={p1}&period2={p2}&interval=1d"], capture_output=True, timeout=30).stdout
    out = []
    try:
        r = json.loads(raw)["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
        for t, o, lo, c in zip(r["timestamp"], q["open"], q["low"], q["close"]):
            if None not in (o, lo, c):
                out.append((datetime.fromtimestamp(t, timezone.utc).date(), o, lo, c))
    except Exception:
        pass
    _cache[key] = out
    time.sleep(0.3)
    return out


def window(series, after):
    """Index of the first bar strictly after `after`, or None."""
    return next((i for i, b in enumerate(series) if b[0] > after), None)


def rets(series, i):
    entry = series[i][1]
    r = {}
    for h in HORIZONS:
        j = i + h - 1
        r[h] = (series[j][3] / entry - 1) if j < len(series) else None
    lows = [b[2] for b in series[i:i + 20]]
    r["dd20"] = (min(lows) / entry - 1) if len(series) >= i + 20 else None
    return r


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows = list(csv.DictReader(open(SIGNALS, encoding="utf-8")))
    out = []
    for s in rows:
        backfill = "BACKFILL" in s.get("notes", "")
        event_day = date.fromisoformat(s["signal_id"].split("-", 1)[1][:10])
        detect_day = datetime.fromisoformat(s["detected_at_utc"].replace("Z", "+00:00")).date()
        after = event_day if backfill else max(event_day, detect_day)
        tk, bench = s["ticker"], BENCH.get(s["market"], "IWM")
        sb, bb = bars(tk, after), bars(bench, after)
        i, k = window(sb, after), window(bb, after)
        row = {"signal_id": s["signal_id"], "bench": bench}
        if i is not None and k is not None:
            r, b = rets(sb, i), rets(bb, k)
            for h in HORIZONS:
                if r[h] is not None and b[h] is not None:
                    row[f"ret_{h}d"], row[f"bench_ret_{h}d"] = round(r[h] * 100, 2), round(b[h] * 100, 2)
                    row[f"excess_{h}d"] = round((r[h] - b[h]) * 100, 2)
            if "excess_20d" in row:
                row["excess_20d_net"] = round(row["excess_20d"] - float(s["est_cost_pct"] or 0), 2)
            if r["dd20"] is not None:
                row["max_drawdown_20d"] = round(r["dd20"] * 100, 2)
        out.append(row)
        print(f"{s['signal_id']:<45} {tk:<6} 5d {row.get('ret_5d','…'):>7} | 20d {row.get('ret_20d','…'):>7} "
              f"| excess20 net {row.get('excess_20d_net','…'):>7}{'  (backfill)' if backfill else ''}")
    with open(OUTCOMES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(out)


if __name__ == "__main__":
    main()
