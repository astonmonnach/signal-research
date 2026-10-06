"""Options as information: before every dated event, record the move the options market expects; after expiry,
record the move that actually happened. -> ledger/implied_moves.csv and ledger/IMPLIED_MOVES.md

Paper only. It tests one question before any money goes into options: does nth know better than the options market
how big a move will be? Judge it after 20-30 settled events.

For each stock we follow (and any stock named in a calendar event) with an event in the next 60 days:
  - expiry = the first monthly or weekly expiry on or after the event date;
  - expected move = the at-the-money straddle (call + put at the mid price), interpolated to the spot price, as a % of spot;
  - also the nearest-strike straddle's cost, so the result can say what buying it would have made or lost;
  - spread = the average bid/ask gap of those two options, as a % of their mid price (over ~20% = too thin to trade).
After expiry: actual move = |close on expiry / spot when logged - 1|, the straddle's result, and bigger/smaller than expected.
`nth_view` (bigger / smaller / none) is filled in by the research run when it has a view, BEFORE the event.

Data: CBOE delayed quotes (free, ~15 minutes delayed) and Yahoo closes. Usage: python collectors/implied_moves.py
"""
import csv, json, re, sys, time, urllib.request, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "briefing")); sys.path.insert(0, str(ROOT / "reports"))
from sources import calendar_events  # noqa: E402

OUT = ROOT / "ledger/implied_moves.csv"
MD = ROOT / "ledger/IMPLIED_MOVES.md"
COLS = ["logged", "ticker", "event_date", "event", "expiry", "spot", "implied_move_pct", "strike", "straddle_cost", "leg_spread_pct",
        "open_interest", "nth_view", "status", "expiry_close", "actual_move_pct", "straddle_result_pct", "outcome"]
SKIP = re.compile(r"re-check|13f|day-10|day ~?28|observation|check \(|first scan", re.I)
TODAY = dt.date.today()


def chain(t):
    u = f"https://cdn.cboe.com/api/global/delayed_quotes/options/{t}.json"
    d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30))["data"]
    rows = {}
    for o in d["options"]:
        m = re.match(rf"{re.escape(t)}(\d{{6}})([CP])(\d{{8}})$", o["option"])
        if not m: continue
        exp = dt.datetime.strptime(m.group(1), "%y%m%d").date()
        rows.setdefault(exp, {}).setdefault(int(m.group(3)) / 1000, {})[m.group(2)] = o
    return d.get("current_price"), rows


def mid(o):
    return (o["bid"] + o["ask"]) / 2 if o and o.get("bid") and o.get("ask") and o["ask"] >= o["bid"] > 0 else None


def straddle(strikes, k):
    c, p = strikes.get(k, {}).get("C"), strikes.get(k, {}).get("P")
    mc, mp = mid(c), mid(p)
    if mc is None or mp is None: return None
    spread = ((c["ask"] - c["bid"]) / mc + (p["ask"] - p["bid"]) / mp) / 2 * 100
    return mc + mp, spread, (c.get("open_interest") or 0) + (p.get("open_interest") or 0)


def measure(t, event_date):
    spot, rows = chain(t)
    exps = sorted(e for e in rows if e >= event_date)
    if not spot or not exps: return None
    exp = exps[0]
    ks = sorted(k for k in rows[exp] if straddle(rows[exp], k))
    if not ks: return None
    lo = max([k for k in ks if k <= spot], default=ks[0]); hi = min([k for k in ks if k >= spot], default=ks[-1])
    s_lo, s_hi = straddle(rows[exp], lo), straddle(rows[exp], hi)
    implied = s_lo[0] if lo == hi else s_lo[0] + (s_hi[0] - s_lo[0]) * (spot - lo) / (hi - lo)
    near = min(ks, key=lambda k: abs(k - spot)); s_near = straddle(rows[exp], near)
    return dict(expiry=exp.isoformat(), spot=round(spot, 2), implied_move_pct=round(implied / spot * 100, 1), strike=near,
                straddle_cost=round(s_near[0], 2), leg_spread_pct=round(s_near[1], 1), open_interest=int(s_near[2]))


