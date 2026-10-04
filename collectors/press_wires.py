"""Press-release collector: company-issued press releases -> catalyst hits.

Usage:
  python collectors/press_wires.py              # fetch every feed, report new hits
  python collectors/press_wires.py --dry-run    # print hits only; write nothing, leave seen.json alone
  python collectors/press_wires.py --self-test  # offline check of the parser and matcher (no network)

Why: two catalysts were missed because they came out as press releases, not SEC filings
(Metallus 29 Sep 2026, $125M initial DLA delivery order, PR Newswire; Elmet 14 Sep 2026, $2B DLA
tungsten stockpile contract). Sources are primary only: the wires companies pay to issue their own
releases (GlobeNewswire, PR Newswire, Business Wire) and official company IR feeds. The tested feed
list, and the sources deliberately not used, are in SOURCES.md.

An item is flagged when
  a) it names a watch-universe ticker listed on a US venue: watch/watchlist.json, open trades in
     journal/trades.csv, data/signals.csv rows from the last 30 days, ledger/manual_calls.csv; or
  b) its title/summary matches CATALYST_KEYWORDS and it names a NYSE / Nasdaq / NYSE American ticker.
Law-firm "investor alerts" and paid stock-promotion commentary are dropped (not company-issued).

Writes (each item is reported once; state is data/press/seen.json, hashed links):
  data/press/YYYY-MM-DD.csv   every hit found that UTC day, appended by each run
  watch/press/latest.json     the new hits from this run only ([] when none)
  watch/press/YYYY-MM-DD.md   readable digest of the day: watchlist/position hits, then keyword hits
Standard library only, so it runs on GitHub Actions with no pip installs.
"""
import argparse
import csv
import gzip
import hashlib
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree as ET

# Catalyst phrases, matched case-insensitively against title + summary. A space or hyphen inside a
# phrase also matches the other or nothing ("spin-off" = "spin off" = "spinoff").
# Keyword-only hits must also name a NYSE / Nasdaq / NYSE American ticker (rule b).
CATALYST_KEYWORDS = [
    # government contracts
    "Defense Logistics Agency", "delivery order", "IDIQ", "indefinite-delivery", "sole-source",
    "National Defense Stockpile", "Department of War", "Defense Production Act", "Office of Strategic Capital",
    "contract award", "awarded a contract",
    # corporate events
    "definitive agreement", "merger agreement", "to be acquired", "tender offer", "strategic alternatives",
    "special dividend", "spin-off", "carve-out", "listing standards", "noncompliance", "uplisting", "uplist", "share repurchase", "stock repurchase",
    # drug development
    "Phase 3", "Phase III", "FDA approval", "FDA approves", "PDUFA",
]

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "press"
OUTDIR = ROOT / "watch" / "press"
SEEN = DATA / "seen.json"
WATCHLIST = ROOT / "watch" / "watchlist.json"
SIGNALS = ROOT / "data" / "signals.csv"
TRADES = ROOT / "journal" / "trades.csv"
MANUAL = ROOT / "ledger" / "manual_calls.csv"

TIMEOUT = 20          # seconds, per request
HOST_GAP = 1.0        # at most one request per second per host
MAX_AGE_DAYS = 7      # older items are never reported (first run, slow feeds resurfacing old news)
SIGNAL_DAYS = 30      # signals.csv rows this recent join the watch universe
SEEN_KEEP_DAYS = 60   # seen.json entries older than this are pruned (feeds never reach that far back)
CSV_COLS = ["published_utc", "wire", "ticker", "exchange", "title", "link", "matched_on"]

# GlobeNewswire's Akamai front end stalls (no response) on a Chrome UA without the rest of the
# browser headers; with the full set it answers straight away. Same set as collectors/s1_dod.py.
BROWSER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Accept-Language": "en-GB,en;q=0.9", "Accept-Encoding": "gzip, deflate",
           "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate",
           "Sec-Fetch-Site": "none"}

