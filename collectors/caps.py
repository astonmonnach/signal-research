"""Market cap and size bucket for every watchlist stock -> watch/caps.json.

Shares outstanding come from the latest SEC cover-page figure (dei:EntityCommonStockSharesOutstanding,
all share classes on the latest date added together). watch/caps_manual.csv overrides it when a recent
spin-off, IPO or reverse merger makes the SEC figure stale (ticker,shares,source,date). The price is the
latest Yahoo daily close.

Buckets (the usual US cut-offs, also used for the Discord channels and IBKR watchlists):
  micro < $300M · small $300M–$2B · mid $2B–$10B · large > $10B

Usage: python collectors/caps.py
"""
import csv, json, time, urllib.request, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC_UA = {"User-Agent": "PersonalResearch research@example.com"}
BUCKETS = [("micro", 0, 300e6), ("small", 300e6, 2e9), ("mid", 2e9, 10e9), ("large", 10e9, float("inf"))]


def get(url, headers):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
        return json.load(r)


def bucket(mcap):
    return next(name for name, lo, hi in BUCKETS if lo <= mcap < hi)


def sec_shares(cik):
    facts = get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json", SEC_UA)
    units = facts.get("facts", {}).get("dei", {}).get("EntityCommonStockSharesOutstanding", {}).get("units", {}).get("shares", [])
    if not units: return None, None
    latest = max(u["end"] for u in units)
    # One row per share class on the cover page; the same class can repeat across filings, so keep one per accession+frame.
    rows = {(u.get("accn"), u.get("frame"), u["val"]) for u in units if u["end"] == latest}
    accn = max(r[0] for r in rows)
    return sum(v for a, _, v in rows if a == accn), latest


def last_close(t):
    r = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=5d&interval=1d", {"User-Agent": "Mozilla/5.0"})["chart"]["result"][0]
    c = [x for x in r["indicators"]["quote"][0]["close"] if x]
    return c[-1] if c else r["meta"].get("regularMarketPrice")


def main():
    tickers = json.load(open(ROOT / "watch/watchlist.json", encoding="utf-8"))["tickers"]
    sp = ROOT / "watch/strategies.json"                    # strategy lists can hold names that aren't on ALL (e.g. merger arb)
    for s in (json.load(open(sp, encoding="utf-8"))["strategies"] if sp.exists() else []):
        tickers += [t for t in s["tickers"] if t not in tickers]
    manual = {r["ticker"]: r for r in csv.DictReader(open(ROOT / "watch/caps_manual.csv", encoding="utf-8"))} \
        if (ROOT / "watch/caps_manual.csv").exists() else {}
    ciks = {v["ticker"]: v["cik_str"] for v in get("https://www.sec.gov/files/company_tickers.json", SEC_UA).values()}
    out = {}
    for t in tickers:
        row = {"ticker": t}
        try:
            if t in manual:
                row.update(shares=float(manual[t]["shares"]), shares_source=manual[t]["source"], shares_date=manual[t]["date"])
            elif t in ciks:
                sh, d = sec_shares(ciks[t]); time.sleep(0.15)
                if sh: row.update(shares=sh, shares_source="SEC cover page (dei)", shares_date=d)
            px = last_close(t); time.sleep(0.15)
            row["price"] = px
            if row.get("shares") and px:
                row["mcap"] = row["shares"] * px
                row["bucket"] = bucket(row["mcap"])
        except Exception as e:
            row["error"] = str(e)[:120]
        out[t] = row
    payload = {"updated": dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC"),
               "buckets": {n: [lo, hi if hi != float("inf") else None] for n, lo, hi in BUCKETS}, "stocks": out}
    (ROOT / "watch/caps.json").write_text(json.dumps(payload, indent=1), encoding="utf-8")
    for t, r in out.items():
        print(f"{t:6} {r.get('bucket', '?'):6} mcap ${r.get('mcap', 0) / 1e9:7.2f}B  shares {r.get('shares', 0) / 1e6:8.1f}M "
              f"({r.get('shares_source', 'none')} {r.get('shares_date', '')}) {r.get('error', '')}")


if __name__ == "__main__":
    main()