def close_on(t, d):
    try:
        u = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=6mo&interval=1d"
        r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))["chart"]["result"][0]
        bars = [(dt.datetime.fromtimestamp(ts, dt.UTC).date(), c) for ts, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if c]
        on = [c for day, c in bars if day <= d]
        return on[-1] if on else None
    except Exception:
        return None


def followed():
    t = list(json.load(open(ROOT / "watch/watchlist.json", encoding="utf-8"))["tickers"])
    sp = ROOT / "watch/strategies.json"
    for s in (json.load(open(sp, encoding="utf-8"))["strategies"] if sp.exists() else []):
        t += s["tickers"]
    return set(t)


def main():
    rows = list(csv.DictReader(open(OUT, encoding="utf-8"))) if OUT.exists() else []
    have = {(r["ticker"], r["event_date"], r["event"]) for r in rows}
    fol = followed()
    for e in calendar_events():
        if not (TODAY <= e["date"] <= TODAY + dt.timedelta(days=60)) or SKIP.search(e["summary"]): continue
        for t in sorted(set(re.findall(r"\b([A-Z]{2,5})\b", e["summary"])) & (fol | {"HZO", "UTZ", "INM", "SSTI", "GETY"})):
            key = (t, e["date"].isoformat(), e["summary"][:120])
            if key in have: continue
            try:
                m = measure(t, e["date"]); time.sleep(0.3)
            except Exception as ex:
                print(f"{t}: no options data ({str(ex)[:60]})"); continue
            if not m: print(f"{t}: no usable options for {e['date']}"); continue
            rows.append(dict(logged=TODAY.isoformat(), ticker=t, event_date=key[1], event=key[2], nth_view="", status="open", **m))
            have.add(key)
            print(f"logged {t} {key[1]}: expected move {m['implied_move_pct']}% by {m['expiry']} (spread {m['leg_spread_pct']}%)")
    for r in rows:                                              # settle anything whose expiry has passed
        if r["status"] == "open" and dt.date.fromisoformat(r["expiry"]) < TODAY:
            c = close_on(r["ticker"], dt.date.fromisoformat(r["expiry"]))
            if c:
                spot, k, cost = float(r["spot"]), float(r["strike"]), float(r["straddle_cost"])
                actual = abs(c / spot - 1) * 100
                r.update(status="settled", expiry_close=round(c, 2), actual_move_pct=round(actual, 1),
                         straddle_result_pct=round((abs(c - k) - cost) / cost * 100, 1),
                         outcome="bigger" if actual > float(r["implied_move_pct"]) else "smaller")
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    st = [r for r in rows if r["status"] == "settled"]
    L = ["# Options: expected move vs actual move", "",
         "Paper only. Before each dated event we record the move the options market expects (the at-the-money straddle). After expiry "
         "we record the move that happened, and what buying that straddle would have made. The question: does nth know better than the "
         "options market how big a move will be? Judge after 20-30 settled events. Built by `collectors/implied_moves.py` from CBOE delayed quotes.", "",
         f"**Settled:** {len(st)}" + (f" · actual move bigger than expected in {sum(r['outcome'] == 'bigger' for r in st)}/{len(st)} · average straddle "
         f"result {sum(float(r['straddle_result_pct']) for r in st) / len(st):+.1f}%" if st else " (none yet)"), "",
         "| logged | ticker | event | event date | expiry | spot | expected move | straddle cost | spread | nth view | actual | straddle result |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: r["event_date"]):
        L.append(f"| {r['logged']} | {r['ticker']} | {r['event'][:60]} | {r['event_date']} | {r['expiry']} | ${float(r['spot']):.2f} | ±{r['implied_move_pct']}% | "
                 f"${float(r['straddle_cost']):.2f} @ {r['strike']} | {r['leg_spread_pct']}% | {r['nth_view'] or '-'} | "
                 f"{(r['actual_move_pct'] + '%') if r.get('actual_move_pct') else 'open'} | {(r['straddle_result_pct'] + '%') if r.get('straddle_result_pct') else ''} |")
    MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"implied moves: {len(rows)} logged, {len(st)} settled -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
