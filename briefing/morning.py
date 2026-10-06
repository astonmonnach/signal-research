"""Morning briefing: everything the pipeline found, in one message.

Run:  python briefing/morning.py            (writes briefings/YYYY-MM-DD.md, sends if secrets set)
      python briefing/morning.py --dry-run  (prints, sends nothing)

Reads only files other jobs wrote (it never fetches anything except via notify.py):
  watch/positions.md, watch/nq_regime.md        collectors/positions.py, nq_regime.py
  data/signals.csv                               S1 DoD contracts (evening job)
  watch/digests/*-triage.md                      evening triage of SEC filings
  watch/press/latest.json                        collectors/press_wires.py
  watch/context/latest.json                      collectors/market_context.py
  ledger/ledger.csv                              ledger/build_ledger.py
  data/crypto/trending_*.csv                     C1 (GitHub Actions)
  calendar/catalyst-dates.ics                    dated events
"""
import csv, json, os, re, sys, datetime as dt
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
import notify  # noqa: E402
from claim import claim  # noqa: E402

REPO_URL = "https://github.com/astonmonnach/signal-research/blob/main"
NOW = dt.datetime.now(dt.UTC)
TODAY = NOW.date()


def read(p):
    p = ROOT / p
    return p.read_text(encoding="utf-8") if p.exists() else ""


def section(md, title):
    """Body of a '## title' section of a markdown file."""
    m = re.search(rf"^## {re.escape(title)}.*?$\n(.*?)(?=^## |\Z)", md, re.S | re.M)
    return m.group(1).strip() if m else ""


def positions():
    md = read("watch/positions.md")
    out = []
    for block in re.split(r"^## ", md, flags=re.M)[1:]:
        head, *lines = block.strip().splitlines()
        keep = [l.strip("- ").strip() for l in lines if l.startswith("- ") and not l.startswith("- Thesis")]
        out.append(f"**{head.split()[0]}**: " + " · ".join(keep[:3]))
    return out


def nq():
    md = read("watch/nq_regime.md")
    m = re.search(r"\*\*Next session: (.*?)\*\*(.*?)\n", md)
    return f"NQ next session: **{m.group(1).strip('.')}**. {m.group(2).strip()}" if m else ""


def new_signals(days=3):
    p = ROOT / "data/signals.csv"
    if not p.exists(): return []
    out = []
    for r in csv.DictReader(open(p, encoding="utf-8")):
        try:
            t = dt.datetime.fromisoformat(r["detected_at_utc"].replace("Z", "+00:00"))
        except ValueError:
            continue
        if NOW - t <= dt.timedelta(days=days):
            mat = float(r["materiality"] or 0) * 100
            out.append(f"**{r['ticker']}** ${float(r['value_usd'] or 0)/1e6:,.0f}M = {mat:.0f}% of mcap · {r['decision']} · "
                       f"{r['event_summary'][:110]}…")
    return out


def latest_triage():
    files = sorted((ROOT / "watch/digests").glob("*-triage.md"))
    if not files: return None, []
    f = files[-1]
    body = section(f.read_text(encoding="utf-8"), "Filings worth reading")
    bullets = [b.strip() for b in re.split(r"\n(?=- )", body) if b.strip().startswith("- ")]
    return f.name[:10], bullets


def press(limit=15):
    """All wire hits found since the last briefing (24h; 72h on Mondays), from the daily CSVs."""
    files = sorted((ROOT / "data/press").glob("*.csv"))
    if not files: return None
    window = dt.timedelta(hours=72 if TODAY.weekday() == 0 else 24)
    items, seen = [], set()
    for f in files[-4:]:
        for r in csv.DictReader(open(f, encoding="utf-8", newline="")):
            try:
                t = dt.datetime.fromisoformat(r["published_utc"].replace("Z", "+00:00"))
            except ValueError:
                continue
            if NOW - t <= window and r["link"] not in seen:
                seen.add(r["link"]); items.append(r)
    strong = ("position", "watchlist", "signal", "manual_call")
    items.sort(key=lambda r: (not r["matched_on"].startswith(strong), r["published_utc"]))
    return [f"**{r['ticker'] or '?'}** {r['title'][:120]} ({r['wire']}) <{r['link']}> [{r['matched_on'].split(';')[0]}]"
            for r in items[:limit]], len(items)


def context():
    p = ROOT / "watch/context/latest.json"
    if not p.exists(): return None
    d = json.loads(p.read_text(encoding="utf-8"))
    com = [c for c in d.get("commodities", []) if c.get("unusual")]
    lines = [f"{c['name']} ({c['symbol']}) {c['chg_1d']:+.1f}% 1d, {c['chg_5d']:+.1f}% 5d (z {c['z_1d']:+.1f})" for c in com]
    ca = {}
    cap = ROOT / "ledger/corporate_actions.csv"
    if cap.exists():
        for a in csv.DictReader(open(cap, encoding="utf-8")):
            ex = dt.date.fromisoformat(a["ex_date"])
            if TODAY - dt.timedelta(days=10) <= ex <= TODAY:
                ca[a["ticker"]] = f"{a['kind'].replace('_', ' ')} on {ex:%d %b}"
    for t, v in d.get("tickers", {}).items():
        if t in ca:
            lines.append(f"**{t}**: move distorted by {ca[t]}, ignore the raw %")
            continue
        if v.get("sympathy_flag"):
            lines.append(f"**{t}**: {v['sympathy_flag']} (self 5d {v.get('self_5d', 0):+.1f}% vs peer median {v.get('peer_median_5d', 0):+.1f}%)")
    return lines