# ---------- sources (tested 4 Oct 2026; see SOURCES.md) ----------
# Every feed returns only its newest 20 (Business Wire: ~10) items, so the busy ones (PR Newswire
# all-news, GlobeNewswire public companies) cover well under an hour on a weekday. The topic feeds
# (contracts, M&A, defense, metals) reach back days, which is what makes an hourly run workable.
GNW = "https://www.globenewswire.com/RssFeed/"
PRN = "https://www.prnewswire.com/rss/"
BW = "https://feed.businesswire.com/rss/home/?rss="
FEEDS = [  # (wire, feed name, url)
    ("GlobeNewswire", "Public companies", GNW + "orgclass/1/feedTitle/GlobeNewswire%20-%20News%20about%20Public%20Companies"),
    ("GlobeNewswire", "United States", GNW + "country/United%20States/feedTitle/GlobeNewswire%20-%20News%20from%20United%20States"),
    ("GlobeNewswire", "Business Contracts", GNW + "subjectcode/7-Business%20Contracts/feedTitle/GlobeNewswire%20-%20Business%20Contracts"),
    ("GlobeNewswire", "Mergers and Acquisitions", GNW + "subjectcode/27-Mergers%20And%20Acquisitions/feedTitle/GlobeNewswire%20-%20Mergers%20And%20Acquisitions"),
    ("GlobeNewswire", "Dividend Reports", GNW + "subjectcode/12-Dividend%20Reports%20And%20Estimates/feedTitle/GlobeNewswire%20-%20Dividend%20Reports%20And%20Estimates"),
    ("GlobeNewswire", "Government News", GNW + "subjectcode/19-Government%20News/feedTitle/GlobeNewswire%20-%20Government%20News"),
    ("GlobeNewswire", "Corporate Action", GNW + "subjectcode/61-Corporate%20Action/feedTitle/GlobeNewswire%20-%20Corporate%20Action"),
    ("GlobeNewswire", "Restructuring / Recapitalization", GNW + "subjectcode/37-Restructuring%202f%20Recapitalization/feedTitle/GlobeNewswire%20-%20Restructuring%20%20Recapitalization"),
    ("GlobeNewswire", "Financing Agreements", GNW + "subjectcode/17-Financing%20Agreements/feedTitle/GlobeNewswire%20-%20Financing%20Agreements"),
    ("GlobeNewswire", "Clinical Study", GNW + "subjectcode/90-Clinical%20Study/feedTitle/GlobeNewswire%20-%20Clinical%20Study"),
    ("GlobeNewswire", "Industry: Defense", GNW + "industry/2717-Defense/feedTitle/GlobeNewswire%20-%20Industry%20News%20on%20Defense"),
    ("GlobeNewswire", "Industry: Aerospace", GNW + "industry/2713-Aerospace/feedTitle/GlobeNewswire%20-%20Industry%20News%20on%20Aerospace"),
    ("GlobeNewswire", "Industry: Iron & Steel", GNW + "industry/1757-Iron%2026%20Steel/feedTitle/GlobeNewswire%20-%20Industry%20News%20on%20Iron%20and%20Steel"),
    ("GlobeNewswire", "Industry: Nonferrous Metals", GNW + "industry/1755-Nonferrous%20Metals/feedTitle/GlobeNewswire%20-%20Industry%20News%20on%20Nonferrous%20Metals"),
    ("GlobeNewswire", "Industry: General Mining", GNW + "industry/1775-General%20Mining/feedTitle/GlobeNewswire%20-%20Industry%20News%20on%20General%20Mining"),
    ("GlobeNewswire", "Industry: Basic Materials", GNW + "industry/1000-Basic%20Materials/feedTitle/GlobeNewswire%20-%20Industry%20News%20on%20Basic%20Materials"),
    ("GlobeNewswire", "Industry: Industrials", GNW + "industry/2000-Industrials/feedTitle/GlobeNewswire%20-%20Industry%20News%20on%20Industrials"),
    ("GlobeNewswire", "Industry: Biotechnology", GNW + "industry/4573-Biotechnology/feedTitle/GlobeNewswire%20-%20Industry%20News%20on%20Biotechnology"),
    ("GlobeNewswire", "Industry: Pharmaceuticals", GNW + "industry/4577-Pharmaceuticals/feedTitle/GlobeNewswire%20-%20Industry%20News%20on%20Pharmaceuticals"),
    ("PR Newswire", "All news releases", PRN + "news-releases-list.rss"),
    ("PR Newswire", "Financial Services & Investing", PRN + "financial-services-latest-news/financial-services-latest-news-list.rss"),
    ("PR Newswire", "General Business", PRN + "general-business-latest-news/general-business-latest-news-list.rss"),
    ("PR Newswire", "Heavy Industry & Manufacturing", PRN + "heavy-industry-manufacturing-latest-news/heavy-industry-manufacturing-latest-news-list.rss"),
    ("PR Newswire", "Aerospace & Defense", PRN + "heavy-industry-manufacturing-latest-news/aerospace-defense-list.rss"),
    ("PR Newswire", "Contracts", PRN + "financial-services-latest-news/contracts-list.rss"),
    ("PR Newswire", "Acquisitions, Mergers and Takeovers", PRN + "financial-services-latest-news/acquisitions-mergers-and-takeovers-list.rss"),
    ("PR Newswire", "Dividends", PRN + "financial-services-latest-news/dividends-list.rss"),
    ("PR Newswire", "Stock Offering", PRN + "financial-services-latest-news/stock-offering-list.rss"),
    ("PR Newswire", "Earnings", PRN + "financial-services-latest-news/earnings-list.rss"),
    ("PR Newswire", "Mining & Metals", PRN + "energy-latest-news/mining-metals-list.rss"),
    ("PR Newswire", "Energy", PRN + "energy-latest-news/energy-latest-news-list.rss"),
    ("PR Newswire", "Health", PRN + "health-latest-news/health-latest-news-list.rss"),
    ("PR Newswire", "FDA Approval", PRN + "health-latest-news/fda-approval-list.rss"),
    ("PR Newswire", "Business Technology", PRN + "business-technology-latest-news/business-technology-latest-news-list.rss"),
    ("PR Newswire", "Policy & Public Interest", PRN + "policy-public-interest-latest-news/policy-public-interest-latest-news-list.rss"),
    # Business Wire codes are opaque; each was checked against the feed's own <channel><title>.
    ("Business Wire", "Merger/Acquisition", BW + "G1QFDERJXkJeEFtRWA=="),
    ("Business Wire", "Manufacturing", BW + "G1QFDERJXkJeEFpTXA=="),
    ("Business Wire", "Manufacturing: Aerospace", BW + "G1QFDERJXkJeGFNZXQ=="),
    ("Business Wire", "Manufacturing: Steel", BW + "G1QFDERJXkJeGFNZWw=="),
    ("Business Wire", "Manufacturing: Machine Tools, Metalworking & Metallurgy", BW + "G1QFDERJXkJaF1tQWA=="),
    ("Business Wire", "Natural Resources: Mining/Minerals", BW + "G1QFDERJXkJeGFNYXQ=="),
    ("Business Wire", "Energy: Oil/Gas", BW + "G1QFDERJXkJeGFNSVQ=="),
    ("Business Wire", "Health: Pharmaceutical", BW + "G1QFDERJXkJeGFNWWg=="),
    ("Business Wire", "Health: Oncology", BW + "G1QFDERJXkJeGFNWWQ=="),
    ("Business Wire", "Professional Services: Banking", BW + "G1QFDERJXkJeGFNTXA=="),
    ("Business Wire", "Professional Services: Business", BW + "G1QFDERJXkJaF1tQVQ=="),
    ("Business Wire", "Communications: Public Relations/Investor Relations", BW + "G1QFDERJXkJeGVpUWg=="),
    ("Business Wire", "Public Policy/Government: Public Policy", BW + "G1QFDERJXkJeGVpTXA=="),
]
# Official IR-site feeds for names we hold or watch closely. Items carry no ticker text, so the
# ticker is assigned here. Q4-hosted IR sites serve /rss/PressRelease.aspx?LanguageId=1.
OFFICIAL_FEEDS = [  # (ticker, exchange, feed name, url)
    ("MTUS", "NYSE", "Metallus IR press releases", "https://investors.metallus.com/rss/PressRelease.aspx?LanguageId=1"),
]

