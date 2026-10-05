"""Public calls: the conviction track record. Not trades, so capital doesn't matter.

A call is a stock we commit to publicly and keep, no matter what, until its own pre-stated exit
rule closes it. Calls are append-only: never edit or delete a row; closing a call only fills the
exit columns. Every call is marked from the next session's open after it was posted, on a
standard $1,000 notional, against a benchmark (IWM for swing calls, SPY for long-term calls) and a
named control ticker.

Run:  python calls/build_calls.py            -> calls/README.md (the public record), calls/marks.csv
      python calls/build_calls.py --post ID  -> prints the facts block for an X post (you write the post)
      python calls/build_calls.py --announce -> also posts new and newly closed calls to Discord #calls (once each)

calls/CALLS.csv columns:
  id, posted_utc, ticker, direction (+1 long / -1 short), thesis, dossier, invalidation_close
  (exit if a daily close crosses it), review_date (exit at that day's close), control,
  conviction (1-3), source (where it was posted: X url or 'repo'), exit_date, exit_price, exit_reason,
  horizon (swing / long), benchmark (IWM default; SPY for long-term)
"""
import csv, json, sys, time, urllib.request, datetime as dt
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).resolve().parents[1]
CALLS = ROOT / "calls/CALLS.csv"
NOTIONAL = 1000.0
_cache = {}


def bars(t):
    if t in _cache: return _cache[t]
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=1y&interval=1d"
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
        # Yahoo stamps each daily bar at that session's open (09:30 New York, in UTC), kept as `opened`.
        b = [(dt.datetime.fromtimestamp(ts, dt.UTC).date(), o, c, dt.datetime.fromtimestamp(ts, dt.UTC))
             for ts, o, c in zip(r["timestamp"], q["open"], q["close"]) if o and c]
    except Exception:
        b = []
    _cache[t] = b; time.sleep(0.2)
    return b


def mark(call):
    """Entry = next session's open after posting; exit by rule (invalidation close / review date) or still open."""
    posted = dt.datetime.fromisoformat(call["posted_utc"].replace("Z", "+00:00"))
    # Entry is the first session that OPENS after the post: posted pre-market enters that morning,
    # posted mid-session or after the close enters the next day. Never a price seen before posting.
    b = [x[:3] for x in bars(call["ticker"]) if x[3] >= posted]
    ctl = {d: (o, c) for d, o, c, _ in bars(call["control"] or "IWM")}
    bench = call.get("benchmark") or "IWM"
    mkt = {d: (o, c) for d, o, c, _ in bars(bench)}
    after = b
    if not after:
        return dict(call, status="pending (enters next open)")
    ed, eo, _ = after[0]
    d_dir = int(call["direction"])
    exit_d, exit_p, reason = None, None, ""
    if call.get("exit_date"):
        exit_d, exit_p, reason = dt.date.fromisoformat(call["exit_date"]), float(call["exit_price"]), call["exit_reason"]
    else:
        inv = float(call["invalidation_close"]) if call.get("invalidation_close") else None
        rev = dt.date.fromisoformat(call["review_date"]) if call.get("review_date") else None
        for d, o, c in after:
            if inv is not None and ((d_dir > 0 and c < inv) or (d_dir < 0 and c > inv)):
                exit_d, exit_p, reason = d, c, f"invalidation close {c:.2f} vs {inv:.2f}"; break
            if rev and d >= rev:
                exit_d, exit_p, reason = d, c, "review date reached"; break
    end_d, end_p = (exit_d, exit_p) if exit_d else (after[-1][0], after[-1][2])
    ret = d_dir * (end_p / eo - 1) * 100
    def ctl_ret(series):
        if ed in series and end_d in series:
            return (series[end_d][1] / series[ed][0] - 1) * 100
        return None
    r_mkt, r_ctl = ctl_ret(mkt), ctl_ret(ctl)
    return dict(call, entry_date=ed.isoformat(), entry=round(eo, 4), end_date=end_d.isoformat(), end_price=round(end_p, 4),
                ret_pct=round(ret, 2), pnl_usd=round(NOTIONAL * ret / 100, 2),
                bench=bench, bench_pct=None if r_mkt is None else round(r_mkt, 2),
                excess_bench=None if r_mkt is None else round(ret - d_dir * r_mkt, 2),
                control_pct=None if r_ctl is None else round(r_ctl, 2),
                excess_control=None if r_ctl is None else round(ret - d_dir * r_ctl, 2),
                days=(end_d - ed).days, status="closed: " + reason if exit_d else "open")


def post_text(c, link=True):
    side = ("LONG" if int(c["direction"]) > 0 else "SHORT") + (" (long-term)" if c.get("horizon") == "long" else "")
    inv = f"Exit if it closes {'below' if int(c['direction']) > 0 else 'above'} ${c['invalidation_close']} · " if c.get("invalidation_close") else ""
    return (f"CALL #{c['id']} · {side} ${c['ticker']}\nThesis: {c['thesis']}\n{inv}review {c['review_date']}\n"
            f"Measured from the next open vs ${c.get('benchmark') or 'IWM'} and ${c['control']}."
            + (" Every call stays on the public record: github.com/astonmonnach/signal-research/tree/main/calls" if link else ""))