def ledger(top=4):
    """Honest scoreboard: only what we could actually have taken (long, liquid, $1+, net of 1% costs);
    short bets are paper-only, shown as a don't-buy list. Rule 2026-10-05, ledger/RULES.md."""
    p = ROOT / "ledger/ledger.csv"
    if not p.exists(): return []
    live = [r for r in csv.DictReader(open(p, encoding="utf-8")) if r["status"] == "live" and r["excess_pct"]]
    if not live: return []
    tk = [r for r in live if r.get("takeable") == "yes" and r.get("net_excess_pct")]
    judged = [r for r in tk if int(r.get("tdays") or 0) >= 20]
    xs = [float(r["net_excess_pct"]) for r in tk]
    sh = [float(r["excess_pct"]) for r in live if int(r["direction"]) < 0]
    out = []
    if xs:
        out.append(f"Takeable (long, liquid, $1+, after 1% costs): {len(tk)} live, {len(judged)} held the 20 trading days needed to judge · "
                   f"beat IWM {sum(x > 0 for x in xs)}/{len(xs)} · median {median(xs):+.1f}% · mean {mean(xs):+.1f}%. Early read, not a result.")
        tk = [r for r in tk if int(r.get("tdays") or 0) >= 1]        # a 0-day "result" is just the first open
        tk.sort(key=lambda r: float(r["net_excess_pct"]), reverse=True)
        f = lambda r: f"{r['ticker']} {float(r['net_excess_pct']):+.1f}% ({r['category']}, {r.get('tdays') or r['days']} trading days)"
        out += ["Best takeable: " + ", ".join(f(r) for r in tk[:top]), "Worst takeable: " + ", ".join(f(r) for r in tk[-top:][::-1])]
    if sh:
        out.append(f"Paper only, short bets we can't take: {sum(x > 0 for x in sh)}/{len(sh)} lagged IWM. Useful as a don't-buy list, never counted as wins.")
    return out


def calls():
    """Public calls (calls/marks.csv, built by calls/build_calls.py): one line per call."""
    p = ROOT / "calls/marks.csv"
    if not p.exists(): return []
    out = []
    for r in csv.DictReader(open(p, encoding="utf-8")):
        side = "LONG" if int(r["direction"]) > 0 else "SHORT"
        if not r["ret_pct"]:
            out.append(f"#{r['id']} {side} {r['ticker']}: {r['status']}"); continue
        vs = f", {float(r['excess_bench']):+.1f}% vs {r['bench']}" if r["excess_bench"] else ""
        side += " (long-term)" if r.get("horizon") == "long" else ""
        out.append(f"#{r['id']} {side} {r['ticker']} {float(r['ret_pct']):+.1f}%{vs} since ${float(r['entry']):.2f} ({r['entry_date']}), {r['status']}")
    return out