# ---------- exchanges and tickers ----------
EXCHANGES = [  # (label regex, canonical); longer labels first, the alternation is tried in order
    (r"NYSE[\s-]*American|NYSE[\s-]*MKT|NYSE[\s-]*Amex|AMEX", "NYSE American"),
    (r"NYSE[\s-]*Arca", "NYSE Arca"),
    (r"NYSE", "NYSE"),
    (r"Nasdaq(?:[\s-]*(?:GS|GM|CM|Global[\s-]+Select(?:[\s-]+Market)?|Global[\s-]+Market|Capital[\s-]+Market"
     r"|Stock[\s-]+Market|SmallCap))?", "NASDAQ"),
    (r"OTCQX(?:[\s-]*Best[\s-]+Market)?", "OTCQX"),
    (r"OTCQB(?:[\s-]*Venture[\s-]+Market)?", "OTCQB"),
    (r"OTC[\s-]*Pink|OTC[\s-]*Markets|Other[\s-]*OTC|OTC", "OTC"),
    (r"TSX[\s-]*Venture(?:[\s-]+Exchange)?|TSX[\s-]*V|TSXV", "TSXV"),
    (r"TSX", "TSX"),
    (r"CSE|CNSX", "CSE"),
    (r"Cboe[\s-]*Canada|NEO(?:[\s-]+Exchange)?", "Cboe Canada"),
    (r"Cboe(?:[\s-]*BZX)?|BATS", "Cboe"),
    (r"ASX|AUST", "ASX"),
    (r"LSE|AIM", "LSE"),
    (r"Frankfurt|FSE|XETRA", "Frankfurt"),
    (r"HKSE|HKEX|SEHK", "HKEX"),
]
US_LISTED = {"NYSE", "NASDAQ", "NYSE American"}                          # rule b: tradeable listings
US_VENUES = US_LISTED | {"NYSE Arca", "Cboe", "OTCQX", "OTCQB", "OTC"}  # rule a: where a watch ticker trades
LABELS = "|".join(f"(?:{rx})" for rx, _ in EXCHANGES)
TICKER = r"[A-Z][A-Z0-9]{0,5}(?:[.\-][A-Z0-9]{1,3})?"
# "(NYSE: MTUS)", "(NASDAQ:ELMT)", "(NYSE: MOG.A and MOG.B)", "(TSXV: ABC; OTCQB: ABCF)",
# '(NASDAQ SmallCap: "TAYD")', and the full-width colon of Japanese releases "（Nasdaq：AGEN）"
LISTING_RX = re.compile(rf"(?<![A-Za-z])((?i:{LABELS}))\s*[:\uff1a]\s*[\"'\u201c\u2018]?"
                        rf"({TICKER}(?:\s*(?:,|/|&|\band\b)\s*{TICKER})*)")
# "...begin trading on the NYSE American under the ticker symbol "XYZ""
SYMBOL_RX = re.compile(rf"(?<![A-Za-z])((?i:{LABELS}))\b[^.;()]{{0,80}}?\b(?i:symbol)\s*[\"'\u201c\u2018]?({TICKER})\b")

# Wire items that are not company-issued: law-firm solicitations and paid stock promotion.
THIRD_PARTY = re.compile(
    r"\b(?:investor|shareholder|stockholder|deadline)s?\s+(?:alert|notice|reminder)\b"
    r"|\b(?:investor|filing|lead[\s-]+plaintiff)\s+deadline\b|\blead[\s-]+plaintiff\b"
    r"|\binvestors?\s+(?:who|with)\b.{0,40}\blos(?:s|ses|t)\b"
    r"|\b(?:encourages|reminds|alerts|notifies|invites)\b.{0,80}\b(?:investors|shareholders|stockholders)\b"
    r".{0,80}\b(?:contact|losses|lawsuit|class action|the firm)\b"
    r"|\binvestigat\w*\b.{0,60}\bon behalf of\b"
    r"|\b(?:news|market)\s+commentary\b|\bpaid\s+(?:advertisement|promotion)\b|\bsponsored\s+content\b",
    re.I)
# Issuer names: a law firm by name, or an LLP writing about litigation (plain "LLP" alone also
# covers real companies, e.g. Samfara LLP announcing its own acquisition).
THIRD_PARTY_ISSUER = re.compile(r"\b(?:law|lawyers?|attorneys?)\b", re.I)
LITIGATION = re.compile(r"\b(?:class action|lawsuit|investor|shareholder|stockholder|securities fraud"
                        r"|investigation|data breach|deadline|losses)\b", re.I)

KEYWORD_RX = [(kw, re.compile(r"(?<![A-Za-z0-9])" + r"[\s\-]*".join(re.escape(p) for p in re.split(r"[\s\-]+", kw))
                              + r"(?![A-Za-z0-9])", re.I)) for kw in CATALYST_KEYWORDS]
