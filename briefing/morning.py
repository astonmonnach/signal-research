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
import csv, json, re, sys, datetime as dt
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
import notify  # noqa: E402

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


def press(limit=12):
    p = ROOT / "watch/press/latest.json"
    if not p.exists(): return None
    items = json.loads(p.read_text(encoding="utf-8"))
    items = sorted(items, key=lambda x: (not str(x.get("matched_on", "")).startswith(("watchlist", "signal", "position")), x.get("published_utc", "")))
    return [f"**{i.get('ticker') or '?'}** {i.get('title','')[:120]} ({i.get('wire','')}) <{i.get('link','')}> [{i.get('matched_on','')}]"
            for i in items[:limit]], len(items)


def context():
    p = ROOT / "watch/context/latest.json"
    if not p.exists(): return None
    d = json.loads(p.read_text(encoding="utf-8"))
    com = [c for c in d.get("commodities", []) if c.get("unusual")]
    lines = [f"{c['name']} ({c['symbol']}) {c['chg_1d']:+.1f}% 1d, {c['chg_5d']:+.1f}% 5d (z {c['z_1d']:+.1f})" for c in com]
    for t, v in d.get("tickers", {}).items():
        if v.get("sympathy_flag"):
            lines.append(f"**{t}**: {v['sympathy_flag']} (self 5d {v.get('self_5d', 0):+.1f}% vs peer median {v.get('peer_median_5d', 0):+.1f}%)")
    return lines


def ledger(top=5):
    p = ROOT / "ledger/ledger.csv"
    if not p.exists(): return []
    live = [r for r in csv.DictReader(open(p, encoding="utf-8")) if r["status"] == "live" and r["excess_pct"]]
    if not live: return []
    live.sort(key=lambda r: float(r["excess_pct"]), reverse=True)
    fmt = lambda r: f"{r['ticker']} {float(r['excess_pct']):+.1f}% ({r['category']}, {r['days']}d)"
    best, worst = [fmt(r) for r in live[:top]], [fmt(r) for r in live[-top:][::-1]]
    xs = [float(r["excess_pct"]) for r in live]
    return [f"{len(live)} directional calls live · mean excess vs IWM {mean(xs):+.1f}% · hit rate {sum(x > 0 for x in xs)}/{len(xs)} (early, tiny samples)",
            "Best: " + ", ".join(best), "Worst: " + ", ".join(worst)]


def crypto():
    s, o = ROOT / "data/crypto/trending_signals.csv", ROOT / "data/crypto/trending_outcomes.csv"
    if not s.exists(): return ""
    sig = list(csv.DictReader(open(s, encoding="utf-8")))
    outs = list(csv.DictReader(open(o, encoding="utf-8"))) if o.exists() else []
    recent = [r for r in outs if r.get("horizon") == "24h" and r.get("ret_net_pct")]
    m24 = mean(float(r["ret_net_pct"]) for r in recent) if recent else None
    return (f"C1 trending: {len(sig)} signals logged · 24h net return so far "
            f"{'n/a' if m24 is None else f'{m24:+.1f}% avg over {len(recent)}'} (forward test, no trades)")


def calendar(days=14):
    ics = read("calendar/catalyst-dates.ics")
    out = []
    for ev in ics.split("BEGIN:VEVENT")[1:]:
        s = re.search(r"SUMMARY:(.*)", ev); d = re.search(r"DTSTART[^:]*:(\d{8})", ev)
        if s and d:
            day = dt.datetime.strptime(d.group(1), "%Y%m%d").date()
            if TODAY <= day <= TODAY + dt.timedelta(days=days):
                out.append((day, s.group(1).strip()))
    return [f"{d:%a %d %b}: {t}" for d, t in sorted(out)]


def build():
    L = [f"# ☀️ Morning briefing · {TODAY:%a %d %b %Y}", ""]
    pos = positions()
    if pos: L += ["## Positions"] + [f"- {p}" for p in pos] + [""]
    n = nq()
    if n: L += [n, ""]
    sig = new_signals()
    L += ["## New contract signals (S1, last 3 days)"] + ([f"- {s}" for s in sig] or ["- none"]) + [""]
    day, tri = latest_triage()
    if day: L += [f"## Filings worth reading (triage {day})"] + ([f"- {b[2:700]}" for b in tri] or ["- none"]) + [""]
    pr = press()
    if pr is not None:
        items, total = pr
        L += [f"## Press releases (trusted wires, {total} new)"] + ([f"- {x}" for x in items] or ["- none"]) + [""]
    ctx = context()
    if ctx is not None: L += ["## Commodities & sympathy moves"] + ([f"- {c}" for c in ctx] or ["- nothing unusual"]) + [""]
    led = ledger()
    if led: L += ["## Ledger (every call vs IWM)"] + [f"- {x}" for x in led] + [f"- Full table: <{REPO_URL}/ledger/LEDGER.md>", ""]
    c = crypto()
    if c: L += ["## Crypto", f"- {c}", ""]
    cal = calendar()
    L += ["## Next 14 days"] + ([f"- {x}" for x in cal] or ["- nothing scheduled"]) + [""]
    L += [f"Full briefing: <{REPO_URL}/briefings/{TODAY.isoformat()}.md>"]
    return "\n".join(L)


def main():
    text = build()
    out = ROOT / "briefings" / f"{TODAY.isoformat()}.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    if "--dry-run" in sys.argv:
        print(text); return
    sent = notify.send(text)
    print(f"briefing written to {out.relative_to(ROOT)}; sent via: {', '.join(sent) or 'nothing (no secrets set)'}")


if __name__ == "__main__":
    main()
