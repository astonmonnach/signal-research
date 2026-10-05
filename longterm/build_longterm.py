"""Long-term section: track every long-term candidate against SPY and its sector, and post to Discord #long-term.

Run:  python longterm/build_longterm.py                -> longterm/README.md (tracking table)
      python longterm/build_longterm.py --post-weekly  -> also: announce new candidates once, and on Mondays post the
                                                          weekly summary once (longterm/state.json remembers both)
      add --force to post the weekly summary on another day or again

Inputs: longterm/candidates.csv (ticker,theme,role,thesis,evidence_url,score,verdict,benchmark,sector_etf,review_trigger),
written from nth-order research (research/longterm-*/). The date a ticker first appears is kept in state.json as
"added", and every move here is measured from that day's close. Prices: Yahoo daily closes.
"""
import csv, json, sys, time, urllib.request, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAND = ROOT / "longterm/candidates.csv"
STATE = ROOT / "longterm/state.json"
REPO_URL = "https://github.com/astonmonnach/signal-research/blob/main"
TODAY = dt.date.today()
_cache = {}


def closes(t):
    if t in _cache: return _cache[t]
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=2y&interval=1d"
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))["chart"]["result"][0]
        out = [(dt.datetime.fromtimestamp(ts, dt.UTC).date(), c) for ts, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if c]
    except Exception:
        out = []
    _cache[t] = out; time.sleep(0.2)
    return out


def corporate_actions():
    p = ROOT / "ledger/corporate_actions.csv"
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


def move(t, start):
    """% change for a holder from the close on/before `start` to the latest close. Cash and spun-off shares
    received in between are added back (ledger/corporate_actions.csv), so spin-offs don't fake a drop."""
    c = closes(t)
    base = [x for x in c if x[0] <= start]
    if not c or not base: return None
    d0, d1, val = base[-1][0], c[-1][0], c[-1][1]
    for ca in corporate_actions():
        ex = dt.date.fromisoformat(ca["ex_date"])
        if ca["ticker"] == t and d0 < ex <= d1:
            if ca["receive_ticker"] == "CASH":
                val += float(ca["ratio"])
            elif closes(ca["receive_ticker"]):
                val += float(ca["ratio"]) * closes(ca["receive_ticker"])[-1][1]
    return (val / base[-1][1] - 1) * 100


def f(v):
    return "" if v is None else f"{v:+.1f}%"


def rows():
    return list(csv.DictReader(open(CAND, encoding="utf-8"))) if CAND.exists() else []


def build(R, state):
    L = ["# Long-term research (6–36 months)", "",
         f"Candidates from nth-order research ([how it works](METHOD.md)). Moves are measured from the close on the day each name was "
         "added, against SPY and its sector ETF. This is a research log, not advice. A name only becomes a call (in the "
         "[calls record](../calls/README.md)) when it's committed publicly.", ""]
    if not R:
        return L + ["_No candidates yet: the first long-term nth-order research is in progress._", ""], []
    L += ["| ticker | theme | verdict | score | added | since added | vs SPY | vs sector | 1y vs SPY | review trigger |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    out = []
    for r in sorted(R, key=lambda r: -float(r.get("score") or 0)):
        t = r["ticker"].strip().upper()
        added = dt.date.fromisoformat(state["added"][t])
        bench, sect = (r.get("benchmark") or "SPY").strip(), (r.get("sector_etf") or "").strip()
        m, mb = move(t, added), move(bench, added)
        ms = move(sect, added) if sect else None
        y, yb = move(t, TODAY - dt.timedelta(days=365)), move(bench, TODAY - dt.timedelta(days=365))
        vs = None if m is None or mb is None else m - mb
        vsec = None if m is None or ms is None else m - ms
        y_vs = None if y is None or yb is None else y - yb
        dossier = ROOT / f"stocks/{t}.md"
        name = f"[{t}](../stocks/{t}.md)" if dossier.exists() else t
        L.append(f"| {name} | {r.get('theme', '')} | {r.get('verdict', '')} | {r.get('score', '')} | {added} | {f(m)} | {f(vs)} | "
                 f"{f(vsec)}{f' ({sect})' if sect and vsec is not None else ''} | {f(y_vs)} | {r.get('review_trigger', '')} |")
        out.append(dict(r, ticker=t, since=m, vs=vs))
    L += ["", "**Theses** (one line each; evidence links go to the primary source):", ""]
    for r in R:
        ev = f" ([evidence]({r['evidence_url']}))" if r.get("evidence_url") else ""
        L.append(f"- **{r['ticker'].strip().upper()}** ({r.get('role', '')}): {r.get('thesis', '')}{ev}")
    return L + [""], out


def main():
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    state.setdefault("added", {}); state.setdefault("announced", []); state.setdefault("weekly_posted", [])
    R = rows()
    for r in R:
        state["added"].setdefault(r["ticker"].strip().upper(), TODAY.isoformat())
    L, out = build(R, state)
    (ROOT / "longterm/README.md").write_text("\n".join(L), encoding="utf-8")
    if "--post-weekly" in sys.argv:
        sys.path.insert(0, str(ROOT / "briefing"))
        import notify
        if not notify.has_own_channel("longterm"):
            print("long-term: no #long-term webhook, nothing sent")
        else:
            for r in R:
                t = r["ticker"].strip().upper()
                if t not in state["announced"]:
                    msg = (f"**NEW LONG-TERM RESEARCH: {t}** · {r.get('verdict', '')} ({r.get('score', '')}/10) · {r.get('theme', '')}\n"
                           f"{r.get('thesis', '')}\nReview trigger: {r.get('review_trigger', '')} · <{REPO_URL}/longterm/README.md>")
                    if notify.send(msg, "longterm"): state["announced"].append(t)
            wk = f"{TODAY.isocalendar()[0]}-W{TODAY.isocalendar()[1]:02d}"
            if out and (TODAY.weekday() == 0 or "--force" in sys.argv) and (wk not in state["weekly_posted"] or "--force" in sys.argv):
                lines = [f"**LONG-TERM WEEKLY** · {TODAY:%d %b %Y} (since added, against SPY)"]
                lines += [f"- {r['ticker']} {f(r['since'])} ({f(r['vs'])} vs SPY) · {r.get('verdict', '')} · next: {r.get('review_trigger', '')}" for r in out]
                lines.append(f"Full table: <{REPO_URL}/longterm/README.md>")
                if notify.send("\n".join(lines), "longterm"): state["weekly_posted"].append(wk)
    STATE.write_text(json.dumps(state, indent=1), encoding="utf-8")
    print(f"long-term: {len(R)} candidates -> longterm/README.md")


if __name__ == "__main__":
    main()