LABEL_RANK = {"position": 0, "watchlist": 1, "signal": 2, "manual_call": 3}


def norm_exchange(label):
    label = " ".join(label.split())
    for rx, canon in EXCHANGES:
        if re.fullmatch(rx, label, re.I):
            return canon
    return label.upper()


def norm_ticker(t):
    return (t or "").strip().upper().replace("-", ".")


def find_listings(text):
    """[(ticker, exchange)] in order of appearance, from "(NYSE: MTUS)"-style mentions."""
    out = []
    for m in LISTING_RX.finditer(text):
        ex = norm_exchange(m.group(1))
        out += [(norm_ticker(t), ex) for t in re.findall(TICKER, m.group(2))]
    for m in SYMBOL_RX.finditer(text):
        out.append((norm_ticker(m.group(2)), norm_exchange(m.group(1))))
    return list(dict.fromkeys(out))


# ---------- fetching ----------
_last_hit = {}


def fetch(url):
    """GET with browser headers, <= 1 request/second/host, 20s timeout, one retry on transient errors."""
    host = urllib.parse.urlsplit(url).netloc
    for attempt in (1, 2):
        wait = HOST_GAP - (time.monotonic() - _last_hit.get(host, float("-inf")))
        if wait > 0:
            time.sleep(wait)
        _last_hit[host] = time.monotonic()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=BROWSER), timeout=TIMEOUT) as r:
                raw, enc = r.read(), r.headers.get("Content-Encoding", "")
            if enc == "gzip":
                raw = gzip.decompress(raw)
            elif enc == "deflate":
                raw = zlib.decompress(raw)
            return raw
        except urllib.error.HTTPError as e:
            if attempt == 2 or (e.code < 500 and e.code != 429):
                raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt == 2:
                raise
        time.sleep(3)


def interleave(feeds):
    """Round-robin across hosts so the per-host gap overlaps with requests to the other wires."""
    queues = {}
    for f in feeds:
        queues.setdefault(urllib.parse.urlsplit(f["url"]).netloc, []).append(f)
    out, qs = [], list(queues.values())
    while any(qs):
        out += [q.pop(0) for q in qs if q]
    return out


# ---------- parsing ----------
def local(tag):
    return tag.rsplit("}", 1)[-1].lower() if isinstance(tag, str) else ""


def clean(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    return " ".join(s.replace("\u00ad", "").split())


def parse_date(s):
    s = (s or "").strip()
    if not s:
        return None
    try:
        d = parsedate_to_datetime(re.sub(r" UT$", " GMT", s))       # RFC 822 (RSS); Business Wire writes "UT"
    except (TypeError, ValueError, IndexError):
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))    # ISO 8601 (Atom)
        except ValueError:
            return None
    return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)


def parse_feed(raw, wire, feed, fixed=None):
    """RSS 2.0 or Atom bytes -> item dicts. `fixed` = (ticker, exchange) for an official IR feed."""
    root = ET.fromstring(raw)
    items = []
    for node in (el for el in root.iter() if local(el.tag) in ("item", "entry")):
        f, link, cats = {}, "", []
        for ch in node:
            name, text = local(ch.tag), (ch.text or "").strip()
            if name == "link":
                href = ch.get("href")
                if href and ch.get("rel", "alternate") == "alternate":
                    link = link or href.strip()
                elif text:
                    link = link or text
            elif name == "category":
                cats.append((ch.get("domain") or ch.get("scheme") or "", text or ch.get("term") or ""))
            elif name == "author":
                f.setdefault(name, " ".join(" ".join(ch.itertext()).split()))
            else:
                f.setdefault(name, text)
        if not link and f.get("guid", "").startswith("http"):
            link = f["guid"]
        title = clean(f.get("title"))
        summary = clean(f.get("description") or f.get("summary") or f.get("content") or f.get("encoded"))
        listings = [fixed] if fixed else []
        for domain, value in cats:                     # GlobeNewswire: <category domain=".../rss/stock">NYSE:MTUS
            if "stock" in domain.lower() and ":" in value:
                ex, t = value.rsplit(":", 1)
                listings.append((norm_ticker(t), norm_exchange(ex)))
        listings += find_listings(f"{title} {summary}")
        items.append({"wire": wire, "feed": feed, "title": title, "link": link.strip(), "summary": summary,
                      "issuer": f.get("contributor") or f.get("author") or f.get("creator") or "",
                      "published": parse_date(f.get("pubdate") or f.get("published") or f.get("updated")
                                              or f.get("date") or f.get("modified")),
                      "listings": list(dict.fromkeys(listings)), "official": bool(fixed)})
    return items


# ---------- matching ----------
def read_csv(path):
    return list(csv.DictReader(open(path, encoding="utf-8", newline=""))) if path.exists() else []


def load_universe(now):
    """{ticker: label}; label is the strongest reason we care: position > watchlist > signal > manual_call."""
    uni = {}

    def add(t, label):
        t = norm_ticker(t)
        if t and (t not in uni or LABEL_RANK[label] < LABEL_RANK[uni[t]]):
            uni[t] = label
    try:
        for t in json.loads(WATCHLIST.read_text(encoding="utf-8")).get("tickers", []):
            add(t, "watchlist")
    except (OSError, ValueError) as e:
        print(f"  warning: watchlist not read ({e})")
    for r in read_csv(SIGNALS):
        d = parse_date(r.get("detected_at_utc"))
        if d and now - d <= timedelta(days=SIGNAL_DAYS):
            add(r.get("ticker"), "signal")
    for r in read_csv(TRADES):
        # trades.csv has no status column yet: a trade is open while exit_date and exit are blank
        if "status" in r:
            is_open = (r.get("status") or "").strip().upper() == "OPEN"
        else:
            is_open = not (r.get("exit_date") or "").strip() and not (r.get("exit") or "").strip()
        if is_open:
            add(r.get("symbol") or r.get("ticker"), "position")
    for r in read_csv(MANUAL):
        add(r.get("ticker"), "manual_call")
    return uni


