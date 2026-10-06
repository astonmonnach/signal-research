"""Alerts: new filings and news on the stocks we follow -> Discord #alerts, every 30 minutes. No emojis.

Followed = ALL (watch/watchlist.json) + every strategy list + open trades + public calls + long-term candidates.
Checks:
  - SEC: each followed company's filing list (data.sec.gov submissions). Any new filing except insider forms
    (3/4/5/144), with its form, time and items, as a short link.
  - Press: releases from trusted wires (data/press/*.csv, collected by the press-wires job) about a followed stock.
  - DoD: new S1 contract signals (data/signals.csv), plus any DoD award matched to a followed stock (watch/dod/).
Each item is alerted once: alerts/seen.json is pushed BEFORE posting (briefing/claim.py), so a failed run can't repeat
alerts. The first run only records what already exists, so it doesn't flood the channel.

Usage: python briefing/alerts.py [--dry-run]
"""
import csv, json, re, sys, time, urllib.request, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "briefing"))
import notify  # noqa: E402
from claim import push_state  # noqa: E402

SEEN = "alerts/seen.json"
SEC_UA = {"User-Agent": "PersonalResearch research@example.com"}
INSIDER = {"3", "4", "5", "144", "3/A", "4/A", "5/A", "144/A"}
# Routine paperwork that would drown the real news (RXO filed 14 "425" deal-marketing documents in two days).
NOISE = {"425", "DEFA14A", "FWP", "CORRESP", "UPLOAD", "8-A12B", "8-A12G", "497", "497K", "S-8", "S-8 POS", "CERT"}  # EFFECT stays: e.g. HMH's resale going effective is the trigger
CIK_MANUAL = {"VYLR": 2128626, "HMH": 2021880}
NOW = dt.datetime.now(dt.UTC)


def followed():
    t = list(json.load(open(ROOT / "watch/watchlist.json", encoding="utf-8"))["tickers"])
    sp = ROOT / "watch/strategies.json"
    for s in (json.load(open(sp, encoding="utf-8"))["strategies"] if sp.exists() else []):
        t += s["tickers"]
    for f, col in [("journal/trades.csv", "symbol"), ("calls/CALLS.csv", "ticker"), ("longterm/candidates.csv", "ticker")]:
        p = ROOT / f
        if p.exists():
            for r in csv.DictReader(open(p, encoding="utf-8")):
                if col == "symbol" and r.get("exit"): continue
                t.append(r[col].strip().upper())
    return list(dict.fromkeys(x for x in t if x))


def ciks():
    try:
        req = urllib.request.Request("https://www.sec.gov/files/company_tickers.json", headers=SEC_UA)
        m = {v["ticker"]: v["cik_str"] for v in json.load(urllib.request.urlopen(req, timeout=30)).values()}
    except Exception:
        m = {}
    m.update(CIK_MANUAL)
    return m


def sec_items(tickers, days=3):
    out, cmap = [], ciks()
    since = (NOW - dt.timedelta(days=days)).date().isoformat()
    for t in tickers:
        cik = cmap.get(t)
        if not cik: continue
        try:
            req = urllib.request.Request(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json", headers=SEC_UA)
            rec = json.load(urllib.request.urlopen(req, timeout=30))["filings"]["recent"]
        except Exception:
            continue
        time.sleep(0.15)
        for i, (form, d, acc, doc) in enumerate(zip(rec["form"], rec["filingDate"], rec["accessionNumber"], rec["primaryDocument"])):
            if d < since: break
            if form in INSIDER or form in NOISE: continue
            when = (rec.get("acceptanceDateTime") or [""] * (i + 1))[i][11:16]
            items = (rec.get("items") or [""] * (i + 1))[i]
            url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/{doc}"
            label = f"{form.replace('SCHEDULE ', '').replace('SC ', '')} {dt.date.fromisoformat(d):%d %b}"
            out.append((f"sec:{acc}", t, f"[{label}]({url})" + (f" · {when} New York" if when else "") + (f" · items {items}" if items else "")))
    return out


def press_items(tickers, days=2):
    out, keep = [], set(tickers)
    for f in sorted((ROOT / "data/press").glob("*.csv"))[-days - 1:]:
        for r in csv.DictReader(open(f, encoding="utf-8", newline="")):
            tk = (r.get("ticker") or "").upper()
            if tk in keep and r.get("link"):
                out.append((f"press:{r['link']}", tk, f"{r['title'][:140]} ({r['wire']}) {r['link']}"))
    return out


def dod_items(tickers):
    out = []
    p = ROOT / "data/signals.csv"
    for r in (csv.DictReader(open(p, encoding="utf-8")) if p.exists() else []):
        out.append((f"s1:{r['signal_id']}", r["ticker"], f"**S1 contract signal**: ${float(r['value_usd'] or 0) / 1e6:,.0f}M = "
                    f"{float(r['materiality'] or 0) * 100:.0f}% of market cap · {r['decision']} · {r['event_summary'][:120]}"))
    keep = set(tickers)
    for f in sorted((ROOT / "watch/dod").glob("*.md"))[-2:]:
        for line in f.read_text(encoding="utf-8").splitlines():
            for t in re.findall(r"\*\*([A-Z]{1,5})\*\*", line):
                if t in keep:
                    out.append((f"dod:{f.stem}:{t}:{hash(line) & 0xffffffff}", t, f"**DoD award** ({f.stem}): {line.strip('- ')[:200]}"))
    return out


def main():
    tickers = followed()
    items = sec_items(tickers) + press_items(tickers) + dod_items(tickers)
    p = ROOT / SEEN
    first = not p.exists()
    seen = set(json.loads(p.read_text(encoding="utf-8"))) if p.exists() else set()
    new = [it for it in items if it[0] not in seen]
    if first or "--dry-run" in sys.argv:
        print(("first run: recording " if first else "dry run, would alert on ") + f"{len(new)} items")
        for k, t, txt in new[:40]: print(f"  {t}: {notify.plain(txt)[:160]}")
        if first and "--dry-run" not in sys.argv:
            push_state(SEEN, lambda path: (path.parent.mkdir(parents=True, exist_ok=True),
                                           path.write_text(json.dumps(sorted(seen | {k for k, _, _ in items}), indent=0), encoding="utf-8")))
        return
    if not new:
        print("no new items"); return
    if not notify.has_own_channel("alerts"):
        print(f"{len(new)} new items but no #alerts webhook; not recorded, so they'll post once the webhook exists"); return

    def write(path):                                     # merge with whatever the latest main already holds
        cur = set(json.loads(path.read_text(encoding="utf-8"))) if path.exists() else set()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(sorted(cur | {k for k, _, _ in new}), indent=0), encoding="utf-8")
    if not push_state(SEEN, write):
        print("couldn't record the alerts first, so nothing sent (next run retries)"); return
    uk = NOW.astimezone(dt.timezone(dt.timedelta(hours=1 if 3 < NOW.month < 11 else 0)))
    lines = [f"**ALERTS** · {uk:%a %d %b %H:%M} UK"]
    for k, t, txt in sorted(new, key=lambda x: x[1]):
        lines.append(f"- **{t}** · {txt}")
    sent = notify.send("\n".join(lines), "alerts")
    print(f"alerted {len(new)} items via {', '.join(sent) or 'nothing'}")


if __name__ == "__main__":
    main()
