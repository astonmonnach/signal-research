"""Public calls: the conviction track record. Not trades, so capital doesn't matter.

A call is a stock we commit to publicly and keep, no matter what, until its own pre-stated exit
rule closes it. Calls are append-only: never edit or delete a row; closing a call only fills the
exit columns. Every call is marked from the next session's open after it was posted, on a
standard $1,000 notional, against a benchmark (IWM for swing calls, SPY for long-term calls) and a
named control ticker.

Run:  python calls/build_calls.py            -> calls/README.md (the public record), calls/marks.csv
      python calls/build_calls.py --post ID  -> prints the facts block for an X post (you write the post)
      python calls/build_calls.py --announce -> also posts new and newly closed calls to Discord #calls (once each)
      python calls/build_calls.py --weekly   -> Fridays: calls/weekly/<date>.md and the X thread for the weekly scoreboard

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
    b = split_adjust(t, b)
    _cache[t] = b; time.sleep(0.2)
    return b


def split_adjust(t, b):
    """Yahoo can lag a split by days, which fakes a huge move (ITA's 3-for-1 on 5 Nov 2026 read as -67%).
    Splits in ledger/corporate_actions.csv (kind split, ratio = new shares per old; 0.1 for a 1-for-10
    reverse split) rescale the earlier bars, unless Yahoo has already adjusted them. Any other overnight
    gap of 2.5x either way is flagged so a missing split can't trip an invalidation close unseen."""
    p = ROOT / "ledger/corporate_actions.csv"
    splits = {}
    if p.exists():
        splits = {dt.date.fromisoformat(r["ex_date"]): float(r["ratio"]) for r in csv.DictReader(open(p, encoding="utf-8"))
                  if r["ticker"] == t and r["kind"] == "split"}
    for i in range(1, len(b)):
        d, o = b[i][0], b[i][1]
        gap = b[i - 1][2] / o
        if d in splits and abs(gap / splits[d] - 1) < 0.2:
            k = splits[d]
            b = [(x[0], x[1] / k, x[2] / k, x[3]) for x in b[:i]] + b[i:]
        elif d not in splits and (gap >= 2.5 or gap <= 0.4):
            print(f"WARNING {t} {d}: overnight gap x{gap:.2f}; if it's a split, add it to ledger/corporate_actions.csv", file=sys.stderr)
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


def side_label(c):
    """LONG, or AVOID for a -1 call: a cash account can't short, so a down call means 'don't buy' (rule 2026-10-23)."""
    return ("LONG" if int(c["direction"]) > 0 else "AVOID") + (" (long-term)" if c.get("horizon") == "long" else "")


def post_text(c, link=True):
    side = side_label(c)
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


# On X these cashtags open a crypto token, so the weekly thread writes them without the $.
NOT_CASHTAG = {"NCT"}


def tag(t):
    return t if t in NOT_CASHTAG else "$" + t


def weekly(marked):
    """Friday scoreboard: calls/weekly/<last session>.md plus an X thread (each post under 280 characters)."""
    live = [m for m in marked if "ret_pct" in m]
    asof = max(dt.date.fromisoformat(m["end_date"]) for m in live)
    wk = asof - dt.timedelta(days=7)
    opn = [m for m in live if m["status"] == "open"]
    closed = [m for m in live if m["status"].startswith("closed")]
    xs = [m["excess_bench"] for m in live if m.get("excess_bench") is not None]
    cs = [m["excess_control"] for m in live if m.get("excess_control") is not None]
    stock = lambda m: m["ret_pct"] * int(m["direction"])  # the stock's own move since entry

    def line(m):
        state = "open" if m["status"] == "open" else "closed"
        return (f"#{m['id']} {side_label(m).split()[0]} {tag(m['ticker'])}: stock {fmt(stock(m))}, "
                f"{fmt(m['excess_bench'], ' pts')} vs {tag(m['bench'])}, {state}")

    def to_line(m):
        """How far the price must move to hit the invalidation close (positive = room left)."""
        inv, p = float(m["invalidation_close"]), m["end_price"]
        return (inv / p - 1) * 100 if int(m["direction"]) < 0 else (1 - inv / p) * 100

    new = [m for m in live if dt.date.fromisoformat(m["entry_date"]) > wk]
    shut = [m for m in closed if dt.date.fromisoformat(m["end_date"]) > wk]
    near = sorted((m for m in opn if m.get("invalidation_close")), key=to_line)[:3]
    due = [m for m in opn if m.get("review_date") and asof < dt.date.fromisoformat(m["review_date"]) <= asof + dt.timedelta(days=7)]
    young = sum(1 for m in live if m["days"] < 28)
    day = f"{asof.day} {asof:%b}"

    head = (f"Weekly scoreboard, w/e {day}: {len(live)} public calls, {len(opn)} open, {len(closed)} closed "
            f"({sum(m['ret_pct'] > 0 for m in closed)} right, {sum(m['ret_pct'] <= 0 for m in closed)} wrong). "
            f"Average vs {tag('IWM')} {fmt(mean(xs), ' pts')}, beat it {sum(x > 0 for x in xs)}/{len(xs)}. "
            f"Vs each call's control {fmt(mean(cs), ' pts')}. {young} of {len(live)} are under 4 weeks old. Losers stay up.")
    thread, cur = [head], ""
    for s in [line(m) for m in live]:
        if len(cur) + len(s) + 1 > 270:
            thread.append(cur); cur = ""
        cur = (cur + "\n" + s).strip()
    thread.append(cur)
    week = []
    if shut: week.append("Closed this week: " + "; ".join(f"{tag(m['ticker'])}, call {fmt(m['ret_pct'])} ({m['status'][8:]})" for m in shut) + ".")
    if new: week.append("New this week: " + ", ".join(f"#{m['id']} {tag(m['ticker'])}" for m in new) + ".")
    if near: week.append("Closest to the exit line: " + ", ".join(f"{tag(m['ticker'])} {to_line(m):.0f}% away" for m in near) + ".")
    cur = ""
    for s in week:
        if len(cur) + len(s) + 1 > 280:
            thread.append(cur); cur = ""
        cur = (cur + " " + s).strip()
    if cur: thread.append(cur)
    thread.append("AVOID names usually fall, so the real test is each call vs its control. "
                  "Every call, losers included: github.com/astonmonnach/signal-research/tree/main/calls")
    assert all(len(t) <= 280 for t in thread), [len(t) for t in thread]

    L = [f"# Weekly scoreboard: week ending {asof:%a %d %b %Y}", "",
         f"- Calls: **{len(live)}** · open {len(opn)} · closed {len(closed)} "
         f"({sum(m['ret_pct'] > 0 for m in closed)} right, {sum(m['ret_pct'] <= 0 for m in closed)} wrong)",
         f"- Average vs the market: **{fmt(mean(xs), ' pts')}** · beat it {sum(x > 0 for x in xs)}/{len(xs)}",
         f"- Average vs each call's control: **{fmt(mean(cs), ' pts')}** · beat it {sum(x > 0 for x in cs)}/{len(cs)}",
         f"- {young} of {len(live)} calls are under 4 weeks old; judge the record after 20+ closed calls (rule 5).", "",
         "## This week", ""] + [f"- {w}" for w in week[:-1]] + \
        ([f"- Review dates in the next 7 days: " + ", ".join(f"{m['ticker']} {m['review_date']}" for m in due)] if due else []) + \
        ["", "## Every call", "", "| # | call | entry | now / exit | stock | vs market | vs control | to exit line | status |",
         "|---|---|---|---|---|---|---|---|---|"]
    for m in live:
        dist = f"{to_line(m):.0f}%" if m["status"] == "open" and m.get("invalidation_close") else ""
        L.append(f"| {m['id']} | {side_label(m)} {m['ticker']} | ${m['entry']:.2f} ({m['entry_date']}) | ${m['end_price']:.2f} | "
                 f"{fmt(stock(m))} | {fmt(m['excess_bench'], ' pts')} | {fmt(m['excess_control'], ' pts')} ({m['control']}) | {dist} | {m['status']} |")
    L += ["", "## X thread", ""] + [f"```\n{t}\n```" for t in thread] + [""]
    out = ROOT / f"calls/weekly/{asof}.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print("\n\n".join(thread))
    print(f"\nweekly -> {out.relative_to(ROOT)}")


def main():
    rows = list(csv.DictReader(open(CALLS, encoding="utf-8"))) if CALLS.exists() else []
    if "--post" in sys.argv:
        cid = sys.argv[sys.argv.index("--post") + 1]
        # rule 2026-11-01: the post is written only from claims whose quotes check out in the filings
        import check_evidence as ev
        evid = ev.load(int(cid))
        if evid is None and int(cid) >= ev.FIRST_ID:
            sys.exit(f"call {cid}: no calls/evidence/{cid}.csv; write it and run python calls/check_evidence.py {cid}")
        bad = ev.problems(int(cid), evid) if evid else []
        if bad:
            sys.exit("\n".join(["evidence problems, fix before posting:"] + bad))
        print(post_text(next(r for r in rows if r["id"] == cid)))
        if evid:
            print("\nVerified claims (write the post from these only):")
            for c in dict.fromkeys(r["claim"] for r in evid):
                fixes = [r["note"] for r in evid if r["claim"] == c and r.get("note", "").startswith("CORRECTION")]
                print("-", c + (f"  [{'; '.join(fixes)}]" if fixes else ""))
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
        side = side_label(m)
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
    if "--weekly" in sys.argv:
        weekly(marked)


if __name__ == "__main__":
    main()