def third_party(item):
    text = f"{item['title']} {item['summary'][:400]}"
    return bool(THIRD_PARTY.search(text) or THIRD_PARTY_ISSUER.search(item["issuer"])
                or (re.search(r"\bLLP\b", item["issuer"]) and LITIGATION.search(text)))


def classify(item, universe):
    """-> (listings to report, matched_on list) or None. Rule a: watch ticker; rule b: keyword + US listing."""
    watch = [(t, ex) for t, ex in item["listings"] if ex in US_VENUES and t in universe]
    us = [(t, ex) for t, ex in item["listings"] if ex in US_LISTED]
    text = f"{item['title']} {item['summary']}"
    kws = [f"keyword:{kw}" for kw, rx in KEYWORD_RX if rx.search(text)]
    if watch:
        best = min((universe[t] for t, _ in watch), key=LABEL_RANK.get)
        listings, matched = watch + us, [best] + kws
    elif kws and us:
        listings, matched = us, kws
    else:
        return None
    seen_t, out = set(), []
    for t, ex in listings:
        if t not in seen_t:
            seen_t.add(t)
            out.append((t, ex))
    return out, matched


def norm_link(u):
    p = urllib.parse.urlsplit(u.strip())
    return urllib.parse.urlunsplit(("https", p.netloc.lower(), p.path.rstrip("/"), "", ""))


