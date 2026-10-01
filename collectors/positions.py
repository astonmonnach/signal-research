"""Open positions check: price, P&L after fees, distance to the exit line, vs benchmark.

Usage:  python collectors/positions.py
Reads open rows (no exit) from journal/trades.csv and each idea file's exit line.
Writes watch/positions.md. Never trades.
"""
import csv
import json
import re
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCH = "IWM"


def closes(ticker, start):
    p1 = int(datetime.combine(start, datetime.min.time(), timezone.utc).timestamp()) - 5 * 86400
    raw = subprocess.run(["curl", "-s", "-A", "Mozilla/5.0",
                          f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={p1}"
                          f"&period2={int(datetime.now(timezone.utc).timestamp())}&interval=1d"],
                         capture_output=True, timeout=30).stdout
    r = json.loads(raw)["chart"]["result"][0]
    out = [(datetime.fromtimestamp(t, timezone.utc).date(), c)
           for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if c is not None]
    return out, r["meta"].get("regularMarketPrice")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows = [r for r in csv.DictReader(open(ROOT / "journal" / "trades.csv", encoding="utf-8"))
            if r["entry"] and not r["exit"]]
    lines = [f"# Open positions: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC", ""]
    if not rows:
        lines.append("No open positions.")
    for r in rows:
        sym, qty, entry = r["symbol"], float(r["quantity"]), float(r["entry"])
        fees = float(r["fees_total"] or 0)
        start = date.fromisoformat(r["entry_date"])
        series, last = closes(sym, start)
        bseries, blast = closes(BENCH, start)
        b0 = next((c for d, c in bseries if d >= start), bseries[-1][1])
        stop = float(r["stop"]) if r["stop"] else None
        sell_comm = 0.58                                           # IBKR min-ish on a small sale
        pnl = (last - entry) * qty - fees - sell_comm
        days_below = sum(1 for d, c in series if d > start and stop and c < stop)
        last_close = series[-1][1]
        idea = (ROOT / r["idea_file"]).read_text(encoding="utf-8") if r["idea_file"] else ""
        check = re.search(r"Thesis check:\*\*(.+)", idea)
        lines += [f"## {sym}  (trade #{r['id']}, {r['strategy']})",
                  f"- Price **${last:.2f}** vs entry ${entry:.3f}: **{(last / entry - 1) * 100:+.1f}%**",
                  f"- P&L if sold now, after all fees: **${pnl:+.2f}**  (fees paid so far ${fees:.2f})",
                  f"- vs {BENCH} since entry: {(last / entry - 1) * 100 - (blast / b0 - 1) * 100:+.1f} pts",
                  (f"- Exit line: daily close below **${stop:.2f}**, which is {(last_close / stop - 1) * 100:.1f}% away "
                   f"(last close ${last_close:.2f}). {'⚠️ CLOSED BELOW. Exit rule triggered.' if last_close < stop else 'OK.'}")
                  if stop else "- No exit line set.",
                  f"- Thesis check:{check.group(1).strip()}" if check else "", ""]
    out = ROOT / "watch" / "positions.md"
    out.write_text("\n".join(l for l in lines if l is not None) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
