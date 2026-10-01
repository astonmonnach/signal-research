"""S1 CONTRACT_MCAP collector: DoD daily contract announcements -> signals.

Usage:
  python collectors/s1_dod.py              # latest announcement day
  python collectors/s1_dod.py --date 2026-09-30
  python collectors/s1_dod.py --dry-run    # report only, don't append to signals.csv

Writes watch/dod/YYYY-MM-DD.md (every award: match status, materiality) and
appends v1 signals (listed, mcap < $2bn, materiality >= 5%) to data/signals.csv.
Plain Python, no AI. The matching table is data/entities.csv (private).
"""
import argparse
import csv
import json
import re
import subprocess
import sys
import time
import urllib.request
from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIGNALS = ROOT / "data" / "signals.csv"
ENTITIES = ROOT / "data" / "entities.csv"
OUTDIR = ROOT / "watch" / "dod"

STRATEGY, VERSION = "S1_CONTRACT_MCAP", "v1"
MAX_MCAP, MIN_MATERIALITY, EST_COST_PCT = 2e9, 0.05, 3.5

RSS = "https://www.war.gov/DesktopModules/ArticleCS/RSS.ashx?ContentType=400&Site=945&max=20"
BROWSER = ["-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
           "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
           "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "-H", "Accept-Language: en-GB,en;q=0.9", "-H", "Upgrade-Insecure-Requests: 1",
           "-H", "Sec-Fetch-Dest: document", "-H", "Sec-Fetch-Mode: navigate", "-H", "Sec-Fetch-Site: none"]
SEC_UA = {"User-Agent": "PersonalResearch research@example.com"}

SUFFIXES = r"\b(inc|incorporated|corp|corporation|co|company|llc|l\.l\.c|lp|l\.p|ltd|limited|plc|holdings?|group|the)\b"
MONEY = r"\$\s?([\d,]+(?:\.\d+)?)"


# ---------- fetching ----------
def curl(url):
    """war.gov sits behind bot protection that blocks Python's TLS; curl with browser headers passes."""
    out = subprocess.run(["curl", "-s", "-L", "--compressed", *BROWSER, url],
                         capture_output=True, timeout=60)
    return out.stdout.decode("utf-8", "ignore")


def sec_json(url):
    time.sleep(0.15)
    with urllib.request.urlopen(urllib.request.Request(url, headers=SEC_UA), timeout=30) as r:
        return json.load(r)


def yahoo_closes(ticker):
    raw = subprocess.run(["curl", "-s", "-A", "Mozilla/5.0",
                          f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1mo&interval=1d"],
                         capture_output=True, timeout=30).stdout
    try:
        res = json.loads(raw)["chart"]["result"][0]
        closes = [c for c in res["indicators"]["quote"][0]["close"] if c is not None]
        return closes
    except Exception:
        return []


# ---------- parsing ----------
def announcement_days():
    """[(date, url, pubdate_utc)] from the RSS feed, newest first."""
    from xml.etree import ElementTree as ET
    root = ET.fromstring(curl(RSS).encode("utf-8"))
    days = []
    for item in root.iter("item"):
        title = item.findtext("title", "").strip()
        m = re.search(r"Contracts for (\w+)\.? (\d+), (\d{4})", title)
        if not m:
            continue
        d = datetime.strptime(f"{m.group(1)[:3]} {m.group(2)} {m.group(3)}", "%b %d %Y").date()
        pub = parsedate_to_datetime(item.findtext("pubDate").strip()).astimezone(timezone.utc)
        days.append((d, item.findtext("link").strip(), pub))
    return days


def parse_awards(html):
    from bs4 import BeautifulSoup
    body = BeautifulSoup(html, "lxml").select_one("div.body")
    if body is None:
        raise RuntimeError("page layout changed: no div.body")
    agency, awards = "", []
    for p in body.find_all("p"):
        text = " ".join(p.get_text(" ", strip=True).split())
        if not text:
            continue
        if text.isupper() and len(text) < 60:          # section header: NAVY, ARMY, AIR FORCE...
            agency = text.title()
            continue
        if "$" not in text or text.upper().startswith("CORRECTION"):
            continue
        awards.append(parse_one(text, agency))
    return awards


def parse_one(text, agency):
    low = text.lower()
    multi = bool(re.search(r"\b(are|were|have been) (being )?awarded\b|\bshare\b.*\bmultiple[- ]award", low)) \
        or ("multiple award" in low or "multiple-award" in low) and ";" in text
    # awardee(s): text before the first "(contract no.)" or " is/was awarded"
    head = re.split(r"\b(?:is|was|has been|are|were|have been)\s+(?:being\s+)?awarded\b", text, 1)[0]
    if multi:
        # each awardee appears as "Name, City, State (CONTRACT-NO)"; split on those units
        units = re.findall(r"([^;()]+?)\s*\([A-Z0-9-]{8,}\)", head) or head.split(";")
        names = [re.split(r",", re.sub(r"^\s*and\s+", "", u).strip(), 1)[0] for u in units]
    else:
        names = [re.split(r",", head, 1)[0]]
    names = [n.replace("*", "").strip(" .") for n in names if n and n[0].isalnum()]
    small_biz = "*" in head

    amounts = [float(a.replace(",", "")) for a in re.findall(MONEY, text)]
    value = amounts[0] if amounts else None

    if "modification" in low and ("option" in low and "exercis" in low):
        award_type = "option"
    elif "modification" in low:
        award_type = "modification"
    elif "indefinite-delivery" in low or "maximum" in low or "ceiling" in low:
        award_type = "IDIQ_ceiling"
    else:
        award_type = "definitive"
    if multi:
        award_type += "|multi"

    obligated = None
    if re.search(r"no funds (were|will be|are being) obligated", low):
        obligated = 0.0
    else:
        # sum "...funds in the amount of $X" when the paragraph says they are obligated at award
        if re.search(r"obligated (at (the )?time of award|on this award|at award)", low):
            obligated = sum(float(a.replace(",", "")) for a in
                            re.findall(r"in the amount of " + MONEY, text)) or None
    # contract length -> value per year (a 5-year $1bn ceiling is ~$200m a year, not $1bn)
    years = None
    cm = re.search(r"(?:completion date is|completed (?:by|in|on)|performance period (?:through|ending))\s+"
                   r"(?:[A-Z][a-z]+\.? )?(?:\d{1,2}, )?(\d{4})", text)
    if cm:
        years = max(int(cm.group(1)) - date.today().year, 1)
    m = re.search(r"\(([A-Z0-9]{5,6}-?\d{2}-?[A-Z]-?[A-Z0-9]{4,})\)", text)
    contract_no = m.group(1) if m else ""
    return {"agency": agency, "names": names, "small_business": small_biz, "value_usd": value,
            "obligated_usd": obligated, "years": years, "award_type": award_type, "contract_no": contract_no,
            "summary": text[:400]}


# ---------- matching ----------
def norm(s):
    s = s.lower().replace("&", " and ")
    s = re.sub(SUFFIXES, " ", s)
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s).split())


