"""Backfill Discord with the last few days, oldest first. Run once from GitHub (Actions -> backfill); it needs the webhook secrets.

  #daily-recap   a recap for every trading day in the range, rebuilt from that day's closing prices
  #weekly-recap  each full week in the range (as of its Friday close)
  #filings       per day: what the pipeline found (scan summary + S1 contract signals) and the evening triage notes
  #press         per day: press releases matched to the watchlist (trusted wires)
  #briefing      the saved morning briefings
  #calendar, #ledger, #crypto   the current snapshot (once)
Today's full recap (size, strategies, trades open, calls, setups, daily recap) is sent by the workflow's next step,
`python briefing/recap.py`, so it lands after the backlog.

Each post goes out once: briefing/backfilled.json remembers what was sent, so a second run only sends what's new.
Usage: python briefing/backfill.py --from 2026-09-28 [--to 2026-10-05] [--dry-run]
"""
import csv, json, re, sys, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "briefing"))
import notify  # noqa: E402
import recap  # noqa: E402
import morning  # noqa: E402

DONE = ROOT / "briefing/backfilled.json"
DRY = "--dry-run" in sys.argv


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def clean(md):
    """Repo-relative markdown links become plain text (they point into the repo); SEC/press links stay."""
    return re.sub(r"\[([^\]]+)\]\((?!https?://)[^)]+\)", r"\1", md)


def triage_bullets(d):
    f = ROOT / f"watch/digests/{d.isoformat()}-triage.md"
    if not f.exists(): return []
    txt = f.read_text(encoding="utf-8")
    body = morning.section(txt, "Filings worth reading") or morning.section(txt, "Worth reading")   # older triage heading
    return [clean(b.strip()) for b in re.split(r"\n(?=- )", body) if b.strip().startswith("- ")]


def scan_summary(d):
    f = ROOT / f"scans/{d.isoformat()}.md"
    if not f.exists(): return ""
    m = re.search(r"^\*\*Found:\*\*(.*)$", f.read_text(encoding="utf-8"), re.M)
    return clean(m.group(1).strip()) if m else ""


def signals(d):
    p = ROOT / "data/signals.csv"
    out = []
    for r in (csv.DictReader(open(p, encoding="utf-8")) if p.exists() else []):
        if r["detected_at_utc"][:10] == d.isoformat():
            out.append(f"**{r['ticker']}** ${float(r['value_usd'] or 0) / 1e6:,.0f}M = {float(r['materiality'] or 0) * 100:.0f}% of market cap · "
                       f"{r['decision']} · {r['event_summary'][:120]}")
    return out


def press_items(d, limit=12):
    f = ROOT / f"data/press/{d.isoformat()}.csv"
    if not f.exists(): return []
    rows = list(csv.DictReader(open(f, encoding="utf-8", newline="")))
    strong = ("position", "watchlist", "signal", "manual_call")
    rows.sort(key=lambda r: (not r["matched_on"].startswith(strong), r["published_utc"]))
    return [f"**{r['ticker'] or '?'}** {r['title'][:120]} ({r['wire']}) {r['link']}" for r in rows[:limit]], len(rows)


def main():
    start = dt.date.fromisoformat(arg("--from", "2026-09-28"))
    end = dt.date.fromisoformat(arg("--to", dt.date.today().isoformat()))
    done = set(json.loads(DONE.read_text(encoding="utf-8"))) if DONE.exists() else set()
    sent = []

    def post(key, ch, text):
        if not text or key in done: return
        if DRY:
            print(f"\n===== #{ch} ({key}) =====\n{notify.plain(text)}"); return
        if notify.has_own_channel(ch) and notify.send(text, ch):
            done.add(key); sent.append(key)

    caps = json.load(open(ROOT / "watch/caps.json", encoding="utf-8"))["stocks"] if (ROOT / "watch/caps.json").exists() else {}
    tickers = json.load(open(ROOT / "watch/watchlist.json", encoding="utf-8"))["tickers"]
    groups = {k: [t for t in tickers if caps.get(t, {}).get("bucket") == k] for k in recap.BUCKETS}
    groups["small"] += [t for t in tickers if not caps.get(t, {}).get("bucket")]
    fnd, events = recap.found(), recap.calendar_events()
    spy = [d for d, _ in recap.bars("SPY")]
    last_session = spy[-1]

    days = [start + dt.timedelta(days=i) for i in range((end - start).days + 1)]
    for d in days:
        # Daily recap for past trading days (today's comes from recap.py in the next step).
        if d in spy and d < last_session:
            recap.AS_OF = d
            post(f"dailyrecap:{d}", "dailyrecap", recap.daily_post(f"{d:%a %d %b} close", d, groups, caps, fnd, events))
            if d.weekday() == 4:
                text, wk = recap.weekly_post(d, groups, fnd, events)
                post(f"weeklyrecap:{wk}", "weeklyrecap", text)
            recap.AS_OF = None
        # Filings: the scan summary, S1 signals and the evening triage for that date.
        summ, sig, tri = scan_summary(d), signals(d), triage_bullets(d)
        if summ or sig or tri:
            L = [f"**FILINGS** · {d:%a %d %b}"]
            if summ: L.append(f"Found: {summ}")
            if sig: L += ["**New contract signals (S1)**"] + [f"- {x}" for x in sig]
            if tri: L += ["**Worth reading (evening triage)**"] + tri
            post(f"filings:{d}", "filings", "\n".join(L))
        pr = press_items(d)
        if pr and pr[0]:
            items, total = pr
            post(f"press:{d}", "press", "\n".join([f"**PRESS RELEASES** · {d:%a %d %b} ({total} matched, trusted wires)"] + [f"- {x}" for x in items]))
        b = ROOT / f"briefings/{d.isoformat()}.md"
        if b.exists():
            post(f"briefing:{d}", "briefing", clean(b.read_text(encoding="utf-8")))

    # Current snapshot for the morning-only channels.
    _, S = morning.build()
    for ch in ("calendar", "ledger", "crypto"):
        if S.get(ch): post(f"{ch}:snapshot:{end}", ch, S[ch])

    if not DRY:
        DONE.write_text(json.dumps(sorted(done), indent=1), encoding="utf-8")
    print(f"backfill {start} to {end}: sent {len(sent)} posts" + (f" ({', '.join(sent)})" if sent else ""))


if __name__ == "__main__":
    main()