def crypto():
    s, o = ROOT / "data/crypto/trending_signals.csv", ROOT / "data/crypto/trending_outcomes.csv"
    if not s.exists(): return ""
    sig = list(csv.DictReader(open(s, encoding="utf-8")))
    outs = list(csv.DictReader(open(o, encoding="utf-8"))) if o.exists() else []
    r24 = [r for r in outs if r.get("horizon") == "24h" and r.get("ret_net_pct") and r.get("late") == "False"]
    if not r24: return f"C1 trending: {len(sig)} signals logged"
    xs = sorted(float(r["ret_net_pct"]) for r in r24); med = xs[len(xs) // 2]
    rug = sum(r.get("rugged") == "True" for r in r24)
    return (f"C1 trending Solana pools: {len(sig)} logged · after 24h: median {med:+.0f}%, "
            f"{sum(x > 0 for x in xs)}/{len(xs)} up, {rug} rugged ({rug/len(xs)*100:.0f}%) · forward test, no trades")


def calendar(days=14):
    ics = read("calendar/catalyst-dates.ics")
    out = []
    for ev in ics.split("BEGIN:VEVENT")[1:]:
        s = re.search(r"SUMMARY:(.*)", ev); d = re.search(r"DTSTART[^:]*:(\d{8})", ev)
        if s and d:
            day = dt.datetime.strptime(d.group(1), "%Y%m%d").date()
            if TODAY <= day <= TODAY + dt.timedelta(days=days):
                out.append((day, re.sub(r"^[^\w$£(]+", "", s.group(1).strip())))
    return [f"{d:%a %d %b}: {t}" for d, t in sorted(out)]


def setups():
    """Watch-only setups (e.g. KNRX-like: registered supply + listing deficiency). Flags big moves."""
    p = ROOT / "ledger/ledger.csv"
    if not p.exists(): return []
    rows = [r for r in csv.DictReader(open(p, encoding="utf-8")) if r["category"].startswith("setup_")]
    out = []
    for r in sorted(rows, key=lambda r: -abs(float(r["since_found_pct"] or 0))):
        move = float(r["since_found_pct"]) if r["since_found_pct"] else None
        flag = " SPIKE" if move is not None and move >= 50 else (" (big move)" if move is not None and abs(move) >= 20 else "")
        now = f"${float(r['now']):.2f}" if r["now"] else "?"
        out.append(f"**{r['ticker']}** {now} ({'n/a' if move is None else f'{move:+.0f}%'} since logged {r['found']}){flag}: {r['note'][:80]}")
    return out


def build():
    """Returns (full briefing text, {channel: section text})."""
    S = {}
    head = [f"# Morning briefing · {TODAY:%a %d %b %Y}", ""]
    w = []
    pos = positions()
    if pos: w += ["## Positions"] + [f"- {p}" for p in pos] + [""]
    n = nq()
    if n: w += [n, ""]
    ctx = context()
    if ctx is not None: w += ["## Commodities & sympathy moves"] + ([f"- {c}" for c in ctx] or ["- nothing unusual"]) + [""]
    pots = ROOT / "watch/pots/latest.json"
    if pots.exists():
        w += ["## Funding pots (capped funds behind our contracts)"] + [
            f"- {s['name']}: ${s['ordered_usd'] / 1e9:.2f}bn ordered = {s['committed_pct']:.0f}% of ${s['money_usd'] / 1e9:.1f}bn; "
            f"ceilings {s['ceiling_multiple']:.1f}x the money ({', '.join(s['tickers'])})"
            for o, s in json.load(open(pots, encoding="utf-8")).items()] + [""]
    S["watchlist"] = w
    sig = new_signals()
    f = ["## New contract signals (S1, last 3 days)"] + ([f"- {x}" for x in sig] or ["- none"]) + [""]
    day, tri = latest_triage()
    if day: f += [f"## Filings worth reading (triage {day})"] + ([f"- {b[2:700]}" for b in tri] or ["- none"]) + [""]
    S["filings"] = f
    pr = press()
    if pr is not None:
        items, total = pr
        S["press"] = [f"## Press releases (trusted wires, {total} since last briefing)"] + ([f"- {x}" for x in items] or ["- none"]) + [""]
    st_ = setups()
    if st_: S["setups"] = ["## Setups (watch only, not buys)"] + [f"- {x}" for x in st_] + [""]
    led, cl = ledger(), calls()
    if cl: S["calls"] = ["## Public calls (the track record)"] + [f"- {x}" for x in cl] + [""]
    if led: S["ledger"] = ["## Ledger (every scan item vs IWM)"] + [f"- {x}" for x in led] + [""]
    c = crypto()
    if c: S["crypto"] = ["## Crypto", f"- {c}", ""]
    cal = calendar()
    S["calendar"] = ["## Next 14 days"] + ([f"- {x}" for x in cal] or ["- nothing scheduled"]) + [""]
    order = ["calls", "watchlist", "filings", "press", "setups", "ledger", "crypto", "calendar"]
    full = head + [l for k in order for l in S.get(k, [])]
    return "\n".join(full), {k: "\n".join([f"**{TODAY:%a %d %b}**"] + v) for k, v in S.items()}


# Sections that go to their own channel in the morning. Watchlist (by size), positions, calls and setups
# go out after the close instead (briefing/recap.py), when the day's prices are final; they stay in the
# full #briefing post.
MORNING_CHANNELS = {"filings", "press", "calendar", "ledger", "crypto"}


def main():
    text, sections = build()
    out = ROOT / "briefings" / f"{TODAY.isoformat()}.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    if "--dry-run" in sys.argv:
        print(text); return
    marker = f"briefings/.sent-{TODAY.isoformat()}"
    if not notify.webhook("briefing") and not os.getenv("DISCORD_WEBHOOK_URL"):
        print("no #briefing webhook: briefing written, nothing sent"); return
    # Claim first, send second (rule 2026-10-06): the marker is pushed BEFORE posting, so a later failure can't repost.
    if "--force" not in sys.argv and not claim(marker, f"claimed {dt.datetime.now(dt.UTC):%H:%M} UTC"):
        print(f"already sent today ({marker}); briefing file refreshed, nothing sent")
        return
    sent = notify.send(text, "briefing")                       # the whole thing, once
    for ch, body in sections.items():                         # plus each morning section to its own channel
        if ch in MORNING_CHANNELS and notify.has_own_channel(ch):
            sent += notify.send(body, ch)
    print(f"briefing written to {out.relative_to(ROOT)}; sent via: {', '.join(sent) or 'nothing (no secrets set)'}")


if __name__ == "__main__":
    main()