def load_entities():
    rows = list(csv.DictReader(open(ENTITIES, encoding="utf-8"))) if ENTITIES.exists() else []
    return [(norm(r["name_as_seen"]), r) for r in rows if r.get("name_as_seen")]


def match(name, entities, sec_index):
    n = norm(name)
    # 1) manual table: longest prefix wins ("lockheed martin rotary..." -> "lockheed martin")
    best = max(((k, r) for k, r in entities if n.startswith(k)), key=lambda kr: len(kr[0]), default=None)
    if best:
        r = best[1]
        return r["ticker"], r.get("market", "US"), r.get("confidence", "manual"), r.get("parent_name", "")
    # 2) exact normalised match against SEC registrants
    if n in sec_index:
        t, cik, title = sec_index[n]
        return t, "US", "auto_exact", title
    return "", "", "unmatched", ""


def sec_tickers():
    data = sec_json("https://www.sec.gov/files/company_tickers.json")
    idx, by_ticker = {}, {}
    for v in data.values():
        idx.setdefault(norm(v["title"]), (v["ticker"], v["cik_str"], v["title"]))
        by_ticker[v["ticker"]] = v["cik_str"]
    return idx, by_ticker


def market_cap(ticker, cik):
    closes = yahoo_closes(ticker)
    if not closes:
        return None, None, None
    price = closes[-1]
    pre5 = (closes[-1] / closes[-6] - 1) * 100 if len(closes) >= 6 else None
    try:
        facts = sec_json(f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/dei/EntityCommonStockSharesOutstanding.json")
        units = facts["units"]["shares"]
        latest = max(u["end"] for u in units)
        # latest cover page: one row per share class, so sum the rows from that single filing
        rows = [u for u in units if u["end"] == latest]
        accn = max(u["accn"] for u in rows)
        shares = sum(u["val"] for u in rows if u["accn"] == accn)
    except Exception:
        return None, price, pre5
    return price * shares, price, pre5


# ---------- main ----------
def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--backfill", action="store_true",
                    help="mark rows as detected after the fact (excluded from forward-test stats)")
    args = ap.parse_args()

    days = announcement_days()
    if not days:
        sys.exit("RSS returned no contract days (blocked or layout changed).")
    want = date.fromisoformat(args.date) if args.date else days[0][0]
    hits = [d for d in days if d[0] == want]
    if not hits:
        sys.exit(f"{want} not in the RSS feed (it only covers recent days). Available: {[str(d[0]) for d in days]}")
    day, url, pub = hits[-1]
    awards, seen = [], set()
    for _, u, _ in hits:            # some days get a second page (supplement or re-post)
        for a in parse_awards(curl(u)):
            if a["summary"] not in seen:
                seen.add(a["summary"])
                awards.append(a)
    url = " ".join(u for _, u, _ in hits)
    entities = load_entities()
    sec_index, by_ticker = sec_tickers()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines, signals, unmatched = [], [], set()
    cache = {}
    for a in awards:
        for name in a["names"]:
            ticker, market, conf, parent = match(name, entities, sec_index)
            row = dict(a, name=name, ticker=ticker, market=market, conf=conf, parent=parent,
                       mcap=None, price=None, pre5=None, mat=None, mat_upper=None, mat_year=None)
            if not ticker:
                unmatched.add(name)
            elif market == "US" and ticker in by_ticker:
                if ticker not in cache:
                    cache[ticker] = market_cap(ticker, by_ticker[ticker])
                row["mcap"], row["price"], row["pre5"] = cache[ticker]
                if row["mcap"]:
                    share = 1 / len(a["names"])          # multi-award ceilings are shared
                    if a["obligated_usd"] is not None:
                        row["mat"] = a["obligated_usd"] * share / row["mcap"]
                    if a["value_usd"]:
                        row["mat_upper"] = a["value_usd"] * share / row["mcap"]
                        if a["years"]:
                            row["mat_year"] = row["mat_upper"] / a["years"]
            lines.append(row)

            m = row["mat"] if row["mat"] is not None else row["mat_upper"]
            if row["mcap"] and row["mcap"] < MAX_MCAP and m is not None and m >= MIN_MATERIALITY:
                signals.append(row)

    # ---- daily report ----
    OUTDIR.mkdir(parents=True, exist_ok=True)
    def pct(x): return "" if x is None else f"{x*100:.1f}%"
    def usd(x): return "" if x is None else f"${x/1e6:,.1f}M"
    def signed(x): return "" if x is None else f"{x:+.1f}%"
    rep = [f"# DoD contracts {day} (S1 {VERSION})", f"Source: {url}", f"Published {pub:%Y-%m-%d %H:%M} UTC, collected {now}", "",
           f"{len(awards)} awards, {len(lines)} awardee lines, {sum(1 for l in lines if l['ticker'])} matched to a ticker, "
           f"**{len(signals)} v1 signals** (mcap < $2bn, materiality ≥ 5%).", ""]
    if signals:
        rep += ["## Signals", "| ticker | awardee | type | value | obligated | mcap | materiality (obligated / upper / per year) | pre-move 5d |", "|---|---|---|---|---|---|---|---|"]
        for s in signals:
            rep.append(f"| **{s['ticker']}** | {s['name']} | {s['award_type']} | {usd(s['value_usd'])} | {usd(s['obligated_usd'])} | "
                       f"{usd(s['mcap'])} | {pct(s['mat'])} / {pct(s['mat_upper'])} / {pct(s['mat_year'])} | {signed(s['pre5'])} |")
        rep.append("")
    rep += ["## All matched awardees", "| ticker | awardee | match | type | value | mcap | materiality upper |", "|---|---|---|---|---|---|---|"]
    for l in sorted((l for l in lines if l["ticker"]), key=lambda l: -(l["mat_upper"] or 0)):
        rep.append(f"| {l['ticker']} | {l['name']} | {l['conf']} | {l['award_type']} | {usd(l['value_usd'])} | {usd(l['mcap'])} | {pct(l['mat_upper'])} |")
    rep += ["", f"## Unmatched ({len(unmatched)}): add listed parents to data/entities.csv",
            *[f"- {n}" for n in sorted(unmatched)]]
    (OUTDIR / f"{day}.md").write_text("\n".join(rep) + "\n", encoding="utf-8")

    # ---- append signals ----
    if signals and not args.dry_run:
        existing = {r["signal_id"] for r in csv.DictReader(open(SIGNALS, encoding="utf-8"))}
        with open(SIGNALS, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for s in signals:
                sid = f"S1-{day}-{s['ticker']}-{s['contract_no'] or abs(hash(s['summary']))%10**6}"
                if sid in existing:
                    continue
                m = s["mat"] if s["mat"] is not None else s["mat_upper"]
                w.writerow([sid, now, STRATEGY, VERSION, "US", "war.gov", url, s["name"], s["ticker"], s["conf"],
                            s["summary"][:200], s["award_type"], s["value_usd"], s["obligated_usd"],
                            round(s["mcap"]), round(m, 4), round(s["price"], 4), "",
                            "" if s["pre5"] is None else round(s["pre5"], 2), EST_COST_PCT, "",
                            "PENDING", "", "", ("materiality=obligated" if s["mat"] is not None else "materiality=upper_bound")
                            + (f"; per_year={s['mat_year']:.4f} over {s['years']}y" if s["mat_year"] else "")
                            + ("; BACKFILL: detected after the fact, exclude from forward stats" if args.backfill else "")])
    print("\n".join(rep[:6 + (len(signals) + 3 if signals else 0)]))
    print(f"\nReport: {OUTDIR / f'{day}.md'}")


if __name__ == "__main__":
    main()