def digest(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def item_keys(item, ticker):
    """Link hash, plus ticker+title so the IR-site copy of a wire release isn't reported twice."""
    keys = ["l:" + digest(norm_link(item["link"]))]
    if ticker:
        title = " ".join(re.sub(r"[^a-z0-9]+", " ", item["title"].lower()).split())
        keys.append("t:" + digest(f"{ticker}|{title}"))
    return keys


def select(items, universe, seen, now):
    """Flag, filter and dedupe. -> (new hit rows, stats)."""
    st = {"items": len(items), "unique": len({norm_link(i["link"]) for i in items if i["link"]}),
          "third_party": 0, "flagged": 0, "old": 0, "already": 0}
    hits, run_keys, tp_links = [], set(), set()
    cutoff = now - timedelta(days=MAX_AGE_DAYS)
    for it in sorted(items, key=lambda i: i["official"]):          # wire copy wins over the IR-site copy
        if not it["link"] or not it["title"]:
            continue
        if not it["official"] and third_party(it):
            tp_links.add(norm_link(it["link"]))
            continue
        res = classify(it, universe)
        if res is None:
            continue
        listings, matched = res
        keys = item_keys(it, listings[0][0])
        if keys[0] in run_keys:                                    # same release in several feeds
            continue
        st["flagged"] += 1
        if it["published"] and it["published"] < cutoff:
            st["old"] += 1
            run_keys.update(keys)
            continue
        if any(k in seen or k in run_keys for k in keys):
            st["already"] += 1
            run_keys.update(keys)
            continue
        run_keys.update(keys)
        hits.append({"published_utc": it["published"].strftime("%Y-%m-%dT%H:%M:%SZ") if it["published"] else "",
                     "wire": it["wire"], "ticker": ";".join(t for t, _ in listings),
                     "exchange": ";".join(ex for _, ex in listings), "title": it["title"], "link": it["link"],
                     "matched_on": ";".join(matched), "_keys": keys, "_feed": it["feed"]})
    st["third_party"] = len(tp_links)
    hits.sort(key=lambda h: h["published_utc"], reverse=True)       # newest first...
    hits.sort(key=lambda h: not is_watch(h))                         # ...watchlist/position hits on top
    return hits, st


def is_watch(row):
    return not row["matched_on"].startswith("keyword:")


# ---------- output ----------
def load_seen():
    try:
        return json.loads(SEEN.read_text(encoding="utf-8")).get("seen", {})
    except (OSError, ValueError):
        return {}


def save_seen(seen, now):
    keep = (now - timedelta(days=SEEN_KEEP_DAYS)).strftime("%Y-%m-%d")
    seen = {k: v for k, v in seen.items() if v >= keep}
    SEEN.write_text(json.dumps({"_note": "sha256[:16] of reported press releases: l: = normalised link, "
                                         "t: = ticker|title. Value = date first reported (UTC). "
                                         "Written by collectors/press_wires.py.",
                                "seen": dict(sorted(seen.items()))}, indent=1) + "\n", encoding="utf-8")


def md_line(r):
    title = r["title"].replace("[", "(").replace("]", ")")
    when = r["published_utc"][:16].replace("T", " ") + "Z" if r["published_utc"] else "undated"
    return f"- **{r['ticker']}** ({r['exchange']}), {when}, {r['wire']}: [{title}]({r['link']}). Matched: `{r['matched_on']}`"


def write_digest(day, rows, status, stamp, n_new):
    watch = sorted((r for r in rows if is_watch(r)), key=lambda r: r["published_utc"], reverse=True)
    kw = sorted((r for r in rows if not is_watch(r)), key=lambda r: r["published_utc"], reverse=True)
    ok = [s for s in status if s["ok"]]
    per_wire = {}
    for s in status:
        a = per_wire.setdefault(s["wire"], [0, 0, 0])
        a[0] += s["ok"]
        a[1] += 1
        a[2] += s["items"]
    lines = [f"# Press releases {day}", "",
             "Company-issued releases from the wires and official IR feeds (collectors/press_wires.py). "
             "Each release is listed once, on the day it was first seen.", "",
             f"Last run {stamp}: {len(ok)}/{len(status)} feeds OK, {n_new} new hits. "
             + ", ".join(f"{w} {a[0]}/{a[1]} feeds, {a[2]} items" for w, a in per_wire.items()) + ".", "",
             f"## Watchlist / position hits ({len(watch)})", ""]
    lines += [md_line(r) for r in watch] or ["None today."]
    lines += ["", f"## Keyword hits, NYSE / Nasdaq / NYSE American only ({len(kw)})", ""]
    lines += [md_line(r) for r in kw] or ["None today."]
    failed = [s for s in status if not s["ok"]]
    lines += ["", f"## Feeds that failed on the last run ({len(failed)})", ""]
    lines += [f"- {s['wire']} / {s['feed']}: {s['error']}" for s in failed] or ["None."]
    (OUTDIR / f"{day}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------- main ----------
def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print hits; write nothing")
    ap.add_argument("--self-test", action="store_true", help="offline parser/matcher check")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    now = datetime.now(timezone.utc)
    stamp, day = now.strftime("%Y-%m-%dT%H:%MZ"), now.strftime("%Y-%m-%d")
    universe = load_universe(now)
    seen = load_seen()
    feeds = ([{"wire": w, "feed": n, "url": u, "fixed": None} for w, n, u in FEEDS]
             + [{"wire": "Company IR", "feed": n, "url": u, "fixed": (t, ex)} for t, ex, n, u in OFFICIAL_FEEDS])

    status, items = [], []
    for f in interleave(feeds):
        t0 = time.monotonic()
        try:
            got = parse_feed(fetch(f["url"]), f["wire"], f["feed"], f["fixed"])
            status.append({"wire": f["wire"], "feed": f["feed"], "ok": True, "items": len(got), "error": ""})
            items += got
        except ET.ParseError as e:
            status.append({"wire": f["wire"], "feed": f["feed"], "ok": False, "items": 0,
                           "error": f"not XML ({e}); blocked or feed retired?"})
        except Exception as e:          # one bad feed must never stop the run
            status.append({"wire": f["wire"], "feed": f["feed"], "ok": False, "items": 0,
                           "error": f"{type(e).__name__}: {e}"})
        s = status[-1]
        print(f"  [{'ok' if s['ok'] else 'FAIL'}] {s['wire']} / {s['feed']}: "
              f"{s['items'] if s['ok'] else s['error']}{' items' if s['ok'] else ''} ({time.monotonic() - t0:.1f}s)",
              flush=True)

    hits, st = select(items, universe, seen, now)
    n_ok = sum(s["ok"] for s in status)
    n_watch = sum(is_watch(h) for h in hits)
    print(f"\nPress wires {stamp}: {n_ok}/{len(status)} feeds OK, {st['items']} items ({st['unique']} unique), "
          f"{st['third_party']} law-firm/promo items skipped.")
    print(f"Watch universe: {len(universe)} tickers ({', '.join(f'{t}={l}' for t, l in sorted(universe.items()))}).")
    print(f"Flagged {st['flagged']}: {len(hits)} new ({n_watch} watchlist/position, {len(hits) - n_watch} keyword), "
          f"{st['already']} already reported, {st['old']} older than {MAX_AGE_DAYS} days.")
    for h in hits:
        print(f"  [{h['matched_on']}] {h['ticker']} {h['published_utc'][:16]} {h['wire']}: {h['title'][:110]}")

    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return 0 if n_ok else 2
    DATA.mkdir(parents=True, exist_ok=True)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    for h in hits:
        for k in h["_keys"]:
            seen[k] = day
    save_seen(seen, now)
    rows = [{c: h[c] for c in CSV_COLS} for h in hits]
    day_csv = DATA / f"{day}.csv"
    new_file = not day_csv.exists()
    with open(day_csv, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLS)
        if new_file:
            w.writeheader()
        w.writerows(rows)
    latest = [{k: h[k] for k in ("published_utc", "wire", "ticker", "title", "link", "matched_on")} for h in hits]
    (OUTDIR / "latest.json").write_text(json.dumps(latest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    write_digest(day, read_csv(day_csv), status, stamp, len(hits))
    print(f"\nReport: {OUTDIR / f'{day}.md'}\nCSV: {day_csv}\nNew this run: {OUTDIR / 'latest.json'}")
    return 0 if n_ok else 2                                         # every feed failing should fail the job


# ---------- self-test (offline) ----------
SAMPLE_PRN = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/"><channel><title>Aerospace &amp; Defense</title>
<item><title>Metallus Receives Initial $125 Million Delivery Order from U.S. Defense Logistics Agency</title>
<link>https://www.prnewswire.com/news-releases/metallus-sample-302000001.html?tc=eml_cleartime</link>
<pubDate>Tue, 29 Sep 2026 13:20:00 +0000</pubDate>
<description><![CDATA[<p>CANTON, Ohio, Sept. 29, 2026 /PRNewswire/ -- Metallus Inc. (NYSE: MTUS) today announced an initial
$125 million delivery order under its sole-source contract...</p>]]></description>
<dc:contributor>Metallus Inc.</dc:contributor></item>
<item><title>INVESTOR ALERT: Metallus Inc. (NYSE: MTUS) Investors with Losses Encouraged to Contact the Firm</title>
<link>https://www.prnewswire.com/news-releases/law-firm-sample-302000002.html</link>
<pubDate>Tue, 29 Sep 2026 14:00:00 +0000</pubDate><description>Example Law LLP announces...</description>
<dc:contributor>Example Law LLP</dc:contributor></item>
<item><title>Defense Small Caps Rally on New Delivery Order</title>
<link>https://www.prnewswire.com/news-releases/promo-sample-302000003.html</link>
<pubDate>Tue, 29 Sep 2026 15:00:00 +0000</pubDate>
<description>Example Preachers News Commentary - Metallus (NYSE: MTUS) delivery order...</description>
<dc:contributor>Example Preachers</dc:contributor></item>
<item><title>Northern Example Metals Signs Definitive Agreement</title>
<link>https://www.prnewswire.com/news-releases/tsxv-sample-302000004.html</link>
<pubDate>Tue, 29 Sep 2026 16:00:00 +0000</pubDate>
<description>Northern Example Metals Corp. (TSXV: NEM) (OTCQB: NEMXF) signed a definitive agreement...</description></item>
<item><title>Example Antimony Awarded a Contract by the Defense Logistics Agency</title>
<link>https://www.prnewswire.com/news-releases/amex-sample-302000005.html</link>
<pubDate>Tue, 29 Sep 2026 17:00:00 +0000</pubDate>
<description>Example Antimony Corp. (NYSE American: XSB) was awarded a contract...</description></item>
<item><title>Example Corp Names New Chief Financial Officer</title>
<link>https://www.prnewswire.com/news-releases/cfo-sample-302000006.html</link>
<pubDate>Tue, 29 Sep 2026 18:00:00 +0000</pubDate><description>Example Corp (NASDAQ: EXMP) named...</description></item>
<item><title>Moog Enters Merger Agreement</title>
<link>https://www.prnewswire.com/news-releases/moog-sample-302000007.html</link>
<pubDate>Tue, 29 Sep 2026 19:00:00 +0000</pubDate><description>Moog Inc. (NYSE: MOG.A and MOG.B) entered a merger agreement...</description></item>
<item><title>Old Contract Award</title><link>https://www.prnewswire.com/news-releases/old-sample-302000008.html</link>
<pubDate>Mon, 03 Aug 2026 12:00:00 +0000</pubDate><description>Example (NYSE: OLDC) contract award...</description></item>
</channel></rss>"""
SAMPLE_GNW = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel xmlns:dc="http://dublincore.org/documents/dcmi-namespace/"><title>GlobeNewswire - Defense</title>
<item><guid isPermaLink="true">https://www.globenewswire.com/news-release/2026/09/14/1/0/en/elmet-sample.html</guid>
<link>https://www.globenewswire.com/news-release/2026/09/14/1/0/en/elmet-sample.html</link>
<category domain="https://www.globenewswire.com/rss/stock">Nasdaq:ELMT</category>
<title>The Elmet Group Awarded $2 Billion IDIQ Contract to Supply the National Defense Stockpile</title>
<description><![CDATA[The Elmet Group Co. (NASDAQ: ELMT) was awarded a $2 billion IDIQ contract by the Defense Logistics Agency...]]></description>
<pubDate>Mon, 14 Sep 2026 11:00 GMT</pubDate><dc:contributor>The Elmet Group Co.</dc:contributor></item>
</channel></rss>"""
SAMPLE_ATOM = """<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom"><title>Example</title>
<entry><title>Example Bio Announces Uplisting</title><link rel="alternate" href="https://example.com/news/uplist"/>
<updated>2026-09-28T12:00:00Z</updated><author><name>Example Bio</name></author>
<summary>Example Bio (OTCQB: EXBO) shares will begin trading on the Nasdaq Capital Market under the ticker
symbol &#8220;EXBO&#8221; on October 1, 2026.</summary></entry></feed>"""
SAMPLE_IR = """<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel><title>Metallus Inc. Press Releases</title>
<item><title>Metallus receives initial $125 million delivery order from U.S. Defense Logistics Agency.</title>
<link>https://investors.metallus.com/news/news-details/2026/sample/default.aspx</link>
<pubDate>Tue, 29 Sep 2026 09:20:00 -0400</pubDate><description></description></item>
<item><title>Metallus Announces Planned Retirement of Chief Executive Officer</title>
<link>https://investors.metallus.com/news/news-details/2026/ceo-sample/default.aspx</link>
<pubDate>Mon, 28 Sep 2026 16:30:00 -0400</pubDate><description></description></item>
</channel></rss>"""


def self_test():
    now = datetime(2026, 9, 30, 12, tzinfo=timezone.utc)
    uni = {"MTUS": "position", "THRM": "watchlist"}
    items = (parse_feed(SAMPLE_PRN.encode(), "PR Newswire", "sample")
             + parse_feed(SAMPLE_GNW.encode(), "GlobeNewswire", "sample")
             + parse_feed(SAMPLE_ATOM.encode(), "Atom", "sample")
             + parse_feed(SAMPLE_IR.encode(), "Company IR", "sample", fixed=("MTUS", "NYSE")))
    checks = []

    def check(name, cond):
        checks.append((name, bool(cond)))

    mt = items[0]
    check("parser: '(NYSE: MTUS)' -> ticker MTUS on NYSE", mt["listings"] == [("MTUS", "NYSE")])
    check("parser: pubDate -> UTC", mt["published"] == datetime(2026, 9, 29, 13, 20, tzinfo=timezone.utc))
    check("parser: HTML stripped from summary", "<p>" not in mt["summary"] and "(NYSE: MTUS)" in mt["summary"])
    check("parser: 'NYSE: MOG.A and MOG.B' -> both classes", items[6]["listings"] == [("MOG.A", "NYSE"), ("MOG.B", "NYSE")])
    check("parser: '(TSXV: NEM) (OTCQB: NEMXF)'", items[3]["listings"] == [("NEM", "TSXV"), ("NEMXF", "OTCQB")])
    check("parser: GNW <category> Nasdaq:ELMT", ("ELMT", "NASDAQ") in items[8]["listings"])
    check("parser: Atom entry + 'under the ticker symbol' -> NASDAQ EXBO",
          items[9]["link"] == "https://example.com/news/uplist" and ("EXBO", "NASDAQ") in items[9]["listings"])
    check("parser: GNW 'Mon, 14 Sep 2026 11:00 GMT' (no seconds)", items[8]["published"] is not None)
    check("parser: '(NASDAQ SmallCap: \"TAYD\")'", find_listings('Taylor Devices, Inc. (NASDAQ SmallCap: "TAYD")')
          == [("TAYD", "NASDAQ")])
    check("parser: full-width '（Nasdaq：AGEN）'", find_listings("アジーナス （Nasdaq：AGEN）は") == [("AGEN", "NASDAQ")])
    check("parser: 'listed on the NYSE: the' is not a ticker", find_listings("listed on the NYSE: the company") == [])

    def wire_item(title, issuer, summary=""):
        return {"title": title, "issuer": issuer, "summary": summary}
    check("filter: LLP company announcing its own deal is kept",
          not third_party(wire_item("Samfara completes acquisition of Chr. Olesen Synthesis", "Samfara LLP")))
    check("filter: LLP law-firm deadline notice dropped",
          third_party(wire_item("AST SpaceMobile, Inc. Investors: November 13, 2026, Filing Deadline in Securities "
                                "Fraud Class Action", "Kessler Topaz Meltzer & Check LLP")))
    check("filter: company release about its own lawsuit win is kept",
          not third_party(wire_item("Example Corp Wins Dismissal of Patent Lawsuit", "Example Corp")))

    elmet = items.pop(8)                                     # 14 Sep release: checked as of its own day below
    elmet_day = datetime(2026, 9, 14, 18, tzinfo=timezone.utc)
    hits, st = select(items, uni, {}, now)
    by = {h["link"]: h for h in hits}
    h = by.get(mt["link"])
    check("rule a: MTUS release flagged as position", h and h["matched_on"].split(";")[0] == "position"
          and h["ticker"] == "MTUS" and h["exchange"] == "NYSE")
    check("rule a: MTUS keywords recorded", h and "keyword:delivery order" in h["matched_on"]
          and "keyword:Defense Logistics Agency" in h["matched_on"] and "keyword:sole-source" in h["matched_on"])
    e_hits, _ = select([elmet], uni, {}, elmet_day)
    e = e_hits[0] if e_hits else None
    check("rule b: Elmet (NASDAQ: ELMT) keyword hit", e and e["ticker"] == "ELMT" and e["exchange"] == "NASDAQ"
          and "keyword:National Defense Stockpile" in e["matched_on"] and "keyword:IDIQ" in e["matched_on"])
    check("rule b: NYSE American ticker kept", any(x["ticker"] == "XSB" and x["exchange"] == "NYSE American" for x in hits))
    check("rule b: Nasdaq uplisting kept", any(x["ticker"] == "EXBO" for x in hits))
    check("rule b: TSXV/OTC-only keyword item dropped", not any("NEM" in x["ticker"] for x in hits))
    check("rule b: US ticker without keyword dropped", not any(x["ticker"] == "EXMP" for x in hits))
    check("law-firm alert dropped", not any("law-firm" in x["link"] for x in hits))
    check("paid promotion dropped", not any("promo" in x["link"] for x in hits) and st["third_party"] == 2)
    check("older than 7 days not reported", not any(x["ticker"] == "OLDC" for x in hits) and st["old"] == 1)
    check("IR-site copy of the PRN release deduped", not any(x["link"].endswith("2026/sample/default.aspx") for x in hits))
    check("other IR-site release flagged (ticker assigned)", any("ceo-sample" in x["link"] and x["ticker"] == "MTUS"
                                                                 for x in hits))
    seen = {k: "2026-09-30" for x in hits for k in x["_keys"]}
    hits2, st2 = select(items, uni, seen, now)
    check("second run: nothing reported twice", hits2 == [] and st2["already"] == st["already"] + len(hits))
    variant = dict(mt, link=mt["link"].split("?")[0] + "?tc=other", feed="other")
    check("dedupe ignores query string", item_keys(variant, "MTUS")[0] == item_keys(mt, "MTUS")[0])

    # the real watch universe from the repo: an MTUS release would be caught as a position/watchlist hit
    real = load_universe(datetime.now(timezone.utc))
    r_hits, _ = select([mt], real, {}, now)
    r_el, _ = select([elmet], real, {}, elmet_day)
    r_mt = next((x for x in r_hits if x["ticker"] == "MTUS"), None)
    check(f"repo universe ({len(real)} tickers) contains MTUS", "MTUS" in real)
    check("repo universe: MTUS release flagged", r_mt and r_mt["matched_on"].split(";")[0] in ("position", "watchlist"))
    check("repo universe: ELMT release flagged", any(x["ticker"] == "ELMT" for x in r_el))

    for name, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    print("\nSample hits (fixtures):")
    for x in hits + e_hits:
        print(f"  [{x['matched_on']}] {x['ticker']} ({x['exchange']}) {x['wire']}: {x['title']}")
    print("Against the repo's real watch universe:")
    for x in r_hits + r_el:
        print(f"  [{x['matched_on']}] {x['ticker']} ({x['exchange']}) {x['wire']}: {x['title']}")
    failed = [n for n, ok in checks if not ok]
    print(f"\n{len(checks) - len(failed)}/{len(checks)} checks passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
