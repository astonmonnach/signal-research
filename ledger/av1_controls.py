"""AV1 (ledger/PREREG_AV1.md): do our AVOIDs fall more than matched stocks we did not flag?

Run:  python ledger/av1_controls.py   -> ledger/AV1_PROGRESS.md (description only until 30 primary rows are judged)

Implementation notes (not changes to the rules):
- Market values come from the Nasdaq screener cache on the run date, scaled back to the entry date by the price ratio.
- A control needs prices over the AVOID's whole window; candidates without them are skipped and the next seeded one is used.
"""
import csv
import json
import random
import time
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "ledger" / "cache_av1"
PRIMARY = {"ongoing_supply", "warrant_supply", "distress", "holder_selling", "deal_dilution"}
JUDGE_DAYS = 20


def bars(t):
    """[(date, open, close)] for the past year, cached per run day."""
    CACHE.mkdir(exist_ok=True)
    p = CACHE / f"{t}_{date.today()}.json"
    if p.exists():
        return [(date.fromisoformat(d), o, c) for d, o, c in json.loads(p.read_text())]
    out = []
    try:
        u = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=1y&interval=1d"
        r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))
        r = r["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
        out = [(datetime.fromtimestamp(ts, timezone.utc).date(), o, c)
               for ts, o, c in zip(r["timestamp"], q["open"], q["close"]) if o and c]
        time.sleep(0.2)
    except Exception:
        pass
    p.write_text(json.dumps([(d.isoformat(), o, c) for d, o, c in out]))
    return out


def bucket(px):
    return 0 if px < 1 else 1 if px < 5 else 2 if px < 20 else 3


def window(b, start, stop=None):
    """Entry = first session after `start`; end = the 20th session, or the last close before `stop` if earlier."""
    after = [x for x in b if x[0] > start]
    if not after:
        return None
    seg = after[:JUDGE_DAYS]
    if stop:
        seg = [x for x in seg if x[0] < stop] or seg[:1]
    return seg[0], seg[-1], len(seg) >= JUDGE_DAYS or bool(stop and len(seg) < JUDGE_DAYS)


def eligible(sym):
    if not sym.isalpha() or not sym.isupper() or len(sym) > 5:
        return False
    return not (len(sym) == 5 and sym[-1] in "WUR")


def main():
    reg = list(csv.DictReader(open(ROOT / "ledger" / "avoid_register.csv", encoding="utf-8")))
    caps = json.load(open(ROOT / "watch" / "marketcap.json", encoding="utf-8"))["caps"]
    skip = {r["ticker"] for r in reg} | set(json.load(open(ROOT / "watch" / "watchlist.json", encoding="utf-8"))["tickers"])
    universe = sorted(s for s, c in caps.items() if c and eligible(s) and s not in skip)
    rows = []
    for r in reg:
        t, d0 = r["ticker"], date.fromisoformat(r["date"])
        stop = date.fromisoformat(r["status_date"]) if r.get("status") == "reversed" and r.get("status_date") else None
        b = bars(t)
        w = window(b, d0, stop)
        if not w or not b:
            rows.append(dict(r, note="no prices")); continue
        (ed, eo, _), (xd, _, xc), judged = w
        ret = (xc / eo - 1) * 100
        cap_now = caps.get(t) or 0
        cap_entry = cap_now * eo / b[-1][2] if cap_now else 0
        cands = [s for s in universe if cap_entry and 0.5 * cap_entry <= caps[s] * 1.0 <= 2 * cap_entry] if cap_entry else []
        random.Random(f"{t}{r['date']}").shuffle(cands)
        ctl = []
        for s in cands[:60]:
            cb = bars(s)
            seg = [x for x in cb if ed <= x[0] <= xd]
            if not seg or seg[0][0] != ed or seg[-1][0] != xd or bucket(seg[0][1]) != bucket(eo):
                continue
            ctl.append((seg[-1][2] / seg[0][1] - 1) * 100)
            if len(ctl) == 10:
                break
        excess = ret - median(ctl) if ctl else None
        rows.append(dict(r, entry=ed.isoformat(), end=xd.isoformat(), ret=ret, ctl_n=len(ctl),
                         ctl_median=median(ctl) if ctl else None, excess=excess, judged=judged))
    write(rows)


def write(rows):
    ok = [r for r in rows if r.get("excess") is not None]
    L = ["# AV1 progress: our AVOIDs against matched unflagged stocks", "",
         f"Run {date.today()}. Rules frozen in [PREREG_AV1.md](PREREG_AV1.md). **Description only**: the test reads once 30 "
         "primary rows are judged at 20 trading days, or on 31 Dec 2026.", "",
         "Excess = the AVOID's return minus the median of up to 10 matched controls (same price bucket, half to twice the "
         "market value), over the same window. Negative = the AVOID fell more than similar stocks.", "",
         "| group | rows with controls | judged (20 days or reversed) | mean excess, all | mean excess, judged | AVOID behind its controls |",
         "|---|---|---|---|---|---|"]
    groups = [("Primary: supply and distress", lambda r: r["supply_type"] in PRIMARY),
              ("One-off offerings", lambda r: r["supply_type"] == "one_off_offering"),
              ("Killed long theses", lambda r: r["supply_type"] == "kill"),
              ("Other", lambda r: r["supply_type"] not in PRIMARY | {"one_off_offering", "kill"})]
    for name, f in groups:
        g = [r for r in ok if f(r)]
        if not g:
            L.append(f"| {name} | 0 | 0 | | | |")
            continue
        j = [r for r in g if r["judged"]]
        judged_mean = f"{mean(r['excess'] for r in j):+.1f} pts" if j else "n/a"
        L.append(f"| {name} | {len(g)} | {len(j)} | {mean(r['excess'] for r in g):+.1f} pts | {judged_mean} | "
                 f"{sum(r['excess'] < 0 for r in g)}/{len(g)} |")
    L += ["", "## Every AVOID", "", "| date | ticker | type | status | entry | end | AVOID | controls (median, n) | excess |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["date"], r["ticker"])):
        if r.get("excess") is None:
            L.append(f"| {r['date']} | {r['ticker']} | {r['supply_type']} | {r.get('status','')} | | | | {r.get('note','no controls')} | |")
            continue
        L.append(f"| {r['date']} | {r['ticker']} | {r['supply_type']} | {r.get('status','')} | {r['entry']} | {r['end']}"
                 f"{'' if r['judged'] else ' (open)'} | {r['ret']:+.1f}% | {r['ctl_median']:+.1f}% ({r['ctl_n']}) | {r['excess']:+.1f} |")
    (ROOT / "ledger" / "AV1_PROGRESS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:14]))


if __name__ == "__main__":
    main()
