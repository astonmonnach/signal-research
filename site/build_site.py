"""Build the research website: one searchable place for every stock, call, strategy, report and lesson.

  python site/build_site.py            -> _site/index.html + _site/data.json (deployed to GitHub Pages by .github/workflows/site.yml)

Everything comes from files already in the repo, plus Yahoo closes and SEC filing lists for the stock pages. Nothing here is
hand-edited: fix the source file and the site follows on the next build.
"""
import csv, json, re, shutil, sys, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
sys.path.insert(0, str(ROOT / "briefing")); sys.path.insert(0, str(ROOT / "reports"))
import recap  # noqa: E402  (prices with corporate-action add-back, verdicts, SEC filings, calendar)

# Documents shown on the site, by section. Generated or hand-written markdown only; raw data files stay out.
DOC_GROUPS = [
    ("Calls", ["calls/README.md"]),
    ("Long-term", ["longterm/README.md", "longterm/METHOD.md", "research/longterm-*/REPORT.md"]),
    ("Dossiers", ["stocks/README.md", "stocks/*.md", "ideas/*.md"]),
    ("Recaps", ["recaps/weekly/*.md", "recaps/daily/*.md"]),
    ("Reports", ["reports/weekly/*.md", "reports/monthly/*.md", "reports/quarterly/*.md"]),
    ("Scans", ["scans/*.md"]),
    ("Triage", ["watch/digests/*-triage.md"]),
    ("Research", ["research/**/*.md"]),
    ("Strategies", ["strategies/**/*.md"]),
    ("Ledger", ["ledger/LEDGER.md", "ledger/RULES.md"]),
    ("Funding pots", ["watch/pots/*.md"]),
    ("Method", ["LESSONS.md", ".claude/skills/nth-order/SKILL.md", "SOURCES.md", "PLAN.md"]),
]
SKIP = ("/work/", "_TEMPLATE", "/node_modules/")
PRIVATE = re.compile(r"noxar", re.I)          # never publish anything that names the private business


def title_of(path, md):
    m = re.search(r"^#\s+(.+)$", md, re.M)
    return re.sub(r"[*`]", "", m.group(1)).strip() if m else Path(path).stem


def docs():
    out, seen = {}, set()
    for group, pats in DOC_GROUPS:
        for pat in pats:
            for f in sorted(ROOT.glob(pat), reverse=group in ("Recaps", "Reports", "Scans", "Triage")):
                rel = f.relative_to(ROOT).as_posix()
                if rel in seen or any(s in rel for s in SKIP) or not f.is_file(): continue
                md = f.read_text(encoding="utf-8", errors="ignore")
                if PRIVATE.search(md): continue
                seen.add(rel)
                out[rel] = {"group": group, "title": title_of(rel, md), "md": md, "size": len(md)}
    return out


def list_name(s):
    """Display name of a strategy list ("STRAT: SPIN-OFF" -> "Spin-off"), shared by the data and the page."""
    n = re.sub(r"^STRAT:\s*", "", s["title"]).lower()
    return n[:1].upper() + n[1:]