def announce(rows, marked):
    """Post each new call, and each call that has just closed, to Discord #calls once (calls/announced.json)."""
    sys.path.insert(0, str(ROOT / "briefing"))
    import notify
    if not notify.has_own_channel("calls"):
        print("announce: no #calls webhook, nothing sent"); return
    path = ROOT / "calls/announced.json"
    done = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"opened": [], "closed": []}
    for c in rows:
        if c["id"] not in done["opened"] and notify.send("**NEW CALL**\n" + post_text(c, link=False), "calls"):
            done["opened"].append(c["id"])
    for m in marked:
        if m.get("status", "").startswith("closed") and m["id"] not in done["closed"]:
            msg = (f"**CALL #{m['id']} CLOSED** · {m['ticker']} {fmt(m['ret_pct'])} (${m['pnl_usd']:+,.2f} on ${NOTIONAL:,.0f}), "
                   f"{fmt(m['excess_bench'])} vs {m['bench']}, {fmt(m['excess_control'])} vs {m['control']} · {m['status'][8:]}")
            if notify.send(msg, "calls"):
                done["closed"].append(m["id"])
    path.write_text(json.dumps(done, indent=1), encoding="utf-8")


def fmt(v, suf="%"):
    return "" if v in (None, "") else f"{float(v):+.1f}{suf}"


def main():
    rows = list(csv.DictReader(open(CALLS, encoding="utf-8"))) if CALLS.exists() else []
    if "--post" in sys.argv:
        cid = sys.argv[sys.argv.index("--post") + 1]
        print(post_text(next(r for r in rows if r["id"] == cid)))
        return
    marked = [mark(r) for r in rows]
    live = [m for m in marked if "ret_pct" in m]
    with open(ROOT / "calls/marks.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["id", "posted_utc", "ticker", "direction", "horizon", "entry_date", "entry", "end_date", "end_price", "ret_pct",
                "pnl_usd", "bench", "bench_pct", "excess_bench", "control", "control_pct", "excess_control", "days", "status"]
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(marked)
    xs = [m["excess_bench"] for m in live if m.get("excess_bench") is not None]
    t = (mean(xs) / (stdev(xs) / len(xs) ** 0.5)) if len(xs) >= 3 and stdev(xs) > 0 else None
    L = ["# Public calls: the track record", "",
         "Every stock we commit to publicly. **Append-only:** calls are never edited or deleted, losers stay. Each one is marked "
         f"from the **next session's open** after it was posted, on a standard **${NOTIONAL:,.0f}** notional, against the market "
         "(**IWM** for swing calls, **SPY** for long-term calls) and a "
         "named control stock, and closed only by its own pre-stated rule (an invalidation close or the review date). "
         "These are research calls, not trades or advice.", "",
         "## Scoreboard", "",
         f"- Calls: **{len(rows)}** · marked: {len(live)} · open: {sum(1 for m in live if m['status'] == 'open')} · "
         f"closed: {sum(1 for m in live if m['status'].startswith('closed'))}",
         f"- Total P&L on ${NOTIONAL:,.0f} per call: **${sum(m['pnl_usd'] for m in live):+,.2f}**",
         f"- Average vs the market: **{fmt(mean(xs)) if xs else 'n/a'}** · beat it: {sum(x > 0 for x in xs)}/{len(xs)}"
         + (f" · t-stat {t:.2f} (need about 2 and 20+ calls before it means anything)" if t is not None else ""), "",
         "## Every call", "",
         "| # | posted | call | thesis | entry | now / exit | return | vs market | vs control | days | status |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in marked:
        side = ("LONG" if int(m["direction"]) > 0 else "SHORT") + (" (long-term)" if m.get("horizon") == "long" else "")
        thesis = m["thesis"] if not m.get("dossier") else f"[{m['thesis']}]({'../' + m['dossier']})"
        if "ret_pct" not in m:
            L.append(f"| {m['id']} | {m['posted_utc'][:10]} | {side} {m['ticker']} | {thesis} | | | | | | | {m['status']} |"); continue
        L.append(f"| {m['id']} | {m['posted_utc'][:10]} | {side} **{m['ticker']}** | {thesis} | ${m['entry']:.2f} ({m['entry_date']}) | "
                 f"${m['end_price']:.2f} | {fmt(m['ret_pct'])} | {fmt(m['excess_bench'])} ({m['bench']}) | {fmt(m['excess_control'])} ({m['control']}) | "
                 f"{m['days']} | {m['status']} |")
    L += ["", "## Rules", "",
          "1. A call is posted publicly (X) and added here in the same hour. The git commit time is the timestamp.",
          "2. Entry is the next session's open. No cherry-picking a better fill.",
          "3. Each call states its invalidation close and review date up front. It closes only by those rules.",
          "4. Nothing is ever deleted or edited. A mistake gets a new row that says so.",
          "5. Judge the record after 20+ closed calls, against the market and the controls, not by the best winner.",
          "6. Long-term calls (horizon `long`) are measured against SPY and can also close on a pre-stated thesis break "
          "(for example the theme's segment revenue falling two quarters running), recorded in the exit columns with the reason.", ""]
    (ROOT / "calls/README.md").write_text("\n".join(L), encoding="utf-8")
    if "--announce" in sys.argv:
        announce(rows, marked)
    print(f"calls: {len(rows)} total, {len(live)} marked -> calls/README.md, calls/marks.csv")


if __name__ == "__main__":
    main()