def sec_links(t):
    s = recap.filings(t, n=4)
    return [{"label": a, "url": b} for a, b in re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", s)]


def stocks(caps, strategies, events):
    info, fnd = recap.dossiers(), recap.found()
    watch = json.load(open(ROOT / "watch/watchlist.json", encoding="utf-8"))["tickers"]
    setups = sorted(recap.setup_found())
    calls = [r for r in csv.DictReader(open(ROOT / "calls/CALLS.csv", encoding="utf-8"))] if (ROOT / "calls/CALLS.csv").exists() else []
    lt = [r for r in csv.DictReader(open(ROOT / "longterm/candidates.csv", encoding="utf-8"))] if (ROOT / "longterm/candidates.csv").exists() else []
    trades = [r for r in csv.DictReader(open(ROOT / "journal/trades.csv", encoding="utf-8")) if r["entry"] and not r["exit"]]
    universe = list(dict.fromkeys(watch + setups + [c["ticker"] for c in calls] + [r["ticker"] for r in lt]))
    out = []
    for t in universe:
        c = caps.get(t, {})
        bench = recap.bench_of(t, caps)
        f0 = fnd.get(t, (None, ""))[0]
        if t in setups: f0 = recap.setup_found()[t]
        since = recap.holder_pct(t, f0) if f0 else None
        b = recap.bars(t)
        lists = (["All"] if t in watch else []) + [list_name(s) for s in strategies if t in s["tickers"]]
        if t in setups: lists.append("Setups")
        if any(x["ticker"] == t for x in calls): lists.append("Called")
        if any(x["symbol"] == t for x in trades): lists.append("Trades open")
        if any(x["ticker"] == t for x in lt): lists.append("Long-term")
        i = info.get(t, {})
        rx = re.compile(rf"\b{re.escape(t)}\b")
        out.append({
            "t": t, "lists": lists, "bucket": c.get("bucket") if t in watch else ("micro" if t in setups else c.get("bucket")),
            "mcap": c.get("mcap"), "close": b[-1][1] if b else None, "asof": b[-1][0].isoformat() if b else None,
            "day": recap.day(t) if b else None, "five": recap.five(t) if b else None,
            "since": since, "since_vs": recap.minus(since, recap.holder_pct(bench, f0)) if f0 else None, "bench": bench,
            "found": f0.isoformat() if f0 else None, "verdict": i.get("verdict", ""), "score": i.get("score", ""),
            "thesis": recap.clip(i.get("thesis", ""), 400), "pot": re.sub(r"\s*·\s*\[pot\]\([^)]*\)", "", recap.pot_line(t)),
            "events": [{"date": e["date"].isoformat(), "summary": e["summary"]} for e in events
                       if e["date"] >= dt.date.today() and rx.search(e["summary"])][:6],
            "sec": sec_links(t),
            "doc": f"stocks/{t}.md" if (ROOT / f"stocks/{t}.md").exists() else None,
            "idea": f"ideas/{t}.md" if (ROOT / f"ideas/{t}.md").exists() else None,
        })
    return out


def main():
    OUT.mkdir(exist_ok=True)
    caps = json.load(open(ROOT / "watch/caps.json", encoding="utf-8"))["stocks"] if (ROOT / "watch/caps.json").exists() else {}
    strategies = json.load(open(ROOT / "watch/strategies.json", encoding="utf-8"))["strategies"]
    events = recap.calendar_events()
    marks = list(csv.DictReader(open(ROOT / "calls/marks.csv", encoding="utf-8"))) if (ROOT / "calls/marks.csv").exists() else []
    pots = json.load(open(ROOT / "watch/pots/latest.json", encoding="utf-8")) if (ROOT / "watch/pots/latest.json").exists() else {}
    recaps = sorted((ROOT / "recaps/daily").glob("*.md"))
    D = docs()
    data = {
        "built": dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC"),
        "stocks": stocks(caps, strategies, events),
        "strategies": [{"name": list_name(s), "about": s["about"], "tickers": s["tickers"]} for s in strategies],
        "calls": marks,
        "events": [{"date": e["date"].isoformat(), "summary": e["summary"]} for e in events if e["date"] >= dt.date.today() - dt.timedelta(days=1)],
        "pots": list(pots.values()),
        "positions": (ROOT / "watch/positions.md").read_text(encoding="utf-8") if (ROOT / "watch/positions.md").exists() else "",
        "latest_recap": recaps[-1].relative_to(ROOT).as_posix() if recaps else None,
        "docs": D,
    }
    (OUT / "data.json").write_text(json.dumps(data, default=str, separators=(",", ":")), encoding="utf-8")
    shutil.copy(ROOT / "site/index.html", OUT / "index.html")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"site: {len(data['stocks'])} stocks, {len(D)} documents, data.json {(OUT / 'data.json').stat().st_size / 1e6:.1f} MB -> _site/")


if __name__ == "__main__":
    main()
